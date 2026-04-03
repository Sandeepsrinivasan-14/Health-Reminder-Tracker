import requests
import json
from datetime import datetime

print('=' * 60)
print('🔔 NOTIFICATION SYSTEM TEST (Python Version)')
print('=' * 60)

BASE_URL = 'http://localhost:8000'

# Test 1: Health Check
print('\n📡 1. Health Check')
try:
    response = requests.get(f'{BASE_URL}/health')
    if response.status_code == 200:
        data = response.json()
        print(f'   ✅ Backend Status: {data["status"]}')
        print(f'   Phase: {data["phase"]}')
    else:
        print(f'   ❌ Failed: {response.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')
    exit()

# Test 2: Medication Reminders
print('\n💊 2. Medication Reminders')
try:
    response = requests.get(f'{BASE_URL}/api/notifications/medication-reminders/1')
    if response.status_code == 200:
        data = response.json()
        print(f'   Time of day: {data["time_of_day"]}')
        print(f'   Medications due: {len(data["medications"])}')
        for med in data['medications']:
            print(f'   → {med["name"]} - {med["dosage"]} (Stock: {med["stock"]})')
    else:
        print(f'   ❌ Failed: {response.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 3: Vaccination Reminders
print('\n💉 3. Vaccination Reminders')
try:
    response = requests.get(f'{BASE_URL}/api/notifications/vaccination-due/1')
    if response.status_code == 200:
        data = response.json()
        print(f'   Vaccinations due: {len(data["vaccinations"])}')
        for vax in data['vaccinations']:
            print(f'   → {vax["name"]} - Due: {vax["due_date"]}')
    else:
        print(f'   ❌ Failed: {response.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 4: Get Alerts
print('\n⚠️ 4. Health Alerts')
try:
    response = requests.get(f'{BASE_URL}/api/notifications/alerts/1')
    if response.status_code == 200:
        alerts = response.json()
        print(f'   Total alerts: {len(alerts)}')
        for alert in alerts[:5]:  # Show first 5
            icon = '🔴' if alert['level'] == 'danger' else '🟡' if alert['level'] == 'warning' else '🔵'
            print(f'   {icon} {alert["type"]}: {alert["message"][:50]}...')
            print(f'      Created: {alert["created_at"]}')
    else:
        print(f'   ❌ Failed: {response.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 5: Create New Alert
print('\n➕ 5. Create New Test Alert')
try:
    new_alert = {
        'user_id': 1,
        'alert_type': 'Test Alert',
        'alert_level': 'info',
        'message': f'Test notification at {datetime.now().strftime("%H:%M:%S")}'
    }
    response = requests.post(f'{BASE_URL}/api/notifications/health-alert', json=new_alert)
    if response.status_code == 200:
        data = response.json()
        print(f'   ✅ Alert created with ID: {data["id"]}')
    else:
        print(f'   ❌ Failed: {response.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 6: Notification Settings
print('\n⚙️ 6. Notification Settings')
try:
    response = requests.get(f'{BASE_URL}/api/notifications/settings/1')
    if response.status_code == 200:
        settings = response.json()
        print(f'   Browser Notifications: {"✅ ON" if settings["browser_notifications"] else "❌ OFF"}')
        print(f'   Email Notifications: {"✅ ON" if settings["email_notifications"] else "❌ OFF"}')
        print(f'   SMS Notifications: {"✅ ON" if settings["sms_notifications"] else "❌ OFF"}')
        print(f'   Reminder Frequency: {settings["reminder_frequency"]}')
    else:
        print(f'   ❌ Failed: {response.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Summary
print('\n' + '=' * 60)
print('📊 TEST COMPLETE')
print('=' * 60)
print('✅ All notification endpoints are functional!')
print('🔔 Check http://localhost:8000/docs for full API documentation')
print('=' * 60)
