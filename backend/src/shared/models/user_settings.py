"""
User Settings Models for RepoChat v1.0

Contains data models for user preferences, API keys, and personal settings.
Implements secure storage and encryption for sensitive data.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import hashlib
import base64
from cryptography.fernet import Fernet


class APIKeyProvider(str, Enum):
    """Supported API key providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GENAI = "google_genai"
    AZURE_OPENAI = "azure_openai"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


class UserRole(str, Enum):
    """User roles with different permissions."""
    VIEWER = "viewer"
    USER = "user"
    ADMIN = "admin"
    ENTERPRISE = "enterprise"


@dataclass
class EncryptedAPIKey:
    """Encrypted API key storage."""
    provider: APIKeyProvider
    encrypted_key: str  # Encrypted API key
    key_hash: str  # Hash để verify không lưu plaintext
    created_at: datetime
    last_used: Optional[datetime] = None
    is_valid: bool = True
    nickname: Optional[str] = None  # User-friendly name
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()


@dataclass
class UserPreferences:
    """User preferences and UI settings."""
    language: str = "vi"
    theme: str = "light"
    timezone: str = "Asia/Ho_Chi_Minh"
    date_format: str = "DD/MM/YYYY"
    verbose_output: bool = False
    auto_confirm: bool = False
    notification_email: bool = True
    notification_browser: bool = True
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o-mini"
    max_tokens_default: int = 1000
    temperature_default: float = 0.1


@dataclass 
class UserSecuritySettings:
    """User security and privacy settings."""
    two_factor_enabled: bool = False
    session_timeout_minutes: int = 480  # 8 hours
    allow_data_collection: bool = True
    allow_analytics: bool = True
    ip_whitelist: List[str] = field(default_factory=list)
    require_encryption: bool = True


class UserSettings(BaseModel):
    """Complete user settings model."""
    user_id: str = Field(..., description="Unique user identifier")
    email: Optional[str] = Field(None, description="User email address")
    display_name: str = Field(..., description="User display name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    
    # API Keys - encrypted storage
    api_keys: Dict[str, EncryptedAPIKey] = Field(default_factory=dict)
    
    # User preferences
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    # Security settings
    security: UserSecuritySettings = Field(default_factory=UserSecuritySettings)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        arbitrary_types_allowed = True


class APIKeyManager:
    """Manages encryption/decryption of API keys."""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize with master encryption key."""
        if master_key:
            # Convert string to proper Fernet key
            import base64
            # Pad or truncate to 32 bytes, then base64 encode
            key_bytes = master_key.encode('utf-8')[:32].ljust(32, b'\0')
            key_b64 = base64.urlsafe_b64encode(key_bytes)
            self.cipher = Fernet(key_b64)
        else:
            # Generate new key - in production này sẽ được lưu trong secure storage
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt_api_key(self, api_key: str, provider: APIKeyProvider, nickname: Optional[str] = None) -> EncryptedAPIKey:
        """
        Encrypt an API key for secure storage.
        
        Args:
            api_key: Plain text API key
            provider: API key provider
            nickname: Optional user-friendly name
            
        Returns:
            EncryptedAPIKey object
        """
        # Encrypt the key
        encrypted_key = self.cipher.encrypt(api_key.encode()).decode()
        
        # Create hash for verification (không thể reverse)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        return EncryptedAPIKey(
            provider=provider,
            encrypted_key=encrypted_key,
            key_hash=key_hash,
            created_at=datetime.now(),
            nickname=nickname
        )
    
    def decrypt_api_key(self, encrypted_key: EncryptedAPIKey) -> str:
        """
        Decrypt an API key for use.
        
        Args:
            encrypted_key: EncryptedAPIKey object
            
        Returns:
            Plain text API key
            
        Raises:
            Exception: If decryption fails
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encrypted_key.encode()).decode()
            
            # Verify hash để đảm bảo integrity
            if hashlib.sha256(decrypted.encode()).hexdigest() != encrypted_key.key_hash:
                raise ValueError("API key integrity check failed")
                
            return decrypted
        except Exception as e:
            raise Exception(f"Failed to decrypt API key: {e}")
    
    def verify_api_key(self, api_key: str, encrypted_key: EncryptedAPIKey) -> bool:
        """
        Verify if plain text API key matches encrypted version.
        
        Args:
            api_key: Plain text API key to verify
            encrypted_key: Encrypted version to compare
            
        Returns:
            True if keys match
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return key_hash == encrypted_key.key_hash


class UserSettingsRequest(BaseModel):
    """Request model for updating user settings."""
    user_id: str
    preferences: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None


class APIKeyRequest(BaseModel):
    """Request model for API key operations."""
    provider: APIKeyProvider
    api_key: str
    nickname: Optional[str] = None


class APIKeyResponse(BaseModel):
    """Response model for API key operations."""
    provider: APIKeyProvider
    nickname: Optional[str]
    created_at: datetime
    last_used: Optional[datetime]
    is_valid: bool
    # Note: Never return the actual API key in responses 