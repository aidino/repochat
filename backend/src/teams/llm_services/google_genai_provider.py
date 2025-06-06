"""
Google Gemini Provider for TEAM LLM Services

Implements LLM provider interface for Google's Generative AI (Gemini) models.
Supports text generation, conversation, and code analysis capabilities.

Created: 2025-06-06
Author: TEAM LLM Services
Status: PRODUCTION READY
"""

import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import (
    LLMProviderInterface,
    LLMConfig,
    LLMProviderType, 
    LLMServiceRequest,
    LLMServiceResponse,
    LLMServiceStatus,
    LLMProviderError,
    LLMProviderStats,
    LLMCapability
)

# Mock logging for now
import logging
def get_logger(name, **kwargs):
    return logging.getLogger(name)


class GoogleGenAIProvider(LLMProviderInterface):
    """
    Google Gemini provider implementation.
    
    Supports:
    - Gemini Pro (text generation)
    - Gemini Pro Vision (multimodal)
    - Gemini Ultra (advanced reasoning)
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize Google Gemini provider.
        
        Args:
            config: LLM configuration with API key and model settings
        """
        super().__init__(config)
        self.logger = get_logger(
            "llm_services.google_genai_provider",
            extra_context={'provider': 'google_genai'}
        )
        
        # Validate configuration
        if config.provider != LLMProviderType.GOOGLE_GENAI:
            raise LLMProviderError(
                f"Invalid provider type: {config.provider}",
                error_code="INVALID_PROVIDER_TYPE",
                status=LLMServiceStatus.ERROR
            )
        
        # Check for API key
        self.api_key = config.api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise LLMProviderError(
                "Google API key not found in config or environment",
                error_code="MISSING_API_KEY",
                status=LLMServiceStatus.UNAUTHORIZED
            )
        
        # Set up client (lazy initialization)
        self._client = None
        self._model = None
        
        # Supported models
        self.supported_models = {
            "gemini-pro": {
                "name": "Gemini Pro",
                "capabilities": [
                    LLMCapability.TEXT_GENERATION,
                    LLMCapability.CODE_ANALYSIS,
                    LLMCapability.CONVERSATION,
                    LLMCapability.JSON_MODE
                ],
                "max_tokens": 32768,
                "supports_system_message": True
            },
            "gemini-pro-vision": {
                "name": "Gemini Pro Vision", 
                "capabilities": [
                    LLMCapability.TEXT_GENERATION,
                    LLMCapability.VISION,
                    LLMCapability.CODE_ANALYSIS
                ],
                "max_tokens": 16384,
                "supports_system_message": True
            },
            "gemini-ultra": {
                "name": "Gemini Ultra",
                "capabilities": [
                    LLMCapability.TEXT_GENERATION,
                    LLMCapability.CODE_ANALYSIS,
                    LLMCapability.CONVERSATION,
                    LLMCapability.FUNCTION_CALLING,
                    LLMCapability.JSON_MODE
                ],
                "max_tokens": 32768,
                "supports_system_message": True
            }
        }
        
        # Default to gemini-pro if model not specified
        if not config.model:
            config.model = "gemini-pro"
        
        if config.model not in self.supported_models:
            raise LLMProviderError(
                f"Unsupported model: {config.model}",
                error_code="UNSUPPORTED_MODEL",
                status=LLMServiceStatus.ERROR
            )
        
        self.logger.info(f"Google GenAI provider initialized with model: {config.model}")
    
    def _get_client(self):
        """Get or create Google GenAI client (lazy initialization)."""
        if self._client is None:
            try:
                # Try to import Google GenAI SDK
                import google.generativeai as genai
                
                # Configure API key
                genai.configure(api_key=self.api_key)
                
                # Initialize model
                self._model = genai.GenerativeModel(self.config.model)
                self._client = genai
                
                self.logger.info("Google GenAI client initialized successfully")
                
            except ImportError:
                raise LLMProviderError(
                    "Google GenerativeAI package not installed. Please install: pip install google-generativeai",
                    error_code="PACKAGE_NOT_INSTALLED",
                    status=LLMServiceStatus.ERROR
                )
            except Exception as e:
                raise LLMProviderError(
                    f"Failed to initialize Google GenAI client: {str(e)}",
                    error_code="CLIENT_INITIALIZATION_FAILED",
                    status=LLMServiceStatus.ERROR
                )
        
        return self._client, self._model
    
    def generate_text(self, request: LLMServiceRequest) -> LLMServiceResponse:
        """
        Generate text using Google Gemini.
        
        Args:
            request: LLM service request
            
        Returns:
            LLM service response with generated text
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Generating text with Google GenAI model: {self.config.model}")
            
            # Get client and model
            client, model = self._get_client()
            
            # Prepare messages for Gemini
            prompt_parts = []
            
            # Handle system message
            if request.system_message:
                prompt_parts.append(f"System: {request.system_message}")
            
            # Handle conversation messages
            if request.messages:
                for message in request.messages:
                    role = message.get("role", "user")
                    content = message.get("content", "")
                    
                    if role == "system":
                        prompt_parts.append(f"System: {content}")
                    elif role == "user":
                        prompt_parts.append(f"User: {content}")
                    elif role == "assistant":
                        prompt_parts.append(f"Assistant: {content}")
            
            # Handle single prompt
            if request.prompt:
                prompt_parts.append(request.prompt)
            
            # Combine all parts
            combined_prompt = "\n\n".join(prompt_parts)
            
            # Generation config
            generation_config = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
                "top_p": getattr(request, 'top_p', 0.8),
                "top_k": getattr(request, 'top_k', 40),
            }
            
            # Generate response
            response = model.generate_content(
                combined_prompt,
                generation_config=generation_config
            )
            
            # Extract response text
            if hasattr(response, 'text') and response.text:
                response_text = response.text
                finish_reason = "stop"
            else:
                response_text = ""
                finish_reason = "content_filter"  # Likely blocked by safety filters
            
            execution_time = time.time() - start_time
            
            # Update stats
            self.stats.requests_total += 1
            self.stats.requests_successful += 1
            self.stats.total_tokens_used += len(combined_prompt.split()) + len(response_text.split())
            
            self.logger.info(f"Google GenAI generation completed in {execution_time:.2f}s")
            
            return LLMServiceResponse(
                status=LLMServiceStatus.SUCCESS,
                content=response_text,
                metadata={
                    "model": self.config.model,
                    "provider": "google_genai",
                    "execution_time_seconds": execution_time,
                    "finish_reason": finish_reason,
                    "prompt_tokens": len(combined_prompt.split()),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(combined_prompt.split()) + len(response_text.split())
                },
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.stats.requests_total += 1
            self.stats.requests_failed += 1
            
            # Handle specific Google API errors
            error_code = "GENERATION_FAILED"
            status = LLMServiceStatus.ERROR
            
            if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                error_code = "RATE_LIMITED"
                status = LLMServiceStatus.RATE_LIMITED
            elif "unauthorized" in str(e).lower() or "api key" in str(e).lower():
                error_code = "UNAUTHORIZED" 
                status = LLMServiceStatus.UNAUTHORIZED
            elif "content" in str(e).lower() and "filter" in str(e).lower():
                error_code = "CONTENT_FILTERED"
                
            self.logger.error(f"Google GenAI generation failed: {str(e)}", exc_info=True)
            
            return LLMServiceResponse(
                status=status,
                content="",
                error=str(e),
                error_code=error_code,
                metadata={
                    "model": self.config.model,
                    "provider": "google_genai",
                    "execution_time_seconds": execution_time
                },
                execution_time_seconds=execution_time
            )
    
    def is_available(self) -> bool:
        """
        Check if Google GenAI service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            # Try to get client
            client, model = self._get_client()
            
            # Simple test generation
            test_response = model.generate_content(
                "Say 'test' if you can respond.",
                generation_config={"max_output_tokens": 10}
            )
            
            return test_response is not None
            
        except Exception as e:
            self.logger.warning(f"Google GenAI availability check failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary containing model information
        """
        model_info = self.supported_models.get(self.config.model, {})
        
        return {
            "provider": "google_genai",
            "model": self.config.model,
            "name": model_info.get("name", self.config.model),
            "capabilities": [cap.value for cap in model_info.get("capabilities", [])],
            "max_tokens": model_info.get("max_tokens", 32768),
            "supports_system_message": model_info.get("supports_system_message", True),
            "supports_streaming": False,  # Not implemented yet
            "cost_per_token": self._get_cost_info()
        }
    
    def _get_cost_info(self) -> Dict[str, float]:
        """Get cost information for the model."""
        # Google GenAI pricing (as of 2024)
        cost_mapping = {
            "gemini-pro": {
                "input_tokens_per_1k": 0.0005,  # $0.0005 per 1K input tokens
                "output_tokens_per_1k": 0.0015   # $0.0015 per 1K output tokens
            },
            "gemini-pro-vision": {
                "input_tokens_per_1k": 0.0005,
                "output_tokens_per_1k": 0.0015
            },
            "gemini-ultra": {
                "input_tokens_per_1k": 0.0125,   # More expensive for ultra model
                "output_tokens_per_1k": 0.0375
            }
        }
        
        return cost_mapping.get(self.config.model, {
            "input_tokens_per_1k": 0.001,
            "output_tokens_per_1k": 0.003
        })
    
    def get_supported_capabilities(self) -> List[LLMCapability]:
        """
        Get list of capabilities supported by this provider.
        
        Returns:
            List of supported capabilities
        """
        model_info = self.supported_models.get(self.config.model, {})
        return model_info.get("capabilities", [LLMCapability.TEXT_GENERATION])
    
    def validate_request(self, request: LLMServiceRequest) -> bool:
        """
        Validate if request is compatible with this provider.
        
        Args:
            request: LLM service request to validate
            
        Returns:
            True if request is valid, False otherwise
        """
        # Check token limits
        model_info = self.supported_models.get(self.config.model, {})
        max_tokens = model_info.get("max_tokens", 32768)
        
        if request.max_tokens and request.max_tokens > max_tokens:
            return False
        
        # Check temperature range (0.0 to 1.0 for Gemini)
        if request.temperature is not None and (request.temperature < 0.0 or request.temperature > 1.0):
            return False
        
        # Check if we have content to process
        if not request.prompt and not request.messages:
            return False
        
        return True
    
    def get_stats(self) -> LLMProviderStats:
        """Get provider statistics."""
        return self.stats
    
    def reset_stats(self):
        """Reset provider statistics."""
        self.stats = LLMProviderStats()
        self.logger.info("Google GenAI provider stats reset")


# Utility functions
def create_google_genai_config(
    model: str = "gemini-pro",
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> LLMConfig:
    """
    Create Google GenAI configuration.
    
    Args:
        model: Model name (gemini-pro, gemini-pro-vision, gemini-ultra)
        api_key: Google API key (optional, will use environment if not provided)
        temperature: Generation temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        LLM configuration for Google GenAI
    """
    return LLMConfig(
        provider=LLMProviderType.GOOGLE_GENAI,
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens
    )


def is_google_genai_available() -> bool:
    """
    Check if Google GenAI is available in the environment.
    
    Returns:
        True if Google GenAI can be used, False otherwise
    """
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        return api_key is not None
    except ImportError:
        return False 