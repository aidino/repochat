"""
Unit Tests for User LLM Integration

Tests the integration between user API key management and LLM services.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from datetime import datetime

# Add src to path
current_dir = os.path.dirname(__file__)
src_path = os.path.join(current_dir, '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.llm_service_integration import UserLLMService
from shared.models.user_settings import (
    APIKeyProvider, 
    UserSettings, 
    UserPreferences, 
    UserSecuritySettings,
    EncryptedAPIKey,
    UserRole
)


class TestUserLLMIntegration(unittest.TestCase):
    """Test user LLM integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_id = "test_user_123"
        
        # Mock user settings service
        self.mock_user_settings_service = Mock()
        
        # Create test user settings with API key
        self.test_encrypted_key = EncryptedAPIKey(
            provider=APIKeyProvider.OPENAI,
            encrypted_key="test_encrypted_key_data",
            key_hash="test_hash",
            created_at=datetime.now(),
            last_used=None,
            is_valid=True,
            nickname="Test OpenAI Key"
        )
        
        self.test_user_settings = UserSettings(
            user_id=self.user_id,
            display_name="Test User",
            role=UserRole.USER,
            api_keys={"openai": self.test_encrypted_key},
            preferences=UserPreferences(
                default_llm_model="gpt-4o-mini",
                temperature_default=0.7,
                max_tokens_default=1000
            ),
            security=UserSecuritySettings()
        )
    
    @patch('services.llm_service_integration.UserSettingsService')
    def test_user_llm_service_initialization(self, mock_settings_service_class):
        """Test UserLLMService initialization."""
        mock_settings_service_class.return_value = self.mock_user_settings_service
        
        service = UserLLMService()
        
        self.assertIsNotNone(service)
        self.assertEqual(service.user_settings_service, self.mock_user_settings_service)
        self.assertIn(APIKeyProvider.OPENAI, service.provider_mapping)
    
    @patch('services.llm_service_integration.UserSettingsService')
    def test_get_user_api_key_success(self, mock_settings_service_class):
        """Test successful API key retrieval."""
        # Setup mocks
        mock_settings_service = Mock()
        mock_settings_service.get_user_settings.return_value = self.test_user_settings
        mock_settings_service.api_key_manager.decrypt_api_key.return_value = "sk-test123456789"
        mock_settings_service_class.return_value = mock_settings_service
        
        service = UserLLMService()
        
        # Test API key retrieval
        api_key = service.get_user_api_key(self.user_id, APIKeyProvider.OPENAI)
        
        self.assertEqual(api_key, "sk-test123456789")
        mock_settings_service.get_user_settings.assert_called_once_with(self.user_id)
        mock_settings_service.api_key_manager.decrypt_api_key.assert_called_once()
    
    @patch('services.llm_service_integration.UserSettingsService')
    def test_get_user_api_key_not_found(self, mock_settings_service_class):
        """Test API key retrieval when key doesn't exist."""
        # Setup mocks - user settings without API key
        empty_settings = UserSettings(
            user_id=self.user_id,
            display_name="Test User",
            role=UserRole.USER,
            api_keys={},  # No API keys
            preferences=UserPreferences(),
            security=UserSecuritySettings()
        )
        
        mock_settings_service = Mock()
        mock_settings_service.get_user_settings.return_value = empty_settings
        mock_settings_service_class.return_value = mock_settings_service
        
        service = UserLLMService()
        
        # Test API key retrieval
        api_key = service.get_user_api_key(self.user_id, APIKeyProvider.OPENAI)
        
        self.assertIsNone(api_key)
    
    @patch('services.llm_service_integration.UserSettingsService')
    @patch('services.llm_service_integration.OpenAIProvider')
    def test_create_openai_provider_success(self, mock_openai_provider_class, mock_settings_service_class):
        """Test successful OpenAI provider creation."""
        # Setup mocks
        mock_settings_service = Mock()
        mock_settings_service.get_user_settings.return_value = self.test_user_settings
        mock_settings_service.api_key_manager.decrypt_api_key.return_value = "sk-test123456789"
        mock_settings_service_class.return_value = mock_settings_service
        
        mock_provider = Mock()
        mock_openai_provider_class.return_value = mock_provider
        
        service = UserLLMService()
        
        # Test provider creation
        provider = service.create_openai_provider(self.user_id)
        
        self.assertEqual(provider, mock_provider)
        mock_openai_provider_class.assert_called_once()
        
        # Verify config was created correctly
        call_args = mock_openai_provider_class.call_args[0][0]  # First argument (config)
        self.assertEqual(call_args.api_key, "sk-test123456789")
        self.assertEqual(call_args.model, "gpt-4o-mini")
        self.assertEqual(call_args.temperature, 0.7)
        self.assertEqual(call_args.max_tokens, 1000)
    
    @patch('services.llm_service_integration.UserSettingsService')
    def test_create_openai_provider_no_api_key(self, mock_settings_service_class):
        """Test OpenAI provider creation when no API key exists."""
        # Setup mocks - user settings without API key
        empty_settings = UserSettings(
            user_id=self.user_id,
            display_name="Test User",
            role=UserRole.USER,
            api_keys={},  # No API keys
            preferences=UserPreferences(),
            security=UserSecuritySettings()
        )
        
        mock_settings_service = Mock()
        mock_settings_service.get_user_settings.return_value = empty_settings
        mock_settings_service_class.return_value = mock_settings_service
        
        service = UserLLMService()
        
        # Test provider creation
        provider = service.create_openai_provider(self.user_id)
        
        self.assertIsNone(provider)
    
    @patch('services.llm_service_integration.UserSettingsService')
    def test_get_user_preferred_model(self, mock_settings_service_class):
        """Test getting user's preferred model."""
        mock_settings_service = Mock()
        mock_settings_service.get_user_settings.return_value = self.test_user_settings
        mock_settings_service_class.return_value = mock_settings_service
        
        service = UserLLMService()
        
        # Test OpenAI model preference
        model = service.get_user_preferred_model(self.user_id, APIKeyProvider.OPENAI)
        self.assertEqual(model, "gpt-4o-mini")
        
        # Test Anthropic model preference (default)
        model = service.get_user_preferred_model(self.user_id, APIKeyProvider.ANTHROPIC)
        self.assertEqual(model, "claude-3-sonnet-20240229")
        
        # Test Google GenAI model preference (default)
        model = service.get_user_preferred_model(self.user_id, APIKeyProvider.GOOGLE_GENAI)
        self.assertEqual(model, "gemini-pro")
    
    @patch('services.llm_service_integration.UserSettingsService')
    def test_get_available_providers_for_user(self, mock_settings_service_class):
        """Test getting available providers for user."""
        mock_settings_service = Mock()
        mock_settings_service.get_user_settings.return_value = self.test_user_settings
        mock_settings_service_class.return_value = mock_settings_service
        
        service = UserLLMService()
        
        # Test getting available providers
        providers = service.get_available_providers_for_user(self.user_id)
        
        self.assertEqual(len(providers), 1)
        self.assertIn(APIKeyProvider.OPENAI, providers)
        
        openai_details = providers[APIKeyProvider.OPENAI]
        self.assertEqual(openai_details['nickname'], "Test OpenAI Key")
        self.assertEqual(openai_details['preferred_model'], "gpt-4o-mini")
        self.assertIn('created_at', openai_details)
    
    @patch('services.llm_service_integration.UserSettingsService')
    @patch('services.llm_service_integration.OpenAIProvider')
    def test_test_user_api_key_success(self, mock_openai_provider_class, mock_settings_service_class):
        """Test successful API key testing."""
        # Setup mocks
        mock_settings_service = Mock()
        mock_settings_service.get_user_settings.return_value = self.test_user_settings
        mock_settings_service.api_key_manager.decrypt_api_key.return_value = "sk-test123456789"
        mock_settings_service_class.return_value = mock_settings_service
        
        mock_provider = Mock()
        mock_provider.test_connection.return_value = True
        mock_openai_provider_class.return_value = mock_provider
        
        service = UserLLMService()
        
        # Test API key testing
        result = service.test_user_api_key(self.user_id, APIKeyProvider.OPENAI)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['provider'], 'openai')
        self.assertIn('tested_at', result)
    
    @patch('services.llm_service_integration.UserSettingsService')
    def test_test_user_api_key_no_provider(self, mock_settings_service_class):
        """Test API key testing for unsupported provider."""
        mock_settings_service = Mock()
        mock_settings_service_class.return_value = mock_settings_service
        
        service = UserLLMService()
        
        # Test API key testing for unsupported provider
        result = service.test_user_api_key(self.user_id, APIKeyProvider.ANTHROPIC)
        
        self.assertFalse(result['success'])
        self.assertIn('Testing not implemented', result['error'])


