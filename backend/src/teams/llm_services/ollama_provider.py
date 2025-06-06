"""
Ollama Provider Implementation

Ollama local LLM provider using langchain-ollama.
"""

import os
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# Import langchain-ollama components
try:
    from langchain_ollama import OllamaLLM
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    OllamaLLM = None

from .models import (
    LLMProviderInterface, 
    LLMConfig, 
    LLMProviderError, 
    LLMServiceStatus,
    LLMProviderType
)
# Mock logger for now
def get_logger(name, **kwargs):
    import logging
    return logging.getLogger(name)


class OllamaProvider(LLMProviderInterface):
    """Ollama provider implementation using langchain-ollama."""
    
    def __init__(self, config: LLMConfig):
        """Initialize Ollama provider."""
        self.logger = get_logger("llm_services.ollama_provider")
        
        if not OLLAMA_AVAILABLE:
            raise LLMProviderError(
                "langchain-ollama not installed",
                error_code="OLLAMA_NOT_AVAILABLE"
            )
        
        self.config = config
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        try:
            self.client = OllamaLLM(
                model=config.model,
                base_url=self.base_url,
                temperature=config.temperature,
                timeout=config.timeout,
            )
            self.logger.info(f"Ollama provider initialized: {config.model}")
        except Exception as e:
            raise LLMProviderError(f"Failed to init Ollama: {e}")
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion using Ollama."""
        try:
            response = self.client.invoke(prompt)
            return response
        except Exception as e:
            raise LLMProviderError(f"Ollama completion failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        if not OLLAMA_AVAILABLE:
            return False
        try:
            self.client.invoke("test")
            return True
        except:
            return False
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Ollama models."""
        return [
            "llama2:7b", "llama2:13b", "codellama:7b", 
            "mistral:7b", "neural-chat:7b", "phi:2.7b"
        ]
    
    def validate_config(self, config: LLMConfig) -> bool:
        """Validate Ollama configuration."""
        return (
            config.provider == LLMProviderType.OLLAMA
            and config.model is not None
            and 0.0 <= config.temperature <= 2.0
            and config.timeout > 0
        )


def create_ollama_provider(model: str = "llama2:7b") -> OllamaProvider:
    """Create Ollama provider with default config."""
    config = LLMConfig(
        provider=LLMProviderType.OLLAMA,
        model=model,
        temperature=0.7,
        timeout=30
    )
    return OllamaProvider(config)


def is_ollama_available() -> bool:
    """Check if Ollama is available."""
    return OLLAMA_AVAILABLE


def get_ollama_default_models() -> List[str]:
    """Get list of default Ollama models."""
    return [
        "llama2:7b", "llama2:13b", "codellama:7b",
        "mistral:7b", "neural-chat:7b", "phi:2.7b"
    ] 