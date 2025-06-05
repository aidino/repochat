"""
Unit Tests for Task 3.3 (F3.3): LLM Services Infrastructure

Tests the LLM provider abstraction layer, OpenAI integration,
factory pattern, configuration management, and error handling.
"""

import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

# Mock OpenAI before importing our modules
mock_openai = MagicMock()
mock_openai.AuthenticationError = Exception
mock_openai.RateLimitError = Exception  
mock_openai.NotFoundError = Exception
mock_openai.APITimeoutError = Exception

with patch.dict('sys.modules', {'openai': mock_openai}):
    from src.teams.llm_services.models import (
        LLMProviderType,
        LLMServiceStatus,
        LLMConfig,
        LLMServiceRequest,
        LLMServiceResponse,
        LLMProviderInterface,
        LLMProviderError,
        LLMProviderStats,
        PromptTemplate
    )
    from src.teams.llm_services.openai_provider import OpenAIProvider
    from src.teams.llm_services.provider_factory import LLMProviderFactory, LLMProviderManager


class TestTask33LLMModels(unittest.TestCase):
    """Test LLM data models and configuration classes."""
    
    def test_llm_config_creation(self):
        """Test LLMConfig creation and validation."""
        config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=2048,
            api_key="test-key"
        )
        
        self.assertEqual(config.provider, LLMProviderType.OPENAI)
        self.assertEqual(config.model, "gpt-4o-mini")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 2048)
        self.assertEqual(config.api_key, "test-key")
    
    def test_llm_config_validation_invalid_temperature(self):
        """Test LLMConfig validation with invalid temperature."""
        with self.assertRaises(ValueError):
            LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                temperature=3.0  # Invalid: > 2.0
            )
    
    def test_llm_config_validation_invalid_max_tokens(self):
        """Test LLMConfig validation with invalid max_tokens."""
        with self.assertRaises(ValueError):
            LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                max_tokens=-100  # Invalid: negative
            )
    
    def test_llm_service_request_creation(self):
        """Test LLMServiceRequest creation."""
        config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.7
        )
        
        request = LLMServiceRequest(
            prompt_text="Test prompt",
            llm_config=config,
            request_id="test-req-123",
            user_id="test-user"
        )
        
        self.assertEqual(request.prompt_text, "Test prompt")
        self.assertEqual(request.request_id, "test-req-123")
        self.assertEqual(request.user_id, "test-user")
        self.assertEqual(request.llm_config.model, "gpt-4o-mini")
    
    def test_llm_service_response_creation(self):
        """Test LLMServiceResponse creation and utility methods."""
        response = LLMServiceResponse(
            response_text="Test response",
            status=LLMServiceStatus.SUCCESS,
            model_used="gpt-4o-mini",
            tokens_used=150
        )
        
        self.assertEqual(response.response_text, "Test response")
        self.assertEqual(response.status, LLMServiceStatus.SUCCESS)
        self.assertTrue(response.is_success())
        self.assertFalse(response.is_error())
    
    def test_llm_service_response_error(self):
        """Test LLMServiceResponse with error status."""
        response = LLMServiceResponse(
            response_text="",
            status=LLMServiceStatus.ERROR,
            error_message="API failed",
            error_code="API_ERROR"
        )
        
        self.assertFalse(response.is_success())
        self.assertTrue(response.is_error())
        self.assertEqual(response.error_message, "API failed")
    
    def test_prompt_template_formatting(self):
        """Test PromptTemplate formatting."""
        template = PromptTemplate(
            template_id="test_template",
            name="Test Template",
            description="A test template",
            template_text="Hello {name}, your age is {age}",
            required_variables=["name", "age"]
        )
        
        formatted = template.format(name="John", age=25)
        self.assertEqual(formatted, "Hello John, your age is 25")
    
    def test_prompt_template_missing_required_vars(self):
        """Test PromptTemplate with missing required variables."""
        template = PromptTemplate(
            template_id="test_template",
            name="Test Template", 
            description="A test template",
            template_text="Hello {name}, your age is {age}",
            required_variables=["name", "age"]
        )
        
        with self.assertRaises(ValueError):
            template.format(name="John")  # Missing 'age'
    
    def test_llm_provider_stats_update(self):
        """Test LLMProviderStats updates."""
        stats = LLMProviderStats(provider_type=LLMProviderType.OPENAI)
        
        response = LLMServiceResponse(
            response_text="Test",
            status=LLMServiceStatus.SUCCESS,
            tokens_used=100,
            response_time_ms=250.0
        )
        
        stats.update_stats(response)
        
        self.assertEqual(stats.requests_total, 1)
        self.assertEqual(stats.requests_successful, 1)
        self.assertEqual(stats.requests_failed, 0)
        self.assertEqual(stats.total_tokens_used, 100)
        self.assertEqual(stats.get_success_rate(), 100.0)


