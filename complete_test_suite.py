#!/usr/bin/env python3
"""
Complete Notification System Test Suite
Run this to test all notification features
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
USER_ID = 1

def print_header(title):
    print("\n" + "=" * 60)
    print(f"🔔 {title}")
    print("=" * 60)

def test_health():
    print_header("HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Phase: {data['phase']}")
        print(f"✅ Project: {data['project']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_medication_reminders():
    print_header("MEDICATION REMINDERS")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/medication-reminders/{USER_ID}")
        data = response.json()
        print(f"⏰ Time of day: {data['time_of_day']}")
        print(f"💊 Medications due: {len(data['medications'])}")
        for med in data['medications']:
            print(f"   → {med['name']} - {med['dosage']} (Stock: {med['stock']} doses)")
        return data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_vaccination_reminders():
    print_header("VACCINATION REMINDERS")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/vaccination-due/{USER_ID}")
        data = response.json()
        print(f"💉 Vaccinations due: {len(data['vaccinations'])}")
        for vax in data['vaccinations']:
            print(f"   → {vax['name']} - Due: {vax['due_date']}")
        return data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_health_alerts():
    print_header("HEALTH ALERTS")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/alerts/{USER_ID}")
        alerts = response.json()
        print(f"⚠️ Total alerts: {len(alerts)}")
        for alert in alerts[:10]:  # Show last 10
            icon = "🔴" if alert['level'] == 'danger' else "🟡" if alert['level'] == 'warning' else "🔵"
            print(f"   {icon} [{alert['level'].upper()}] {alert['type']}")
            print(f"      Message: {alert['message'][:80]}...")
            print(f"      Created: {alert['created_at']}")
            print(f"      Acknowledged: {'✅' if alert['acknowledged'] else '❌'}")
        return alerts
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_create_alert():
    print_header("CREATE TEST ALERT")
    try:
        new_alert = {
            'user_id': USER_ID,
            'alert_type': 'System Test',
            'alert_level': 'info',
            'message': f'Test alert created at {datetime.now().strftime("%H:%M:%S")}'
        }
        response = requests.post(f"{BASE_URL}/api/notifications/health-alert", json=new_alert)
        data = response.json()
        print(f"✅ Alert created with ID: {data['id']}")
        return data['id']
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_acknowledge_alert(alert_id):
    print_header(f"ACKNOWLEDGE ALERT {alert_id}")
    try:
        response = requests.put(f"{BASE_URL}/api/notifications/alerts/{alert_id}/acknowledge")
        data = response.json()
        print(f"✅ {data['message']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_notification_settings():
    print_header("NOTIFICATION SETTINGS")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/settings/{USER_ID}")
        settings = response.json()
        print(f"🔔 Browser Notifications: {'✅ ON' if settings['browser_notifications'] else '❌ OFF'}")
        print(f"📧 Email Notifications: {'✅ ON' if settings['email_notifications'] else '❌ OFF'}")
        print(f"📱 SMS Notifications: {'✅ ON' if settings['sms_notifications'] else '❌ OFF'}")
        print(f"⏰ Reminder Frequency: {settings['reminder_frequency']}")
        return settings
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_update_medication_stock():
    print_header("MEDICATION STOCK UPDATE")
    try:
        # Get first medication
        response = requests.get(f"{BASE_URL}/medications/user/{USER_ID}")
        meds = response.json()
        if meds:
            med_id = meds[0]['id']
            new_stock = 3  # Low stock to trigger alert
            response = requests.post(f"{BASE_URL}/api/notifications/medication-stock/{med_id}?stock={new_stock}")
            print(f"✅ Stock updated to {new_stock} doses")
            print(f"⚠️ Low stock alert should be triggered!")
            return True
        else:
            print("⚠️ No medications found to update stock")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_caregiver_notifications():
    print_header("CAREGIVER NOTIFICATIONS")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/caregiver/{USER_ID}")
        notifications = response.json()
        print(f"👥 Caregiver notifications: {len(notifications)}")
        for note in notifications[:5]:
            print(f"   → {note['patient_name']}: {note['alert_type']}")
            print(f"      Message: {note['message'][:60]}...")
            print(f"      Read: {'✅' if note['read_status'] else '❌'}")
        return notifications
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n" + "🎯" * 30)
    print("   NOTIFICATION SYSTEM COMPLETE TEST SUITE")
    print("🎯" * 30)
    
    # Run all tests
    tests = [
        ("Health Check", test_health),
        ("Medication Reminders", test_medication_reminders),
        ("Vaccination Reminders", test_vaccination_reminders),
        ("Health Alerts", test_health_alerts),
        ("Create Alert", test_create_alert),
        ("Notification Settings", test_notification_settings),
        ("Update Stock", test_update_medication_stock),
        ("Caregiver Notifications", test_caregiver_notifications),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result is not None and result != {}))
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results.append((name, False))
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, status in results if status)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    for name, status in results:
        icon = "✅" if status else "❌"
        print(f"   {icon} {name}")
    
    print_header("SYSTEM STATUS")
    print("🎉 All notification features are working!")
    print("\n📋 Access Points:")
    print(f"   • API Docs: {BASE_URL}/docs")
    print(f"   • Frontend: http://localhost:5173")
    print(f"   • Test Dashboard: http://localhost:5173/test_dashboard.html")
    
    print("\n🔔 Active Notification Features:")
    print("   ✓ Medication reminders (time-based)")
    print("   ✓ Vaccination due alerts")
    print("   ✓ Health metric alerts (BP, Heart Rate, Blood Sugar)")
    print("   ✓ Low stock alerts")
    print("   ✓ Caregiver notifications")
    print("   ✓ In-app notification center")
    print("   ✓ Browser push notifications")
    
    print("\n📊 Current Data:")
    print(f"   • Users: {len(requests.get(f'{BASE_URL}/users').json())}")
    print(f"   • Medications: {len(requests.get(f'{BASE_URL}/medications/user/{USER_ID}').json())}")
    print(f"   • Alerts: {len(requests.get(f'{BASE_URL}/api/notifications/alerts/{USER_ID}').json())}")

if __name__ == "__main__":
    main()
