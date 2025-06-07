#!/usr/bin/env python3
"""
Test simplified LLM intent parser
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

async def test_simplified_llm_parser():
    """Test simplified LLM intent parser"""
    
    print("=== TEST SIMPLIFIED LLM INTENT PARSER ===\n")
    
    try:
        from teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
        
        # Tạo parser
        parser = SimplifiedLLMIntentParser()
        
        print("✅ SimplifiedLLMIntentParser initialized successfully")
        
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
            },
            {
                "input": "xin chào",
                "expected_intent": "greeting",
                "expected_response_contains": "Chào bạn"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 Test Case {i}: '{test_case['input']}'")
            
            try:
                # Parse intent
                intent = parser.parse_user_intent(test_case['input'])
                
                print(f"  Intent Type: {intent.intent_type.value}")
                print(f"  Confidence: {intent.confidence}")
                print(f"  Missing Info: {intent.missing_information}")
                if intent.suggested_questions:
                    print(f"  Response: {intent.suggested_questions[0][:100]}...")
                
                # Validate kết quả
                intent_correct = intent.intent_type.value == test_case['expected_intent']
                response_correct = False
                
                if intent.suggested_questions:
                    response_text = intent.suggested_questions[0]
                    if 'expected_response' in test_case:
                        response_correct = response_text == test_case['expected_response']
                    elif 'expected_response_contains' in test_case:
                        response_correct = test_case['expected_response_contains'] in response_text
                
                if intent_correct and response_correct:
                    print(f"  ✅ SUCCESS: Intent và response đều chính xác!")
                elif intent_correct:
                    print(f"  ⚠️ PARTIAL: Intent đúng nhưng response có thể cần cải thiện")
                else:
                    print(f"  ❌ FAILED: Intent sai. Expected: {test_case['expected_intent']}, Got: {intent.intent_type.value}")
                
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
            
            print("-" * 60)
        
        # Test chính - User scenario
        print(f"\n🎯 MAIN USER SCENARIO TEST:")
        user_input = "tôi muốn review code của dự án" 
        print(f"Input: '{user_input}'")
        
        intent = parser.parse_user_intent(user_input)
        expected_response = "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
        
        print(f"Intent: {intent.intent_type.value}")
        if intent.suggested_questions:
            actual_response = intent.suggested_questions[0]
            print(f"Actual Response: {actual_response}")
            print(f"Expected Response: {expected_response}")
            
            if actual_response == expected_response:
                print("✅ PERFECT MATCH: Response hoàn toàn chính xác!")
            elif "source code của bạn được lưa ở đâu" in actual_response:
                print("✅ GOOD MATCH: Response đúng ý nghĩa!")
            else:
                print("⚠️ RESPONSE MISMATCH: Cần điều chỉnh")
                
        print(f"\n🔧 Parser Status:")
        print(f"  Available: {parser.is_available()}")
        print(f"  OpenAI Client: {'✅ Ready' if parser.openai_client else '❌ Not available'}")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simplified_llm_parser()) 