#!/usr/bin/env python3
"""Debug script to test API key encryption and storage."""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from services.user_settings_service import UserSettingsService
from shared.models.user_settings import APIKeyProvider, APIKeyRequest

def main():
    print("=== Debugging API Key Encryption and Storage ===")
    
    service = UserSettingsService()
    
    # Test encryption directly
    print("1. Testing API key encryption...")
    try:
        encrypted_key = service.api_key_manager.encrypt_api_key(
            "sk-test123456789",
            APIKeyProvider.OPENAI,
            "Test Key"
        )
        print(f"✅ Encryption successful")
        print(f"  Provider: {encrypted_key.provider}")
        print(f"  Nickname: {encrypted_key.nickname}")
        print(f"  Encrypted key length: {len(encrypted_key.encrypted_key)}")
        print(f"  Hash: {encrypted_key.key_hash[:20]}...")
        print(f"  Created: {encrypted_key.created_at}")
        print(f"  Valid: {encrypted_key.is_valid}")
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test adding API key
    print("\n2. Testing add_api_key method...")
    request = APIKeyRequest(
        provider=APIKeyProvider.OPENAI,
        api_key="sk-test123456789",
        nickname="Debug Test Key"
    )
    
    try:
        # Get settings before
        settings_before = service.get_user_settings('user123')
        print(f"API keys before: {len(settings_before.api_keys)}")
        
        # Add API key
        success = service.add_api_key('user123', request)
        print(f"Add API key result: {success}")
        
        # Get settings after
        settings_after = service.get_user_settings('user123')
        print(f"API keys after: {len(settings_after.api_keys)}")
        
        # Check if key exists
        key_id = "openai"
        if key_id in settings_after.api_keys:
            print(f"✅ Found API key with ID '{key_id}'")
            encrypted_key = settings_after.api_keys[key_id]
            print(f"  Provider: {encrypted_key.provider}")
            print(f"  Nickname: {encrypted_key.nickname}")
        else:
            print(f"❌ API key with ID '{key_id}' not found")
            print("Available keys:")
            for k, v in settings_after.api_keys.items():
                print(f"  - '{k}': {v.provider}")
        
    except Exception as e:
        print(f"❌ Add API key failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test serialization
    print("\n3. Testing serialization...")
    try:
        settings = service.get_user_settings('user123')
        serialized = service._serialize_user_settings(settings)
        print(f"Serialized API keys: {len(serialized.get('api_keys', {}))}")
        
        for key_id, key_data in serialized.get('api_keys', {}).items():
            print(f"  Key ID: {key_id}")
            print(f"  Provider: {key_data.get('provider')}")
            print(f"  Nickname: {key_data.get('nickname')}")
            
    except Exception as e:
        print(f"❌ Serialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 