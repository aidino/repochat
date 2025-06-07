#!/usr/bin/env python3
"""
Test User LLM Integration

Kiểm tra việc tích hợp API key của user với LLM services.
"""

import os
import sys

# Add src to path
current_dir = os.path.dirname(__file__)
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_user_llm_service():
    """Test UserLLMService functionality."""
    print("=== Testing UserLLMService ===")
    
    try:
        from services.llm_service_integration import UserLLMService
        from shared.models.user_settings import APIKeyProvider
        
        # Create service
        user_llm_service = UserLLMService()
        print("✅ UserLLMService created successfully")
        
        # Test with default user
        user_id = "user123"
        
        # Check if user has OpenAI API key
        api_key = user_llm_service.get_user_api_key(user_id, APIKeyProvider.OPENAI)
        if api_key:
            print(f"✅ Found OpenAI API key for user {user_id}: {api_key[:10]}...")
            
            # Try to create OpenAI provider
            provider = user_llm_service.create_openai_provider(user_id)
            if provider:
                print(f"✅ Created OpenAI provider with model: {provider.config.model}")
                print(f"   - Temperature: {provider.config.temperature}")
                print(f"   - Max tokens: {provider.config.max_tokens}")
                
                # Test the provider
                if provider.is_available():
                    print("✅ Provider is available")
                    
                    # Test with simple prompt
                    try:
                        test_result = provider.test_connection()
                        print(f"✅ Connection test: {'PASSED' if test_result else 'FAILED'}")
                    except Exception as e:
                        print(f"⚠️  Connection test failed: {e}")
                else:
                    print("❌ Provider is not available")
            else:
                print("❌ Failed to create OpenAI provider")
        else:
            print(f"⚠️  No OpenAI API key found for user {user_id}")
            
        # Test available providers
        available_providers = user_llm_service.get_available_providers_for_user(user_id)
        print(f"✅ Available providers for user {user_id}: {len(available_providers)}")
        for provider, details in available_providers.items():
            provider_name = provider.value if hasattr(provider, 'value') else str(provider)
            print(f"   - {provider_name}: {details['nickname']} (model: {details['preferred_model']})")
        
    except Exception as e:
        print(f"❌ UserLLMService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_simplified_llm_with_user_id():
    """Test SimplifiedLLMIntentParser with user_id."""
    print("\n=== Testing SimplifiedLLMIntentParser with User ID ===")
    
    try:
        from teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
        
        # Test with user that has API key
        user_id = "user123"
        parser = SimplifiedLLMIntentParser(user_id=user_id)
        print(f"✅ SimplifiedLLMIntentParser created for user: {user_id}")
        
        # Check if parser has user-specific settings
        if hasattr(parser, 'user_model'):
            print(f"✅ Using user model: {parser.user_model}")
            print(f"   - Temperature: {parser.user_temperature}")
            print(f"   - Max tokens: {parser.user_max_tokens}")
        else:
            print("⚠️  Using fallback/system settings")
        
        # Test intent parsing
        test_message = "Xin chào, tôi muốn review code của dự án"
        print(f"\nTesting with message: '{test_message}'")
        
        intent = parser.parse_user_intent(test_message)
        print(f"✅ Parsed intent: {intent.intent_type.value}")
        print(f"   - Confidence: {intent.confidence}")
        print(f"   - Suggested response: {intent.suggested_questions[0] if intent.suggested_questions else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ SimplifiedLLMIntentParser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_endpoint_with_user_id():
    """Test chat endpoint with user_id."""
    print("\n=== Testing Chat Endpoint Integration ===")
    
    try:
        import requests
        import json
        
        # Test chat endpoint
        url = "http://localhost:8000/chat"
        payload = {
            "message": "Xin chào, tôi muốn review code",
            "user_id": "user123"
        }
        
        print(f"Sending request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint responded successfully")
            print(f"   - Session ID: {data.get('session_id')}")
            print(f"   - Bot response: {data.get('bot_response', {}).get('content', 'No content')}")
            print(f"   - Conversation state: {data.get('conversation_state')}")
            
            # Check if LLM was used
            context = data.get('bot_response', {}).get('context', {})
            if context.get('llm_powered'):
                print("✅ LLM was used for response")
                print(f"   - Intent: {context.get('intent', 'unknown')}")
                print(f"   - Confidence: {context.get('confidence', 'unknown')}")
            else:
                print("⚠️  Fallback response was used")
                
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing User LLM Integration")
    print("=" * 50)
    
    tests = [
        test_user_llm_service,
        test_simplified_llm_with_user_id,
        test_chat_endpoint_with_user_id
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary")
    print("=" * 50)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    total_passed = sum(results)
    total_tests = len(results)
    print(f"\n📊 Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! User LLM integration is working!")
    else:
        print("⚠️  Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main() 