#!/usr/bin/env python3
"""
Test script for streaming chat functionality
Kiểm tra tính năng streaming chat với real-time status updates
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_regular_chat():
    """Test regular (non-streaming) chat endpoint"""
    print("🧪 Testing regular chat endpoint...")
    
    payload = {
        "message": "Xin chào, tôi muốn test chức năng chat",
        "session_id": None,
        "repository_context": None,
        "user_id": "test_user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Regular chat successful!")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Bot response: {data.get('bot_response', {}).get('content', 'No response')[:100]}...")
            return data.get('session_id')
        else:
            print(f"❌ Regular chat failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in regular chat: {e}")
        return None

def test_streaming_chat():
    """Test streaming chat endpoint với SSE"""
    print("\n🌊 Testing streaming chat endpoint...")
    
    payload = {
        "message": "Tôi muốn test streaming chat với real-time status",
        "session_id": None,
        "repository_context": None,
        "user_id": "test_user"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/stream", 
            json=payload, 
            stream=True,
            headers={"Accept": "text/event-stream"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Streaming connection established!")
            
            events_received = 0
            status_updates = 0
            completion_received = False
            
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])  # Remove "data: " prefix
                        events_received += 1
                        
                        event_type = data.get("type")
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        if event_type == "status":
                            status_updates += 1
                            status = data.get("status", "Unknown")
                            progress = data.get("progress", 0)
                            print(f"   [{timestamp}] 📊 Status: {status} ({progress}%)")
                            
                        elif event_type == "complete":
                            completion_received = True
                            bot_response = data.get("bot_response", {}).get("content", "No response")
                            print(f"   [{timestamp}] ✅ Complete: {bot_response[:100]}...")
                            break
                            
                        elif event_type == "error":
                            print(f"   [{timestamp}] ❌ Error: {data.get('error')}")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️ Failed to parse SSE data: {line}")
            
            print(f"\n📊 Streaming Statistics:")
            print(f"   Total events received: {events_received}")
            print(f"   Status updates: {status_updates}")
            print(f"   Completion received: {'✅' if completion_received else '❌'}")
            
            return completion_received
            
        else:
            print(f"❌ Streaming failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in streaming chat: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend healthy!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 STREAMING CHAT FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Test health first
    if not test_health():
        print("\n❌ Backend not available. Make sure to start backend with:")
        print("   cd backend && python main.py")
        return
    
    # Test regular chat
    session_id = test_regular_chat()
    
    # Test streaming chat
    streaming_success = test_streaming_chat()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Health check: {'✅ PASS' if test_health() else '❌ FAIL'}")
    print(f"Regular chat: {'✅ PASS' if session_id else '❌ FAIL'}")
    print(f"Streaming chat: {'✅ PASS' if streaming_success else '❌ FAIL'}")
    
    if session_id and streaming_success:
        print("\n🎉 All tests passed! Streaming functionality working correctly.")
        print("\n💡 Frontend testing:")
        print("   1. Start frontend: cd frontend && npm run dev")
        print("   2. Open http://localhost:5173")
        print("   3. Send a message and watch for real-time status updates!")
    else:
        print("\n⚠️ Some tests failed. Check backend logs for details.")

if __name__ == "__main__":
    main() 