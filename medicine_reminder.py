import threading
import time
import winsound
from datetime import datetime
from plyer import notification

class MedicineReminder:
    def __init__(self):
        self.reminders = []
        self.running = False
        self.thread = None
    
    def add_reminder(self, user_id, medicine_name, dosage, time_of_day, reminder_time):
        reminder = {
            'user_id': user_id,
            'medicine_name': medicine_name,
            'dosage': dosage,
            'time_of_day': time_of_day,
            'reminder_time': reminder_time,
            'last_notified': None,
            'active': True
        }
        self.reminders.append(reminder)
        return reminder
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._check_reminders, daemon=True)
        self.thread.start()
        print("✅ Medicine Reminder Service Started")
    
    def stop(self):
        self.running = False
    
    def _check_reminders(self):
        while self.running:
            current_time = datetime.now().strftime("%H:%M")
            for reminder in self.reminders:
                if not reminder['active']:
                    continue
                if reminder['reminder_time'] == current_time:
                    if reminder['last_notified']:
                        last = datetime.strptime(reminder['last_notified'], "%Y-%m-%d %H:%M")
                        if (datetime.now() - last).seconds < 300:
                            continue
                    self._send_notification(reminder)
                    reminder['last_notified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            time.sleep(60)
    
    def _send_notification(self, reminder):
        title = f"💊 Medicine Reminder - {reminder['medicine_name']}"
        message = f"Time to take {reminder['dosage']} ({reminder['time_of_day']})"
        try:
            for i in range(3):
                winsound.Beep(1000, 500)
                time.sleep(0.2)
            notification.notify(title=title, message=message, timeout=10, app_name="Health Tracker")
            print(f"🔔 Reminder: {title} - {message}")
        except Exception as e:
            print(f"Error: {e}")

reminder_service = MedicineReminder()
reminder_service.start()

def add_medicine_reminder(user_id, medicine_name, dosage, time_of_day, reminder_time):
    return reminder_service.add_reminder(user_id, medicine_name, dosage, time_of_day, reminder_time)

def get_reminders_for_user(user_id):
    return [r for r in reminder_service.reminders if r['user_id'] == user_id and r['active']]

def test_reminder(user_id):
    test = {
        'user_id': user_id,
        'medicine_name': 'Test Medicine',
        'dosage': '500mg',
        'time_of_day': 'Now',
        'reminder_time': 'test'
    }
    reminder_service._send_notification(test)
    return {"status": "test sent"}
