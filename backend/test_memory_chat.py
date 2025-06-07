#!/usr/bin/env python3
"""
Test script for memory integration in chat
"""
import requests
import time
import json

def test_memory_integration():
    print("🧪 Testing Memory Integration with New Server")
    
    # First message
    response1 = requests.post('http://localhost:8000/chat', json={
        'message': 'Tôi muốn học React programming', 
        'user_id': 'new_memory_test'
    })
    print(f"Response 1 status: {response1.status_code}")
    
    if response1.status_code == 200:
        data1 = response1.json()
        context1 = data1['bot_response']['context']
        print(f"Memory context 1: {context1.get('has_memory_context')}")
        print(f"Memories used: {context1.get('memories_used')}")
        print(f"Bot said: {data1['bot_response']['content'][:100]}...")
    
    time.sleep(3)
    
    # Second message (should have memory context)
    response2 = requests.post('http://localhost:8000/chat', json={
        'message': 'Tôi nên bắt đầu từ component nào?', 
        'user_id': 'new_memory_test'
    })
    print(f"\nResponse 2 status: {response2.status_code}")
    
    if response2.status_code == 200:
        data2 = response2.json()
        context2 = data2['bot_response']['context']
        print(f"Memory context 2: {context2.get('has_memory_context')}")
        print(f"Memories used: {context2.get('memories_used')}")
        print(f"Bot said: {data2['bot_response']['content'][:100]}...")
        
        # Check if memory is working
        if context2.get('memories_used', 0) > 0:
            print("\n✅ Memory integration is working!")
        else:
            print("\n❌ Memory integration is not working")
    
    # Check memory API
    print("\n📊 Checking memory stats...")
    response3 = requests.get('http://localhost:8000/users/new_memory_test/memories/stats')
    if response3.status_code == 200:
        data = response3.json()
        stats = data.get('stats', {})
        print(f"Total memories: {stats.get('total_memories')}")
        print(f"Memory service active: {stats.get('memory_service_active')}")
        print(f"Response: {data}")

if __name__ == "__main__":
    test_memory_integration() 