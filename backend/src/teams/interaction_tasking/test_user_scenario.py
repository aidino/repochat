#!/usr/bin/env python3
"""
Test đặc biệt cho scenario của người dùng
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
    """Test fallback intent logic - cùng logic như trong UserIntentParserAgent"""
    
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

def test_user_scenario():
    """Test scenario cụ thể của người dùng"""
    
    print("=== TEST USER SCENARIO ===\n")
    
    # Câu hỏi của người dùng
    user_question = "tôi muốn review code của dự án"
    
    print(f"User: '{user_question}'")
    
    intent = create_fallback_intent(user_question)
    
    print(f"Detected Intent: {intent.intent_type.value}")
    print(f"Response: {intent.suggested_questions[0] if intent.suggested_questions else 'None'}")
    
    # So sánh với kết quả mong đợi
    expected_response = "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
    actual_response = intent.suggested_questions[0] if intent.suggested_questions else ""
    
    print(f"\n--- COMPARISON ---")
    print(f"Expected: {expected_response}")
    print(f"Actual  : {actual_response}")
    
    if intent.intent_type == IntentType.SCAN_PROJECT and actual_response == expected_response:
        print("\n✅ SUCCESS: Detected correct intent and response!")
    else:
        print(f"\n❌ FAILED: Wrong intent ({intent.intent_type.value}) or response")
    
    print("\n" + "="*60)
    
    # Test follow-up với GitHub URL  
    follow_up = "https://github.com/aidino/repochat"
    print(f"\nUser follow-up: '{follow_up}'")
    
    # Giả lập extract GitHub URL
    github_patterns = [
        r'https?://github\.com/([^/\s]+)/([^/\s]+)',
        r'github\.com/([^/\s]+)/([^/\s]+)',
    ]
    
    extracted_url = None
    for pattern in github_patterns:
        match = re.search(pattern, follow_up, re.IGNORECASE)
        if match:
            extracted_url = match.group(0)
            if not extracted_url.startswith('http'):
                extracted_url = f"https://{extracted_url}"
            break
    
    if extracted_url:
        print(f"✅ Extracted GitHub URL: {extracted_url}")
        print("✅ System can now proceed with project scan!")
    else:
        print("❌ Failed to extract GitHub URL")

if __name__ == "__main__":
    test_user_scenario() 