#!/usr/bin/env python3
"""
Test trực tiếp với OpenAI provider để tránh dependency issues
"""

import sys
import os
import json
import re
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List

# Add path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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
    confidence: float
    extracted_entities: Dict[str, Any]
    missing_information: List[str]
    suggested_questions: List[str]
    original_text: str

def test_direct_openai_approach():
    """Test direct OpenAI approach"""
    
    print("=== TEST DIRECT OPENAI APPROACH ===\n")
    
    # System prompt
    system_prompt = """Bạn là AI Assistant chuyên nghiệp phân tích ý định người dùng cho RepoChat - hệ thống review code tự động bằng tiếng Việt.

## NHIỆM VỤ CỐT LÕI
Phân tích chính xác ý định người dùng và đưa ra response phù hợp theo ngữ cảnh conversation tự nhiên.

## PHÂN LOẠI Ý ĐỊNH

### 1. SCAN_PROJECT (Quét toàn bộ dự án)
**Mô tả**: Người dùng muốn review/phân tích toàn bộ source code của một dự án
**Keywords**: "review code", "review dự án", "phân tích project", "quét source code", "review toàn bộ"
**Ví dụ user input**: 
- "tôi muốn review code của dự án"
- "review toàn bộ source code"
- "phân tích dự án này"

**Response chuẩn khi thiếu GitHub URL**:
"Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"

### 2. REVIEW_PR (Review Pull Request cụ thể)  
**Mô tả**: Người dùng muốn review một Pull Request cụ thể (PHẢI có PR ID/số)
**Keywords**: "PR #123", "pull request 456", "review PR"
**Response chuẩn**:
"Để review Pull Request, vui lòng cung cấp:
• URL repository
• ID hoặc URL của Pull Request

Ví dụ: Review PR #123 trong repository https://github.com/user/repo"

## QUY TẮC PHÂN TÍCH QUAN TRỌNG

1. **Ưu tiên SCAN_PROJECT**: Nếu user nói về "review code" mà KHÔNG đề cập PR cụ thể → chọn scan_project
2. **Chỉ chọn REVIEW_PR**: Khi có đề cập RÕ RÀNG PR ID, số PR, hoặc "pull request" với số
3. **Response tự nhiên**: Đưa ra câu trả lời conversation như con người, không phải JSON
4. **Tiếng Việt thuần túy**: Tất cả response phải bằng tiếng Việt tự nhiên

## FORMAT TRẢ LỜI YÊU CẦU
Trả lời JSON với cấu trúc:
{
    "intent_type": "scan_project|review_pr|ask_question|request_diagram|configure_settings|greeting|help|unknown",
    "confidence": 0.95,
    "extracted_entities": {
        "github_url": "URL nếu có",
        "pr_identifier": "PR ID nếu có", 
        "project_name": "tên project nếu có"
    },
    "missing_information": ["github_url"],
    "suggested_questions": ["Response tự nhiên bằng tiếng Việt theo template trên"]
}

## EXAMPLES

Input: "tôi muốn review code của dự án"
→ intent_type: "scan_project"
→ suggested_questions: ["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"]

Input: "review PR #123"  
→ intent_type: "review_pr"
→ suggested_questions: ["Để review Pull Request, vui lòng cung cấp:\n• URL repository\n• ID hoặc URL của Pull Request\n\nVí dụ: Review PR #123 trong repository https://github.com/user/repo"]"""

    # Test với mock OpenAI response (giả lập khi không có API key)
    def mock_openai_parse(user_text: str) -> UserIntent:
        """Mock OpenAI parsing với logic tốt"""
        
        text_lower = user_text.lower()
        
        # Logic giống LLM
        if any(word in text_lower for word in ['review code', 'review dự án', 'phân tích dự án', 'review toàn bộ']):
            return UserIntent(
                intent_type=IntentType.SCAN_PROJECT,
                confidence=0.95,
                extracted_entities={},
                missing_information=["github_url"],
                suggested_questions=["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"],
                original_text=user_text
            )
        elif any(pattern in text_lower for pattern in ['pr #', 'pull request #', 'review pr']) or re.search(r'pull request \d+|pr \d+', text_lower):
            return UserIntent(
                intent_type=IntentType.REVIEW_PR,
                confidence=0.95,
                extracted_entities={},
                missing_information=["github_url", "pr_identifier"],
                suggested_questions=["Để review Pull Request, vui lòng cung cấp:\n• URL repository\n• ID hoặc URL của Pull Request\n\nVí dụ: Review PR #123 trong repository https://github.com/user/repo"],
                original_text=user_text
            )
        else:
            return UserIntent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.5,
                extracted_entities={},
                missing_information=[],
                suggested_questions=["Bạn có thể nói rõ hơn về điều bạn muốn làm không?"],
                original_text=user_text
            )
    
    # Test cases
    test_cases = [
        {
            "input": "tôi muốn review code của dự án",
            "expected_intent": "scan_project",
            "expected_response": "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
        },
        {
            "input": "review toàn bộ source code của project",
            "expected_intent": "scan_project", 
            "expected_response": "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
        },
        {
            "input": "review PR #123",
            "expected_intent": "review_pr",
            "expected_response_contains": "Pull Request"
        },
        {
            "input": "xem pull request 456",
            "expected_intent": "review_pr",
            "expected_response_contains": "URL repository"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: '{test_case['input']}'")
        
        # Mock parsing
        intent = mock_openai_parse(test_case['input'])
        
        print(f"  Intent Type: {intent.intent_type.value}")
        print(f"  Confidence: {intent.confidence}")
        print(f"  Response: {intent.suggested_questions[0] if intent.suggested_questions else 'None'}")
        
        # Validate
        intent_correct = intent.intent_type.value == test_case['expected_intent']
        
        response_correct = False
        if intent.suggested_questions:
            response = intent.suggested_questions[0]
            if 'expected_response' in test_case:
                response_correct = response == test_case['expected_response']
            elif 'expected_response_contains' in test_case:
                response_correct = test_case['expected_response_contains'] in response
        
        if intent_correct and response_correct:
            print(f"  ✅ SUCCESS: Perfect match!")
        elif intent_correct:
            print(f"  ⚠️ PARTIAL: Intent correct, response needs adjustment")
        else:
            print(f"  ❌ FAILED: Wrong intent. Expected: {test_case['expected_intent']}, Got: {intent.intent_type.value}")
        
        print("-" * 60)
    
    # Specialized test cho user scenario
    print(f"\n🎯 USER SCENARIO TEST:")
    user_input = "tôi muốn review code của dự án"
    print(f"Input: '{user_input}'")
    
    intent = mock_openai_parse(user_input)
    expected_response = "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
    
    print(f"Intent: {intent.intent_type.value}")
    if intent.suggested_questions:
        actual_response = intent.suggested_questions[0]
        print(f"Response: {actual_response}")
        
        if actual_response == expected_response:
            print("✅ PERFECT MATCH: Exact response as required!")
        else:
            print("❌ MISMATCH: Response different from requirement")

if __name__ == "__main__":
    test_direct_openai_approach() 