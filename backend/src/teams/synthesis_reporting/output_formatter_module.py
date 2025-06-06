from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class FinalReviewReport(BaseModel):
    """Final review report data structure - DoD Task 4.7"""
    report_content: str = Field(..., description="The main content of the report")
    report_format: str = Field(default="text", description="Format of the report")
    generated_at: Optional[datetime] = Field(default=None)
    report_id: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

class OutputFormatterModule:
    """Module for formatting text reports into FinalReviewReport objects."""
    def __init__(self): pass
    def format_text_report(self, report_text: str) -> FinalReviewReport:
        """DoD Task 4.7: Hàm nhận chuỗi báo cáo text từ ReportGeneratorModule và tạo FinalReviewReport."""
        return FinalReviewReport(report_content=report_text)
from dataclasses import dataclass

@dataclass
class OutputFormatterConfig:
    """Configuration for OutputFormatterModule."""
    default_format: str = "text"
