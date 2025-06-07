"""
User Settings Service for RepoChat v1.0

Provides high-level service for managing user settings, preferences, and API keys.
Implements secure storage, validation, and encryption.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from shared.utils.logging_config import get_logger
from shared.models.user_settings import (
    UserSettings, UserPreferences, UserSecuritySettings,
    EncryptedAPIKey, APIKeyProvider, APIKeyManager,
    APIKeyRequest, APIKeyResponse, UserRole
)


class UserSettingsService:
    """Service for managing user settings and API keys."""
    
    def __init__(self, storage_dir: Optional[str] = None, master_key: Optional[str] = None):
        """
        Initialize user settings service.
        
        Args:
            storage_dir: Directory to store user settings files
            master_key: Master encryption key for API keys
        """
        self.logger = get_logger("services.user_settings")
        
        # Setup storage directory
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".repochat" / "user_settings"
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize API key manager
        self.api_key_manager = APIKeyManager(master_key)
        
        # Cache for user settings
        self._settings_cache: Dict[str, UserSettings] = {}
        
        self.logger.info(f"UserSettingsService initialized with storage: {self.storage_dir}")
    
    def get_user_settings(self, user_id: str, create_if_not_exists: bool = True) -> Optional[UserSettings]:
        """
        Get user settings by user ID.
        
        Args:
            user_id: User identifier
            create_if_not_exists: Create default settings if user doesn't exist
            
        Returns:
            UserSettings object or None
        """
        # Check cache first
        if user_id in self._settings_cache:
            return self._settings_cache[user_id]
        
        # Load from file
        settings_file = self.storage_dir / f"{user_id}.json"
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                settings = self._deserialize_user_settings(data)
                self._settings_cache[user_id] = settings
                
                self.logger.info(f"Loaded settings for user: {user_id}")
                return settings
                
            except Exception as e:
                self.logger.error(f"Failed to load settings for user {user_id}: {e}")
                if create_if_not_exists:
                    return self._create_default_settings(user_id)
                return None
        
        elif create_if_not_exists:
            return self._create_default_settings(user_id)
        
        return None
    
    def save_user_settings(self, settings: UserSettings) -> bool:
        """
        Save user settings to storage.
        
        Args:
            settings: UserSettings object to save
            
        Returns:
            True if successful
        """
        try:
            settings.updated_at = datetime.now()
            
            # Serialize to JSON
            data = self._serialize_user_settings(settings)
            
            # Save to file
            settings_file = self.storage_dir / f"{settings.user_id}.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            # Update cache
            self._settings_cache[settings.user_id] = settings
            
            self.logger.info(f"Saved settings for user: {settings.user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save settings for user {settings.user_id}: {e}")
            return False
    
    def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            preferences: Dictionary of preference updates
            
        Returns:
            True if successful
        """
        settings = self.get_user_settings(user_id)
        if not settings:
            return False
        
        try:
            # Update preferences
            for key, value in preferences.items():
                if hasattr(settings.preferences, key):
                    setattr(settings.preferences, key, value)
            
            return self.save_user_settings(settings)
            
        except Exception as e:
            self.logger.error(f"Failed to update preferences for user {user_id}: {e}")
            return False
    
    def add_api_key(self, user_id: str, request: APIKeyRequest) -> bool:
        """
        Add or update an API key for a user.
        
        Args:
            user_id: User identifier
            request: API key request with provider and key
            
        Returns:
            True if successful
        """
        settings = self.get_user_settings(user_id)
        if not settings:
            return False
        
        try:
            # Encrypt the API key
            encrypted_key = self.api_key_manager.encrypt_api_key(
                request.api_key,
                request.provider,
                request.nickname
            )
            
            # Store in settings
            key_id = f"{request.provider.value}"
            settings.api_keys[key_id] = encrypted_key
            
            # Save settings
            success = self.save_user_settings(settings)
            
            if success:
                self.logger.info(f"Added API key for provider {request.provider} for user: {user_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to add API key for user {user_id}: {e}")
            return False
    
    def get_api_key(self, user_id: str, provider: APIKeyProvider) -> Optional[str]:
        """
        Get decrypted API key for a provider.
        
        Args:
            user_id: User identifier
            provider: API key provider
            
        Returns:
            Decrypted API key or None
        """
        settings = self.get_user_settings(user_id, create_if_not_exists=False)
        if not settings:
            return None
        
        key_id = f"{provider.value}"
        if key_id not in settings.api_keys:
            return None
        
        try:
            encrypted_key = settings.api_keys[key_id]
            
            # Update last used timestamp
            encrypted_key.last_used = datetime.now()
            self.save_user_settings(settings)
            
            # Decrypt and return
            return self.api_key_manager.decrypt_api_key(encrypted_key)
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt API key for user {user_id}, provider {provider}: {e}")
            return None
    
    def list_api_keys(self, user_id: str) -> List[APIKeyResponse]:
        """
        List all API keys for a user (metadata only, no actual keys).
        
        Args:
            user_id: User identifier
            
        Returns:
            List of API key metadata
        """
        settings = self.get_user_settings(user_id, create_if_not_exists=False)
        if not settings:
            return []
        
        responses = []
        for key_id, encrypted_key in settings.api_keys.items():
            response = APIKeyResponse(
                provider=encrypted_key.provider,
                nickname=encrypted_key.nickname,
                created_at=encrypted_key.created_at,
                last_used=encrypted_key.last_used,
                is_valid=encrypted_key.is_valid
            )
            responses.append(response)
        
        return responses
    
    def remove_api_key(self, user_id: str, provider: APIKeyProvider) -> bool:
        """
        Remove an API key for a provider.
        
        Args:
            user_id: User identifier
            provider: API key provider to remove
            
        Returns:
            True if successful
        """
        settings = self.get_user_settings(user_id, create_if_not_exists=False)
        if not settings:
            return False
        
        key_id = f"{provider.value}"
        if key_id in settings.api_keys:
            del settings.api_keys[key_id]
            success = self.save_user_settings(settings)
            
            if success:
                self.logger.info(f"Removed API key for provider {provider} for user: {user_id}")
            
            return success
        
        return True  # Already doesn't exist
    
    def validate_api_key(self, user_id: str, provider: APIKeyProvider, api_key: str) -> bool:
        """
        Validate if provided API key matches stored one.
        
        Args:
            user_id: User identifier
            provider: API key provider
            api_key: API key to validate
            
        Returns:
            True if valid
        """
        settings = self.get_user_settings(user_id, create_if_not_exists=False)
        if not settings:
            return False
        
        key_id = f"{provider.value}"
        if key_id not in settings.api_keys:
            return False
        
        encrypted_key = settings.api_keys[key_id]
        return self.api_key_manager.verify_api_key(api_key, encrypted_key)
    
    def _create_default_settings(self, user_id: str) -> UserSettings:
        """Create default settings for a new user."""
        settings = UserSettings(
            user_id=user_id,
            display_name=f"User {user_id}",
            role=UserRole.USER,
            preferences=UserPreferences(),
            security=UserSecuritySettings()
        )
        
        # Save immediately
        self.save_user_settings(settings)
        
        self.logger.info(f"Created default settings for new user: {user_id}")
        return settings
    
    def _serialize_user_settings(self, settings: UserSettings) -> Dict[str, Any]:
        """Serialize UserSettings to JSON-compatible dict."""
        data = {
            "user_id": settings.user_id,
            "email": settings.email,
            "display_name": settings.display_name,
            "role": settings.role.value,
            "api_keys": {},
            "preferences": settings.preferences.__dict__,
            "security": settings.security.__dict__,
            "created_at": settings.created_at.isoformat(),
            "updated_at": settings.updated_at.isoformat(),
            "last_login": settings.last_login.isoformat() if settings.last_login else None,
            "is_active": settings.is_active
        }
        
        # Serialize encrypted API keys
        for key_id, encrypted_key in settings.api_keys.items():
            data["api_keys"][key_id] = {
                "provider": encrypted_key.provider.value,
                "encrypted_key": encrypted_key.encrypted_key,
                "key_hash": encrypted_key.key_hash,
                "created_at": encrypted_key.created_at.isoformat(),
                "last_used": encrypted_key.last_used.isoformat() if encrypted_key.last_used else None,
                "is_valid": encrypted_key.is_valid,
                "nickname": encrypted_key.nickname
            }
        
        return data
    
    def _deserialize_user_settings(self, data: Dict[str, Any]) -> UserSettings:
        """Deserialize JSON dict to UserSettings."""
        # Deserialize API keys
        api_keys = {}
        for key_id, key_data in data.get("api_keys", {}).items():
            encrypted_key = EncryptedAPIKey(
                provider=APIKeyProvider(key_data["provider"]),
                encrypted_key=key_data["encrypted_key"],
                key_hash=key_data["key_hash"],
                created_at=datetime.fromisoformat(key_data["created_at"]),
                last_used=datetime.fromisoformat(key_data["last_used"]) if key_data.get("last_used") else None,
                is_valid=key_data.get("is_valid", True),
                nickname=key_data.get("nickname")
            )
            api_keys[key_id] = encrypted_key
        
        # Create preferences
        prefs_data = data.get("preferences", {})
        preferences = UserPreferences(**prefs_data)
        
        # Create security settings
        security_data = data.get("security", {})
        security = UserSecuritySettings(**security_data)
        
        # Create main settings object
        settings = UserSettings(
            user_id=data["user_id"],
            email=data.get("email"),
            display_name=data["display_name"],
            role=UserRole(data.get("role", "user")),
            api_keys=api_keys,
            preferences=preferences,
            security=security,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
            is_active=data.get("is_active", True)
        )
        
        return settings 