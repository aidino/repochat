"""
Test suite for Ollama Provider

Test Ollama LLM provider implementation.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from teams.llm_services.models import LLMConfig, LLMProviderType, LLMProviderError
from teams.llm_services.ollama_provider import (
    OllamaProvider, 
    create_ollama_provider,
    is_ollama_available,
    get_ollama_default_models
)


class TestOllamaProvider(unittest.TestCase):
    """Test Ollama provider functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = LLMConfig(
            provider=LLMProviderType.OLLAMA,
            model="llama2:7b",
            temperature=0.7,
            timeout=30
        )
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_provider_initialization_success(self, mock_ollama_llm):
        """Test successful Ollama provider initialization."""
        mock_client = Mock()
        mock_ollama_llm.return_value = mock_client
        
        provider = OllamaProvider(self.config)
        
        self.assertEqual(provider.config, self.config)
        self.assertEqual(provider.client, mock_client)
        mock_ollama_llm.assert_called_once()
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', False)
    def test_provider_initialization_ollama_not_available(self):
        """Test provider initialization when Ollama not available."""
        with self.assertRaises(LLMProviderError) as context:
            OllamaProvider(self.config)
        
        self.assertIn("langchain-ollama not installed", str(context.exception))
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_provider_initialization_client_error(self, mock_ollama_llm):
        """Test provider initialization with client creation error."""
        mock_ollama_llm.side_effect = Exception("Connection failed")
        
        with self.assertRaises(LLMProviderError) as context:
            OllamaProvider(self.config)
        
        self.assertIn("Failed to init Ollama", str(context.exception))
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_complete_success(self, mock_ollama_llm):
        """Test successful completion generation."""
        mock_client = Mock()
        mock_client.invoke.return_value = "This is a test response"
        mock_ollama_llm.return_value = mock_client
        
        provider = OllamaProvider(self.config)
        response = provider.complete("Test prompt")
        
        self.assertEqual(response, "This is a test response")
        mock_client.invoke.assert_called_once_with("Test prompt")
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_complete_error(self, mock_ollama_llm):
        """Test completion generation with error."""
        mock_client = Mock()
        mock_client.invoke.side_effect = Exception("Model error")
        mock_ollama_llm.return_value = mock_client
        
        provider = OllamaProvider(self.config)
        
        with self.assertRaises(LLMProviderError) as context:
            provider.complete("Test prompt")
        
        self.assertIn("Ollama completion failed", str(context.exception))
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_is_available_success(self, mock_ollama_llm):
        """Test availability check when Ollama is working."""
        mock_client = Mock()
        mock_client.invoke.return_value = "test response"
        mock_ollama_llm.return_value = mock_client
        
        provider = OllamaProvider(self.config)
        available = provider.is_available()
        
        self.assertTrue(available)
        mock_client.invoke.assert_called_with("test")
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_is_available_failure(self, mock_ollama_llm):
        """Test availability check when Ollama is not working."""
        mock_client = Mock()
        mock_client.invoke.side_effect = Exception("Connection error")
        mock_ollama_llm.return_value = mock_client
        
        provider = OllamaProvider(self.config)
        available = provider.is_available()
        
        self.assertFalse(available)
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', False)
    def test_is_available_ollama_not_installed(self):
        """Test availability when Ollama not installed."""
        # Can't create provider, but can test static method
        from teams.llm_services.ollama_provider import OllamaProvider
        
        # Create a mock provider to test is_available
        provider = Mock(spec=OllamaProvider)
        provider.is_available = OllamaProvider.is_available.__get__(provider)
        
        # Mock OLLAMA_AVAILABLE on the provider
        with patch.object(provider, '__class__') as mock_class:
            mock_class.__module__ = 'teams.llm_services.ollama_provider'
            
            # Test that it returns False when OLLAMA_AVAILABLE is False
            available = provider.is_available()
            self.assertFalse(available)
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_get_supported_models(self, mock_ollama_llm):
        """Test getting supported models list."""
        mock_client = Mock()
        mock_ollama_llm.return_value = mock_client
        
        provider = OllamaProvider(self.config)
        models = provider.get_supported_models()
        
        expected_models = [
            "llama2:7b", "llama2:13b", "codellama:7b", 
            "mistral:7b", "neural-chat:7b", "phi:2.7b"
        ]
        
        self.assertEqual(models, expected_models)
        self.assertIn("llama2:7b", models)
        self.assertIn("codellama:7b", models)
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_validate_config_valid(self, mock_ollama_llm):
        """Test configuration validation with valid config."""
        mock_client = Mock()
        mock_ollama_llm.return_value = mock_client
        
        provider = OllamaProvider(self.config)
        is_valid = provider.validate_config(self.config)
        
        self.assertTrue(is_valid)
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_validate_config_invalid_provider(self, mock_ollama_llm):
        """Test configuration validation with wrong provider type."""
        mock_client = Mock()
        mock_ollama_llm.return_value = mock_client
        
        invalid_config = LLMConfig(
            provider=LLMProviderType.OPENAI,  # Wrong provider
            model="llama2:7b",
            temperature=0.7
        )
        
        provider = OllamaProvider(self.config)
        is_valid = provider.validate_config(invalid_config)
        
        self.assertFalse(is_valid)
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_validate_config_invalid_temperature(self, mock_ollama_llm):
        """Test configuration validation with invalid temperature."""
        mock_client = Mock()
        mock_ollama_llm.return_value = mock_client
        
        # Create provider first with valid config
        provider = OllamaProvider(self.config)
        
        # Test validation with invalid temperature manually
        # (bypass LLMConfig constructor validation)
        invalid_config = Mock()
        invalid_config.provider = LLMProviderType.OLLAMA
        invalid_config.model = "llama2:7b"
        invalid_config.temperature = 3.0  # Invalid temperature
        invalid_config.timeout = 30
        
        is_valid = provider.validate_config(invalid_config)
        
        self.assertFalse(is_valid)


