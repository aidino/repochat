"""
Unit tests for User Settings Service

Tests encryption, API key management, and user preferences.
"""

import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from services.user_settings_service import UserSettingsService
from shared.models.user_settings import (
    APIKeyProvider, APIKeyRequest, UserRole,
    UserPreferences, UserSecuritySettings
)


class TestUserSettingsService:
    """Test cases for UserSettingsService."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def settings_service(self, temp_dir):
        """Create UserSettingsService instance for testing."""
        return UserSettingsService(
            storage_dir=temp_dir,
            master_key="test_master_key_32_characters_long"
        )
    
    def test_create_default_user_settings(self, settings_service):
        """Test creating default settings for new user."""
        user_id = "test_user_123"
        
        # Get settings (should create default)
        settings = settings_service.get_user_settings(user_id)
        
        assert settings is not None
        assert settings.user_id == user_id
        assert settings.display_name == f"User {user_id}"
        assert settings.role == UserRole.USER
        assert settings.preferences.language == "vi"
        assert settings.preferences.theme == "light"
        assert settings.security.require_encryption is True
        assert len(settings.api_keys) == 0
    
    def test_save_and_load_user_settings(self, settings_service):
        """Test saving and loading user settings."""
        user_id = "test_user_456"
        
        # Create and modify settings
        settings = settings_service.get_user_settings(user_id)
        settings.display_name = "Test User"
        settings.preferences.theme = "dark"
        settings.preferences.language = "en"
        
        # Save settings
        success = settings_service.save_user_settings(settings)
        assert success is True
        
        # Clear cache and reload
        settings_service._settings_cache.clear()
        loaded_settings = settings_service.get_user_settings(user_id)
        
        assert loaded_settings.display_name == "Test User"
        assert loaded_settings.preferences.theme == "dark"
        assert loaded_settings.preferences.language == "en"
    
    def test_update_preferences(self, settings_service):
        """Test updating user preferences."""
        user_id = "test_user_789"
        
        # Update preferences
        preferences_update = {
            "theme": "dark",
            "verbose_output": True,
            "auto_confirm": True,
            "temperature_default": 0.7
        }
        
        success = settings_service.update_preferences(user_id, preferences_update)
        assert success is True
        
        # Verify changes
        settings = settings_service.get_user_settings(user_id)
        assert settings.preferences.theme == "dark"
        assert settings.preferences.verbose_output is True
        assert settings.preferences.auto_confirm is True
        assert settings.preferences.temperature_default == 0.7
    
    def test_add_api_key(self, settings_service):
        """Test adding encrypted API key."""
        user_id = "test_user_api"
        
        # Add API key
        request = APIKeyRequest(
            provider=APIKeyProvider.OPENAI,
            api_key="sk-test123456789abcdef",
            nickname="My OpenAI Key"
        )
        
        success = settings_service.add_api_key(user_id, request)
        assert success is True
        
        # Verify API key was added
        settings = settings_service.get_user_settings(user_id)
        assert len(settings.api_keys) == 1
        
        api_key_data = settings.api_keys["openai"]
        assert api_key_data.provider == APIKeyProvider.OPENAI
        assert api_key_data.nickname == "My OpenAI Key"
        assert api_key_data.encrypted_key != request.api_key  # Should be encrypted
        assert api_key_data.key_hash is not None
    
    def test_get_api_key_decryption(self, settings_service):
        """Test getting and decrypting API key."""
        user_id = "test_user_decrypt"
        original_key = "sk-test987654321fedcba"
        
        # Add API key
        request = APIKeyRequest(
            provider=APIKeyProvider.OPENAI,
            api_key=original_key,
            nickname="Test Key"
        )
        
        settings_service.add_api_key(user_id, request)
        
        # Get decrypted API key
        decrypted_key = settings_service.get_api_key(user_id, APIKeyProvider.OPENAI)
        
        assert decrypted_key == original_key
    
    def test_validate_api_key(self, settings_service):
        """Test API key validation."""
        user_id = "test_user_validate"
        correct_key = "sk-correct123456789"
        wrong_key = "sk-wrong987654321"
        
        # Add API key
        request = APIKeyRequest(
            provider=APIKeyProvider.ANTHROPIC,
            api_key=correct_key
        )
        
        settings_service.add_api_key(user_id, request)
        
        # Test validation
        assert settings_service.validate_api_key(user_id, APIKeyProvider.ANTHROPIC, correct_key) is True
        assert settings_service.validate_api_key(user_id, APIKeyProvider.ANTHROPIC, wrong_key) is False
    
    def test_list_api_keys(self, settings_service):
        """Test listing API keys metadata."""
        user_id = "test_user_list"
        
        # Add multiple API keys
        keys = [
            APIKeyRequest(provider=APIKeyProvider.OPENAI, api_key="sk-openai123", nickname="OpenAI"),
            APIKeyRequest(provider=APIKeyProvider.ANTHROPIC, api_key="sk-ant-claude456", nickname="Claude"),
            APIKeyRequest(provider=APIKeyProvider.GOOGLE_GENAI, api_key="AI-google789")
        ]
        
        for key_request in keys:
            settings_service.add_api_key(user_id, key_request)
        
        # List API keys
        api_keys = settings_service.list_api_keys(user_id)
        
        assert len(api_keys) == 3
        
        # Check that actual keys are not returned
        for api_key in api_keys:
            assert hasattr(api_key, 'provider')
            assert hasattr(api_key, 'created_at')
            assert hasattr(api_key, 'is_valid')
            # Should not contain actual key data
            assert not hasattr(api_key, 'api_key')
            assert not hasattr(api_key, 'encrypted_key')
    
    def test_remove_api_key(self, settings_service):
        """Test removing API key."""
        user_id = "test_user_remove"
        
        # Add API key
        request = APIKeyRequest(
            provider=APIKeyProvider.HUGGINGFACE,
            api_key="hf_test123456789"
        )
        
        settings_service.add_api_key(user_id, request)
        
        # Verify it exists
        api_keys = settings_service.list_api_keys(user_id)
        assert len(api_keys) == 1
        
        # Remove API key
        success = settings_service.remove_api_key(user_id, APIKeyProvider.HUGGINGFACE)
        assert success is True
        
        # Verify it's gone
        api_keys = settings_service.list_api_keys(user_id)
        assert len(api_keys) == 0
        
        # Try to get removed key
        decrypted_key = settings_service.get_api_key(user_id, APIKeyProvider.HUGGINGFACE)
        assert decrypted_key is None
    
    def test_multiple_users_isolation(self, settings_service):
        """Test that different users' data is isolated."""
        user1_id = "user_1"
        user2_id = "user_2"
        
        # Add API key for user 1
        request1 = APIKeyRequest(
            provider=APIKeyProvider.OPENAI,
            api_key="sk-user1-key123",
            nickname="User 1 Key"
        )
        settings_service.add_api_key(user1_id, request1)
        
        # Add API key for user 2
        request2 = APIKeyRequest(
            provider=APIKeyProvider.OPENAI,
            api_key="sk-user2-key456",
            nickname="User 2 Key"
        )
        settings_service.add_api_key(user2_id, request2)
        
        # Verify isolation
        user1_key = settings_service.get_api_key(user1_id, APIKeyProvider.OPENAI)
        user2_key = settings_service.get_api_key(user2_id, APIKeyProvider.OPENAI)
        
        assert user1_key == "sk-user1-key123"
        assert user2_key == "sk-user2-key456"
        assert user1_key != user2_key
        
        # Verify user 1 can't access user 2's keys
        user1_keys = settings_service.list_api_keys(user1_id)
        user2_keys = settings_service.list_api_keys(user2_id)
        
        assert len(user1_keys) == 1
        assert len(user2_keys) == 1
        assert user1_keys[0].nickname == "User 1 Key"
        assert user2_keys[0].nickname == "User 2 Key"
    
    def test_encryption_integrity(self, settings_service):
        """Test that encrypted data maintains integrity."""
        user_id = "test_encryption"
        original_key = "sk-integrity-test-123456789"
        
        # Add API key
        request = APIKeyRequest(
            provider=APIKeyProvider.AZURE_OPENAI,
            api_key=original_key
        )
        
        settings_service.add_api_key(user_id, request)
        
        # Get settings and check encrypted data
        settings = settings_service.get_user_settings(user_id)
        encrypted_data = settings.api_keys["azure_openai"]
        
        # Verify encryption worked
        assert encrypted_data.encrypted_key != original_key
        assert len(encrypted_data.encrypted_key) > len(original_key)
        assert encrypted_data.key_hash is not None
        
        # Verify decryption works
        decrypted_key = settings_service.get_api_key(user_id, APIKeyProvider.AZURE_OPENAI)
        assert decrypted_key == original_key
    
    def test_nonexistent_user(self, settings_service):
        """Test behavior with nonexistent user."""
        # Try to get API key for nonexistent user
        api_key = settings_service.get_api_key("nonexistent_user", APIKeyProvider.OPENAI)
        assert api_key is None
        
        # Try to list API keys for nonexistent user
        api_keys = settings_service.list_api_keys("nonexistent_user")
        assert api_keys == []
    
    def test_invalid_preferences_update(self, settings_service):
        """Test updating with invalid preference keys."""
        user_id = "test_invalid_prefs"
        
        # Try to update with invalid keys (should be ignored)
        invalid_update = {
            "theme": "dark",  # Valid
            "invalid_key": "invalid_value",  # Invalid - should be ignored
            "language": "en"  # Valid
        }
        
        success = settings_service.update_preferences(user_id, invalid_update)
        assert success is True
        
        # Verify only valid preferences were updated
        settings = settings_service.get_user_settings(user_id)
        assert settings.preferences.theme == "dark"
        assert settings.preferences.language == "en"
        # Invalid key should not exist
        assert not hasattr(settings.preferences, "invalid_key")


if __name__ == "__main__":
    pytest.main([__file__]) 