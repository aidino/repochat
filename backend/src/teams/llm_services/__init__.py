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

import logging
from typing import Dict, Any, List, Optional

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
from .google_genai_provider import GoogleGenAIProvider, create_google_genai_config, is_google_genai_available
from .anthropic_provider import AnthropicProvider, create_anthropic_config, is_anthropic_available

# Factory and management
from .provider_factory import LLMProviderFactory, LLMProviderManager

# NEW: Task 3.4 modules
from .template_loader import (
    TemplateLoader,
    TemplateLoadError,
    TemplateLoadResult,
    create_template_loader,
    load_templates_from_directory
)

from .prompt_formatter import (
    PromptFormatterModule,
    TemplateType,
    FormattingError,
    FormattingResult,
    create_prompt_formatter,
    format_explain_code_prompt,
    get_available_templates
)

from .llm_gateway import (
    LLMGatewayModule,
    GatewayStatus,
    GatewayStats,
    GatewayRequest,
    GatewayResponse,
    create_llm_gateway,
    explain_code_with_gateway
)

# Import convenience function từ code analysis
# Note: Import moved to avoid circular dependency - will be added dynamically

# Setup logging
logger = logging.getLogger(__name__)

# Dynamic import function to avoid circular dependency
def create_explain_code_request(code_snippet: str, language: str = "python"):
    """
    Convenience function để tạo explain_code request.
    
    Args:
        code_snippet: Đoạn code cần giải thích
        language: Ngôn ngữ lập trình
        
    Returns:
        LLMServiceRequest: Request đã được tạo
    """
    # Import locally to avoid circular dependency
    from ..code_analysis.llm_analysis_support_module import create_llm_analysis_support
    
    module = create_llm_analysis_support()
    return module.create_explain_code_request(code_snippet, language)

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
    "GoogleGenAIProvider",
    "AnthropicProvider",
    "create_google_genai_config",
    "create_anthropic_config",
    "is_google_genai_available", 
    "is_anthropic_available",
    
    # Factory and management
    "LLMProviderFactory",
    "LLMProviderManager",
    
    # Task 3.4: Template Loader
    "TemplateLoader",
    "TemplateLoadError",
    "TemplateLoadResult",
    "create_template_loader",
    "load_templates_from_directory",
    
    # Task 3.4: Prompt Formatter
    "PromptFormatterModule",
    "TemplateType",
    "FormattingError",
    "FormattingResult",
    "create_prompt_formatter",
    "format_explain_code_prompt",
    "get_available_templates",
    
    # Task 3.4: LLM Gateway
    "LLMGatewayModule",
    "GatewayStatus",
    "GatewayStats", 
    "GatewayRequest",
    "GatewayResponse",
    "create_llm_gateway",
    "explain_code_with_gateway",
    
    # Task 3.6: TEAM LLM Services Facade
    "TeamLLMServices",
    
    # Task 3.5: Convenience functions
    "create_explain_code_request",
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
        model="gpt-3.5-turbo",  # User requested model
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

