#!/usr/bin/env python3
"""
Test đơn giản cho fallback intent parsing
"""

import sys
import os
import re
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List

class IntentType(Enum):
    """Các loại ý định người dùng có thể có"""
    SCAN_PROJECT = "scan_project"
    REVIEW_PR = "review_pr"
    ASK_QUESTION = "ask_question"
    REQUEST_DIAGRAM = "request_diagram"
    CONFIGURE_SETTINGS = "configure_settings"
    UNKNOWN = "unknown"
    GREETING = "greeting"
    HELP = "help"

@dataclass
class UserIntent:
    """Thông tin ý định đã được phân tích"""
    intent_type: IntentType
    confidence: float  # 0.0 - 1.0
    extracted_entities: Dict[str, Any]
    missing_information: List[str]
    suggested_questions: List[str]
    original_text: str

def create_fallback_intent(user_text: str) -> UserIntent:
    """Test fallback intent logic"""
    
    # Cố gắng phân tích đơn giản bằng keyword matching
    text_lower = user_text.lower()
    
    intent_type = IntentType.UNKNOWN
    entities = {}
    missing_info = []
    questions = ["Bạn có thể nói rõ hơn về điều bạn muốn làm không?"]
    
    # Detect intent dựa trên keywords - ưu tiên SCAN_PROJECT cho review code chung
    if any(word in text_lower for word in ['review code', 'review source', 'review dự án', 'review project', 'phân tích code', 'phân tích dự án', 'quét dự án', 'quét project', 'review toàn bộ']):
        intent_type = IntentType.SCAN_PROJECT
        missing_info = ["github_url"]
        questions = ["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"]
    
    elif any(word in text_lower for word in ['scan', 'quét', 'phân tích', 'analyze']) and 'pr' not in text_lower:
        intent_type = IntentType.SCAN_PROJECT
        missing_info = ["github_url"]
        questions = ["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"]
    
    # Tìm PR với số cụ thể
    elif any(pattern in text_lower for pattern in ['pr #', 'pull request #', 'review pr']) or re.search(r'pull request \d+|pr \d+', text_lower):
        intent_type = IntentType.REVIEW_PR  
        missing_info = ["github_url", "pr_identifier"]
        questions = ["Để review Pull Request, vui lòng cung cấp:\n• URL repository\n• ID hoặc URL của Pull Request\n\nVí dụ: Review PR #123 trong repository https://github.com/user/repo"]
    
    elif any(word in text_lower for word in ['hỏi', 'gì', 'như thế nào', 'tại sao']):
        intent_type = IntentType.ASK_QUESTION
    
    elif any(word in text_lower for word in ['xin chào', 'hello', 'hi', 'chào']):
        intent_type = IntentType.GREETING
        questions = ["Chào bạn! Tôi có thể giúp gì cho bạn? Bạn muốn quét project hay review PR?"]
    
    # Fallback cho "review" chung chung -> SCAN_PROJECT
    elif 'review' in text_lower and 'pr' not in text_lower and '#' not in text_lower:
        intent_type = IntentType.SCAN_PROJECT
        missing_info = ["github_url"]
        questions = ["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"]
    
    return UserIntent(
        intent_type=intent_type,
        confidence=0.6,  # Confidence thấp hơn cho fallback
        extracted_entities=entities,
        missing_information=missing_info,
        suggested_questions=questions,
        original_text=user_text
    )

def test_fallback_intent():
    """Test fallback intent logic"""
    
    print("=== TEST FALLBACK INTENT PARSING ===\n")
    
    # Test cases
    test_cases = [
        "tôi muốn review code của dự án",
        "review toàn bộ source code của project", 
        "phân tích dự án này",
        "quét source code",
        "review PR #123",
        "xem pull request 456",
        "review pull request trong repo này"
    ]
    
    for test_case in test_cases:
        print(f"Input: '{test_case}'")
        
        intent = create_fallback_intent(test_case)
        
        print(f"  Intent Type: {intent.intent_type.value}")
        print(f"  Confidence: {intent.confidence}")
        print(f"  Missing Info: {intent.missing_information}")
        print(f"  Questions: {intent.suggested_questions[0] if intent.suggested_questions else 'None'}")
        
        # Validate expected results
        if "review code" in test_case.lower() or "phân tích dự án" in test_case.lower() or "quét source" in test_case.lower():
            if "pr" not in test_case.lower() and "#" not in test_case:
                expected = IntentType.SCAN_PROJECT
                if intent.intent_type == expected:
                    print("  ✅ CORRECT: Detected SCAN_PROJECT")
                else:
                    print(f"  ❌ WRONG: Expected {expected.value}, got {intent.intent_type.value}")
        elif "pr #" in test_case.lower() or "pull request" in test_case.lower():
            expected = IntentType.REVIEW_PR
            if intent.intent_type == expected:
                print("  ✅ CORRECT: Detected REVIEW_PR")
            else:
                print(f"  ❌ WRONG: Expected {expected.value}, got {intent.intent_type.value}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_fallback_intent() 