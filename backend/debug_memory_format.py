#!/usr/bin/env python3
"""
Debug memory format
"""
import sys
import os
sys.path.append('src')

from src.services.memory_service import memory_service
import json

def debug_memory_format():
    print("=== DEBUG MEMORY FORMAT ===")
    
    user_id = "test_context_debug"
    
    # Add test memory
    result = memory_service.add_conversation_memory(
        user_id=user_id,
        session_id="debug_session",
        user_message="Hello test",
        bot_response="Hi there!"
    )
    print(f"Add memory result: {result}")
    
    # Get memories
    memories = memory_service.get_user_memories(user_id)
    print(f"\n=== MEMORIES STRUCTURE ===")
    print(f"Type: {type(memories)}")
    print(f"Content: {json.dumps(memories, indent=2, default=str)}")
    
    # Get relevant memories
    relevant = memory_service.get_relevant_memories(user_id, "test message", limit=3)
    print(f"\n=== RELEVANT MEMORIES STRUCTURE ===")
    print(f"Type: {type(relevant)}")
    print(f"Content: {json.dumps(relevant, indent=2, default=str)}")
    
    # Test slice operation
    try:
        if isinstance(relevant, dict) and 'results' in relevant:
            sliced = relevant['results'][-2:]
            print(f"\n=== SLICE TEST ===")
            print(f"relevant['results'][-2:] works: {len(sliced)} items")
            for i, mem in enumerate(sliced):
                memory_text = mem.get('memory', mem.get('user_message', ''))
                print(f"  {i}: {memory_text}")
        else:
            sliced = relevant[-2:]
            print(f"\n=== SLICE TEST ===")
            print(f"relevant[-2:] works: {len(sliced)} items")
    except Exception as e:
        print(f"\n=== SLICE ERROR ===")
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    debug_memory_format() 