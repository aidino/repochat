#!/usr/bin/env python3
"""
Debug intent parser logic
"""
import sys
import os
sys.path.append('src')

from src.teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser

def test_parser():
    print("Testing SimplifiedLLMIntentParser...")
    
    parser = SimplifiedLLMIntentParser(user_id="debug_user")
    
    test_messages = [
        "Xin chào, tôi muốn học Python",
        "Tôi nên bắt đầu như thế nào?",
        "Tôi muốn review code của dự án",
        "Review PR #123"
    ]
    
    for msg in test_messages:
        print(f"\n--- Testing: {msg} ---")
        intent = parser.parse_user_intent(msg)
        print(f"Intent: {intent.intent_type.value}")
        print(f"Confidence: {intent.confidence}")
        print(f"Suggested: {intent.suggested_questions}")
        print(f"OpenAI available: {parser.openai_client is not None}")

if __name__ == "__main__":
    test_parser() 