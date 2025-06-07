#!/usr/bin/env python3
"""
Test memory service manually
"""
import sys
import os
sys.path.append('src')

from src.services.memory_service import memory_service

print('Testing memory service...')

# Test add memory
result = memory_service.add_conversation_memory(
    user_id='test123',
    session_id='session456', 
    user_message='Hello, I want to learn Python',
    bot_response='Hi there! I can help you learn Python.'
)
print(f'Add memory result: {result}')

# Test get memories
memories = memory_service.get_user_memories('test123')
print(f'Retrieved memories: {len(memories) if isinstance(memories, list) else memories}')
print(f'Memory content: {memories}')

# Test relevant memories
relevant = memory_service.get_relevant_memories('test123', 'Python tutorial', limit=2)
print(f'Relevant memories: {len(relevant) if isinstance(relevant, list) else relevant}')

# Test stats
stats = memory_service.get_memory_stats('test123')
print(f'Memory stats: {stats}') 