# Task 3.6: TeamLLMServices Facade for Orchestrator integration
class TeamLLMServices:
    """
    TEAM LLM Services Facade - Cung cấp interface thống nhất cho Orchestrator Agent.
    
    Đây là facade class cho Task 3.6, cung cấp một interface đơn giản
    để Orchestrator có thể định tuyến LLMServiceRequest và nhận LLMServiceResponse.
    """
    
    def __init__(self, default_provider: LLMProviderType = LLMProviderType.OPENAI):
        """
        Khởi tạo TeamLLMServices facade.
        
        Args:
            default_provider: Provider LLM mặc định
        """
        self.logger = logging.getLogger(f"{__name__}.TeamLLMServices")
        self.gateway = LLMGatewayModule(default_provider=default_provider)
        self.logger.info(f"TeamLLMServices facade initialized with provider: {default_provider.value}")
    
    def process_request(self, llm_request: LLMServiceRequest) -> LLMServiceResponse:
        """
        Xử lý LLMServiceRequest và trả về LLMServiceResponse.
        
        Đây là method chính cho Task 3.6 DoD requirements:
        - Nhận LLMServiceRequest từ Orchestrator
        - Gọi LLMGatewayModule để xử lý
        - Trả về LLMServiceResponse
        
        Args:
            llm_request: LLMServiceRequest từ team khác (ví dụ: Code Analysis)
            
        Returns:
            LLMServiceResponse: Response từ LLM service
        """
        self.logger.info(f"Processing LLMServiceRequest: prompt_id='{llm_request.prompt_id}', user_id='{llm_request.user_id}'")
        
        try:
            # Gọi LLMGatewayModule để xử lý request
            gateway_response = self.gateway.process_request(
                prompt_id=llm_request.prompt_id,
                context_data=llm_request.context_data,
                llm_config=llm_request.llm_config,
                metadata={
                    "user_id": llm_request.user_id,
                    "request_id": llm_request.request_id,
                    "priority": llm_request.priority,
                    "prompt_text": llm_request.prompt_text
                }
            )
            
            # Convert GatewayResponse thành LLMServiceResponse
            if gateway_response.success:
                response = LLMServiceResponse(
                    response_text=gateway_response.response_text,
                    status=LLMServiceStatus.SUCCESS,
                    request_id=llm_request.request_id,
                    metadata={
                        "processing_time": gateway_response.processing_time,
                        "template_used": gateway_response.template_used,
                        "provider_used": gateway_response.provider_used,
                        "tokens_used": gateway_response.tokens_used,
                        "cost_estimate": gateway_response.cost_estimate,
                        "gateway_request_id": gateway_response.request_id
                    }
                )
                self.logger.info(f"LLMServiceRequest processed successfully in {gateway_response.processing_time:.2f}s")
            else:
                response = LLMServiceResponse(
                    response_text="",
                    status=LLMServiceStatus.ERROR,
                    error_message=gateway_response.error_message,
                    request_id=llm_request.request_id,
                    metadata={
                        "processing_time": gateway_response.processing_time,
                        "template_used": gateway_response.template_used,
                        "provider_used": gateway_response.provider_used,
                        "gateway_request_id": gateway_response.request_id
                    }
                )
                self.logger.error(f"LLMServiceRequest failed: {gateway_response.error_message}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Unexpected error processing LLMServiceRequest: {str(e)}", exc_info=True)
            return LLMServiceResponse(
                response_text="",
                status=LLMServiceStatus.ERROR,
                error_message=f"Unexpected error: {str(e)}",
                request_id=llm_request.request_id,
                metadata={"error_type": "UNEXPECTED_ERROR"}
            )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Lấy trạng thái của TEAM LLM Services.
        
        Returns:
            Dict chứa thông tin trạng thái
        """
        return {
            "team": "LLM Services",
            "facade_ready": True,
            "gateway_status": self.gateway.get_status(),
            "gateway_stats": self.gateway.get_stats()
        }

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

# NEW: Task 3.4 convenience functions

def create_complete_llm_system(provider: LLMProviderType = LLMProviderType.OPENAI) -> LLMGatewayModule:
    """
    Create a complete LLM system với gateway, formatter, và providers.
    
    Args:
        provider: Default provider type
        
    Returns:
        LLMGatewayModule: Complete LLM system
    """
    logger.info(f"Creating complete LLM system with provider: {provider.value}")
    return LLMGatewayModule(default_provider=provider)

def explain_code_simple(code_snippet: str, 
                       language: str = "python",
                       provider: LLMProviderType = LLMProviderType.OPENAI) -> str:
    """
    Simple function để giải thích code với minimal setup.
    
    Args:
        code_snippet: Code cần giải thích
        language: Ngôn ngữ lập trình
        provider: LLM provider
        
    Returns:
        str: Giải thích code hoặc error message
    """
    try:
        gateway = create_complete_llm_system(provider)
        response = gateway.explain_code(code_snippet, language)
        
        if response.success:
            return response.response_text
        else:
            return f"Error: {response.error_message}"
    except Exception as e:
        logger.error(f"Error in explain_code_simple: {str(e)}")
        return f"System error: {str(e)}"

def get_system_status() -> Dict[str, Any]:
    """
    Get overall system status cho LLM services.
    
    Returns:
        Dict[str, Any]: System status information
    """
    try:
        # Check dependencies
        deps = check_dependencies()
        
        # Test gateway creation
        gateway_working = False
        try:
            gateway = create_complete_llm_system()
            status = gateway.get_status()
            gateway_working = status["gateway_status"] == "ready"
        except Exception as e:
            logger.error(f"Gateway test failed: {str(e)}")
        
        # Test formatter
        formatter_working = False
        try:
            formatter = create_prompt_formatter()
            templates = formatter.get_stats()
            formatter_working = templates["total_templates"] > 0
        except Exception as e:
            logger.error(f"Formatter test failed: {str(e)}")
        
        # Test provider factory
        factory_working = False
        try:
            factory = LLMProviderFactory()
            providers = factory.get_supported_providers()
            factory_working = len(providers) > 0
        except Exception as e:
            logger.error(f"Factory test failed: {str(e)}")
        
        return {
            "dependencies": deps,
            "components": {
                "gateway": gateway_working,
                "formatter": formatter_working,
                "factory": factory_working
            },
            "overall_status": all([
                deps.get("openai", False),
                deps.get("pydantic", False),
                gateway_working,
                formatter_working,
                factory_working
            ])
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return {
            "error": str(e),
            "overall_status": False
        }

# Task 3.4 completion info
TASK_3_4_FEATURES = {
    "prompt_formatter": "✅ PromptFormatterModule with 5 predefined templates",
    "llm_gateway": "✅ LLMGatewayModule với full orchestration",
    "explain_code_template": "✅ Template 'Giải thích code' với Vietnamese output",
    "convenience_functions": "✅ High-level functions for easy usage",
    "error_handling": "✅ Comprehensive error handling và validation",
    "statistics": "✅ Performance tracking và usage statistics",
    "template_management": "✅ Template validation và management"
}

def get_task_3_4_info() -> Dict[str, Any]:
    """
    Get Task 3.4 implementation information.
    
    Returns:
        Dict containing Task 3.4 features and status
    """
    return {
        "task": "Task 3.4 (F3.4): LLMGatewayModule và PromptFormatterModule",
        "features": TASK_3_4_FEATURES,
        "modules_added": [
            "prompt_formatter.py (560 lines)",
            "llm_gateway.py (550 lines)"
        ],
        "templates_included": [
            "explain_code - Giải thích chức năng code",
            "analyze_function - Phân tích function chi tiết", 
            "review_changes - Review code changes trong PR",
            "find_issues - Tìm potential issues trong code",
            "suggest_improvements - Đề xuất cải thiện code"
        ],
        "dod_compliance": {
            "prompt_template_explain_code": "✅ Template với placeholder {code_snippet}",
            "prompt_formatter_module": "✅ Module nhận template_id và context_data",
            "llm_gateway_module": "✅ Module nhận prompt_id và context_data, gọi formatter và OpenAI"
        },
        "usage_example": "explain_code_simple('def hello(): return \"world\"')"
    }
