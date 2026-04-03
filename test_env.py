import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("CHECKING ENVIRONMENT VARIABLES")
print("=" * 60)
print(f"GEMINI_API_KEY from .env: {os.getenv('GEMINI_API_KEY', 'NOT FOUND')[:20]}...")
print(f"AI_PROVIDER: {os.getenv('AI_PROVIDER', 'NOT SET')}")

print("\n" + "=" * 60)
print("IMPORTING AI SERVICE")
print("=" * 60)

from ai_service import ai_service

print(f"AI Service Provider: {ai_service.provider}")
print(f"Gemini Key Available: {bool(ai_service.gemini_key)}")

print("\n" + "=" * 60)
print("TESTING HEALTH CHAT")
print("=" * 60)

result = ai_service.get_health_advice('What is normal blood pressure?', None)
print(f"Response: {result['response']}")
print(f"Provider: {result['provider']}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
