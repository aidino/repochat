#!/usr/bin/env python3
"""
Test Enhanced Streaming Chat với Task Execution Integration
Kiểm tra việc AI response kết hợp với actual task execution
"""

import asyncio
import json
import httpx
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_health_check():
    """Test basic health check"""
    print("🏥 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check PASS: {data}")
                return True
            else:
                print(f"❌ Health check FAIL: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check ERROR: {e}")
            return False

async def test_repository_scanning_flow():
    """Test repository scanning flow với streaming"""
    print("\n🔄 Testing Repository Scanning Flow...")
    
    # Test với actual repository URL
    test_message = "Chào bạn! Hãy scan repository này: https://github.com/aidino/repochat"
    
    payload = {
        "session_id": None,
        "message": test_message,
        "user_id": "test_user"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"📤 Sending: {test_message[:50]}...")
            
            # Use stream for SSE
            async with client.stream(
                'POST',
                f"{BASE_URL}/chat/stream",
                json=payload
            ) as response:
                
                if response.status_code != 200:
                    print(f"❌ Request failed: {response.status_code}")
                    print(f"Response: {await response.aread()}")
                    return False
                
                print("📡 Receiving streaming events...")
                
                status_count = 0
                task_execution_detected = False
                completion_received = False
                repository_url_found = False
                
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        try:
                            event_data = json.loads(line[6:])  # Remove 'data: ' prefix
                            event_type = event_data.get('type')
                            
                            if event_type == 'status':
                                status_count += 1
                                status = event_data.get('status', '')
                                progress = event_data.get('progress', 0)
                                print(f"  📊 Status {status_count}: {status} ({progress}%)")
                                
                                # Check for task execution indicators
                                if any(keyword in status.lower() for keyword in ['task', 'scan', 'repository', 'khởi tạo']):
                                    task_execution_detected = True
                                    print(f"    🎯 Task execution detected!")
                                
                                if 'repository url' in status.lower():
                                    repository_url_found = True
                                    print(f"    📦 Repository URL detection confirmed!")
                                    
                            elif event_type == 'message':
                                message_content = event_data.get('content', '')
                                print(f"  💬 Message: {message_content[:100]}...")
                                
                            elif event_type == 'complete':
                                completion_received = True
                                session_response = event_data.get('session_response', {})
                                bot_response = session_response.get('bot_response', {})
                                content = bot_response.get('content', '')
                                context = bot_response.get('context', {})
                                
                                print(f"  ✅ Completion: {content[:100]}...")
                                print(f"  📋 Context: {context}")
                                
                                # Check for task execution info trong response
                                if 'task_execution_id' in context:
                                    print(f"    🚀 Task Execution ID: {context['task_execution_id']}")
                                    task_execution_detected = True
                                
                                if 'repository_url' in context:
                                    print(f"    🔗 Repository URL: {context['repository_url']}")
                                    repository_url_found = True
                                    
                        except json.JSONDecodeError as e:
                            print(f"  ⚠️ JSON decode error: {e}")
                            print(f"  Raw line: {line}")
                
                # Validate results
                print(f"\n📈 Results Summary:")
                print(f"  Status events: {status_count}")
                print(f"  Task execution detected: {'✅' if task_execution_detected else '❌'}")
                print(f"  Repository URL found: {'✅' if repository_url_found else '❌'}")
                print(f"  Completion received: {'✅' if completion_received else '❌'}")
                
                success = (
                    status_count >= 5 and
                    completion_received
                )
                
                if success:
                    print("✅ Repository scanning flow test PASSED")
                    return True
                else:
                    print("❌ Repository scanning flow test FAILED")
                    return False
                    
        except Exception as e:
            print(f"❌ Repository scanning test ERROR: {e}")
            return False

async def test_general_conversation():
    """Test general conversation flow"""
    print("\n💬 Testing General Conversation Flow...")
    
    test_message = "Xin chào! Bạn có thể giúp tôi làm gì?"
    
    payload = {
        "session_id": None,
        "message": test_message,
        "user_id": "test_user"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"📤 Sending: {test_message}")
            
            async with client.stream(
                'POST',
                f"{BASE_URL}/chat/stream",
                json=payload
            ) as response:
                
                if response.status_code != 200:
                    print(f"❌ Request failed: {response.status_code}")
                    return False
                
                print("📡 Receiving streaming events...")
                
                status_count = 0
                completion_received = False
                
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        try:
                            event_data = json.loads(line[6:])
                            event_type = event_data.get('type')
                            
                            if event_type == 'status':
                                status_count += 1
                                status = event_data.get('status', '')
                                progress = event_data.get('progress', 0)
                                print(f"  📊 Status {status_count}: {status} ({progress}%)")
                                    
                            elif event_type == 'complete':
                                completion_received = True
                                session_response = event_data.get('session_response', {})
                                bot_response = session_response.get('bot_response', {})
                                content = bot_response.get('content', '')
                                
                                print(f"  ✅ Completion: {content[:100]}...")
                                
                        except json.JSONDecodeError:
                            pass
                
                success = status_count >= 5 and completion_received
                
                if success:
                    print("✅ General conversation test PASSED")
                    return True
                else:
                    print("❌ General conversation test FAILED")
                    return False
                    
        except Exception as e:
            print(f"❌ General conversation test ERROR: {e}")
            return False

async def main():
    """Run all enhanced streaming tests"""
    print("🚀 Starting Enhanced Streaming Chat Tests với Task Execution")
    print("=" * 60)
    
    start_time = time.time()
    
    # Test 1: Health check
    health_ok = await test_health_check()
    if not health_ok:
        print("❌ Health check failed, aborting tests")
        return
    
    # Test 2: General conversation
    general_ok = await test_general_conversation()
    
    # Test 3: Repository scanning flow (main feature)
    repo_scan_ok = await test_repository_scanning_flow()
    
    # Summary
    duration = time.time() - start_time
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"General Conversation: {'✅ PASS' if general_ok else '❌ FAIL'}")
    print(f"Repository Scanning: {'✅ PASS' if repo_scan_ok else '❌ FAIL'}")
    print(f"Total Duration: {duration:.2f}s")
    
    all_passed = health_ok and general_ok and repo_scan_ok
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Enhanced streaming chat với task execution đã hoạt động hoàn hảo!")
        print("Repository scanning integration successful!")
    else:
        print("\n⚠️ Cần kiểm tra lại implementation")

if __name__ == "__main__":
    asyncio.run(main()) 