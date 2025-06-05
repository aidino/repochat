"""
TEAM LLM Services Package

Provides infrastructure for integrating with Large Language Model providers.
Includes provider abstraction layer, OpenAI integration, configuration management,
and usage tracking.

Key Components:
- LLMProviderInterface: Abstract interface for LLM providers
- OpenAIProvider: OpenAI API integration
- LLMProviderFactory: Factory for creating providers
- LLMProviderManager: High-level provider management
- Data models for requests, responses, and configuration
"""

# Core data models and interfaces
from .models import (
    # Enums
    LLMProviderType,
    LLMServiceStatus,
    
    # Configuration
    LLMConfig,
    
    # Request/Response models
    LLMServiceRequest,
    LLMServiceResponse,
    
    # Template system
    PromptTemplate,
    
    # Provider interface
    LLMProviderInterface,
    LLMProviderError,
    LLMProviderStats
)

# Provider implementations
from .openai_provider import OpenAIProvider

# Factory and management
from .provider_factory import LLMProviderFactory, LLMProviderManager

# Export lists for convenient access
__all__ = [
    # Core models and interfaces
    "LLMProviderType",
    "LLMServiceStatus", 
    "LLMConfig",
    "LLMServiceRequest",
    "LLMServiceResponse",
    "PromptTemplate",
    "LLMProviderInterface",
    "LLMProviderError",
    "LLMProviderStats",
    
    # Provider implementations
    "OpenAIProvider",
    
    # Factory and management
    "LLMProviderFactory",
    "LLMProviderManager",
]

# Package metadata
__version__ = "1.0.0"
__author__ = "TEAM LLM Services"
__description__ = "LLM Provider Infrastructure for RepoChat"

# Default configuration for easy access
def get_default_openai_config() -> LLMConfig:
    """
    Get a default OpenAI configuration.
    
    Returns:
        Default LLMConfig for OpenAI with commonly used settings
    """
    return LLMConfig(
        provider=LLMProviderType.OPENAI,
        model="gpt-4o-mini",  # Cost-effective default
        temperature=0.7,
        max_tokens=2048,
        timeout=30
    )

# Convenience function for quick provider creation
def create_openai_provider(api_key: str = None, model: str = "gpt-4o-mini") -> OpenAIProvider:
    """
    Create an OpenAI provider with default settings.
    
    Args:
        api_key: OpenAI API key (if None, will use environment variable)
        model: Model to use
        
    Returns:
        Configured OpenAI provider
    """
    config = LLMConfig(
        provider=LLMProviderType.OPENAI,
        model=model,
        temperature=0.7,
        max_tokens=2048,
        timeout=30,
        api_key=api_key
    )
    
    return OpenAIProvider(config)

# Version compatibility check
def check_dependencies():
    """
    Check if required dependencies are available.
    
    Returns:
        Dictionary with dependency availability status
    """
    dependencies = {}
    
    try:
        import openai
        dependencies["openai"] = {
            "available": True,
            "version": getattr(openai, "__version__", "unknown")
        }
    except ImportError:
        dependencies["openai"] = {
            "available": False,
            "error": "OpenAI library not installed"
        }
    
    try:
        import pydantic
        dependencies["pydantic"] = {
            "available": True,
            "version": getattr(pydantic, "__version__", "unknown")
        }
    except ImportError:
        dependencies["pydantic"] = {
            "available": False,
            "error": "Pydantic library not installed"
        }
    
    return dependencies
