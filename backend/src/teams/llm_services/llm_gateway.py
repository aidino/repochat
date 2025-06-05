"""
LLMGatewayModule for LLM Services.

Module cao cấp để orchestrate prompt formatting và LLM calls,
cung cấp interface đơn giản cho việc xử lý LLM requests.
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .models import (
    LLMConfig, LLMServiceRequest, LLMServiceResponse, 
    LLMServiceStatus, LLMProviderType
)
from .prompt_formatter import PromptFormatterModule, FormattingResult
from .openai_provider import OpenAIProvider
from .provider_factory import LLMProviderFactory, LLMProviderManager

# Setup logging
logger = logging.getLogger(__name__)

class GatewayStatus(Enum):
    """Status của gateway."""
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class GatewayStats:
    """Thống kê của gateway."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    provider_usage: Dict[str, int] = field(default_factory=dict)
    template_usage: Dict[str, int] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=dict)

@dataclass
class GatewayRequest:
    """Request cho gateway."""
    prompt_id: str
    context_data: Dict[str, Any]
    llm_config: Optional[LLMConfig] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None

@dataclass
class GatewayResponse:
    """Response từ gateway."""
    success: bool
    response_text: Optional[str] = None
    error_message: Optional[str] = None
    request_id: Optional[str] = None
    processing_time: float = 0.0
    template_used: Optional[str] = None
    provider_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class LLMGatewayModule:
    """
    Gateway module cho LLM services.
    
    Chức năng chính:
    - Orchestrate prompt formatting và LLM calls
    - Quản lý providers và configurations
    - Tracking performance và statistics
    - Error handling và retry logic
    """
    
    def __init__(self, 
                 default_provider: LLMProviderType = LLMProviderType.OPENAI,
                 enable_stats: bool = True):
        """
        Khởi tạo LLMGatewayModule.
        
        Args:
            default_provider: Provider mặc định
            enable_stats: Có enable statistics tracking không
        """
        logger.info("Initializing LLMGatewayModule...")
        
        self.default_provider = default_provider
        self.enable_stats = enable_stats
        self.status = GatewayStatus.READY
        
        # Initialize components
        self.prompt_formatter = PromptFormatterModule()
        self.provider_factory = LLMProviderFactory()
        self.provider_manager = LLMProviderManager()
        
        # Statistics tracking
        self.stats = GatewayStats() if enable_stats else None
        
        # Cache for providers
        self._provider_cache = {}
        
        logger.info(f"LLMGatewayModule initialized with default provider: {default_provider.value}")
    
    def process_request(self, 
                       prompt_id: str, 
                       context_data: Dict[str, Any],
                       llm_config: Optional[LLMConfig] = None,
                       metadata: Dict[str, Any] = None) -> GatewayResponse:
        """
        Xử lý LLM request chính.
        
        Args:
            prompt_id: ID của prompt template
            context_data: Data để điền vào template
            llm_config: Cấu hình LLM (nếu None sẽ dùng default)
            metadata: Metadata bổ sung
            
        Returns:
            GatewayResponse: Response từ LLM
        """
        start_time = time.time()
        request_id = f"req_{int(time.time() * 1000)}"
        
        logger.info(f"Processing LLM request {request_id} with prompt_id='{prompt_id}'")
        
        try:
            # Update stats
            if self.stats:
                self.stats.total_requests += 1
                self.stats.template_usage[prompt_id] = self.stats.template_usage.get(prompt_id, 0) + 1
            
            # Validate status
            if self.status != GatewayStatus.READY:
                error_msg = f"Gateway not ready. Current status: {self.status.value}"
                logger.error(error_msg)
                return self._create_error_response(request_id, error_msg, start_time, prompt_id)
            
            # Step 1: Format prompt using PromptFormatterModule
            formatting_result = self.prompt_formatter.format_prompt(prompt_id, context_data)
            if not formatting_result.success:
                error_msg = f"Prompt formatting failed: {formatting_result.error.message}"
                logger.error(f"Request {request_id}: {error_msg}")
                return self._create_error_response(request_id, error_msg, start_time, prompt_id)
            
            formatted_prompt = formatting_result.formatted_prompt
            logger.debug(f"Request {request_id}: Prompt formatted successfully (length: {len(formatted_prompt)})")
            
            # Step 2: Prepare LLM config
            if llm_config is None:
                llm_config = self._get_default_config()
            
            # Step 3: Get LLM provider
            provider = self._get_provider(llm_config.provider)
            if provider is None:
                error_msg = f"Provider {llm_config.provider.value} not available"
                logger.error(f"Request {request_id}: {error_msg}")
                return self._create_error_response(request_id, error_msg, start_time, prompt_id)
            
            # Step 4: Call LLM provider directly (provider.complete expects string prompt)
            
            # Step 5: Call LLM provider
            logger.debug(f"Request {request_id}: Calling {llm_config.provider.value} provider...")
            llm_response = provider.complete(formatted_prompt)
            
            # Step 6: Process response
            processing_time = time.time() - start_time
            
            if llm_response.status == LLMServiceStatus.SUCCESS:
                # Success case
                response = GatewayResponse(
                    success=True,
                    response_text=llm_response.response_text,
                    request_id=request_id,
                    processing_time=processing_time,
                    template_used=prompt_id,
                    provider_used=llm_config.provider.value,
                    tokens_used=llm_response.metadata.get("total_tokens"),
                    cost_estimate=llm_response.metadata.get("cost_estimate"),
                    metadata=llm_response.metadata
                )
                
                # Update success stats
                if self.stats:
                    self.stats.successful_requests += 1
                    self.stats.total_processing_time += processing_time
                    self.stats.average_processing_time = self.stats.total_processing_time / self.stats.total_requests
                    provider_name = llm_config.provider.value
                    self.stats.provider_usage[provider_name] = self.stats.provider_usage.get(provider_name, 0) + 1
                
                logger.info(f"Request {request_id}: Completed successfully in {processing_time:.2f}s")
                return response
                
            else:
                # Error case from LLM
                error_msg = f"LLM call failed: {llm_response.error_message or llm_response.status.value}"
                logger.error(f"Request {request_id}: {error_msg}")
                
                response = GatewayResponse(
                    success=False,
                    error_message=error_msg,
                    request_id=request_id,
                    processing_time=processing_time,
                    template_used=prompt_id,
                    provider_used=llm_config.provider.value,
                    metadata=llm_response.metadata
                )
                
                # Update error stats
                if self.stats:
                    self.stats.failed_requests += 1
                    error_type = llm_response.status.value
                    self.stats.error_counts[error_type] = self.stats.error_counts.get(error_type, 0) + 1
                
                return response
        
        except Exception as e:
            # Unexpected error
            processing_time = time.time() - start_time
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Request {request_id}: {error_msg}", exc_info=True)
            
            if self.stats:
                self.stats.failed_requests += 1
                self.stats.error_counts["UNEXPECTED_ERROR"] = self.stats.error_counts.get("UNEXPECTED_ERROR", 0) + 1
            
            return self._create_error_response(request_id, error_msg, start_time, prompt_id)
    
    def process_gateway_request(self, gateway_request: GatewayRequest) -> GatewayResponse:
        """
        Xử lý gateway request object.
        
        Args:
            gateway_request: GatewayRequest object
            
        Returns:
            GatewayResponse: Response từ LLM
        """
        return self.process_request(
            prompt_id=gateway_request.prompt_id,
            context_data=gateway_request.context_data,
            llm_config=gateway_request.llm_config,
            metadata=gateway_request.metadata
        )
    
    def explain_code(self, 
                    code_snippet: str,
                    language: str = "python",
                    llm_config: Optional[LLMConfig] = None) -> GatewayResponse:
        """
        Convenience method để giải thích code.
        
        Args:
            code_snippet: Đoạn code cần giải thích
            language: Ngôn ngữ lập trình
            llm_config: Cấu hình LLM
            
        Returns:
            GatewayResponse: Response với giải thích code
        """
        context_data = {
            "code_snippet": code_snippet,
            "language": language
        }
        
        return self.process_request(
            prompt_id="explain_code",
            context_data=context_data,
            llm_config=llm_config,
            metadata={"operation": "explain_code", "language": language}
        )
    
    def analyze_function(self,
                        function_name: str,
                        function_code: str,
                        language: str = "python",
                        context: str = "",
                        llm_config: Optional[LLMConfig] = None) -> GatewayResponse:
        """
        Convenience method để phân tích function.
        
        Args:
            function_name: Tên function
            function_code: Code của function
            language: Ngôn ngữ lập trình
            context: Context bổ sung
            llm_config: Cấu hình LLM
            
        Returns:
            GatewayResponse: Response với phân tích function
        """
        context_data = {
            "function_name": function_name,
            "function_code": function_code,
            "language": language,
            "context": context or "Không có context bổ sung"
        }
        
        return self.process_request(
            prompt_id="analyze_function",
            context_data=context_data,
            llm_config=llm_config,
            metadata={"operation": "analyze_function", "function_name": function_name}
        )
    
    def review_changes(self,
                      file_path: str,
                      diff_content: str,
                      pr_context: str = "",
                      llm_config: Optional[LLMConfig] = None) -> GatewayResponse:
        """
        Convenience method để review code changes.
        
        Args:
            file_path: Đường dẫn file
            diff_content: Nội dung diff
            pr_context: Context của PR
            llm_config: Cấu hình LLM
            
        Returns:
            GatewayResponse: Response với review
        """
        context_data = {
            "file_path": file_path,
            "diff_content": diff_content,
            "pr_context": pr_context or "Pull request review"
        }
        
        return self.process_request(
            prompt_id="review_changes",
            context_data=context_data,
            llm_config=llm_config,
            metadata={"operation": "review_changes", "file_path": file_path}
        )
    
    def _get_default_config(self) -> LLMConfig:
        """Lấy configuration mặc định."""
        return LLMConfig(
            provider=self.default_provider,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=2000,
            timeout=30
        )
    
    def _get_provider(self, provider_type: LLMProviderType):
        """
        Lấy provider instance.
        
        Args:
            provider_type: Loại provider
            
        Returns:
            Provider instance hoặc None
        """
        # Check cache first
        provider_key = provider_type.value
        if provider_key in self._provider_cache:
            provider = self._provider_cache[provider_key]
            if provider.is_available():
                return provider
            else:
                # Remove unavailable provider from cache
                del self._provider_cache[provider_key]
        
        # Create new provider
        try:
            # Create a default config for this provider type
            default_config = LLMConfig(
                provider=provider_type,
                model="gpt-3.5-turbo" if provider_type == LLMProviderType.OPENAI else "default",
                temperature=0.7,
                max_tokens=2048,
                timeout=30,
                api_key=os.getenv('OPENAI_API_KEY') if provider_type == LLMProviderType.OPENAI else None
            )
            provider = self.provider_factory.create_provider(default_config)
            if provider and provider.is_available():
                self._provider_cache[provider_key] = provider
                return provider
        except Exception as e:
            logger.error(f"Failed to create provider {provider_type.value}: {str(e)}")
        
        return None
    
    def _create_error_response(self, 
                              request_id: str, 
                              error_message: str, 
                              start_time: float,
                              template_used: Optional[str] = None) -> GatewayResponse:
        """Tạo error response."""
        processing_time = time.time() - start_time
        return GatewayResponse(
            success=False,
            error_message=error_message,
            request_id=request_id,
            processing_time=processing_time,
            template_used=template_used
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Lấy status của gateway.
        
        Returns:
            Dict chứa status information
        """
        provider_status = {}
        for provider_type in LLMProviderType:
            try:
                provider = self._get_provider(provider_type)
                provider_status[provider_type.value] = provider is not None and provider.is_available()
            except:
                provider_status[provider_type.value] = False
        
        return {
            "gateway_status": self.status.value,
            "default_provider": self.default_provider.value,
            "provider_availability": provider_status,
            "total_templates": len(self.prompt_formatter._templates),
            "available_templates": list(self.prompt_formatter._templates.keys()),
            "cache_size": len(self._provider_cache),
            "stats_enabled": self.enable_stats
        }
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """
        Lấy statistics.
        
        Returns:
            Dict chứa statistics hoặc None nếu stats disabled
        """
        if not self.stats:
            return None
        
        success_rate = 0.0
        if self.stats.total_requests > 0:
            success_rate = (self.stats.successful_requests / self.stats.total_requests) * 100
        
        return {
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "success_rate": round(success_rate, 2),
            "average_processing_time": round(self.stats.average_processing_time, 3),
            "total_processing_time": round(self.stats.total_processing_time, 2),
            "provider_usage": dict(self.stats.provider_usage),
            "template_usage": dict(self.stats.template_usage),
            "error_counts": dict(self.stats.error_counts)
        }
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        if self.stats:
            self.stats = GatewayStats()
            logger.info("Gateway statistics reset")
    
    def set_status(self, status: GatewayStatus) -> None:
        """
        Set gateway status.
        
        Args:
            status: New status
        """
        old_status = self.status
        self.status = status
        logger.info(f"Gateway status changed from {old_status.value} to {status.value}")
    
    def clear_provider_cache(self) -> None:
        """Clear provider cache."""
        self._provider_cache.clear()
        logger.info("Provider cache cleared")
    
    def validate_prompt(self, prompt_id: str, context_data: Dict[str, Any]) -> FormattingResult:
        """
        Validate prompt mà không thực hiện LLM call.
        
        Args:
            prompt_id: ID của prompt
            context_data: Context data
            
        Returns:
            FormattingResult: Kết quả validation
        """
        return self.prompt_formatter.validate_context_data(prompt_id, context_data)
    
    def get_available_templates(self) -> List[str]:
        """
        Lấy danh sách available templates.
        
        Returns:
            List[str]: Danh sách template IDs
        """
        return list(self.prompt_formatter._templates.keys())
    
    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin về template.
        
        Args:
            template_id: ID của template
            
        Returns:
            Dict chứa template info hoặc None
        """
        return self.prompt_formatter.get_template_info(template_id)


# Convenience functions
def create_llm_gateway(provider: LLMProviderType = LLMProviderType.OPENAI) -> LLMGatewayModule:
    """
    Tạo instance mới của LLMGatewayModule.
    
    Args:
        provider: Default provider
        
    Returns:
        LLMGatewayModule: Instance đã khởi tạo
    """
    return LLMGatewayModule(default_provider=provider)

def explain_code_with_gateway(code_snippet: str, 
                             language: str = "python",
                             provider: LLMProviderType = LLMProviderType.OPENAI) -> GatewayResponse:
    """
    Convenience function để giải thích code với gateway.
    
    Args:
        code_snippet: Đoạn code cần giải thích
        language: Ngôn ngữ lập trình
        provider: LLM provider
        
    Returns:
        GatewayResponse: Response với giải thích
    """
    gateway = create_llm_gateway(provider)
    return gateway.explain_code(code_snippet, language) 