class TestOllamaConvenienceFunctions(unittest.TestCase):
    """Test Ollama convenience functions."""
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_create_ollama_provider(self, mock_ollama_llm):
        """Test convenience function for creating Ollama provider."""
        mock_client = Mock()
        mock_ollama_llm.return_value = mock_client
        
        provider = create_ollama_provider(model="mistral:7b")
        
        self.assertIsInstance(provider, OllamaProvider)
        self.assertEqual(provider.config.model, "mistral:7b")
        self.assertEqual(provider.config.provider, LLMProviderType.OLLAMA)
        self.assertEqual(provider.config.temperature, 0.7)
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    def test_is_ollama_available_true(self):
        """Test ollama availability check when available."""
        available = is_ollama_available()
        self.assertTrue(available)
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', False)
    def test_is_ollama_available_false(self):
        """Test ollama availability check when not available."""
        available = is_ollama_available()
        self.assertFalse(available)
    
    def test_get_ollama_default_models(self):
        """Test getting default Ollama models list."""
        models = get_ollama_default_models()
        
        expected_models = [
            "llama2:7b", "llama2:13b", "codellama:7b",
            "mistral:7b", "neural-chat:7b", "phi:2.7b"
        ]
        
        self.assertEqual(models, expected_models)
        self.assertIn("llama2:7b", models)
        self.assertIn("codellama:7b", models)


class TestOllamaIntegration(unittest.TestCase):
    """Test Ollama provider integration."""
    
    @patch('teams.llm_services.ollama_provider.OLLAMA_AVAILABLE', True)
    @patch('teams.llm_services.ollama_provider.OllamaLLM')
    def test_environment_configuration(self, mock_ollama_llm):
        """Test environment variable configuration."""
        mock_client = Mock()
        mock_ollama_llm.return_value = mock_client
        
        with patch.dict(os.environ, {
            'OLLAMA_BASE_URL': 'http://custom-ollama:11434',
            'OLLAMA_TOP_P': '0.9',
            'OLLAMA_TOP_K': '50'
        }):
            provider = OllamaProvider(self.config)
            
            self.assertEqual(provider.base_url, 'http://custom-ollama:11434')
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = LLMConfig(
            provider=LLMProviderType.OLLAMA,
            model="llama2:7b",
            temperature=0.7,
            timeout=30
        )


def run_ollama_provider_tests():
    """Run all Ollama provider tests."""
    print("=" * 70)
    print("  Ollama Provider Test Suite")
    print("=" * 70)
    print("Testing Ollama LLM provider implementation")
    print()
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestOllamaProvider))
    suite.addTest(unittest.makeSuite(TestOllamaConvenienceFunctions))
    suite.addTest(unittest.makeSuite(TestOllamaIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("  Ollama Provider Test Results")
    print("=" * 70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("✅ All Ollama provider tests passed!")
    else:
        print("❌ Some tests failed. Check details above.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_ollama_provider_tests() 