class TestSimplifiedLLMIntentParserIntegration(unittest.TestCase):
    """Test SimplifiedLLMIntentParser integration with user API keys."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_id = "test_user_123"
    
    @patch('teams.interaction_tasking.simplified_llm_intent_parser.UserLLMService')
    @patch('teams.interaction_tasking.simplified_llm_intent_parser.OPENAI_AVAILABLE', True)
    @patch('teams.interaction_tasking.simplified_llm_intent_parser.openai.OpenAI')
    def test_parser_with_user_api_key(self, mock_openai_class, mock_user_llm_service_class):
        """Test parser initialization with user API key."""
        # Setup mocks
        mock_user_llm_service = Mock()
        mock_provider = Mock()
        mock_provider.client = Mock()
        mock_provider.config.model = "gpt-4"
        mock_provider.config.temperature = 0.5
        mock_provider.config.max_tokens = 2000
        mock_user_llm_service.create_openai_provider.return_value = mock_provider
        mock_user_llm_service_class.return_value = mock_user_llm_service
        
        # Import and create parser
        from teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
        
        parser = SimplifiedLLMIntentParser(user_id=self.user_id)
        
        # Verify user LLM service was used
        mock_user_llm_service.create_openai_provider.assert_called_once_with(self.user_id)
        
        # Verify user settings were applied
        self.assertEqual(parser.user_model, "gpt-4")
        self.assertEqual(parser.user_temperature, 0.5)
        self.assertEqual(parser.user_max_tokens, 2000)
    
    @patch('teams.interaction_tasking.simplified_llm_intent_parser.UserLLMService')
    @patch('teams.interaction_tasking.simplified_llm_intent_parser.OPENAI_AVAILABLE', True)
    @patch('teams.interaction_tasking.simplified_llm_intent_parser.openai.OpenAI')
    @patch('teams.interaction_tasking.simplified_llm_intent_parser.os.getenv')
    def test_parser_fallback_to_system_key(self, mock_getenv, mock_openai_class, mock_user_llm_service_class):
        """Test parser fallback to system API key when user key not available."""
        # Setup mocks
        mock_user_llm_service = Mock()
        mock_user_llm_service.create_openai_provider.return_value = None  # No user provider
        mock_user_llm_service_class.return_value = mock_user_llm_service
        
        mock_getenv.return_value = "sk-system-key"
        mock_openai_client = Mock()
        mock_openai_class.return_value = mock_openai_client
        
        # Import and create parser
        from teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
        
        parser = SimplifiedLLMIntentParser(user_id=self.user_id)
        
        # Verify fallback to system key
        mock_openai_class.assert_called_once_with(api_key="sk-system-key")
        self.assertEqual(parser.openai_client, mock_openai_client)
        self.assertEqual(parser.user_model, "gpt-4o-mini")  # Default model


if __name__ == '__main__':
    unittest.main() 