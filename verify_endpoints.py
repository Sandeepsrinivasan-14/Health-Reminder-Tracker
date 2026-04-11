import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, method, endpoint, data=None):
    print(f"Testing {name} ({method} {endpoint})...", end=" ", flush=True)
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        elif method == "POST":
            resp = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
        
        if resp.status_code < 300:
            print("SUCCESS")
            return resp.json()
        else:
            print(f"FAILED (Status: {resp.status_code})")
            print(f"   Response: {resp.text}")
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def verify_all():
    print("\nSTARTING BACKEND VERIFICATION SUITE\n" + "="*40)
    
    # 1. Health Check
    test_endpoint("Health Check", "GET", "/health")
    
    # 2. Get Users
    users = test_endpoint("Get Users", "GET", "/users")
    
    # 3. Create New User
    test_user_email = f"test_{int(time.time())}@example.com"
    new_user = test_endpoint("Create User", "POST", "/users", {
        "name": "Verification Tester",
        "email": test_user_email
    })
    
    if new_user:
        user_id = new_user['id']
        
        # 4. Save Health Data
        test_endpoint("Save Health Data", "POST", "/health-data", {
            "user_id": user_id,
            "bp_systolic": 120,
            "bp_diastolic": 80,
            "heart_rate": 72,
            "blood_sugar": 95,
            "weight": 70.5
        })
        
        # 5. Get Health Data
        test_endpoint("Get Health History", "GET", f"/health-data/user/{user_id}")
        
        # 6. AI Chat
        test_endpoint("AI Chat Assistant", "POST", "/api/ai/chat", {
            "user_id": user_id,
            "question": "Give me a health summary based on my latest data."
        })
        
        # 7. AI Medication Suggestions
        test_endpoint("AI Med Suggestions", "POST", "/api/ai/medication-suggestions", {
            "user_id": user_id,
            "medications": [{"name": "Aspirin", "dosage": "75mg", "time": "08:00"}]
        })

    print("="*40 + "\nVERIFICATION COMPLETE\n")

if __name__ == "__main__":
    verify_all()
