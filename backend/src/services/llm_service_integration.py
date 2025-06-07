"""
LLM Service Integration with User Settings

This service integrates user-saved API keys with LLM providers,
allowing users to use their own API keys for different providers.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from teams.llm_services import (
    LLMConfig, 
    LLMProviderType, 
    OpenAIProvider,
    LLMProviderError,
    LLMServiceStatus
)
from services.user_settings_service import UserSettingsService
from shared.models.user_settings import APIKeyProvider
from shared.utils.logging_config import get_logger


class UserLLMService:
    """
    Service to create LLM providers using user's saved API keys.
    """
    
    def __init__(self):
        """Initialize the user LLM service."""
        self.logger = get_logger("services.user_llm")
        self.user_settings_service = UserSettingsService()
        
        # Mapping between our APIKeyProvider and LLMProviderType
        self.provider_mapping = {
            APIKeyProvider.OPENAI: LLMProviderType.OPENAI,
            APIKeyProvider.ANTHROPIC: LLMProviderType.ANTHROPIC,
            APIKeyProvider.GOOGLE_GENAI: LLMProviderType.GOOGLE_GENAI,
            APIKeyProvider.AZURE_OPENAI: LLMProviderType.AZURE_OPENAI,
            APIKeyProvider.HUGGINGFACE: LLMProviderType.HUGGINGFACE,
        }
        
        self.logger.info("User LLM Service initialized")
    
    def get_user_api_key(self, user_id: str, provider: APIKeyProvider) -> Optional[str]:
        """
        Get decrypted API key for user and provider.
        
        Args:
            user_id: User identifier
            provider: API key provider type
            
        Returns:
            Decrypted API key or None if not found
        """
        try:
            user_settings = self.user_settings_service.get_user_settings(user_id)
            
            # Use the provider string key to lookup
            key_id = f"{provider.value}"
            if key_id in user_settings.api_keys:
                encrypted_key = user_settings.api_keys[key_id]
                # Decrypt the API key
                decrypted_key = self.user_settings_service.api_key_manager.decrypt_api_key(encrypted_key)
                
                self.logger.info(f"Retrieved API key for user {user_id}, provider {provider.value}")
                return decrypted_key
            else:
                self.logger.warning(f"No API key found for user {user_id}, provider {provider.value}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get API key for user {user_id}, provider {provider.value}: {e}")
            return None
    
    def create_openai_provider(self, user_id: str, model: Optional[str] = None) -> Optional[OpenAIProvider]:
        """
        Create OpenAI provider using user's API key.
        
        Args:
            user_id: User identifier
            model: Model to use (if None, uses user's default)
            
        Returns:
            Configured OpenAI provider or None if API key not available
        """
        try:
            # Get user's OpenAI API key
            api_key = self.get_user_api_key(user_id, APIKeyProvider.OPENAI)
            if not api_key:
                self.logger.warning(f"No OpenAI API key for user {user_id}")
                return None
            
            # Get user settings for model preference
            user_settings = self.user_settings_service.get_user_settings(user_id)
            
            # Use provided model or user's default or system default
            selected_model = (
                model or 
                user_settings.preferences.default_llm_model or 
                "gpt-4o-mini"
            )
            
            # Create LLM config
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model=selected_model,
                temperature=user_settings.preferences.temperature_default,
                max_tokens=user_settings.preferences.max_tokens_default,
                timeout=30,
                api_key=api_key
            )
            
            # Create and return provider
            provider = OpenAIProvider(config)
            
            self.logger.info(f"Created OpenAI provider for user {user_id} with model {selected_model}")
            return provider
            
        except Exception as e:
            self.logger.error(f"Failed to create OpenAI provider for user {user_id}: {e}")
            return None
    
    def get_user_preferred_model(self, user_id: str, provider: APIKeyProvider) -> str:
        """
        Get user's preferred model for a provider.
        
        Args:
            user_id: User identifier  
            provider: Provider type
            
        Returns:
            Preferred model name
        """
        try:
            user_settings = self.user_settings_service.get_user_settings(user_id)
            
            # Map provider to model preference
            if provider == APIKeyProvider.OPENAI:
                return user_settings.preferences.default_llm_model or "gpt-4o-mini"
            elif provider == APIKeyProvider.ANTHROPIC:
                return "claude-3-sonnet-20240229"  # Default Claude model
            elif provider == APIKeyProvider.GOOGLE_GENAI:
                return "gemini-pro"  # Default Gemini model
            else:
                return "gpt-4o-mini"  # Fallback default
                
        except Exception as e:
            self.logger.error(f"Failed to get preferred model for user {user_id}: {e}")
            return "gpt-4o-mini"  # Safe fallback
    
    def test_user_api_key(self, user_id: str, provider: APIKeyProvider) -> Dict[str, Any]:
        """
        Test user's API key by making a simple request.
        
        Args:
            user_id: User identifier
            provider: Provider type
            
        Returns:
            Test result with success status and details
        """
        try:
            if provider == APIKeyProvider.OPENAI:
                openai_provider = self.create_openai_provider(user_id)
                if not openai_provider:
                    return {
                        "success": False,
                        "error": "Failed to create OpenAI provider - API key may be missing"
                    }
                
                # Test with a simple prompt
                test_result = openai_provider.test_connection()
                
                return {
                    "success": test_result,
                    "provider": provider.value,
                    "tested_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Testing not implemented for provider {provider.value}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to test API key for user {user_id}, provider {provider.value}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_providers_for_user(self, user_id: str) -> Dict[APIKeyProvider, Dict[str, Any]]:
        """
        Get list of providers that user has API keys for.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of available providers with their details
        """
        try:
            user_settings = self.user_settings_service.get_user_settings(user_id)
            available_providers = {}
            
            for provider, encrypted_key in user_settings.api_keys.items():
                available_providers[provider] = {
                    "nickname": encrypted_key.nickname,
                    "created_at": encrypted_key.created_at.isoformat(),
                    "last_used": encrypted_key.last_used.isoformat() if encrypted_key.last_used else None,
                    "preferred_model": self.get_user_preferred_model(user_id, provider)
                }
            
            self.logger.info(f"Found {len(available_providers)} providers for user {user_id}")
            return available_providers
            
        except Exception as e:
            self.logger.error(f"Failed to get available providers for user {user_id}: {e}")
            return {} 