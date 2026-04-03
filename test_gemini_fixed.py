import requests

API_KEY = "AIzaSyArxXY7C928Bt07t5MVyjP_q4p1gcpYSCQ"

print("=" * 60)
print("GEMINI API KEY TEST - CORRECTED VERSION")
print("=" * 60)
print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
print("-" * 60)

# First, list available models
print("\n1. Listing available models...")
url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    data = response.json()
    models = data.get('models', [])
    print(f"? Found {len(models)} models:")
    
    # Show available models
    for model in models[:5]:  # Show first 5
        print(f"   - {model.get('name')}")
    
    # Find the correct model name
    correct_model = None
    for model in models:
        name = model.get('name', '')
        if 'gemini-1.5-pro' in name or 'gemini-1.0-pro' in name or 'gemini-pro' in name:
            correct_model = name
            print(f"\n? Using model: {correct_model}")
            break
    
    if not correct_model:
        correct_model = "models/gemini-1.5-pro-latest"
        print(f"\n?? Using default model: {correct_model}")
    
    # Test with correct model
    print("\n2. Testing content generation with correct model...")
    
    # Try different model formats
    models_to_try = [
        "models/gemini-1.5-pro",
        "models/gemini-1.5-pro-latest",
        "models/gemini-1.0-pro",
        "models/gemini-pro",
        "models/gemini-1.0-pro-latest"
    ]
    
    success = False
    for model_name in models_to_try:
        gen_url = f"https://generativelanguage.googleapis.com/v1/{model_name}:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": "What is a normal blood pressure range? Answer in one short sentence."
                }]
            }]
        }
        
        print(f"\n   Trying: {model_name}")
        try:
            gen_response = requests.post(gen_url, json=payload, timeout=15)
            
            if gen_response.status_code == 200:
                result = gen_response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"   ? SUCCESS!")
                print(f"   Response: {text}")
                success = True
                break
            else:
                print(f"   ? Failed: {gen_response.status_code}")
        except Exception as e:
            print(f"   ? Error: {str(e)[:50]}")
    
    if success:
        print("\n" + "=" * 60)
        print("?? SUCCESS! Your Gemini API key is working!")
        print("=" * 60)
        print("\nFor your Medical Reminder App, use this model:")
        print("   gemini-1.5-pro")
        print("\nUpdate your ai_service.py with:")
        print('   self.model = genai.GenerativeModel("gemini-1.5-pro")')
    else:
        print("\n?? Could not generate content with any model")
        print("Try enabling the Generative Language API v1beta3 version")
        
else:
    print(f"? Failed to list models: {response.status_code}")
    print(f"Error: {response.text}")

print("\n" + "=" * 60)
