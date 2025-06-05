"""
LLM Analysis Support Module for TEAM Code Analysis

This module provides support for creating LLM service requests for code analysis tasks.
It bridges between code analysis needs and LLM services by formatting code contexts
into appropriate LLM requests.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import from TEAM LLM Services
from ..llm_services.models import (
    LLMServiceRequest, LLMServiceResponse, LLMConfig, 
    LLMProviderType, LLMServiceStatus
)

# Import from current TEAM models
from .models import AnalysisFinding, AnalysisFindingType, AnalysisSeverity

logger = logging.getLogger(__name__)


@dataclass
class CodeAnalysisContext:
    """Context data for code analysis requests."""
    code_snippet: str
    language: Optional[str] = "python"
    file_path: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    analysis_type: Optional[str] = "explain_code"
    additional_context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}


class LLMAnalysisSupportModule:
    """
    Module chịu trách nhiệm chuẩn bị ngữ cảnh và tạo LLMServiceRequest cho code analysis.
    
    Module này hoạt động như một bridge giữa TEAM Code Analysis và TEAM LLM Services,
    chuyển đổi các yêu cầu phân tích code thành format phù hợp cho LLM services.
    """
    
    def __init__(self, default_llm_config: Optional[LLMConfig] = None):
        """
        Khởi tạo LLMAnalysisSupportModule.
        
        Args:
            default_llm_config: Cấu hình LLM mặc định. Nếu None, sẽ tạo config mặc định.
        """
        self.default_llm_config = default_llm_config or self._create_default_config()
        logger.info("LLMAnalysisSupportModule initialized")
    
    def _create_default_config(self) -> LLMConfig:
        """Tạo cấu hình LLM mặc định."""
        return LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-3.5-turbo",
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=2000,
            timeout=30
        )
    
    def create_explain_code_request(
        self, 
        code_snippet: str, 
        language: str = "python",
        llm_config: Optional[LLMConfig] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> LLMServiceRequest:
        """
        Tạo LLMServiceRequest để giải thích đoạn code.
        
        Args:
            code_snippet: Đoạn code cần giải thích
            language: Ngôn ngữ lập trình
            llm_config: Cấu hình LLM (nếu None, dùng default)
            additional_context: Context bổ sung
            
        Returns:
            LLMServiceRequest: Request đã được format
        """
        logger.debug(f"Creating explain_code request for {len(code_snippet)} chars of {language} code")
        
        # Prepare context data
        context_data = {
            "code_snippet": code_snippet,
            "language": language
        }
        
        if additional_context:
            context_data.update(additional_context)
        
        # Use provided config or default
        config = llm_config or self.default_llm_config
        
        # Create request
        request = LLMServiceRequest(
            prompt_text="",  # Will be filled by PromptFormatterModule
            prompt_id="explain_code",
            context_data=context_data,
            llm_config=config,
            request_id=f"explain_code_{int(time.time() * 1000)}",
            user_id="code_analysis_team",
            priority=2  # Medium priority for code explanation
        )
        
        logger.info(f"Created explain_code request: {request.request_id}")
        return request
    
    def create_analyze_function_request(
        self,
        function_name: str,
        function_code: str,
        language: str = "python",
        context: Optional[str] = None,
        llm_config: Optional[LLMConfig] = None
    ) -> LLMServiceRequest:
        """
        Tạo LLMServiceRequest để phân tích function chi tiết.
        
        Args:
            function_name: Tên function
            function_code: Code của function
            language: Ngôn ngữ lập trình
            context: Context bổ sung về function
            llm_config: Cấu hình LLM
            
        Returns:
            LLMServiceRequest: Request đã được format
        """
        logger.debug(f"Creating analyze_function request for function: {function_name}")
        
        context_data = {
            "function_name": function_name,
            "function_code": function_code,
            "language": language,
            "context": context or "Không có context bổ sung"
        }
        
        config = llm_config or self.default_llm_config
        
        request = LLMServiceRequest(
            prompt_text="",
            prompt_id="analyze_function",
            context_data=context_data,
            llm_config=config,
            request_id=f"analyze_function_{int(time.time() * 1000)}",
            user_id="code_analysis_team",
            priority=2
        )
        
        logger.info(f"Created analyze_function request: {request.request_id}")
        return request
    
    def create_find_issues_request(
        self,
        code_content: str,
        language: str = "python",
        file_path: Optional[str] = None,
        llm_config: Optional[LLMConfig] = None
    ) -> LLMServiceRequest:
        """
        Tạo LLMServiceRequest để tìm issues trong code.
        
        Args:
            code_content: Nội dung code cần phân tích
            language: Ngôn ngữ lập trình
            file_path: Đường dẫn file (optional)
            llm_config: Cấu hình LLM
            
        Returns:
            LLMServiceRequest: Request đã được format
        """
        logger.debug(f"Creating find_issues request for {len(code_content)} chars of code")
        
        context_data = {
            "code_content": code_content,
            "language": language
        }
        
        if file_path:
            context_data["file_path"] = file_path
        
        config = llm_config or self.default_llm_config
        
        request = LLMServiceRequest(
            prompt_text="",
            prompt_id="find_issues",
            context_data=context_data,
            llm_config=config,
            request_id=f"find_issues_{int(time.time() * 1000)}",
            user_id="code_analysis_team",
            priority=3  # Higher priority for issue detection
        )
        
        logger.info(f"Created find_issues request: {request.request_id}")
        return request
    
    def create_review_changes_request(
        self,
        file_path: str,
        diff_content: str,
        pr_context: Optional[str] = None,
        llm_config: Optional[LLMConfig] = None
    ) -> LLMServiceRequest:
        """
        Tạo LLMServiceRequest để review code changes.
        
        Args:
            file_path: Đường dẫn file được thay đổi
            diff_content: Nội dung diff
            pr_context: Context của PR
            llm_config: Cấu hình LLM
            
        Returns:
            LLMServiceRequest: Request đã được format
        """
        logger.debug(f"Creating review_changes request for file: {file_path}")
        
        context_data = {
            "file_path": file_path,
            "diff_content": diff_content,
            "pr_context": pr_context or "Pull request review"
        }
        
        config = llm_config or self.default_llm_config
        
        request = LLMServiceRequest(
            prompt_text="",
            prompt_id="review_changes",
            context_data=context_data,
            llm_config=config,
            request_id=f"review_changes_{int(time.time() * 1000)}",
            user_id="code_analysis_team",
            priority=1  # High priority for PR reviews
        )
        
        logger.info(f"Created review_changes request: {request.request_id}")
        return request
    
    def create_suggest_improvements_request(
        self,
        code_content: str,
        language: str = "python",
        focus_areas: Optional[List[str]] = None,
        llm_config: Optional[LLMConfig] = None
    ) -> LLMServiceRequest:
        """
        Tạo LLMServiceRequest để đề xuất cải thiện code.
        
        Args:
            code_content: Nội dung code
            language: Ngôn ngữ lập trình
            focus_areas: Các lĩnh vực cần tập trung (performance, readability, etc.)
            llm_config: Cấu hình LLM
            
        Returns:
            LLMServiceRequest: Request đã được format
        """
        logger.debug(f"Creating suggest_improvements request for {len(code_content)} chars of code")
        
        context_data = {
            "code_content": code_content,
            "language": language
        }
        
        if focus_areas:
            context_data["focus_areas"] = ", ".join(focus_areas)
        
        config = llm_config or self.default_llm_config
        
        request = LLMServiceRequest(
            prompt_text="",
            prompt_id="suggest_improvements",
            context_data=context_data,
            llm_config=config,
            request_id=f"suggest_improvements_{int(time.time() * 1000)}",
            user_id="code_analysis_team",
            priority=4  # Lower priority for improvement suggestions
        )
        
        logger.info(f"Created suggest_improvements request: {request.request_id}")
        return request
    
    def create_context_from_code(
        self,
        code_snippet: str,
        language: str = "python",
        file_path: Optional[str] = None,
        analysis_type: str = "explain_code"
    ) -> CodeAnalysisContext:
        """
        Tạo CodeAnalysisContext từ đoạn code.
        
        Args:
            code_snippet: Đoạn code
            language: Ngôn ngữ lập trình
            file_path: Đường dẫn file
            analysis_type: Loại phân tích
            
        Returns:
            CodeAnalysisContext: Context đã được tạo
        """
        return CodeAnalysisContext(
            code_snippet=code_snippet,
            language=language,
            file_path=file_path,
            analysis_type=analysis_type
        )
    
    def process_llm_response_to_finding(
        self,
        response: LLMServiceResponse,
        analysis_context: CodeAnalysisContext
    ) -> Optional[AnalysisFinding]:
        """
        Chuyển đổi LLMServiceResponse thành AnalysisFinding.
        
        Args:
            response: Response từ LLM
            analysis_context: Context của phân tích
            
        Returns:
            AnalysisFinding nếu thành công, None nếu có lỗi
        """
        if not response.is_success():
            logger.error(f"LLM response failed: {response.error_message}")
            return None
        
        # Determine finding type based on analysis type
        finding_type = AnalysisFindingType.CODE_SMELL  # Default
        if analysis_context.analysis_type == "find_issues":
            finding_type = AnalysisFindingType.POTENTIAL_REFACTORING
        elif analysis_context.analysis_type == "review_changes":
            finding_type = AnalysisFindingType.ARCHITECTURAL_VIOLATION
        
        finding = AnalysisFinding(
            finding_type=finding_type,
            title=f"LLM Analysis: {analysis_context.analysis_type}",
            description=response.response_text,
            severity=AnalysisSeverity.MEDIUM,  # Default severity
            file_path=analysis_context.file_path,
            analysis_module="llm_analysis_support",
            confidence_score=0.8,  # LLM suggestions have moderate confidence
            metadata={
                "llm_model": response.model_used,
                "response_time_ms": response.response_time_ms,
                "tokens_used": response.tokens_used,
                "request_id": response.request_id,
                "analysis_context": analysis_context
            }
        )
        
        logger.info(f"Created AnalysisFinding from LLM response: {finding.title}")
        return finding
    
    def set_default_config(self, config: LLMConfig) -> None:
        """
        Cập nhật cấu hình LLM mặc định.
        
        Args:
            config: Cấu hình LLM mới
        """
        self.default_llm_config = config
        logger.info(f"Updated default LLM config: {config.provider.value}/{config.model}")
    
    def get_supported_analysis_types(self) -> List[str]:
        """
        Lấy danh sách các loại phân tích được hỗ trợ.
        
        Returns:
            List các analysis types
        """
        return [
            "explain_code",
            "analyze_function", 
            "find_issues",
            "review_changes",
            "suggest_improvements"
        ]


# Convenience functions
def create_llm_analysis_support() -> LLMAnalysisSupportModule:
    """
    Tạo instance mới của LLMAnalysisSupportModule với cấu hình mặc định.
    
    Returns:
        LLMAnalysisSupportModule: Instance đã khởi tạo
    """
    return LLMAnalysisSupportModule()


def create_explain_code_request(code_snippet: str, language: str = "python") -> LLMServiceRequest:
    """
    Convenience function để tạo explain_code request.
    
    Args:
        code_snippet: Đoạn code cần giải thích
        language: Ngôn ngữ lập trình
        
    Returns:
        LLMServiceRequest: Request đã được tạo
    """
    module = create_llm_analysis_support()
    return module.create_explain_code_request(code_snippet, language) 