"""
LLM Provider Factory for TEAM LLM Services

Implements factory pattern for creating and managing LLM providers.
Supports multiple provider types and provides centralized configuration management.
"""

import logging
from typing import Dict, Type, Optional, Any, List
from datetime import datetime

from .models import (
    LLMProviderInterface,
    LLMConfig,
    LLMProviderType,
    LLMProviderError,
    LLMServiceStatus,
    LLMProviderStats
)
from .openai_provider import OpenAIProvider

# Mock logging for now
def get_logger(name, **kwargs):
    """Mock logger function."""
    return logging.getLogger(name)


class LLMProviderFactory:
    """
    Factory class for creating and managing LLM providers.
    
    Supports multiple provider types and provides centralized configuration
    and provider lifecycle management.
    """
    
    # Registry of available providers
    _provider_registry: Dict[LLMProviderType, Type[LLMProviderInterface]] = {
        LLMProviderType.OPENAI: OpenAIProvider,
        # Future providers can be added here:
        # LLMProviderType.ANTHROPIC: AnthropicProvider,
        # LLMProviderType.AZURE_OPENAI: AzureOpenAIProvider,
        # LLMProviderType.LOCAL: LocalProvider,
    }
    
    # Cache for initialized providers
    _provider_cache: Dict[str, LLMProviderInterface] = {}
    
    def __init__(self):
        """Initialize the provider factory."""
        self.logger = get_logger(
            "llm_services.provider_factory",
            extra_context={'component': 'LLMProviderFactory'}
        )
        
        self.logger.info("LLM Provider Factory initialized")
    
    @classmethod
    def create_provider(cls, config: LLMConfig) -> LLMProviderInterface:
        """
        Create a new LLM provider instance.
        
        Args:
            config: LLM configuration specifying provider type and settings
            
        Returns:
            Initialized LLM provider instance
            
        Raises:
            LLMProviderError: If provider type is not supported or creation fails
        """
        logger = get_logger("llm_services.provider_factory")
        
        if config.provider not in cls._provider_registry:
            error_msg = f"Unsupported provider type: {config.provider}"
            logger.error(error_msg)
            raise LLMProviderError(
                error_msg,
                error_code="UNSUPPORTED_PROVIDER",
                status=LLMServiceStatus.ERROR
            )
        
        provider_class = cls._provider_registry[config.provider]
        
        try:
            logger.info(f"Creating provider: {config.provider}")
            provider = provider_class(config)
            logger.info(f"Provider {config.provider} created successfully")
            return provider
            
        except Exception as e:
            error_msg = f"Failed to create provider {config.provider}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise LLMProviderError(
                error_msg,
                error_code="PROVIDER_CREATION_FAILED",
                status=LLMServiceStatus.ERROR
            )
    
    @classmethod
    def get_cached_provider(cls, cache_key: str, config: LLMConfig) -> LLMProviderInterface:
        """
        Get a cached provider or create a new one if not cached.
        
        Args:
            cache_key: Unique key for caching the provider
            config: LLM configuration
            
        Returns:
            LLM provider instance (cached or newly created)
        """
        if cache_key in cls._provider_cache:
            # Validate cached provider is still available
            cached_provider = cls._provider_cache[cache_key]
            if cached_provider.is_available():
                return cached_provider
            else:
                # Remove unavailable provider from cache
                del cls._provider_cache[cache_key]
        
        # Create new provider and cache it
        provider = cls.create_provider(config)
        cls._provider_cache[cache_key] = provider
        return provider
    
    @classmethod
    def get_supported_providers(cls) -> Dict[LLMProviderType, str]:
        """
        Get list of supported provider types with descriptions.
        
        Returns:
            Dictionary mapping provider types to descriptions
        """
        return {
            LLMProviderType.OPENAI: "OpenAI GPT models (GPT-4, GPT-3.5, etc.)",
            # Future providers:
            # LLMProviderType.ANTHROPIC: "Anthropic Claude models",
            # LLMProviderType.AZURE_OPENAI: "Azure OpenAI Service",
            # LLMProviderType.LOCAL: "Local/self-hosted models",
        }
    
    @classmethod
    def register_provider(cls, provider_type: LLMProviderType, 
                         provider_class: Type[LLMProviderInterface]):
        """
        Register a new provider type.
        
        Args:
            provider_type: The provider type enum
            provider_class: The provider implementation class
        """
        logger = get_logger("llm_services.provider_factory")
        
        if not issubclass(provider_class, LLMProviderInterface):
            raise ValueError("Provider class must implement LLMProviderInterface")
        
        cls._provider_registry[provider_type] = provider_class
        logger.info(f"Registered new provider: {provider_type}")
    
    @classmethod
    def clear_cache(cls):
        """Clear the provider cache."""
        cls._provider_cache.clear()
        logger = get_logger("llm_services.provider_factory")
        logger.info("Provider cache cleared")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        Get statistics about the provider cache.
        
        Returns:
            Cache statistics dictionary
        """
        cache_info = {}
        for key, provider in cls._provider_cache.items():
            cache_info[key] = {
                "provider_type": provider.config.provider.value,
                "model": provider.config.model,
                "is_available": provider.is_available(),
                "stats": provider.get_stats() if hasattr(provider, 'get_stats') else None
            }
        
        return {
            "total_cached_providers": len(cls._provider_cache),
            "providers": cache_info
        }


class LLMProviderManager:
    """
    High-level manager for LLM provider operations.
    
    Provides convenient methods for provider management, configuration,
    and usage tracking across the application.
    """
    
    def __init__(self, default_config: Optional[LLMConfig] = None):
        """
        Initialize the provider manager.
        
        Args:
            default_config: Default configuration to use for providers
        """
        self.logger = get_logger(
            "llm_services.provider_manager",
            extra_context={'component': 'LLMProviderManager'}
        )
        
        self.default_config = default_config
        self.factory = LLMProviderFactory()
        
        # Usage tracking
        self.usage_stats: Dict[LLMProviderType, LLMProviderStats] = {}
        
        self.logger.info("LLM Provider Manager initialized")
    
    def get_provider(self, config: Optional[LLMConfig] = None, 
                    cache_key: Optional[str] = None) -> LLMProviderInterface:
        """
        Get a provider instance with the given configuration.
        
        Args:
            config: LLM configuration (uses default if None)
            cache_key: Cache key for provider reuse
            
        Returns:
            LLM provider instance
        """
        if config is None:
            if self.default_config is None:
                raise LLMProviderError(
                    "No configuration provided and no default configuration set",
                    error_code="NO_CONFIG",
                    status=LLMServiceStatus.ERROR
                )
            config = self.default_config
        
        # Generate cache key if not provided
        if cache_key is None:
            cache_key = self._generate_cache_key(config)
        
        provider = self.factory.get_cached_provider(cache_key, config)
        
        # Initialize usage stats if needed
        if config.provider not in self.usage_stats:
            self.usage_stats[config.provider] = LLMProviderStats(
                provider_type=config.provider
            )
        
        return provider
    
    def _generate_cache_key(self, config: LLMConfig) -> str:
        """
        Generate a cache key for the given configuration.
        
        Args:
            config: LLM configuration
            
        Returns:
            Cache key string
        """
        key_parts = [
            config.provider.value,
            config.model,
            str(config.temperature),
            str(config.max_tokens or "none"),
            config.api_base or "default"
        ]
        return "|".join(key_parts)
    
    def test_all_providers(self) -> Dict[LLMProviderType, bool]:
        """
        Test all registered providers for availability.
        
        Returns:
            Dictionary mapping provider types to availability status
        """
        results = {}
        supported_providers = self.factory.get_supported_providers()
        
        for provider_type in supported_providers.keys():
            try:
                # Create a test configuration
                test_config = LLMConfig(
                    provider=provider_type,
                    model="test-model",  # Will be validated by provider
                    temperature=0.7
                )
                
                provider = self.factory.create_provider(test_config)
                results[provider_type] = provider.is_available()
                
            except Exception as e:
                self.logger.error(f"Failed to test provider {provider_type}: {e}")
                results[provider_type] = False
        
        return results
    
    def get_provider_recommendations(self, use_case: str = "general") -> List[LLMProviderType]:
        """
        Get recommended providers for a specific use case.
        
        Args:
            use_case: The use case (e.g., "general", "code_analysis", "fast", "accurate")
            
        Returns:
            List of recommended provider types in order of preference
        """
        recommendations = {
            "general": [LLMProviderType.OPENAI],
            "code_analysis": [LLMProviderType.OPENAI],
            "fast": [LLMProviderType.OPENAI],  # gpt-3.5-turbo
            "accurate": [LLMProviderType.OPENAI],  # gpt-4
            "cost_effective": [LLMProviderType.OPENAI],  # gpt-4o-mini
        }
        
        return recommendations.get(use_case, [LLMProviderType.OPENAI])
    
    def get_usage_statistics(self) -> Dict[LLMProviderType, LLMProviderStats]:
        """
        Get usage statistics for all providers.
        
        Returns:
            Dictionary mapping provider types to usage statistics
        """
        return self.usage_stats.copy()
    
    def reset_statistics(self):
        """Reset usage statistics for all providers."""
        self.usage_stats.clear()
        self.factory.clear_cache()
        self.logger.info("Provider statistics and cache reset")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status for LLM services.
        
        Returns:
            System status dictionary
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "supported_providers": list(self.factory.get_supported_providers().keys()),
            "provider_availability": self.test_all_providers(),
            "cache_stats": self.factory.get_cache_stats(),
            "usage_stats": {
                provider_type.value: {
                    "requests_total": stats.requests_total,
                    "success_rate": stats.get_success_rate(),
                    "average_response_time": stats.average_response_time_ms
                }
                for provider_type, stats in self.usage_stats.items()
            },
            "default_config": {
                "provider": self.default_config.provider.value if self.default_config else None,
                "model": self.default_config.model if self.default_config else None
            } if self.default_config else None
        } 