"""
Test suite for GoogleGenAIProvider

Tests Google Gemini provider functionality including text generation,
model information, and error handling.

Created: 2025-06-06
Author: AI Agent
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import time

from src.teams.llm_services.google_genai_provider import (
    GoogleGenAIProvider,
    create_google_genai_config,
    is_google_genai_available
)
from src.teams.llm_services.models import (
    LLMConfig,
    LLMProviderType,
    LLMServiceRequest,
    LLMServiceResponse,
    LLMServiceStatus,
    LLMProviderError,
    LLMCapability
)


@pytest.fixture
def google_config():
    """Create test Google GenAI configuration."""
    return LLMConfig(
        provider=LLMProviderType.GOOGLE_GENAI,
        model="gemini-pro",
        api_key="test-google-api-key",
        temperature=0.7,
        max_tokens=1024
    )


@pytest.fixture
def mock_genai_module():
    """Mock google.generativeai module."""
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    return mock_genai, mock_model


class TestGoogleGenAIProviderInitialization:
    """Test GoogleGenAIProvider initialization."""
    
    def test_initialization_success(self, google_config):
        """Test successful provider initialization."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            provider = GoogleGenAIProvider(google_config)
            
            assert provider.config == google_config
            assert provider.api_key == 'test-google-api-key'
            assert provider.config.model == 'gemini-pro'
            
    def test_initialization_with_env_api_key(self):
        """Test initialization using environment API key."""
        config = LLMConfig(
            provider=LLMProviderType.GOOGLE_GENAI,
            model="gemini-pro"
        )
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'env-api-key'}):
            provider = GoogleGenAIProvider(config)
            assert provider.api_key == 'env-api-key'
            
    def test_initialization_missing_api_key(self):
        """Test initialization failure when API key is missing."""
        config = LLMConfig(
            provider=LLMProviderType.GOOGLE_GENAI,
            model="gemini-pro"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(LLMProviderError) as exc_info:
                GoogleGenAIProvider(config)
            
            assert "API key not found" in str(exc_info.value)
            assert exc_info.value.error_code == "MISSING_API_KEY"
            
    def test_initialization_invalid_provider_type(self):
        """Test initialization failure with invalid provider type."""
        config = LLMConfig(
            provider=LLMProviderType.OPENAI,  # Wrong provider
            model="gemini-pro",
            api_key="test-key"
        )
        
        with pytest.raises(LLMProviderError) as exc_info:
            GoogleGenAIProvider(config)
            
        assert "Invalid provider type" in str(exc_info.value)
        
    def test_initialization_unsupported_model(self):
        """Test initialization failure with unsupported model."""
        config = LLMConfig(
            provider=LLMProviderType.GOOGLE_GENAI,
            model="unsupported-model",
            api_key="test-key"
        )
        
        with pytest.raises(LLMProviderError) as exc_info:
            GoogleGenAIProvider(config)
            
        assert "Unsupported model" in str(exc_info.value)
        
    def test_default_model_assignment(self):
        """Test that default model is assigned when none specified."""
        config = LLMConfig(
            provider=LLMProviderType.GOOGLE_GENAI,
            api_key="test-key"
        )
        
        provider = GoogleGenAIProvider(config)
        assert provider.config.model == "gemini-pro"


class TestGoogleGenAIProviderTextGeneration:
    """Test text generation functionality."""
    
    @patch('src.teams.llm_services.google_genai_provider.get_logger')
    def test_generate_text_success(self, mock_logger, google_config, mock_genai_module):
        """Test successful text generation."""
        mock_genai, mock_model = mock_genai_module
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = "Generated response text"
        mock_model.generate_content.return_value = mock_response
        
        with patch('google.generativeai', mock_genai):
            provider = GoogleGenAIProvider(google_config)
            
            request = LLMServiceRequest(
                prompt="Test prompt",
                temperature=0.7,
                max_tokens=100
            )
            
            response = provider.generate_text(request)
            
            assert isinstance(response, LLMServiceResponse)
            assert response.status == LLMServiceStatus.SUCCESS
            assert response.content == "Generated response text"
            assert response.metadata["provider"] == "google_genai"
            assert response.metadata["model"] == "gemini-pro"
            assert "execution_time_seconds" in response.metadata
            
    @patch('src.teams.llm_services.google_genai_provider.get_logger')
    def test_generate_text_with_messages(self, mock_logger, google_config, mock_genai_module):
        """Test text generation with conversation messages."""
        mock_genai, mock_model = mock_genai_module
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = "Generated response"
        mock_model.generate_content.return_value = mock_response
        
        with patch('google.generativeai', mock_genai):
            provider = GoogleGenAIProvider(google_config)
            
            request = LLMServiceRequest(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi there!"},
                    {"role": "user", "content": "How are you?"}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            response = provider.generate_text(request)
            
            assert response.status == LLMServiceStatus.SUCCESS
            assert response.content == "Generated response"
            
            # Verify that generate_content was called with properly formatted prompt
            mock_model.generate_content.assert_called_once()
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]
            
            assert "System: You are a helpful assistant." in prompt
            assert "User: Hello!" in prompt
            assert "Assistant: Hi there!" in prompt
            assert "User: How are you?" in prompt
            
    @patch('src.teams.llm_services.google_genai_provider.get_logger')
    def test_generate_text_content_filtered(self, mock_logger, google_config, mock_genai_module):
        """Test handling of content-filtered responses."""
        mock_genai, mock_model = mock_genai_module
        
        # Mock filtered response (no text)
        mock_response = MagicMock()
        mock_response.text = None
        mock_model.generate_content.return_value = mock_response
        
        with patch('google.generativeai', mock_genai):
            provider = GoogleGenAIProvider(google_config)
            
            request = LLMServiceRequest(
                prompt="Inappropriate content",
                temperature=0.7,
                max_tokens=100
            )
            
            response = provider.generate_text(request)
            
            assert response.status == LLMServiceStatus.SUCCESS
            assert response.content == ""
            assert response.metadata["finish_reason"] == "content_filter"
            
    @patch('src.teams.llm_services.google_genai_provider.get_logger')
    def test_generate_text_api_error(self, mock_logger, google_config, mock_genai_module):
        """Test handling of API errors."""
        mock_genai, mock_model = mock_genai_module
        
        # Mock API error
        mock_model.generate_content.side_effect = Exception("API quota exceeded")
        
        with patch('google.generativeai', mock_genai):
            provider = GoogleGenAIProvider(google_config)
            
            request = LLMServiceRequest(
                prompt="Test prompt",
                temperature=0.7,
                max_tokens=100
            )
            
            response = provider.generate_text(request)
            
            assert response.status == LLMServiceStatus.RATE_LIMITED
            assert response.content == ""
            assert "API quota exceeded" in response.error
            assert response.error_code == "RATE_LIMITED"
            
    @patch('src.teams.llm_services.google_genai_provider.get_logger')
    def test_generate_text_unauthorized_error(self, mock_logger, google_config, mock_genai_module):
        """Test handling of unauthorized errors."""
        mock_genai, mock_model = mock_genai_module
        
        # Mock unauthorized error
        mock_model.generate_content.side_effect = Exception("API key is invalid")
        
        with patch('google.generativeai', mock_genai):
            provider = GoogleGenAIProvider(google_config)
            
            request = LLMServiceRequest(
                prompt="Test prompt",
                temperature=0.7,
                max_tokens=100
            )
            
            response = provider.generate_text(request)
            
            assert response.status == LLMServiceStatus.UNAUTHORIZED
            assert "API key is invalid" in response.error
            assert response.error_code == "UNAUTHORIZED"


class TestGoogleGenAIProviderAvailability:
    """Test provider availability checking."""
    
    @patch('src.teams.llm_services.google_genai_provider.get_logger')
    def test_is_available_success(self, mock_logger, google_config, mock_genai_module):
        """Test successful availability check."""
        mock_genai, mock_model = mock_genai_module
        
        # Mock successful test generation
        mock_response = MagicMock()
        mock_response.text = "test"
        mock_model.generate_content.return_value = mock_response
        
        with patch('google.generativeai', mock_genai):
            provider = GoogleGenAIProvider(google_config)
            
            assert provider.is_available() == True
            
    @patch('src.teams.llm_services.google_genai_provider.get_logger')
    def test_is_available_failure(self, mock_logger, google_config, mock_genai_module):
        """Test availability check failure."""
        mock_genai, mock_model = mock_genai_module
        
        # Mock failed test generation
        mock_model.generate_content.side_effect = Exception("Service unavailable")
        
        with patch('google.generativeai', mock_genai):
            provider = GoogleGenAIProvider(google_config)
            
            assert provider.is_available() == False


class TestGoogleGenAIProviderModelInfo:
    """Test model information and capabilities."""
    
    def test_get_model_info(self, google_config):
        """Test getting model information."""
        provider = GoogleGenAIProvider(google_config)
        
        model_info = provider.get_model_info()
        
        assert model_info["provider"] == "google_genai"
        assert model_info["model"] == "gemini-pro"
        assert model_info["name"] == "Gemini Pro"
        assert "capabilities" in model_info
        assert "max_tokens" in model_info
        assert "cost_per_token" in model_info
        assert model_info["supports_system_message"] == True
        
    def test_get_supported_capabilities(self, google_config):
        """Test getting supported capabilities."""
        provider = GoogleGenAIProvider(google_config)
        
        capabilities = provider.get_supported_capabilities()
        
        assert LLMCapability.TEXT_GENERATION in capabilities
        assert LLMCapability.CODE_ANALYSIS in capabilities
        assert LLMCapability.CONVERSATION in capabilities
        assert LLMCapability.JSON_MODE in capabilities
        
    def test_cost_info_different_models(self):
        """Test cost information for different models."""
        models_to_test = ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]
        
        for model in models_to_test:
            config = LLMConfig(
                provider=LLMProviderType.GOOGLE_GENAI,
                model=model,
                api_key="test-key"
            )
            
            provider = GoogleGenAIProvider(config)
            cost_info = provider._get_cost_info()
            
            assert "input_tokens_per_1k" in cost_info
            assert "output_tokens_per_1k" in cost_info
            assert isinstance(cost_info["input_tokens_per_1k"], float)
            assert isinstance(cost_info["output_tokens_per_1k"], float)


