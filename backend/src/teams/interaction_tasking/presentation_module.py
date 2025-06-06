# Task 4.8 - PresentationModule
from teams.synthesis_reporting import FinalReviewReport
from pydantic import BaseModel
from typing import Dict, Any, Optional
from shared.utils.logging_config import get_logger

logger = get_logger(__name__)

class PresentationModule:
    """Module for presenting FinalReviewReport on CLI - Task 4.8"""
    def __init__(self): pass
    def display_final_review_report(self, report):
        """DoD Task 4.8: Module có hàm nhận FinalReviewReport và in report_content ra console."""
        print(report.report_content)
        logger.info(f"Displayed report: {report.report_id}")
