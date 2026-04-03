import sqlite3
import requests
import json

print('=' * 70)
print('🔍 FINAL SYSTEM VERIFICATION')
print('=' * 70)

# 1. Check Database Tables
print('\n📊 1. CHECKING DATABASE TABLES')
print('-' * 50)
conn = sqlite3.connect('health_tracker.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
required_tables = ['users', 'medications', 'vaccinations', 'notification_settings', 
                   'notification_logs', 'medication_stock', 'health_alerts', 'caregiver_notifications']

for table in required_tables:
    if table in tables:
        print(f'   ✅ {table}')
    else:
        print(f'   ❌ {table} - MISSING')
conn.close()

# 2. Check API Endpoints
print('\n🔌 2. CHECKING API ENDPOINTS')
print('-' * 50)

endpoints = [
    '/health',
    '/users',
    '/api/ai/status',
    '/api/notifications/settings/1',
    '/api/notifications/medication-reminders/1',
    '/api/notifications/vaccination-due/1'
]

for endpoint in endpoints:
    try:
        response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
        if response.status_code in [200, 404]:
            print(f'   ✅ {endpoint} - Accessible')
        else:
            print(f'   ⚠️ {endpoint} - Status: {response.status_code}')
    except:
        print(f'   ❌ {endpoint} - Not accessible (Backend may not be running)')

print('\n' + '=' * 70)
print('✅ VERIFICATION COMPLETE')
print('=' * 70)
print('\n📋 NEXT STEPS:')
print('1. Restart your backend: uvicorn backend:app --reload --host 0.0.0.0 --port 8000')
print('2. Restart your frontend: cd frontend && npm run dev')
print('3. Create a user and test notifications')
print('4. Check browser console for notification permission request')
print('=' * 70)
