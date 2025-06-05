"""
OpenAI Provider Implementation for TEAM LLM Services

Implements the LLMProviderInterface for OpenAI API integration.
Provides secure API key handling, comprehensive error management, and 
support for various OpenAI models.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .models import (
    LLMProviderInterface,
    LLMConfig,
    LLMProviderType,
    LLMProviderError,
    LLMServiceStatus,
    LLMProviderStats
)

# Mock imports for shared utilities (không có sẵn)
def get_logger(name, **kwargs):
    """Mock logger function."""
    return logging.getLogger(name)

def log_function_entry(logger, func_name, **kwargs):
    """Mock function entry logging."""
    logger.debug(f"Entering {func_name} with {kwargs}")

def log_function_exit(logger, func_name, **kwargs):
    """Mock function exit logging."""
    logger.debug(f"Exiting {func_name} with {kwargs}")


class OpenAIProvider(LLMProviderInterface):
    """
    OpenAI provider implementation for LLM services.
    
    Provides integration with OpenAI's API including GPT models,
    secure authentication, comprehensive error handling, and
    usage tracking.
    """
    
    # Supported OpenAI models
    SUPPORTED_MODELS = [
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ]
    
    # Default configuration
    DEFAULT_CONFIG = {
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2048,
        "timeout": 30
    }
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            config: LLM configuration. If None, will use environment variables.
        """
        self.logger = get_logger(
            "llm_services.openai_provider",
            extra_context={'component': 'OpenAIProvider'}
        )
        
        # Check if OpenAI library is available
        if not OPENAI_AVAILABLE:
            raise LLMProviderError(
                "OpenAI library not installed. Please install: pip install openai",
                error_code="OPENAI_NOT_INSTALLED",
                status=LLMServiceStatus.ERROR
            )
        
        # Setup configuration
        self.config = config or self._create_default_config()
        self._validate_and_setup_config()
        
        # Initialize OpenAI client
        self.client = None
        self._initialize_client()
        
        # Statistics tracking
        self.stats = LLMProviderStats(provider_type=LLMProviderType.OPENAI)
        
        self.logger.info("OpenAI Provider initialized successfully")
    
    def _create_default_config(self) -> LLMConfig:
        """Create default configuration from environment variables."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.logger.warning("OPENAI_API_KEY not found in environment variables")
        
        return LLMConfig(
            provider=LLMProviderType.OPENAI,
            model=self.DEFAULT_CONFIG["model"],
            temperature=self.DEFAULT_CONFIG["temperature"], 
            max_tokens=self.DEFAULT_CONFIG["max_tokens"],
            timeout=self.DEFAULT_CONFIG["timeout"],
            api_key=api_key,
            api_base=os.getenv('OPENAI_API_BASE'),
            organization=os.getenv('OPENAI_ORGANIZATION')
        )
    
    def _validate_and_setup_config(self):
        """Validate and setup the configuration."""
        if not self.validate_config(self.config):
            raise LLMProviderError(
                "Invalid configuration for OpenAI provider",
                error_code="INVALID_CONFIG",
                status=LLMServiceStatus.ERROR
            )
        
        if not self.config.api_key:
            raise LLMProviderError(
                "OpenAI API key is required but not provided",
                error_code="API_KEY_MISSING", 
                status=LLMServiceStatus.API_KEY_INVALID
            )
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        try:
            client_kwargs = {
                'api_key': self.config.api_key,
                'timeout': self.config.timeout
            }
            
            if self.config.api_base:
                client_kwargs['base_url'] = self.config.api_base
            
            if self.config.organization:
                client_kwargs['organization'] = self.config.organization
            
            self.client = OpenAI(**client_kwargs)
            
            self.logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize OpenAI client: {str(e)}"
            self.logger.error(error_msg)
            raise LLMProviderError(
                error_msg,
                error_code="CLIENT_INIT_FAILED",
                status=LLMServiceStatus.ERROR
            )
    
    def complete(self, prompt: str, **kwargs) -> str:
        """
        Generate completion using OpenAI API.
        
        Args:
            prompt: The input prompt text
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.)
            
        Returns:
            The generated completion text
            
        Raises:
            LLMProviderError: If the request fails
        """
        start_time = time.time()
        log_function_entry(self.logger, "complete", prompt_length=len(prompt))
        
        if not self.is_available():
            raise LLMProviderError(
                "OpenAI provider is not available",
                error_code="PROVIDER_NOT_AVAILABLE",
                status=LLMServiceStatus.ERROR
            )
        
        # Prepare request parameters
        request_params = {
            'model': kwargs.get('model', self.config.model),
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': kwargs.get('temperature', self.config.temperature),
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens)
        }
        
        # Validate model
        if request_params['model'] not in self.SUPPORTED_MODELS:
            self.logger.warning(f"Model {request_params['model']} not in supported list")
        
        try:
            self.logger.info(f"Making OpenAI API request with model: {request_params['model']}")
            
            # Make API request
            response = self.client.chat.completions.create(**request_params)
            
            # Extract response text
            if response.choices and len(response.choices) > 0:
                completion_text = response.choices[0].message.content
                
                # Calculate metrics
                response_time_ms = (time.time() - start_time) * 1000
                tokens_used = getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') else None
                
                self.logger.info(
                    f"OpenAI request successful. Response time: {response_time_ms:.2f}ms, "
                    f"Tokens used: {tokens_used}"
                )
                
                log_function_exit(self.logger, "complete", 
                                response_length=len(completion_text), 
                                response_time_ms=response_time_ms,
                                tokens_used=tokens_used)
                
                return completion_text
            else:
                raise LLMProviderError(
                    "No completion choices returned from OpenAI API",
                    error_code="NO_CHOICES",
                    status=LLMServiceStatus.ERROR
                )
                
        except openai.AuthenticationError as e:
            error_msg = f"OpenAI authentication failed: {str(e)}"
            self.logger.error(error_msg)
            raise LLMProviderError(
                error_msg,
                error_code="AUTHENTICATION_FAILED",
                status=LLMServiceStatus.API_KEY_INVALID
            )
            
        except openai.RateLimitError as e:
            error_msg = f"OpenAI rate limit exceeded: {str(e)}"
            self.logger.error(error_msg)
            raise LLMProviderError(
                error_msg,
                error_code="RATE_LIMIT_EXCEEDED", 
                status=LLMServiceStatus.RATE_LIMITED
            )
            
        except openai.NotFoundError as e:
            error_msg = f"OpenAI model not found: {str(e)}"
            self.logger.error(error_msg)
            raise LLMProviderError(
                error_msg,
                error_code="MODEL_NOT_FOUND",
                status=LLMServiceStatus.MODEL_NOT_FOUND
            )
            
        except openai.APITimeoutError as e:
            error_msg = f"OpenAI API timeout: {str(e)}"
            self.logger.error(error_msg)
            raise LLMProviderError(
                error_msg,
                error_code="API_TIMEOUT",
                status=LLMServiceStatus.TIMEOUT
            )
            
        except Exception as e:
            error_msg = f"OpenAI API request failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise LLMProviderError(
                error_msg,
                error_code="API_REQUEST_FAILED",
                status=LLMServiceStatus.ERROR
            )
    
    def is_available(self) -> bool:
        """
        Check if the OpenAI provider is available and configured.
        
        Returns:
            True if provider is ready to use
        """
        try:
            # Check if client is initialized
            if not self.client:
                self.logger.debug("OpenAI client not initialized")
                return False
            
            # Check if API key is available
            if not self.config.api_key:
                self.logger.debug("OpenAI API key not available")
                return False
            
            # Optionally test with a simple API call
            # Note: This would consume quota, so we skip for now
            # Simple availability check based on configuration
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking OpenAI availability: {e}")
            return False
    
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported OpenAI models.
        
        Returns:
            List of model names
        """
        return self.SUPPORTED_MODELS.copy()
    
    def validate_config(self, config: LLMConfig) -> bool:
        """
        Validate the given configuration for OpenAI provider.
        
        Args:
            config: LLM configuration to validate
            
        Returns:
            True if configuration is valid
        """
        try:
            # Check provider type
            if config.provider != LLMProviderType.OPENAI:
                self.logger.error(f"Invalid provider type: {config.provider}")
                return False
            
            # Check model
            if config.model not in self.SUPPORTED_MODELS:
                self.logger.warning(f"Model {config.model} not in supported list")
                # Don't fail validation, just warn
            
            # Check temperature range
            if not (0.0 <= config.temperature <= 2.0):
                self.logger.error(f"Invalid temperature: {config.temperature}")
                return False
            
            # Check max_tokens if specified
            if config.max_tokens is not None and config.max_tokens <= 0:
                self.logger.error(f"Invalid max_tokens: {config.max_tokens}")
                return False
            
            # Check timeout
            if config.timeout <= 0:
                self.logger.error(f"Invalid timeout: {config.timeout}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating config: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the connection to OpenAI API with a simple request.
        
        Returns:
            True if connection is successful
        """
        try:
            test_prompt = "Hello"
            response = self.complete(test_prompt, max_tokens=5)
            
            self.logger.info("OpenAI connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    def get_stats(self) -> LLMProviderStats:
        """
        Get usage statistics for this provider.
        
        Returns:
            Provider statistics
        """
        return self.stats
    
    def reset_stats(self):
        """Reset provider statistics."""
        self.stats = LLMProviderStats(provider_type=LLMProviderType.OPENAI)
        self.logger.info("OpenAI provider statistics reset")
    
    def estimate_cost(self, prompt: str, model: Optional[str] = None) -> float:
        """
        Estimate the cost for a given prompt.
        
        Args:
            prompt: The prompt text
            model: Model to use (if None, uses default)
            
        Returns:
            Estimated cost in USD
        """
        # Simple cost estimation based on token count
        # Note: This is a rough estimate, actual costs may vary
        
        model = model or self.config.model
        estimated_tokens = len(prompt.split()) * 1.3  # Rough estimate
        
        # Cost per 1K tokens (approximate, as of 2024)
        cost_per_1k_tokens = {
            "gpt-4o": 0.005,
            "gpt-4o-mini": 0.0015,
            "gpt-4-turbo": 0.01,
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "gpt-3.5-turbo-16k": 0.004
        }
        
        rate = cost_per_1k_tokens.get(model, 0.002)  # Default rate
        estimated_cost = (estimated_tokens / 1000) * rate
        
        return estimated_cost
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model: Model name
            
        Returns:
            Model information dictionary
        """
        model_info = {
            "gpt-4o": {
                "max_tokens": 4096,
                "context_window": 128000,
                "description": "Latest GPT-4 Omni model"
            },
            "gpt-4o-mini": {
                "max_tokens": 4096, 
                "context_window": 128000,
                "description": "Smaller, faster GPT-4 Omni model"
            },
            "gpt-4-turbo": {
                "max_tokens": 4096,
                "context_window": 128000,
                "description": "GPT-4 Turbo with improved performance"
            },
            "gpt-4": {
                "max_tokens": 4096,
                "context_window": 8192,
                "description": "Original GPT-4 model"
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "context_window": 4096,
                "description": "Fast and efficient GPT-3.5 model"
            },
            "gpt-3.5-turbo-16k": {
                "max_tokens": 4096,
                "context_window": 16384,
                "description": "GPT-3.5 with larger context window"
            }
        }
        
        return model_info.get(model, {
            "max_tokens": 4096,
            "context_window": 4096,
            "description": "Unknown model"
        }) 