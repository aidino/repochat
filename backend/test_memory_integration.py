#!/usr/bin/env python3
"""
Test script cho Memory Integration với mem0ai.

Kiểm tra:
1. Memory service initialization
2. Chat với memory context
3. Memory retrieval
4. Memory persistence
"""

import asyncio
import sys
import os
import time
import requests
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_memory_service():
    """Test memory service directly."""
    print("🧠 Testing Memory Service...")
    
    try:
        from src.services.memory_service import memory_service
        
        # Test stats
        stats = memory_service.get_memory_stats("test_user_memory")
        print(f"✅ Memory service initialized: {stats}")
        
        # Test adding memory
        success = memory_service.add_conversation_memory(
            user_id="test_user_memory",
            session_id="test_session_123",
            user_message="Tôi muốn tìm hiểu về Python programming",
            bot_response="Python là một ngôn ngữ lập trình mạnh mẽ và dễ học",
            context={"intent": "learn_programming", "confidence": 0.9}
        )
        print(f"✅ Add memory result: {success}")
        
        # Test retrieving memories
        memories = memory_service.get_user_memories("test_user_memory", limit=5)
        print(f"✅ Retrieved {len(memories)} memories")
        
        # Test searching memories
        relevant = memory_service.get_relevant_memories(
            user_id="test_user_memory",
            current_message="Làm sao để học Python hiệu quả?",
            limit=3
        )
        print(f"✅ Found {len(relevant)} relevant memories")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_with_memory():
    """Test chat API với memory integration."""
    print("\n💬 Testing Chat with Memory...")
    
    try:
        base_url = "http://localhost:8000"
        user_id = "test_user_memory"
        
        # Test conversation 1
        print("📝 Conversation 1: Initial question about coding")
        response1 = requests.post(f"{base_url}/chat", json={
            "message": "Tôi muốn học lập trình Python, bạn có thể hướng dẫn không?",
            "user_id": user_id
        })
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Bot response 1: {result1['bot_response']['content'][:100]}...")
            print(f"   Context: {result1['bot_response'].get('context', {})}")
            session_id = result1['session_id']
        else:
            print(f"❌ Chat 1 failed: {response1.status_code} - {response1.text}")
            return False
        
        # Wait a bit for memory to be saved
        time.sleep(2)
        
        # Test conversation 2 (should have memory context)
        print("\n📝 Conversation 2: Follow-up question (should use memory)")
        response2 = requests.post(f"{base_url}/chat", json={
            "message": "Tôi nên bắt đầu từ đâu?",
            "user_id": user_id,
            "session_id": session_id
        })
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Bot response 2: {result2['bot_response']['content'][:100]}...")
            print(f"   Context: {result2['bot_response'].get('context', {})}")
            
            # Check if memory was used
            context = result2['bot_response'].get('context', {})
            if context.get('has_memory_context'):
                print("🧠 ✅ Memory context was used!")
            else:
                print("🧠 ⚠️  Memory context not detected")
        else:
            print(f"❌ Chat 2 failed: {response2.status_code} - {response2.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Chat with memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_endpoints():
    """Test memory management endpoints."""
    print("\n🔍 Testing Memory Endpoints...")
    
    try:
        base_url = "http://localhost:8000"
        user_id = "test_user_memory"
        
        # Test get memories
        print("📋 Testing get user memories...")
        response = requests.get(f"{base_url}/users/{user_id}/memories?limit=10")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved memories: {result['total_retrieved']} items")
            print(f"   Stats: {result['stats']}")
        else:
            print(f"❌ Get memories failed: {response.status_code} - {response.text}")
            return False
        
        # Test search memories
        print("\n🔎 Testing search memories...")
        search_response = requests.get(f"{base_url}/users/{user_id}/memories/search", params={
            "query": "Python programming",
            "limit": 5
        })
        
        if search_response.status_code == 200:
            search_result = search_response.json()
            print(f"✅ Search found: {search_result['total_found']} relevant memories")
        else:
            print(f"❌ Search memories failed: {search_response.status_code} - {search_response.text}")
            return False
        
        # Test memory stats
        print("\n📊 Testing memory stats...")
        stats_response = requests.get(f"{base_url}/users/{user_id}/memories/stats")
        
        if stats_response.status_code == 200:
            stats_result = stats_response.json()
            print(f"✅ Memory stats: {stats_result['stats']}")
            print(f"   System info: {stats_result['system_info']}")
        else:
            print(f"❌ Memory stats failed: {stats_response.status_code} - {stats_response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Memory endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_persistence():
    """Test memory persistence across sessions."""
    print("\n💾 Testing Memory Persistence...")
    
    try:
        base_url = "http://localhost:8000"
        user_id = "test_user_persistence"
        
        # Create conversation in new session
        print("📝 Creating conversation in new session...")
        response = requests.post(f"{base_url}/chat", json={
            "message": "Tôi đang làm dự án về machine learning với TensorFlow",
            "user_id": user_id
        })
        
        if response.status_code != 200:
            print(f"❌ Initial conversation failed: {response.status_code}")
            return False
        
        time.sleep(3)  # Wait for memory to be saved
        
        # Start completely new session and reference previous conversation
        print("🔄 Starting new session and referencing previous topic...")
        new_response = requests.post(f"{base_url}/chat", json={
            "message": "Bạn có thể giúp tôi optimize model TensorFlow không?",
            "user_id": user_id
            # Note: no session_id - this is a new session
        })
        
        if new_response.status_code == 200:
            result = new_response.json()
            print(f"✅ New session response: {result['bot_response']['content'][:100]}...")
            
            context = result['bot_response'].get('context', {})
            if context.get('has_memory_context'):
                print("🧠 ✅ Memory successfully persisted across sessions!")
            else:
                print("🧠 ⚠️  Memory not used in new session")
            
            return True
        else:
            print(f"❌ New session failed: {new_response.status_code} - {new_response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Memory persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data():
    """Clean up test data."""
    print("\n🧹 Cleaning up test data...")
    
    try:
        base_url = "http://localhost:8000"
        
        # Delete memories for test users
        for user_id in ["test_user_memory", "test_user_persistence"]:
            response = requests.delete(f"{base_url}/users/{user_id}/memories")
            if response.status_code == 200:
                print(f"✅ Cleaned up memories for {user_id}")
            else:
                print(f"⚠️  Cleanup warning for {user_id}: {response.status_code}")
        
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}")


def main():
    """Main test runner."""
    print("🚀 Memory Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Memory Service", test_memory_service),
        ("Chat with Memory", test_chat_with_memory),
        ("Memory Endpoints", test_memory_endpoints), 
        ("Memory Persistence", test_memory_persistence)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All memory integration tests PASSED!")
        return 0
    else:
        print("⚠️  Some tests failed. Check logs for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 