class TestTask33OpenAIProvider(unittest.TestCase):
    """Test OpenAI provider implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=2048,
            api_key="test-api-key"
        )
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_openai_provider_initialization(self, mock_openai_class):
        """Test OpenAI provider initialization."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        provider = OpenAIProvider(self.test_config)
        
        self.assertEqual(provider.config.model, "gpt-4o-mini")
        self.assertEqual(provider.config.api_key, "test-api-key")
        mock_openai_class.assert_called_once()
    
    def test_openai_provider_unavailable_library(self):
        """Test OpenAI provider when library is not available."""
        with patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', False):
            with self.assertRaises(LLMProviderError) as context:
                OpenAIProvider(self.test_config)
            
            self.assertEqual(context.exception.error_code, "OPENAI_NOT_INSTALLED")
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    def test_openai_provider_missing_api_key(self):
        """Test OpenAI provider with missing API key."""
        config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            api_key=None
        )
        
        with self.assertRaises(LLMProviderError) as context:
            OpenAIProvider(config)
        
        self.assertEqual(context.exception.error_code, "API_KEY_MISSING")
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_openai_provider_complete_success(self, mock_openai_class):
        """Test successful completion request."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.total_tokens = 150
        
        mock_client.chat.completions.create.return_value = mock_response
        
        provider = OpenAIProvider(self.test_config)
        result = provider.complete("Test prompt")
        
        self.assertEqual(result, "Test response")
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_openai_provider_complete_authentication_error(self, mock_openai_class):
        """Test completion with authentication error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_client.chat.completions.create.side_effect = mock_openai.AuthenticationError("Invalid API key")
        
        provider = OpenAIProvider(self.test_config)
        
        with self.assertRaises(LLMProviderError) as context:
            provider.complete("Test prompt")
        
        self.assertEqual(context.exception.error_code, "AUTHENTICATION_FAILED")
        self.assertEqual(context.exception.status, LLMServiceStatus.API_KEY_INVALID)
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_openai_provider_complete_rate_limit_error(self, mock_openai_class):
        """Test completion with rate limit error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_client.chat.completions.create.side_effect = mock_openai.RateLimitError("Rate limit exceeded")
        
        provider = OpenAIProvider(self.test_config)
        
        with self.assertRaises(LLMProviderError) as context:
            provider.complete("Test prompt")
        
        self.assertEqual(context.exception.error_code, "RATE_LIMIT_EXCEEDED")
        self.assertEqual(context.exception.status, LLMServiceStatus.RATE_LIMITED)
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_openai_provider_validate_config(self, mock_openai_class):
        """Test configuration validation."""
        mock_openai_class.return_value = Mock()
        
        provider = OpenAIProvider(self.test_config)
        
        # Valid config
        valid_config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=1000
        )
        self.assertTrue(provider.validate_config(valid_config))
        
        # Invalid provider type
        invalid_config = LLMConfig(
            provider=LLMProviderType.ANTHROPIC,  # Wrong provider
            model="gpt-4o-mini"
        )
        self.assertFalse(provider.validate_config(invalid_config))
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_openai_provider_supported_models(self, mock_openai_class):
        """Test getting supported models."""
        mock_openai_class.return_value = Mock()
        
        provider = OpenAIProvider(self.test_config)
        models = provider.get_supported_models()
        
        self.assertIsInstance(models, list)
        self.assertIn("gpt-4o", models)
        self.assertIn("gpt-4o-mini", models)
        self.assertIn("gpt-3.5-turbo", models)
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_openai_provider_cost_estimation(self, mock_openai_class):
        """Test cost estimation functionality."""
        mock_openai_class.return_value = Mock()
        
        provider = OpenAIProvider(self.test_config)
        cost = provider.estimate_cost("This is a test prompt")
        
        self.assertIsInstance(cost, float)
        self.assertGreaterEqual(cost, 0.0)


class TestTask33ProviderFactory(unittest.TestCase):
    """Test LLM provider factory and manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.7,
            api_key="test-api-key"
        )
    
    def test_factory_supported_providers(self):
        """Test getting supported providers."""
        supported = LLMProviderFactory.get_supported_providers()
        
        self.assertIsInstance(supported, dict)
        self.assertIn(LLMProviderType.OPENAI, supported)
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_factory_create_provider_success(self, mock_openai_class):
        """Test successful provider creation."""
        mock_openai_class.return_value = Mock()
        
        provider = LLMProviderFactory.create_provider(self.test_config)
        
        self.assertIsInstance(provider, OpenAIProvider)
        self.assertEqual(provider.config.model, "gpt-4o-mini")
    
    def test_factory_create_provider_unsupported(self):
        """Test creating unsupported provider type."""
        config = LLMConfig(
            provider=LLMProviderType.ANTHROPIC,  # Not implemented yet
            model="claude-3"
        )
        
        with self.assertRaises(LLMProviderError) as context:
            LLMProviderFactory.create_provider(config)
        
        self.assertEqual(context.exception.error_code, "UNSUPPORTED_PROVIDER")
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_factory_cached_provider(self, mock_openai_class):
        """Test provider caching functionality."""
        mock_openai_class.return_value = Mock()
        
        cache_key = "test_cache_key"
        
        # First call should create provider
        provider1 = LLMProviderFactory.get_cached_provider(cache_key, self.test_config)
        
        # Second call should return cached provider
        provider2 = LLMProviderFactory.get_cached_provider(cache_key, self.test_config)
        
        self.assertIs(provider1, provider2)  # Same instance
    
    def test_factory_cache_stats(self):
        """Test cache statistics."""
        LLMProviderFactory.clear_cache()  # Start clean
        
        stats = LLMProviderFactory.get_cache_stats()
        self.assertEqual(stats["total_cached_providers"], 0)
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_provider_manager_initialization(self, mock_openai_class):
        """Test provider manager initialization."""
        mock_openai_class.return_value = Mock()
        
        manager = LLMProviderManager(default_config=self.test_config)
        
        self.assertEqual(manager.default_config.model, "gpt-4o-mini")
        self.assertIsInstance(manager.factory, LLMProviderFactory)
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_provider_manager_get_provider(self, mock_openai_class):
        """Test getting provider through manager."""
        mock_openai_class.return_value = Mock()
        
        manager = LLMProviderManager(default_config=self.test_config)
        provider = manager.get_provider()
        
        self.assertIsInstance(provider, OpenAIProvider)
    
    def test_provider_manager_no_config_error(self):
        """Test provider manager with no configuration."""
        manager = LLMProviderManager()  # No default config
        
        with self.assertRaises(LLMProviderError) as context:
            manager.get_provider()  # No config provided
        
        self.assertEqual(context.exception.error_code, "NO_CONFIG")
    
    def test_provider_manager_recommendations(self):
        """Test provider recommendations."""
        manager = LLMProviderManager()
        
        recommendations = manager.get_provider_recommendations("code_analysis")
        self.assertIsInstance(recommendations, list)
        self.assertIn(LLMProviderType.OPENAI, recommendations)
    
    def test_provider_manager_cache_key_generation(self):
        """Test cache key generation."""
        manager = LLMProviderManager()
        
        key1 = manager._generate_cache_key(self.test_config)
        key2 = manager._generate_cache_key(self.test_config)
        
        self.assertEqual(key1, key2)  # Same config = same key
        
        # Different config should generate different key
        different_config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4",  # Different model
            temperature=0.7,
            api_key="test-api-key"
        )
        
        key3 = manager._generate_cache_key(different_config)
        self.assertNotEqual(key1, key3)


