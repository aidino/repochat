"""
Anthropic Claude Provider for TEAM LLM Services

Implements LLM provider interface for Anthropic's Claude models.
Supports text generation, conversation, and advanced reasoning capabilities.

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


class AnthropicProvider(LLMProviderInterface):
    """
    Anthropic Claude provider implementation.
    
    Supports:
    - Claude 3 Opus (most capable)
    - Claude 3 Sonnet (balanced performance)
    - Claude 3 Haiku (fastest)
    - Claude 2.1 (previous generation)
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize Anthropic Claude provider.
        
        Args:
            config: LLM configuration with API key and model settings
        """
        super().__init__(config)
        self.logger = get_logger(
            "llm_services.anthropic_provider",
            extra_context={'provider': 'anthropic'}
        )
        
        # Validate configuration
        if config.provider != LLMProviderType.ANTHROPIC:
            raise LLMProviderError(
                f"Invalid provider type: {config.provider}",
                error_code="INVALID_PROVIDER_TYPE",
                status=LLMServiceStatus.ERROR
            )
        
        # Check for API key
        self.api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise LLMProviderError(
                "Anthropic API key not found in config or environment",
                error_code="MISSING_API_KEY",
                status=LLMServiceStatus.UNAUTHORIZED
            )
        
        # Set up client (lazy initialization)
        self._client = None
        
        # Supported models
        self.supported_models = {
            "claude-3-opus-20240229": {
                "name": "Claude 3 Opus",
                "capabilities": [
                    LLMCapability.TEXT_GENERATION,
                    LLMCapability.CODE_ANALYSIS,
                    LLMCapability.CONVERSATION,
                    LLMCapability.FUNCTION_CALLING,
                    LLMCapability.JSON_MODE,
                    LLMCapability.VISION
                ],
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_system_message": True
            },
            "claude-3-sonnet-20240229": {
                "name": "Claude 3 Sonnet",
                "capabilities": [
                    LLMCapability.TEXT_GENERATION,
                    LLMCapability.CODE_ANALYSIS,
                    LLMCapability.CONVERSATION,
                    LLMCapability.FUNCTION_CALLING,
                    LLMCapability.JSON_MODE,
                    LLMCapability.VISION
                ],
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_system_message": True
            },
            "claude-3-haiku-20240307": {
                "name": "Claude 3 Haiku",
                "capabilities": [
                    LLMCapability.TEXT_GENERATION,
                    LLMCapability.CODE_ANALYSIS,
                    LLMCapability.CONVERSATION,
                    LLMCapability.JSON_MODE,
                    LLMCapability.VISION
                ],
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_system_message": True
            },
            "claude-2.1": {
                "name": "Claude 2.1",
                "capabilities": [
                    LLMCapability.TEXT_GENERATION,
                    LLMCapability.CODE_ANALYSIS,
                    LLMCapability.CONVERSATION
                ],
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_system_message": True
            }
        }
        
        # Default to Claude 3 Sonnet if model not specified
        if not config.model:
            config.model = "claude-3-sonnet-20240229"
        
        if config.model not in self.supported_models:
            raise LLMProviderError(
                f"Unsupported model: {config.model}",
                error_code="UNSUPPORTED_MODEL",
                status=LLMServiceStatus.ERROR
            )
        
        self.logger.info(f"Anthropic provider initialized with model: {config.model}")
    
    def _get_client(self):
        """Get or create Anthropic client (lazy initialization)."""
        if self._client is None:
            try:
                # Try to import Anthropic SDK
                import anthropic
                
                # Initialize client
                self._client = anthropic.Anthropic(api_key=self.api_key)
                
                self.logger.info("Anthropic client initialized successfully")
                
            except ImportError:
                raise LLMProviderError(
                    "Anthropic package not installed. Please install: pip install anthropic",
                    error_code="PACKAGE_NOT_INSTALLED",
                    status=LLMServiceStatus.ERROR
                )
            except Exception as e:
                raise LLMProviderError(
                    f"Failed to initialize Anthropic client: {str(e)}",
                    error_code="CLIENT_INITIALIZATION_FAILED",
                    status=LLMServiceStatus.ERROR
                )
        
        return self._client
    
    def generate_text(self, request: LLMServiceRequest) -> LLMServiceResponse:
        """
        Generate text using Anthropic Claude.
        
        Args:
            request: LLM service request
            
        Returns:
            LLM service response with generated text
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Generating text with Anthropic model: {self.config.model}")
            
            # Get client
            client = self._get_client()
            
            # Prepare messages for Claude
            messages = []
            system_message = None
            
            # Handle system message
            if request.system_message:
                system_message = request.system_message
            
            # Handle conversation messages
            if request.messages:
                for message in request.messages:
                    role = message.get("role", "user")
                    content = message.get("content", "")
                    
                    if role == "system":
                        # Claude uses system parameter separately
                        if not system_message:
                            system_message = content
                        else:
                            system_message += f"\n\n{content}"
                    elif role in ["user", "assistant"]:
                        messages.append({
                            "role": role,
                            "content": content
                        })
            
            # Handle single prompt
            if request.prompt:
                messages.append({
                    "role": "user",
                    "content": request.prompt
                })
            
            # Build request parameters
            request_params = {
                "model": self.config.model,
                "max_tokens": request.max_tokens or 1024,
                "messages": messages,
                "temperature": request.temperature
            }
            
            # Add system message if present
            if system_message:
                request_params["system"] = system_message
            
            # Add optional parameters
            if hasattr(request, 'top_p') and request.top_p is not None:
                request_params["top_p"] = request.top_p
            
            # Generate response
            response = client.messages.create(**request_params)
            
            # Extract response text
            response_text = ""
            if response.content and len(response.content) > 0:
                # Claude typically returns content as a list of content blocks
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        response_text += content_block.text
                    elif isinstance(content_block, dict) and 'text' in content_block:
                        response_text += content_block['text']
            
            execution_time = time.time() - start_time
            
            # Calculate token usage
            input_tokens = getattr(response.usage, 'input_tokens', 0) if hasattr(response, 'usage') else 0
            output_tokens = getattr(response.usage, 'output_tokens', 0) if hasattr(response, 'usage') else 0
            total_tokens = input_tokens + output_tokens
            
            # Update stats
            self.stats.requests_total += 1
            self.stats.requests_successful += 1
            self.stats.total_tokens_used += total_tokens
            
            self.logger.info(f"Anthropic generation completed in {execution_time:.2f}s")
            
            return LLMServiceResponse(
                status=LLMServiceStatus.SUCCESS,
                content=response_text,
                metadata={
                    "model": self.config.model,
                    "provider": "anthropic",
                    "execution_time_seconds": execution_time,
                    "finish_reason": getattr(response, 'stop_reason', 'stop'),
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "stop_sequence": getattr(response, 'stop_sequence', None)
                },
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.stats.requests_total += 1
            self.stats.requests_failed += 1
            
            # Handle specific Anthropic API errors
            error_code = "GENERATION_FAILED"
            status = LLMServiceStatus.ERROR
            
            error_str = str(e).lower()
            if "rate limit" in error_str or "quota" in error_str:
                error_code = "RATE_LIMITED"
                status = LLMServiceStatus.RATE_LIMITED
            elif "unauthorized" in error_str or "api key" in error_str:
                error_code = "UNAUTHORIZED"
                status = LLMServiceStatus.UNAUTHORIZED
            elif "content policy" in error_str or "safety" in error_str:
                error_code = "CONTENT_FILTERED"
            elif "timeout" in error_str:
                error_code = "TIMEOUT"
                status = LLMServiceStatus.TIMEOUT
                
            self.logger.error(f"Anthropic generation failed: {str(e)}", exc_info=True)
            
            return LLMServiceResponse(
                status=status,
                content="",
                error=str(e),
                error_code=error_code,
                metadata={
                    "model": self.config.model,
                    "provider": "anthropic",
                    "execution_time_seconds": execution_time
                },
                execution_time_seconds=execution_time
            )
    
    def is_available(self) -> bool:
        """
        Check if Anthropic service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            # Try to get client
            client = self._get_client()
            
            # Simple test generation
            test_response = client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'test' if you can respond."}]
            )
            
            return test_response is not None
            
        except Exception as e:
            self.logger.warning(f"Anthropic availability check failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary containing model information
        """
        model_info = self.supported_models.get(self.config.model, {})
        
        return {
            "provider": "anthropic",
            "model": self.config.model,
            "name": model_info.get("name", self.config.model),
            "capabilities": [cap.value for cap in model_info.get("capabilities", [])],
            "max_tokens": model_info.get("max_tokens", 4096),
            "context_window": model_info.get("context_window", 200000),
            "supports_system_message": model_info.get("supports_system_message", True),
            "supports_streaming": True,  # Claude supports streaming
            "cost_per_token": self._get_cost_info()
        }
    
    def _get_cost_info(self) -> Dict[str, float]:
        """Get cost information for the model."""
        # Anthropic pricing (as of 2024)
        cost_mapping = {
            "claude-3-opus-20240229": {
                "input_tokens_per_1k": 0.015,   # $15 per 1M input tokens
                "output_tokens_per_1k": 0.075   # $75 per 1M output tokens
            },
            "claude-3-sonnet-20240229": {
                "input_tokens_per_1k": 0.003,   # $3 per 1M input tokens
                "output_tokens_per_1k": 0.015   # $15 per 1M output tokens
            },
            "claude-3-haiku-20240307": {
                "input_tokens_per_1k": 0.00025, # $0.25 per 1M input tokens
                "output_tokens_per_1k": 0.00125 # $1.25 per 1M output tokens
            },
            "claude-2.1": {
                "input_tokens_per_1k": 0.008,   # $8 per 1M input tokens
                "output_tokens_per_1k": 0.024   # $24 per 1M output tokens
            }
        }
        
        return cost_mapping.get(self.config.model, {
            "input_tokens_per_1k": 0.005,
            "output_tokens_per_1k": 0.015
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
        max_tokens = model_info.get("max_tokens", 4096)
        
        if request.max_tokens and request.max_tokens > max_tokens:
            return False
        
        # Check temperature range (0.0 to 1.0 for Claude)
        if request.temperature is not None and (request.temperature < 0.0 or request.temperature > 1.0):
            return False
        
        # Check if we have content to process
        if not request.prompt and not request.messages:
            return False
        
        # Claude requires at least one user message
        if request.messages:
            has_user_message = any(msg.get("role") == "user" for msg in request.messages)
            if not has_user_message and not request.prompt:
                return False
        
        return True
    
    def get_stats(self) -> LLMProviderStats:
        """Get provider statistics."""
        return self.stats
    
    def reset_stats(self):
        """Reset provider statistics."""
        self.stats = LLMProviderStats()
        self.logger.info("Anthropic provider stats reset")


# Utility functions
def create_anthropic_config(
    model: str = "claude-3-sonnet-20240229",
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> LLMConfig:
    """
    Create Anthropic configuration.
    
    Args:
        model: Model name (claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-2.1)
        api_key: Anthropic API key (optional, will use environment if not provided)
        temperature: Generation temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        LLM configuration for Anthropic
    """
    return LLMConfig(
        provider=LLMProviderType.ANTHROPIC,
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens
    )


def is_anthropic_available() -> bool:
    """
    Check if Anthropic is available in the environment.
    
    Returns:
        True if Anthropic can be used, False otherwise
    """
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        return api_key is not None
    except ImportError:
        return False


# Model recommendations by use case
def get_recommended_claude_model(use_case: str = "general") -> str:
    """
    Get recommended Claude model for specific use case.
    
    Args:
        use_case: Use case (general, code, speed, complex)
        
    Returns:
        Recommended model name
    """
    recommendations = {
        "general": "claude-3-sonnet-20240229",
        "code": "claude-3-sonnet-20240229",
        "speed": "claude-3-haiku-20240307",
        "complex": "claude-3-opus-20240229",
        "reasoning": "claude-3-opus-20240229",
        "vision": "claude-3-sonnet-20240229"
    }
    
    return recommendations.get(use_case, "claude-3-sonnet-20240229") 