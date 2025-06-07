#!/usr/bin/env python3
"""Debug script to check user settings API keys."""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from services.user_settings_service import UserSettingsService
from shared.models.user_settings import APIKeyProvider

def main():
    print("=== Debugging User Settings API Keys ===")
    
    service = UserSettingsService()
    settings = service.get_user_settings('user123')
    
    print(f"User ID: {settings.user_id}")
    print(f"API keys in settings: {len(settings.api_keys)}")
    
    for key_id, encrypted_key in settings.api_keys.items():
        print(f"  Key ID: {key_id}")
        print(f"  Provider: {encrypted_key.provider}")
        print(f"  Nickname: {encrypted_key.nickname}")
        print(f"  Created: {encrypted_key.created_at}")
        print(f"  Valid: {encrypted_key.is_valid}")
        print()
    
    # Test direct API key retrieval
    print("Testing direct API key retrieval:")
    api_key = service.get_api_key('user123', APIKeyProvider.OPENAI)
    if api_key:
        print(f"✅ Found OpenAI API key: {api_key[:10]}...")
    else:
        print("❌ No OpenAI API key found")
    
    # Test with string lookup
    print("\nTesting string key lookup:")
    key_id = "openai"
    if key_id in settings.api_keys:
        print(f"✅ Found key with ID '{key_id}'")
        encrypted_key = settings.api_keys[key_id]
        print(f"  Provider: {encrypted_key.provider}")
        print(f"  Type: {type(encrypted_key.provider)}")
    else:
        print(f"❌ No key found with ID '{key_id}'")
        print("Available key IDs:")
        for k in settings.api_keys.keys():
            print(f"  - '{k}' (type: {type(k)})")

if __name__ == "__main__":
    main() 