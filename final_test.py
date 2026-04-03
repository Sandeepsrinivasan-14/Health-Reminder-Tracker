from ai_service import ai_service

print("=" * 60)
print("FINAL TEST - GEMINI AI WORKING")
print("=" * 60)

result = ai_service.get_health_advice("What is normal blood pressure?", None)

print("\nRESULT:")
print("-" * 40)
print("Response:", result["response"])
print("Provider:", result["provider"])
print("=" * 60)

if "Gemini" in result["provider"]:
    print("SUCCESS: Gemini AI is active and working!")
else:
    print("WARNING: Using fallback mode")
print("=" * 60)