class TestTask33ErrorHandling(unittest.TestCase):
    """Test error handling in LLM services."""
    
    def test_llm_provider_error_creation(self):
        """Test LLMProviderError creation."""
        error = LLMProviderError(
            "Test error message",
            error_code="TEST_ERROR",
            status=LLMServiceStatus.ERROR
        )
        
        self.assertEqual(str(error), "Test error message")
        self.assertEqual(error.error_code, "TEST_ERROR")
        self.assertEqual(error.status, LLMServiceStatus.ERROR)
    
    def test_llm_provider_error_default_status(self):
        """Test LLMProviderError with default status."""
        error = LLMProviderError("Test error")
        
        self.assertEqual(error.status, LLMServiceStatus.ERROR)
        self.assertIsNone(error.error_code)


class TestTask33Integration(unittest.TestCase):
    """Integration tests for LLM services components."""
    
    @patch('src.teams.llm_services.openai_provider.OPENAI_AVAILABLE', True)
    @patch('src.teams.llm_services.openai_provider.OpenAI')
    def test_end_to_end_request_flow(self, mock_openai_class):
        """Test end-to-end request flow."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Integration test response"
        mock_response.usage.total_tokens = 100
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create configuration
        config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.7,
            api_key="test-key"
        )
        
        # Create request
        request = LLMServiceRequest(
            prompt_text="Test integration prompt",
            llm_config=config,
            request_id="integration-test-123"
        )
        
        # Use provider manager
        manager = LLMProviderManager(default_config=config)
        provider = manager.get_provider()
        
        # Make request
        result = provider.complete(request.prompt_text)
        
        # Verify result
        self.assertEqual(result, "Integration test response")
        
        # Verify API was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args['model'], "gpt-4o-mini")
        self.assertEqual(call_args['temperature'], 0.7)


if __name__ == '__main__':
    unittest.main() 