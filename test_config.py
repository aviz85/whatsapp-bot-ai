#!/usr/bin/env python
"""
Test script to check configuration loading
"""
from config import settings

print("=" * 60)
print("Configuration Check")
print("=" * 60)

print(f"\nGreen API URL: {settings.green_api_url}")
print(f"Green API ID Instance: {settings.green_api_id_instance}")
print(f"Green API Token: {settings.green_api_token_instance[:10]}...")
print(f"\n👤 USER PHONE NUMBER: {settings.user_phone_number}")
print(f"\nOpenRouter API Key: {settings.openrouter_api_key[:20]}...")
print(f"OpenRouter Model: {settings.openrouter_model}")

print("\n" + "=" * 60)

if settings.user_phone_number:
    print(f"✅ User phone number is configured: {settings.user_phone_number}")
    print(f"   Chat ID will be: {settings.user_phone_number}@c.us")
else:
    print("❌ User phone number is NOT configured!")
    print("   Reports will be sent to instance ID instead")

print("=" * 60)
