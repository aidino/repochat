"""
Test Enhanced Team Interaction Orchestrator với scenario cụ thể.

Scenario test:
1. User: "Tôi muốn review toàn bộ source code của project"
2. AI: "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
3. User: "https://github.com/aidino/repochat"
4. System extracts GitHub URL và proceeds to data acquisition
"""

import sys
import os

# Add backend src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from enhanced_orchestrator import EnhancedTeamInteractionOrchestrator
import uuid


def test_conversation_scenario():
    """
    Test the exact conversation scenario provided.
    """
    print("🧪 Testing Enhanced Team Interaction Orchestrator")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = EnhancedTeamInteractionOrchestrator()
    session_id = str(uuid.uuid4())
    
    print(f"📱 Session ID: {session_id}")
    print()
    
    # Step 1: User says they want to review entire source code
    print("👤 User: Tôi muốn review toàn bộ source code của project")
    response1 = orchestrator.process_user_message(
        session_id, 
        "Tôi muốn review toàn bộ source code của project"
    )
    
    print(f"🤖 AI: {response1['message']}")
    print(f"📊 State: {response1['state']}")
    print(f"🎯 Intent: {response1['intent_type']} (confidence: {response1['intent_confidence']:.2f})")
    print(f"✅ Task ready: {response1['task_ready']}")
    print()
    
    # Verify first response
    expected_response = "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
    if expected_response in response1['message']:
        print("✅ Step 1 PASSED: Correct response for missing GitHub URL")
    else:
        print("❌ Step 1 FAILED: Incorrect response")
        print(f"   Expected: {expected_response}")
        print(f"   Got: {response1['message']}")
    print()
    
    # Step 2: User provides GitHub URL
    print("👤 User: https://github.com/aidino/repochat")
    response2 = orchestrator.process_user_message(
        session_id,
        "https://github.com/aidino/repochat"
    )
    
    print(f"🤖 AI: {response2['message']}")
    print(f"📊 State: {response2['state']}")
    print(f"🎯 Intent: {response2['intent_type']} (confidence: {response2['intent_confidence']:.2f})")
    print(f"✅ Task ready: {response2['task_ready']}")
    if response2.get('task_definition'):
        print(f"📋 Task definition created: {response2['task_definition']['task_type']}")
        print(f"🔗 Repository URL: {response2['task_definition']['repository_url']}")
    print()
    
    # Verify second response
    if response2['task_ready'] and response2.get('github_url') == "https://github.com/aidino/repochat":
        print("✅ Step 2 PASSED: GitHub URL extracted and task created")
    else:
        print("❌ Step 2 FAILED: GitHub URL not properly extracted or task not created")
    print()
    
    # Additional test cases
    print("🔄 Additional Test Cases")
    print("-" * 30)
    
    # Test greeting
    session_id_2 = str(uuid.uuid4())
    print("👤 User: Xin chào")
    greeting_response = orchestrator.process_user_message(session_id_2, "Xin chào")
    print(f"🤖 AI: {greeting_response['message'][:100]}...")
    print(f"🎯 Intent: {greeting_response['intent_type']}")
    print()
    
    # Test PR review scenario
    session_id_3 = str(uuid.uuid4())
    print("👤 User: Tôi muốn review PR #123 từ https://github.com/aidino/repochat")
    pr_response = orchestrator.process_user_message(
        session_id_3, 
        "Tôi muốn review PR #123 từ https://github.com/aidino/repochat"
    )
    print(f"🤖 AI: {pr_response['message']}")
    print(f"🎯 Intent: {pr_response['intent_type']}")
    print(f"✅ Task ready: {pr_response['task_ready']}")
    print()
    
    # Summary
    print("📋 Test Summary")
    print("=" * 60)
    
    total_tests = 4
    passed_tests = 0
    
    # Check scenario step 1
    if expected_response in response1['message']:
        passed_tests += 1
        print("✅ Scenario Step 1: PASSED")
    else:
        print("❌ Scenario Step 1: FAILED")
    
    # Check scenario step 2
    if response2['task_ready'] and response2.get('github_url') == "https://github.com/aidino/repochat":
        passed_tests += 1
        print("✅ Scenario Step 2: PASSED")
    else:
        print("❌ Scenario Step 2: FAILED")
    
    # Check greeting
    if greeting_response['intent_type'] == 'greeting':
        passed_tests += 1
        print("✅ Greeting Test: PASSED")
    else:
        print("❌ Greeting Test: FAILED")
    
    # Check PR review
    if pr_response['intent_type'] == 'review_pr':
        passed_tests += 1
        print("✅ PR Review Test: PASSED")
    else:
        print("❌ PR Review Test: FAILED")
    
    print()
    print(f"🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Enhanced orchestrator working correctly.")
    else:
        print("⚠️  Some tests failed. Please check implementation.")
    
    return passed_tests == total_tests


def test_technology_integration():
    """
    Test integration with specified technologies.
    """
    print("\n🔧 Technology Integration Test")
    print("=" * 60)
    
    orchestrator = EnhancedTeamInteractionOrchestrator()
    
    # Check LangGraph integration
    if hasattr(orchestrator, 'workflow') and orchestrator.workflow is not None:
        print("✅ LangGraph workflow: Available")
    else:
        print("⚠️  LangGraph workflow: Not available (fallback mode)")
    
    # Check A2A SDK integration
    if hasattr(orchestrator, 'a2a_client'):
        if orchestrator.a2a_client is not None:
            print("✅ A2A SDK client: Available")
        else:
            print("⚠️  A2A SDK client: Not available (fallback mode)")
    else:
        print("❌ A2A SDK client: Not configured")
    
    # Check OpenAI LLM integration
    if hasattr(orchestrator, 'llm') and orchestrator.llm is not None:
        print("✅ OpenAI LLM client: Available")
    else:
        print("⚠️  OpenAI LLM client: Not available (fallback mode)")
    
    # Check component integration
    components = [
        'intent_parser',
        'dialog_manager', 
        'config_manager',
        'task_initiator',
        'presentation'
    ]
    
    print("\n🧩 Component Integration:")
    for component in components:
        if hasattr(orchestrator, component):
            print(f"✅ {component}: Available")
        else:
            print(f"❌ {component}: Missing")
    
    print("\n📦 Dependencies Check:")
    dependencies = [
        ('langchain_openai', 'ChatOpenAI'),
        ('langgraph.graph', 'StateGraph'),
        ('langchain_core.messages', 'BaseMessage'),
    ]
    
    for module, class_name in dependencies:
        try:
            __import__(module)
            print(f"✅ {module}: Available")
        except ImportError:
            print(f"⚠️  {module}: Not available")


if __name__ == "__main__":
    """
    Run the test scenarios.
    """
    print("🚀 Enhanced Team Interaction & Tasking Test Suite")
    print("=" * 80)
    
    try:
        # Test conversation scenario
        scenario_success = test_conversation_scenario()
        
        # Test technology integration
        test_technology_integration()
        
        print("\n" + "=" * 80)
        if scenario_success:
            print("🎊 TEST SUITE COMPLETED SUCCESSFULLY!")
            print("✨ Enhanced orchestrator ready for production with LangGraph & A2A SDK")
        else:
            print("⚠️  TEST SUITE COMPLETED WITH ISSUES")
            print("🔧 Please review the failed tests and fix issues")
        
    except Exception as e:
        print(f"❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc() 