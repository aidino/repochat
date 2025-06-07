#!/usr/bin/env python3
"""
Demo script cho Memory Integration trong Chat.
Demonstrates conversation memory và context awareness.
"""

import requests
import time

def demo_memory_chat():
    """Demo conversation memory functionality."""
    print('🧠 DEMO: Memory Integration trong Chat')
    print('=' * 50)

    base_url = 'http://localhost:8000'
    user_id = 'demo_user_789'

    # Conversation 1
    print('📝 Conversation 1: Hỏi về Python')
    response1 = requests.post(f'{base_url}/chat', json={
        'message': 'Tôi muốn học Python để làm web development. Bạn có thể tư vấn không?',
        'user_id': user_id
    })

    if response1.status_code == 200:
        result1 = response1.json()
        print(f'✅ Bot: {result1["bot_response"]["content"][:80]}...')
        session_id = result1['session_id']
        print(f'   Session: {session_id}')
    else:
        print(f'❌ Error: {response1.status_code}')
        return

    # Wait for memory to be saved
    time.sleep(2)

    # Conversation 2 - continuation
    print('\n📝 Conversation 2: Follow-up question')
    response2 = requests.post(f'{base_url}/chat', json={
        'message': 'Framework nào phù hợp cho beginners?',
        'user_id': user_id,
        'session_id': session_id
    })

    if response2.status_code == 200:
        result2 = response2.json()
        print(f'✅ Bot: {result2["bot_response"]["content"][:80]}...')
        context = result2['bot_response'].get('context', {})
        print(f'   Memory used: {context.get("has_memory_context", False)}')
        print(f'   Memories count: {context.get("memories_used", 0)}')
    else:
        print(f'❌ Error: {response2.status_code}')

    # Check memory stats
    print('\n📊 Memory Stats:')
    stats_response = requests.get(f'{base_url}/users/{user_id}/memories/stats')
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f'✅ Total memories: {stats["stats"]["total_memories"]}')
        print(f'   Service active: {stats["stats"]["memory_service_active"]}')
        print(f'   Fallback mode: {stats["stats"].get("fallback_mode", False)}')
    else:
        print(f'❌ Stats error: {stats_response.status_code}')

    # New session test
    print('\n🔄 New Session Test (Memory Persistence):')
    response3 = requests.post(f'{base_url}/chat', json={
        'message': 'Tôi có nên học Django hay Flask?',
        'user_id': user_id
        # No session_id = new session
    })

    if response3.status_code == 200:
        result3 = response3.json()
        print(f'✅ Bot: {result3["bot_response"]["content"][:80]}...')
        context = result3['bot_response'].get('context', {})
        print(f'   Memory used: {context.get("has_memory_context", False)}')
        print(f'   New session: {result3["session_id"]}')
    else:
        print(f'❌ Error: {response3.status_code}')

    print('\n🎉 Memory integration demo hoàn thành!')

if __name__ == "__main__":
    demo_memory_chat() 