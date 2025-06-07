#!/usr/bin/env python3
"""
Direct LLM Test - import trực tiếp SimplifiedLLMIntentParser
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_direct_llm():
    """Test trực tiếp SimplifiedLLMIntentParser"""
    
    print("=== DIRECT LLM TEST ===")
    
    try:
        # Import trực tiếp file
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'teams', 'interaction_tasking'))
        
        print("1. Testing direct import...")
        import simplified_llm_intent_parser
        parser = simplified_llm_intent_parser.SimplifiedLLMIntentParser()
        print("✅ SimplifiedLLMIntentParser imported directly")
        
        print("\n2. Testing intent parsing...")
        test_input = "tôi muốn review code của dự án"
        intent = parser.parse_user_intent(test_input)
        
        print(f"   Input: '{test_input}'")
        print(f"   Intent Type: {intent.intent_type.value}")
        print(f"   Confidence: {intent.confidence}")
        print(f"   Missing Info: {intent.missing_information}")
        print(f"   Suggested Questions: {intent.suggested_questions}")
        
        # Kiểm tra response có đúng không
        expected_response = "source code của bạn được lưa ở đâu"
        if intent.suggested_questions and expected_response in intent.suggested_questions[0]:
            print("✅ LLM response chính xác!")
            print(f"🎯 Expected match found: '{expected_response}'")
        else:
            print("❌ LLM response không như mong đợi")
            print(f"   Expected: contains '{expected_response}'") 
            print(f"   Actual: {intent.suggested_questions}")
        
        print(f"\n=== KẾT QUẢ TEST ===")
        print(f"📥 User Input: '{test_input}'")
        print(f"🤖 Bot Response: '{intent.suggested_questions[0] if intent.suggested_questions else 'None'}'")
        print(f"🎯 Intent: {intent.intent_type.value} (confidence: {intent.confidence})")
        
        # Kiểm tra intent có đúng là scan_project không
        if intent.intent_type.value == "scan_project":
            print("✅ Intent classification chính xác (scan_project)")
        else:
            print(f"❌ Intent classification sai. Expected: scan_project, Got: {intent.intent_type.value}")
        
        # Test user scenario
        print("\n=== USER SCENARIO TEST ===")
        user_input = "tôi muốn review code của dự án"
        expected_response = "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
        
        intent = parser.parse_user_intent(user_input)
        
        print(f"User input: '{user_input}'")
        print(f"Expected: '{expected_response}'")
        print(f"Actual: '{intent.suggested_questions[0] if intent.suggested_questions else 'None'}'")
        
        # Check exact match
        if intent.suggested_questions and intent.suggested_questions[0] == expected_response:
            print("✅ PERFECT MATCH! Exactly as expected!")
            return True
        elif intent.suggested_questions and expected_response in intent.suggested_questions[0]:
            print("✅ PARTIAL MATCH - contains expected text")
            return True
        else:
            print("❌ NO MATCH - response doesn't match expectation")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_llm()
    
    if success:
        print("\n🎉 DIRECT LLM TEST PASSED!")
        print("✅ SimplifiedLLMIntentParser hoạt động tốt")
    else:
        print("\n❌ Direct LLM test failed")
    
    sys.exit(0 if success else 1) 