class TestGoogleGenAIProviderValidation:
    """Test request validation."""
    
    def test_validate_request_success(self, google_config):
        """Test successful request validation."""
        provider = GoogleGenAIProvider(google_config)
        
        request = LLMServiceRequest(
            prompt="Valid prompt",
            temperature=0.5,
            max_tokens=1000
        )
        
        assert provider.validate_request(request) == True
        
    def test_validate_request_invalid_temperature(self, google_config):
        """Test validation failure for invalid temperature."""
        provider = GoogleGenAIProvider(google_config)
        
        request = LLMServiceRequest(
            prompt="Valid prompt",
            temperature=1.5,  # Invalid: > 1.0
            max_tokens=1000
        )
        
        assert provider.validate_request(request) == False
        
    def test_validate_request_too_many_tokens(self, google_config):
        """Test validation failure for too many tokens."""
        provider = GoogleGenAIProvider(google_config)
        
        request = LLMServiceRequest(
            prompt="Valid prompt",
            temperature=0.7,
            max_tokens=50000  # Exceeds limit
        )
        
        assert provider.validate_request(request) == False
        
    def test_validate_request_no_content(self, google_config):
        """Test validation failure for no content."""
        provider = GoogleGenAIProvider(google_config)
        
        request = LLMServiceRequest(
            temperature=0.7,
            max_tokens=1000
            # No prompt or messages
        )
        
        assert provider.validate_request(request) == False


