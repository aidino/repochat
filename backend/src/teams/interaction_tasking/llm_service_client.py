"""
LLM Service Client for TEAM Interaction & Tasking

Wrapper cho OpenAI provider để tương tác với User thông qua LLM thay vì rule-based.
"""

import os
from typing import Optional, Dict, Any, List
from teams.llm_services import OpenAIProvider, LLMConfig, LLMProviderType, LLMProviderError
from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit


class LLMServiceClient:
    """
    Client để gọi OpenAI LLM cho intent parsing và conversation.
    """
    
    def __init__(self):
        """Initialize LLM Service Client."""
        self.logger = get_logger("team.interaction.llm_client")
        self.provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize OpenAI provider."""
        try:
            # Tạo config cho OpenAI
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",  # Model nhanh và rẻ
                temperature=0.1,  # Giảm randomness để có kết quả ổn định
                max_tokens=500,
                timeout=30,
                api_key=os.getenv('OPENAI_API_KEY')
            )
            
            # Tạo OpenAI provider
            self.provider = OpenAIProvider(config)
            
            # Test connection
            if self.provider.is_available():
                self.logger.info("OpenAI provider initialized successfully")
            else:
                self.logger.warning("OpenAI provider not available - will fallback to rule-based")
                self.provider = None
                
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI provider: {e}")
            self.provider = None
    
    def call_openai(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """
        Gọi OpenAI để generate response.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (instructions)
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
            
        Raises:
            LLMProviderError: If the request fails
        """
        log_function_entry(self.logger, "call_openai", prompt_length=len(prompt))
        
        if not self.provider:
            raise LLMProviderError(
                "OpenAI provider not available",
                error_code="PROVIDER_NOT_AVAILABLE"
            )
        
        try:
            # Kết hợp system prompt và user prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Override parameters nếu có
            call_params = {
                'model': kwargs.get('model', 'gpt-4o-mini'),
                'temperature': kwargs.get('temperature', 0.1),
                'max_tokens': kwargs.get('max_tokens', 500)
            }
            
            # Gọi OpenAI
            response = self.provider.complete(full_prompt, **call_params)
            
            self.logger.info("OpenAI request successful")
            log_function_exit(self.logger, "call_openai", response_length=len(response))
            
            return response
            
        except Exception as e:
            self.logger.error(f"OpenAI request failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.provider is not None and self.provider.is_available()
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported models."""
        if self.provider:
            return self.provider.get_supported_models()
        return [] 