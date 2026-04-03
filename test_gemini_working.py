import requests

API_KEY = "AIzaSyArxXY7C928Bt07t5MVyjP_q4p1gcpYSCQ"

print("=" * 60)
print("GEMINI API KEY TEST - USING AVAILABLE MODELS")
print("=" * 60)
print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
print("-" * 60)

# List available models
print("\n1. Available models from your API:")
url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    data = response.json()
    models = data.get('models', [])
    print(f"? Found {len(models)} models:")
    
    for model in models:
        name = model.get('name', '')
        print(f"   - {name}")
    
    # Test with the actual available models
    print("\n2. Testing content generation with available models...")
    
    # Use the models you actually have access to
    models_to_try = [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-001"
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
        
        print(f"\n   Testing: {model_name}")
        try:
            gen_response = requests.post(gen_url, json=payload, timeout=15)
            
            if gen_response.status_code == 200:
                result = gen_response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"   ? SUCCESS!")
                print(f"   Response: {text}")
                success = True
                print(f"\n?? RECOMMENDED MODEL: {model_name}")
                break
            else:
                print(f"   ? Failed: {gen_response.status_code}")
                if gen_response.status_code == 404:
                    error_json = gen_response.json()
                    if 'error' in error_json:
                        print(f"   Message: {error_json['error'].get('message', 'Unknown')}")
        except Exception as e:
            print(f"   ? Error: {str(e)}")
    
    if not success:
        print("\n?? Testing with v1beta version...")
        # Try v1beta API version
        for model_name in models_to_try:
            gen_url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "What is normal blood pressure?"
                    }]
                }]
            }
            
            print(f"\n   Testing (v1beta): {model_name}")
            try:
                gen_response = requests.post(gen_url, json=payload, timeout=15)
                
                if gen_response.status_code == 200:
                    result = gen_response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"   ? SUCCESS with v1beta!")
                    print(f"   Response: {text}")
                    print(f"\n?? RECOMMENDED: Use v1beta API with {model_name}")
                    success = True
                    break
                else:
                    print(f"   ? Failed: {gen_response.status_code}")
            except Exception as e:
                print(f"   ? Error: {str(e)[:100]}")
    
    print("\n" + "=" * 60)
    if success:
        print("? SUCCESS! Your Gemini API key is working!")
        print("\n?? For your Medical Reminder App, update ai_service.py:")
        print('   self.model = genai.GenerativeModel("gemini-2.0-flash")')
        print("\n   Or with the new google-genai package:")
        print('   from google import genai')
        print('   client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))')
        print('   response = client.models.generate_content(')
        print('       model="gemini-2.0-flash",')
        print('       contents="Your question here"')
        print('   )')
    else:
        print("? No working model found")
        print("\n?? Try using the new google-genai package:")
        print("   pip install google-genai")
        
else:
    print(f"? Failed to list models: {response.status_code}")
    print(f"Error: {response.text}")

print("=" * 60)
