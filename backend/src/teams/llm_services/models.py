"""
Data Models for TEAM LLM Services

Contains common data structures used across LLM service modules.
Includes request/response models, configuration models, and provider interfaces.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class LLMProviderType(Enum):
    """Supported LLM provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"


class LLMServiceStatus(Enum):
    """Status codes for LLM service operations."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    API_KEY_INVALID = "api_key_invalid"
    MODEL_NOT_FOUND = "model_not_found"
    QUOTA_EXCEEDED = "quota_exceeded"


@dataclass
class LLMConfig:
    """Configuration for LLM provider and model."""
    provider: LLMProviderType
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30  # seconds
    
    # Provider-specific configurations
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    organization: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")


class LLMServiceRequest(BaseModel):
    """Request structure for LLM services."""
    
    # Core request data
    prompt_text: str = Field(..., description="The complete prompt text to send to LLM")
    prompt_id: Optional[str] = Field(None, description="Template ID if using prompt templates")
    context_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Context data for prompt formatting")
    
    # LLM configuration
    llm_config: LLMConfig = Field(..., description="LLM configuration to use")
    
    # Request metadata
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User making the request")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Request parameters
    stream: bool = Field(False, description="Whether to stream the response")
    priority: int = Field(1, description="Request priority (1=highest, 5=lowest)")
    
    class Config:
        arbitrary_types_allowed = True


class LLMServiceResponse(BaseModel):
    """Response structure from LLM services."""
    
    # Core response data
    response_text: str = Field(..., description="The LLM response text")
    status: LLMServiceStatus = Field(..., description="Response status")
    
    # Response metadata
    request_id: Optional[str] = Field(None, description="Original request identifier")
    model_used: Optional[str] = Field(None, description="Actual model used for generation")
    
    # Performance metrics
    response_time_ms: float = Field(0.0, description="Response time in milliseconds")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost in USD")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if status is ERROR")
    error_code: Optional[str] = Field(None, description="Error code for debugging")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None, description="When response was completed")
    
    def is_success(self) -> bool:
        """Check if the response was successful."""
        return self.status == LLMServiceStatus.SUCCESS
    
    def is_error(self) -> bool:
        """Check if the response has an error."""
        return self.status == LLMServiceStatus.ERROR


class LLMProviderInterface(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """
        Generate completion for the given prompt.
        
        Args:
            prompt: The input prompt text
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated completion text
            
        Raises:
            LLMProviderError: If the request fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and configured.
        
        Returns:
            True if provider is ready to use
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported models for this provider.
        
        Returns:
            List of model names
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: LLMConfig) -> bool:
        """
        Validate the given configuration for this provider.
        
        Args:
            config: LLM configuration to validate
            
        Returns:
            True if configuration is valid
        """
        pass


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 status: LLMServiceStatus = LLMServiceStatus.ERROR):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status = status


class PromptTemplate(BaseModel):
    """Template for generating prompts."""
    
    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template description")
    template_text: str = Field(..., description="Template string with placeholders")
    required_variables: List[str] = Field(default_factory=list, description="Required template variables")
    optional_variables: List[str] = Field(default_factory=list, description="Optional template variables")
    default_values: Dict[str, Any] = Field(default_factory=dict, description="Default values for optional variables")
    
    # Template metadata
    category: Optional[str] = Field(None, description="Template category")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    version: str = Field("1.0", description="Template version")
    created_at: datetime = Field(default_factory=datetime.now)
    
    def format(self, **kwargs) -> str:
        """
        Format the template with given variables.
        
        Args:
            **kwargs: Template variables
            
        Returns:
            Formatted prompt text
            
        Raises:
            ValueError: If required variables are missing
        """
        # Check for required variables
        missing_vars = [var for var in self.required_variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required template variables: {missing_vars}")
        
        # Format template
        try:
            return self.template_text.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Template variable not provided: {e}")


@dataclass
class LLMProviderStats:
    """Statistics for LLM provider usage."""
    provider_type: LLMProviderType
    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    total_tokens_used: int = 0
    total_response_time_ms: float = 0.0
    average_response_time_ms: float = 0.0
    last_request_at: Optional[datetime] = None
    
    def update_stats(self, response: LLMServiceResponse):
        """Update statistics with a new response."""
        self.requests_total += 1
        self.total_response_time_ms += response.response_time_ms
        self.average_response_time_ms = self.total_response_time_ms / self.requests_total
        
        if response.is_success():
            self.requests_successful += 1
        else:
            self.requests_failed += 1
            
        if response.tokens_used:
            self.total_tokens_used += response.tokens_used
            
        self.last_request_at = datetime.now()
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.requests_total == 0:
            return 0.0
        return (self.requests_successful / self.requests_total) * 100 