import requests
from datetime import datetime, timedelta
import random

API_URL = 'https://health-reminder-tracker-1.onrender.com'

# Detailed health records for each patient (10 days each)
all_records = [
    # Patient 1: John Doe (Healthy, stable)
    (1, 118, 78, 72, 95, 70.0), (1, 120, 80, 73, 96, 70.2),
    (1, 117, 77, 71, 94, 69.8), (1, 119, 79, 72, 95, 70.1),
    (1, 121, 81, 74, 97, 70.3), (1, 116, 76, 70, 93, 69.7),
    (1, 118, 78, 72, 95, 70.0), (1, 120, 80, 73, 96, 70.1),
    (1, 117, 77, 71, 94, 69.9), (1, 119, 79, 72, 95, 70.0),
    
    # Patient 2: Jane Smith (Elevated, improving with meds)
    (2, 130, 85, 80, 110, 75.0), (2, 128, 84, 79, 108, 74.8),
    (2, 126, 83, 78, 106, 74.5), (2, 125, 82, 77, 105, 74.3),
    (2, 124, 81, 76, 104, 74.0), (2, 123, 80, 75, 103, 73.8),
    (2, 122, 80, 75, 102, 73.5), (2, 121, 79, 74, 101, 73.2),
    (2, 120, 78, 74, 100, 73.0), (2, 119, 78, 73, 99, 72.8),
    
    # Patient 3: Bob Johnson (Athletic, very stable)
    (3, 115, 75, 68, 90, 65.0), (3, 114, 74, 67, 89, 64.8),
    (3, 116, 76, 69, 91, 65.2), (3, 115, 75, 68, 90, 65.0),
    (3, 113, 74, 67, 88, 64.7), (3, 115, 75, 68, 90, 65.1),
    (3, 116, 76, 69, 91, 65.0), (3, 114, 74, 67, 89, 64.9),
    (3, 115, 75, 68, 90, 65.0), (3, 115, 75, 68, 90, 65.0),
    
    # Patient 4: Alice Williams (Hypertension)
    (4, 140, 90, 85, 125, 80.0), (4, 142, 91, 86, 128, 80.5),
    (4, 138, 89, 84, 123, 79.8), (4, 141, 90, 85, 126, 80.2),
    (4, 139, 89, 84, 124, 80.0), (4, 143, 92, 87, 129, 80.8),
    (4, 137, 88, 83, 122, 79.5), (4, 140, 90, 85, 125, 80.0),
    (4, 138, 89, 84, 124, 79.7), (4, 136, 88, 83, 121, 79.3),
    
    # Patient 5: Charlie Brown (Borderline, improving)
    (5, 125, 83, 76, 100, 72.0), (5, 124, 82, 75, 99, 71.8),
    (5, 123, 82, 75, 98, 71.5), (5, 122, 81, 74, 97, 71.3),
    (5, 121, 80, 74, 96, 71.0), (5, 120, 80, 73, 95, 70.8),
    (5, 119, 79, 73, 94, 70.5), (5, 118, 79, 72, 93, 70.3),
    (5, 117, 78, 72, 92, 70.0), (5, 116, 78, 71, 91, 69.8),
]

print("=" * 60)
print("Adding Health Records to Render Backend")
print("=" * 60)

count = 0
for record in all_records:
    user_id, bp_sys, bp_dia, hr, sugar, weight = record
    response = requests.post(f'{API_URL}/health-data', json={
        'user_id': user_id,
        'bp_systolic': bp_sys,
        'bp_diastolic': bp_dia,
        'heart_rate': hr,
        'blood_sugar': sugar,
        'weight': weight
    })
    if response.status_code == 200:
        count += 1
        print(f'✅ Patient {user_id}: BP={bp_sys}/{bp_dia}, HR={hr}, Sugar={sugar}')
    else:
        print(f'❌ Failed for patient {user_id}: {response.status_code}')

print("\n" + "=" * 60)
print(f'✅ Successfully added {count} health records!')
print(f'📊 Each patient now has 10 days of health data')
print("=" * 60)

# Summary by patient
print("\n📈 Summary by patient:")
for patient_id in range(1, 6):
    response = requests.get(f'{API_URL}/health-data/user/{patient_id}')
    if response.status_code == 200:
        records = response.json()
        print(f'   Patient {patient_id}: {len(records)} health records')
    else:
        print(f'   Patient {patient_id}: Failed to fetch')
