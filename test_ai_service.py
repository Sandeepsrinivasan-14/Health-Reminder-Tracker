from ai_service import ai_service

print("=" * 60)
print("TESTING AI SERVICE WITH GEMINI 2.5 FLASH")
print("=" * 60)

# Test 1: Health Chat
print("\n1. Testing Health Chat...")
print("-" * 40)
result = ai_service.get_health_advice('What is normal blood pressure?', None)
print(f"Response: {result['response']}")
print(f"Provider: {result['provider']}")

# Test 2: Health Risk Prediction
print("\n2. Testing Health Risk Prediction...")
print("-" * 40)
health_data = {
    'bp_systolic': 145,
    'bp_diastolic': 95,
    'heart_rate': 102,
    'blood_sugar': 150,
    'weight': 75
}
risk = ai_service.predict_health_risk(health_data)
print(f"Risk Level: {risk['risk_level']}")
print(f"Risks: {', '.join(risk['risks'])}")
print(f"Recommendations: {'; '.join(risk['recommendations'])}")

print("\n" + "=" * 60)
print("? AI Service Test Complete!")
print("=" * 60)
