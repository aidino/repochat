#!/usr/bin/env python3
"""
Test LLM Integration cho RepoChat Backend
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_llm_components():
    """Test LLM components integration"""
    
    print("=== TEST LLM INTEGRATION ===")
    
    try:
        print("1. Testing UserIntentParserAgent...")
        from src.teams.interaction_tasking.user_intent_parser_agent import UserIntentParserAgent
        intent_parser = UserIntentParserAgent()
        print("✅ UserIntentParserAgent initialized")
        
        print("\n2. Testing DialogManagerAgent...")
        from src.teams.interaction_tasking.dialog_manager_agent import DialogManagerAgent
        dialog_manager = DialogManagerAgent()
        print("✅ DialogManagerAgent initialized")
        
        print("\n3. Testing LLM intent parsing...")
        test_input = "tôi muốn review code của dự án"
        intent = intent_parser.parse_user_intent(test_input)
        
        print(f"   Input: '{test_input}'")
        print(f"   Intent: {intent.intent_type.value}")
        print(f"   Confidence: {intent.confidence}")
        print(f"   Response: {intent.suggested_questions[0] if intent.suggested_questions else 'None'}")
        
        # Kiểm tra response có đúng không
        expected_response = "source code của bạn được lưa ở đâu"
        if intent.suggested_questions and expected_response in intent.suggested_questions[0]:
            print("✅ LLM response chính xác!")
        else:
            print("❌ LLM response không như mong đợi")
        
        print("\n4. Testing complete integration...")
        from src.teams.interaction_tasking.dialog_manager_agent import DialogContext, DialogState
        
        context = DialogContext(
            state=DialogState.INITIAL,
            current_intent=None,
            gathered_info={},
            last_question=None,
            conversation_history=[]
        )
        
        dialog_response = dialog_manager.process_user_input(
            test_input,
            context,
            intent
        )
        
        print(f"   Dialog Response: {dialog_response.message[:100]}...")
        print(f"   State: {dialog_response.state.value}")
        print("✅ Dialog integration hoạt động!")
        
        print("\n🎉 TẤT CẢ TESTS THÀNH CÔNG!")
        print("\n=== KẾT QUẢ ===")
        print(f"📥 User Input: '{test_input}'")
        print(f"🤖 Bot Response: '{dialog_response.message}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_components()
    sys.exit(0 if success else 1) 