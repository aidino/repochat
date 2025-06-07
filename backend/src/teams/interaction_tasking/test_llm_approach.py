#!/usr/bin/env python3
"""
Test LLM-based intent parsing approach
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

async def test_llm_intent_parsing():
    """Test LLM-based intent parsing"""
    
    print("=== TEST LLM-BASED INTENT PARSING ===\n")
    
    try:
        # Import các components cần thiết
        from teams.interaction_tasking.user_intent_parser_agent import UserIntentParserAgent
        
        # Tạo agent  
        agent = UserIntentParserAgent()
        
        print("✅ UserIntentParserAgent với LLM initialized successfully")
        
        # Test cases
        test_cases = [
            {
                "input": "tôi muốn review code của dự án",
                "expected_intent": "scan_project",
                "expected_response_contains": "source code của bạn được lưa ở đâu"
            },
            {
                "input": "review toàn bộ source code của project",
                "expected_intent": "scan_project", 
                "expected_response_contains": "github repository"
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
            
            try:
                # Parse intent
                intent = agent.parse_user_intent(test_case['input'])
                
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
        
        # Test với enhanced scenario
        print(f"\n🎯 SPECIAL TEST - User Scenario:")
        user_input = "tôi muốn review code của dự án" 
        print(f"Input: '{user_input}'")
        
        intent = agent.parse_user_intent(user_input)
        expected_response = "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
        
        print(f"Intent: {intent.intent_type.value}")
        if intent.suggested_questions:
            actual_response = intent.suggested_questions[0]
            print(f"Response: {actual_response}")
            
            if actual_response == expected_response:
                print("✅ PERFECT MATCH: Response hoàn toàn chính xác!")
            elif "source code của bạn được lưa ở đâu" in actual_response:
                print("✅ GOOD MATCH: Response đúng ý nghĩa!")
            else:
                print("⚠️ RESPONSE MISMATCH: Cần điều chỉnh prompt")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Có thể LLM service dependencies chưa sẵn sàng")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_intent_parsing()) 