#!/usr/bin/env python3

content = '''"""
OutputFormatterModule for TEAM Synthesis & Reporting - Task 4.7
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field

from shared.utils.logging_config import get_logger

logger = get_logger(__name__)


class FinalReviewReport(BaseModel):
    """Final review report data structure - DoD Task 4.7"""
    report_content: str = Field(..., description="The main content of the report as a string")
    report_format: str = Field(default="text", description="Format of the report")
    generated_at: Optional[datetime] = Field(default=None)
    report_id: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default="vietnamese")
    summary: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


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
    DoD Task 4.7: Module có hàm nhận chuỗi báo cáo text từ ReportGeneratorModule
    và tạo và trả về một instance của FinalReviewReport.
    """
    
    def __init__(self, config: Optional[OutputFormatterConfig] = None):
        self.config = config or OutputFormatterConfig()
        self.stats = {"reports_formatted": 0}
        logger.info("OutputFormatterModule initialized")
    
    def format_text_report(self, report_text: str, report_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> FinalReviewReport:
        """
        Format text report into FinalReviewReport object.
        DoD Task 4.7: Hàm nhận chuỗi báo cáo text từ ReportGeneratorModule
        và tạo và trả về một instance của FinalReviewReport.
        """
        if not report_text or not isinstance(report_text, str):
            raise ValueError("report_text must be a non-empty string")
        
        current_time = datetime.now() if self.config.include_timestamp else None
        summary = self._extract_summary(report_text) if self.config.include_summary else None
        
        final_metadata = {}
        if self.config.include_metadata:
            final_metadata = {"original_length": len(report_text), "lines_count": len(report_text.split('\\n'))}
            if metadata:
                final_metadata.update(metadata)
        
        final_report = FinalReviewReport(
            report_content=report_text,
            report_format=self.config.default_format,
            generated_at=current_time,
            report_id=report_id or self._generate_report_id(),
            language=self.config.language,
            summary=summary,
            metadata=final_metadata if final_metadata else None
        )
        
        self.stats["reports_formatted"] += 1
        logger.info(f"Text report formatted successfully: {final_report.report_id}")
        return final_report
    
    def _extract_summary(self, report_text: str) -> str:
        """Extract a brief summary from the report text."""
        lines = report_text.split('\\n')
        for line in lines[:5]:
            line = line.strip()
            if line and not line.startswith('='):
                return line
        return "Code analysis report"
    
    def _generate_report_id(self) -> str:
        """Generate a unique report ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"report_{timestamp}_{self.stats['reports_formatted'] + 1:04d}"
    
    def get_module_stats(self) -> Dict[str, Any]:
        """Get module statistics."""
        return self.stats.copy()
'''

with open('src/teams/synthesis_reporting/output_formatter_module.py', 'w') as f:
    f.write(content)

print("OutputFormatterModule file created successfully!") 