"""
OutputFormatterModule for TEAM Synthesis & Reporting

Implementation of Task 4.7 (F4.7): Tạo FinalReviewReport (text)
This module formats text reports from ReportGeneratorModule into FinalReviewReport objects.

Created: 2025-01-02
Author: RepoChat Development Team
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit

logger = get_logger(__name__)


class FinalReviewReport(BaseModel):
    """
    Final review report data structure.
    
    DoD Requirements Task 4.7:
    - Pydantic model chứa trường report_content: str
    - Có thể có report_format: str = "text"
    """
    report_content: str = Field(
        ..., 
        description="The main content of the report as a string"
    )
    report_format: str = Field(
        default="text", 
        description="Format of the report (text, json, etc.)"
    )
    
    # Additional metadata fields for enhanced functionality
    generated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when report was generated"
    )
    report_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for this report"
    )
    language: Optional[str] = Field(
        default="vietnamese",
        description="Language of the report content"
    )
    summary: Optional[str] = Field(
        default=None,
        description="Brief summary of the report"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the report"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


@dataclass
class OutputFormatterConfig:
    """Configuration for OutputFormatterModule."""
    include_metadata: bool = True
    include_summary: bool = True
    include_timestamp: bool = True
    default_format: str = "text"
    language: str = "vietnamese"


class OutputFormatterModule:
    """
    Module for formatting text reports into FinalReviewReport objects.
    
    DoD Requirements Task 4.7:
    - Module có hàm nhận chuỗi báo cáo text từ ReportGeneratorModule
    - Hàm tạo và trả về một instance của FinalReviewReport
    """
    
    def __init__(self, config: Optional[OutputFormatterConfig] = None):
        """
        Initialize OutputFormatterModule.
        
        Args:
            config: Configuration for output formatting
        """
        log_function_entry(logger, self.__init__, {"config": config})
        
        self.config = config or OutputFormatterConfig()
        self.stats = {
            "reports_formatted": 0,
            "total_processing_time": 0.0,
            "last_format_time": None,
            "average_processing_time": 0.0
        }
        
        logger.info("OutputFormatterModule initialized")
        log_function_exit(logger, self.__init__)
    
    def format_text_report(
        self, 
        report_text: str,
        report_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FinalReviewReport:
        """
        Format text report into FinalReviewReport object.
        
        DoD Requirement: Hàm nhận chuỗi báo cáo text từ ReportGeneratorModule
        và tạo và trả về một instance của FinalReviewReport.
        
        Args:
            report_text: Text content from ReportGeneratorModule
            report_id: Optional unique identifier for the report
            metadata: Optional additional metadata
            
        Returns:
            FinalReviewReport: Formatted report object
            
        Raises:
            ValueError: If report_text is empty or None
        """
        log_function_entry(logger, self.format_text_report, {
            "report_text_length": len(report_text) if report_text else 0,
            "report_id": report_id,
            "has_metadata": metadata is not None
        })
        
        start_time = time.time()
        
        try:
            # Validate input
            if not report_text or not isinstance(report_text, str):
                raise ValueError("report_text must be a non-empty string")
            
            # Generate report metadata
            current_time = datetime.now() if self.config.include_timestamp else None
            
            # Extract summary if configured
            summary = None
            if self.config.include_summary:
                summary = self._extract_summary(report_text)
            
            # Prepare metadata
            final_metadata = {}
            if self.config.include_metadata:
                final_metadata.update({
                    "original_length": len(report_text),
                    "lines_count": len(report_text.split('\n')),
                    "processing_time": time.time() - start_time,
                    "formatter_config": {
                        "language": self.config.language,
                        "format": self.config.default_format
                    }
                })
                
                if metadata:
                    final_metadata.update(metadata)
            
            # Create FinalReviewReport
            final_report = FinalReviewReport(
                report_content=report_text,
                report_format=self.config.default_format,
                generated_at=current_time,
                report_id=report_id or self._generate_report_id(),
                language=self.config.language,
                summary=summary,
                metadata=final_metadata if final_metadata else None
            )
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            logger.info(
                "Text report formatted successfully",
                extra={
                    "report_id": final_report.report_id,
                    "content_length": len(report_text),
                    "processing_time": processing_time
                }
            )
            
            log_function_exit(logger, self.format_text_report)
            return final_report
            
        except Exception as e:
            logger.error(f"Failed to format text report: {str(e)}", extra={
                "error_type": type(e).__name__,
                "report_text_preview": report_text[:100] if report_text else None
            })
            raise
    
    def _extract_summary(self, report_text: str) -> str:
        """
        Extract a brief summary from the report text.
        
        Args:
            report_text: Full report text
            
        Returns:
            str: Brief summary
        """
        # Simple summary extraction - first few lines or section headers
        lines = report_text.split('\n')
        summary_lines = []
        
        for line in lines[:10]:  # First 10 lines
            line = line.strip()
            if line and ('====' in line or '📋' in line or '🔍' in line):
                summary_lines.append(line.replace('=', '').strip())
                if len(summary_lines) >= 3:
                    break
        
        if not summary_lines:
            # Fallback to first non-empty line
            for line in lines[:5]:
                line = line.strip()
                if line and not line.startswith('='):
                    summary_lines.append(line)
                    break
        
        return ' | '.join(summary_lines) if summary_lines else "Code analysis report"
    
    def _generate_report_id(self) -> str:
        """
        Generate a unique report ID.
        
        Returns:
            str: Unique report identifier
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"report_{timestamp}_{self.stats['reports_formatted'] + 1:04d}"
    
    def _update_stats(self, processing_time: float) -> None:
        """
        Update module statistics.
        
        Args:
            processing_time: Time taken to process this report
        """
        self.stats["reports_formatted"] += 1
        self.stats["total_processing_time"] += processing_time
        self.stats["last_format_time"] = processing_time
        self.stats["average_processing_time"] = (
            self.stats["total_processing_time"] / self.stats["reports_formatted"]
        )
    
    def get_module_stats(self) -> Dict[str, Any]:
        """
        Get module statistics.
        
        Returns:
            Dict[str, Any]: Module statistics
        """
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset module statistics."""
        self.stats = {
            "reports_formatted": 0,
            "total_processing_time": 0.0,
            "last_format_time": None,
            "average_processing_time": 0.0
        } 