class TestGoogleGenAIProviderStats:
    """Test provider statistics."""
    
    def test_get_stats(self, google_config):
        """Test getting provider statistics."""
        provider = GoogleGenAIProvider(google_config)
        
        stats = provider.get_stats()
        
        assert stats.requests_total == 0
        assert stats.requests_successful == 0
        assert stats.requests_failed == 0
        assert stats.total_tokens_used == 0
        
    def test_reset_stats(self, google_config):
        """Test resetting provider statistics."""
        provider = GoogleGenAIProvider(google_config)
        
        # Manually set some stats
        provider.stats.requests_total = 10
        provider.stats.requests_successful = 8
        provider.stats.requests_failed = 2
        
        provider.reset_stats()
        
        assert provider.stats.requests_total == 0
        assert provider.stats.requests_successful == 0
        assert provider.stats.requests_failed == 0


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_google_genai_config(self):
        """Test creating Google GenAI configuration."""
        config = create_google_genai_config(
            model="gemini-ultra",
            api_key="test-key",
            temperature=0.8,
            max_tokens=2048
        )
        
        assert config.provider == LLMProviderType.GOOGLE_GENAI
        assert config.model == "gemini-ultra"
        assert config.api_key == "test-key"
        assert config.temperature == 0.8
        assert config.max_tokens == 2048
        
    def test_create_google_genai_config_defaults(self):
        """Test creating Google GenAI configuration with defaults."""
        config = create_google_genai_config()
        
        assert config.provider == LLMProviderType.GOOGLE_GENAI
        assert config.model == "gemini-pro"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        
    @patch('google.generativeai')
    def test_is_google_genai_available_with_package_and_key(self, mock_genai):
        """Test availability check with package and API key."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            assert is_google_genai_available() == True
            
    def test_is_google_genai_available_no_package(self):
        """Test availability check without package."""
        with patch('google.generativeai', side_effect=ImportError):
            assert is_google_genai_available() == False
            
    def test_is_google_genai_available_no_api_key(self):
        """Test availability check without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('google.generativeai'):
                assert is_google_genai_available() == False


class TestGoogleGenAIProviderClientInitialization:
    """Test client initialization scenarios."""
    
    def test_get_client_import_error(self, google_config):
        """Test client initialization with import error."""
        provider = GoogleGenAIProvider(google_config)
        
        with patch('google.generativeai', side_effect=ImportError):
            with pytest.raises(LLMProviderError) as exc_info:
                provider._get_client()
                
            assert "package not installed" in str(exc_info.value)
            assert exc_info.value.error_code == "PACKAGE_NOT_INSTALLED"
            
    @patch('src.teams.llm_services.google_genai_provider.get_logger')
    def test_get_client_initialization_error(self, mock_logger, google_config):
        """Test client initialization with general error."""
        provider = GoogleGenAIProvider(google_config)
        
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.side_effect = Exception("Initialization failed")
        
        with patch('google.generativeai', mock_genai):
            with pytest.raises(LLMProviderError) as exc_info:
                provider._get_client()
                
            assert "Failed to initialize" in str(exc_info.value)
            assert exc_info.value.error_code == "CLIENT_INITIALIZATION_FAILED"


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 