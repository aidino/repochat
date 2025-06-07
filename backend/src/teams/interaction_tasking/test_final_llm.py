#!/usr/bin/env python3
"""
Test trực tiếp SimplifiedLLMIntentParser
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

async def test_final_llm_approach():
    """Test final LLM approach"""
    
    print("=== TEST FINAL LLM APPROACH ===\n")
    
    try:
        # Import trực tiếp SimplifiedLLMIntentParser
        from teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
        
        # Tạo parser
        parser = SimplifiedLLMIntentParser()
        
        print("✅ SimplifiedLLMIntentParser initialized successfully")
        print(f"   OpenAI Available: {'✅' if parser.openai_client else '❌'}")
        print(f"   Parser Available: {'✅' if parser.is_available() else '❌'}")
        
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
        
        success_count = 0
        total_count = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 Test Case {i}: '{test_case['input']}'")
            
            try:
                # Parse intent
                intent = parser.parse_user_intent(test_case['input'])
                
                print(f"  Intent Type: {intent.intent_type.value}")
                print(f"  Confidence: {intent.confidence}")
                print(f"  Missing Info: {intent.missing_information}")
                if intent.suggested_questions:
                    response = intent.suggested_questions[0]
                    print(f"  Response: {response[:80]}...")
                
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
                    print(f"  ✅ SUCCESS: Perfect match!")
                    success_count += 1
                elif intent_correct:
                    print(f"  ⚠️ PARTIAL: Intent correct, response needs adjustment")
                    success_count += 0.5
                else:
                    print(f"  ❌ FAILED: Wrong intent. Expected: {test_case['expected_intent']}, Got: {intent.intent_type.value}")
                
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
                main_test_success = True
            elif "source code của bạn được lưa ở đâu" in actual_response:
                print("✅ GOOD MATCH: Response đúng ý nghĩa!")
                main_test_success = True
            else:
                print("⚠️ RESPONSE MISMATCH: Cần điều chỉnh")
                main_test_success = False
        else:
            main_test_success = False
                
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  Test Cases: {success_count}/{total_count} passed")
        print(f"  Main Scenario: {'✅ PASS' if main_test_success else '❌ FAIL'}")
        print(f"  Overall: {'✅ SUCCESS' if success_count >= total_count * 0.8 and main_test_success else '⚠️ NEEDS IMPROVEMENT'}")
        
        if success_count >= total_count * 0.8 and main_test_success:
            print(f"\n🎉 LLM-BASED INTENT PARSING HOẠT ĐỘNG TỐT!")
            print(f"   Đã thay thế thành công rule-based approach bằng OpenAI LLM")
            print(f"   User scenario test PASS - hệ thống sẽ trả lời đúng như yêu cầu")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_final_llm_approach()) 