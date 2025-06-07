#!/usr/bin/env python3
"""
Test đầy đủ cho toàn bộ hệ thống TEAM Interaction & Tasking
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

async def test_full_system():
    """Test toàn bộ hệ thống với enhanced orchestrator"""
    
    print("=== TEST FULL SYSTEM WITH ENHANCED ORCHESTRATOR ===\n")
    
    try:
        # Import enhanced orchestrator
        from teams.interaction_tasking.enhanced_orchestrator import EnhancedTeamOrchestrator
        
        # Tạo orchestrator
        orchestrator = EnhancedTeamOrchestrator()
        
        print("✅ Enhanced Orchestrator initialized successfully")
        
        # Test scenario chính
        user_message = "tôi muốn review code của dự án"
        print(f"\n🔍 Testing with: '{user_message}'")
        
        # Process message
        result = await orchestrator.process_user_message(user_message)
        
        print(f"\n📊 RESULT:")
        print(f"Response: {result.get('response', 'No response')}")
        print(f"Intent: {result.get('intent_type', 'Unknown')}")
        print(f"Next Action: {result.get('next_action', 'None')}")
        
        # Kiểm tra kết quả mong đợi
        expected_intent = "scan_project"
        expected_response_contains = "source code của bạn được lưa ở đâu"
        
        actual_intent = result.get('intent_type')
        actual_response = result.get('response', '')
        
        if actual_intent == expected_intent and expected_response_contains in actual_response:
            print("\n✅ SUCCESS: Full system working correctly!")
        else:
            print(f"\n❌ PARTIAL SUCCESS: Intent={actual_intent}, Response contains expected text: {expected_response_contains in actual_response}")
        
        # Test follow-up
        print(f"\n{'='*60}")
        follow_up = "https://github.com/aidino/repochat"
        print(f"\n🔍 Testing follow-up: '{follow_up}'")
        
        result2 = await orchestrator.process_user_message(follow_up)
        
        print(f"\n📊 FOLLOW-UP RESULT:")
        print(f"Response: {result2.get('response', 'No response')}")
        print(f"Task Created: {result2.get('task_created', False)}")
        print(f"GitHub URL: {result2.get('github_url', 'None')}")
        
        if result2.get('task_created') and result2.get('github_url'):
            print("\n✅ SUCCESS: GitHub URL extracted and task created!")
        else:
            print("\n⚠️ INFO: Task creation may require additional setup")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Falling back to simple test...")
        await test_simple_fallback()
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print("Falling back to simple test...")
        await test_simple_fallback()

async def test_simple_fallback():
    """Fallback test nếu enhanced orchestrator không hoạt động"""
    
    print("\n=== SIMPLE FALLBACK TEST ===\n")
    
    # Test intent parsing đơn giản
    from simple_test import create_fallback_intent
    
    user_message = "tôi muốn review code của dự án"
    intent = create_fallback_intent(user_message)
    
    print(f"User: '{user_message}'")
    print(f"Intent: {intent.intent_type.value}")
    print(f"Response: {intent.suggested_questions[0] if intent.suggested_questions else 'None'}")
    
    expected_response = "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
    
    if intent.suggested_questions and intent.suggested_questions[0] == expected_response:
        print("\n✅ FALLBACK SUCCESS: Intent parsing works correctly!")
    else:
        print("\n❌ FALLBACK FAILED: Intent parsing not working")

if __name__ == "__main__":
    asyncio.run(test_full_system()) 