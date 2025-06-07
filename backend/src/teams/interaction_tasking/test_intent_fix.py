#!/usr/bin/env python3
"""
Script test để kiểm tra việc sửa lỗi intent parsing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from teams.interaction_tasking.user_intent_parser_agent import UserIntentParserAgent, IntentType

def test_intent_parsing():
    """Test việc phân tích intent cho các câu review code"""
    
    print("=== TEST INTENT PARSING AFTER FIX ===\n")
    
    # Tạo agent
    agent = UserIntentParserAgent()
    
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
        
        try:
            # Parse intent
            intent = agent.parse_user_intent(test_case)
            
            print(f"  Intent Type: {intent.intent_type.value}")
            print(f"  Confidence: {intent.confidence}")
            print(f"  Missing Info: {intent.missing_information}")
            print(f"  Questions: {intent.suggested_questions}")
            
            # Validate expected results
            if "review code" in test_case.lower() or "phân tích dự án" in test_case.lower() or "quét source" in test_case.lower():
                if "pr" not in test_case.lower() and "#" not in test_case:
                    expected = IntentType.SCAN_PROJECT
                    if intent.intent_type == expected:
                        print("  ✅ CORRECT: Detected SCAN_PROJECT")
                    else:
                        print(f"  ❌ WRONG: Expected {expected.value}, got {intent.intent_type.value}")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_intent_parsing() 