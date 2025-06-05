#!/usr/bin/env python3
"""
Debug script to find the exact source of 'LLMProviderType' object has no attribute 'provider' error
"""

import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_provider_creation():
    """Debug provider creation step by step."""
    try:
        print("=== Step 1: Import modules ===")
        from src.teams.llm_services import LLMProviderType, LLMConfig, LLMProviderFactory
        print("✅ Imports successful")
        
        print("\n=== Step 2: Create LLMConfig ===")
        config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key="test_key"
        )
        print(f"✅ Config created: provider={config.provider}, type={type(config.provider)}")
        
        print("\n=== Step 3: Create Factory ===")
        factory = LLMProviderFactory()
        print("✅ Factory created")
        
        print("\n=== Step 4: Check registry ===")
        registry = factory._provider_registry
        print(f"✅ Registry keys: {list(registry.keys())}")
        print(f"✅ OpenAI provider class: {registry[LLMProviderType.OPENAI]}")
        
        print("\n=== Step 5: Create provider ===")
        provider_class = registry[config.provider]
        print(f"✅ Provider class retrieved: {provider_class}")
        
        print("\n=== Step 6: Instantiate provider ===")
        try:
            provider = provider_class(config)
            print(f"✅ Provider instantiated: {provider}")
            print(f"✅ Provider config: {provider.config}")
            print(f"✅ Provider config provider: {provider.config.provider}")
        except Exception as e:
            print(f"❌ Provider instantiation failed: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return
        
        print("\n=== Step 7: Test provider.config.provider.value ===")
        try:
            value = provider.config.provider.value
            print(f"✅ provider.config.provider.value = {value}")
        except Exception as e:
            print(f"❌ Error accessing provider.config.provider.value: {e}")
            print(f"provider.config type: {type(provider.config)}")
            print(f"provider.config.provider type: {type(provider.config.provider)}")
            print(f"provider.config.provider attributes: {dir(provider.config.provider)}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")

def debug_llm_gateway():
    """Debug LLM Gateway creation."""
    try:
        print("\n=== LLM Gateway Debug ===")
        from src.teams.llm_services import create_llm_gateway, get_default_openai_config
        
        print("Step 1: Create gateway")
        gateway = create_llm_gateway()
        print("✅ Gateway created")
        
        print("Step 2: Create config")
        config = get_default_openai_config()
        config.api_key = "test_key"
        print(f"✅ Config created: {config}")
        
        print("Step 3: Test _get_provider method")
        try:
            provider = gateway._get_provider(config.provider)
            print(f"✅ Provider from gateway: {provider}")
        except Exception as e:
            print(f"❌ Gateway _get_provider failed: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            
    except Exception as e:
        print(f"❌ Gateway debug failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🔍 Debugging Provider Error")
    debug_provider_creation()
    debug_llm_gateway() 