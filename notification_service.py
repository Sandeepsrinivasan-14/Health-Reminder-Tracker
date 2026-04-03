import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import json

class NotificationService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        # Configuration (Replace with your actual credentials)
        self.email_enabled = False
        self.sms_enabled = False
        self.push_enabled = False
        
        # Email config (Gmail example)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv('ALERT_EMAIL', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        
        # Twilio SMS config
        self.twilio_sid = os.getenv('TWILIO_SID', '')
        self.twilio_token = os.getenv('TWILIO_TOKEN', '')
        self.twilio_phone = os.getenv('TWILIO_PHONE', '')
        
        # Push notification config (Firebase)
        self.fcm_server_key = os.getenv('FCM_SERVER_KEY', '')
        
        # Caregiver database
        self.db_path = "health_tracker.db"
        
        # Start background jobs
        self.start_scheduled_jobs()
    
    def send_sos_alert(self, patient_name, patient_id, caregiver_phone=None, caregiver_email=None):
        """Send SOS alerts via all channels"""
        results = {
            'sms': False,
            'email': False,
            'push': False
        }
        
        # Get caregiver info from database
        if not caregiver_phone or not caregiver_email:
            caregiver_info = self.get_caregiver_info(patient_id)
            caregiver_phone = caregiver_info.get('phone')
            caregiver_email = caregiver_info.get('email')
        
        message = f"?? SOS ALERT: {patient_name} needs immediate medical attention! Time: {datetime.now().strftime('%H:%M:%S')}"
        
        # Send SMS via Twilio
        if caregiver_phone and self.twilio_sid:
            results['sms'] = self.send_sms(caregiver_phone, message)
        
        # Send Email
        if caregiver_email and self.email_user:
            results['email'] = self.send_email(caregiver_email, "URGENT: SOS Alert", message)
        
        # Send Push Notification via Firebase
        if self.fcm_server_key:
            results['push'] = self.send_push_notification(patient_id, message)
        
        # Log the alert
        self.log_alert(patient_id, 'SOS', results)
        
        return results
    
    def send_medication_reminder(self, user_id, medication_name, dosage, time_of_day):
        """Send medication reminder at scheduled time"""
        caregiver = self.get_caregiver_info(user_id)
        message = f"?? Medication Reminder: Time to take {medication_name} ({dosage})"
        
        if caregiver.get('phone'):
            self.send_sms(caregiver['phone'], message)
        if caregiver.get('email'):
            self.send_email(caregiver['email'], "Medication Reminder", message)
        
        # Also send browser notification via WebSocket
        self.send_websocket_notification(user_id, 'medication', {
            'title': 'Medication Reminder',
            'body': message,
            'medication': medication_name
        })
    
    def send_low_stock_alert(self, user_id, medication_name, stock_left):
        """Alert when medication stock is low"""
        caregiver = self.get_caregiver_info(user_id)
        message = f"?? Low Stock Alert: {medication_name} has only {stock_left} doses left! Please refill."
        
        if caregiver.get('phone'):
            self.send_sms(caregiver['phone'], message)
        if caregiver.get('email'):
            self.send_email(caregiver['email'], "Low Stock Alert", message)
        
        self.send_websocket_notification(user_id, 'stock_alert', {
            'title': 'Low Stock Alert',
            'body': message,
            'medication': medication_name,
            'stock_left': stock_left
        })
    
    def send_weekly_health_report(self, user_id):
        """Generate and send weekly health summary"""
        health_data = self.get_health_data_last_week(user_id)
        if not health_data:
            return
        
        # Generate report
        report = self.generate_health_report(user_id, health_data)
        
        # Send to caregiver
        caregiver = self.get_caregiver_info(user_id)
        if caregiver.get('email'):
            self.send_email(
                caregiver['email'],
                f"Weekly Health Report - {datetime.now().strftime('%Y-%m-%d')}",
                report
            )
    
    def send_caregiver_alert(self, user_id, alert_type, message):
        """Send real-time alerts to caregiver"""
        caregiver = self.get_caregiver_info(user_id)
        
        if caregiver.get('phone'):
            self.send_sms(caregiver['phone'], f"[{alert_type}] {message}")
        if caregiver.get('email'):
            self.send_email(caregiver['email'], f"Alert: {alert_type}", message)
        
        self.send_websocket_notification(user_id, 'caregiver_alert', {
            'type': alert_type,
            'message': message
        })
    
    def send_sms(self, phone_number, message):
        """Send SMS via Twilio"""
        try:
            if not self.twilio_sid:
                print("Twilio not configured")
                return False
            
            from twilio.rest import Client
            client = Client(self.twilio_sid, self.twilio_token)
            message = client.messages.create(
                body=message[:160],  # SMS limit
                from_=self.twilio_phone,
                to=phone_number
            )
            return True
        except Exception as e:
            print(f"SMS failed: {e}")
            return False
    
    def send_email(self, to_email, subject, body):
        """Send email via SMTP"""
        try:
            if not self.email_user:
                print("Email not configured")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email failed: {e}")
            return False
    
    def send_push_notification(self, user_id, message):
        """Send push notification via Firebase Cloud Messaging"""
        try:
            if not self.fcm_server_key:
                return False
            
            # Get FCM token for user
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT fcm_token FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row or not row[0]:
                return False
            
            fcm_token = row[0]
            
            # Send to Firebase
            headers = {
                'Authorization': f'key={self.fcm_server_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'to': fcm_token,
                'notification': {
                    'title': 'Health Alert',
                    'body': message
                }
            }
            
            response = requests.post(
                'https://fcm.googleapis.com/fcm/send',
                headers=headers,
                json=data
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Push notification failed: {e}")
            return False
    
    def send_websocket_notification(self, user_id, event_type, data):
        """Send real-time WebSocket notification"""
        try:
            # This would connect to your WebSocket server
            # For now, we'll store in database for polling
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event_type TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read BOOLEAN DEFAULT 0
                )
            ''')
            cursor.execute(
                "INSERT INTO notifications (user_id, event_type, data) VALUES (?, ?, ?)",
                (user_id, event_type, json.dumps(data))
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
            return False
    
    def get_caregiver_info(self, user_id):
        """Get caregiver contact info for a patient"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add caregiver table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS caregivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                name TEXT,
                phone TEXT,
                email TEXT,
                fcm_token TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute(
            "SELECT name, phone, email, fcm_token FROM caregivers WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {'name': row[0], 'phone': row[1], 'email': row[2], 'fcm_token': row[3]}
        return {'name': None, 'phone': None, 'email': None, 'fcm_token': None}
    
    def get_health_data_last_week(self, user_id):
        """Get health data from last 7 days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bp_systolic INTEGER,
                bp_diastolic INTEGER,
                heart_rate INTEGER,
                blood_sugar INTEGER,
                weight REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM health_records 
            WHERE user_id = ? AND date(recorded_at) >= ?
            ORDER BY recorded_at DESC
        ''', (user_id, week_ago))
        
        records = cursor.fetchall()
        conn.close()
        return records
    
    def generate_health_report(self, user_id, health_data):
        """Generate human-readable health report"""
        if not health_data:
            return "No health data available for this week."
        
        report = f"Weekly Health Report\n{'='*50}\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Calculate averages
        bp_sys_avg = sum(r[2] for r in health_data) / len(health_data)
        bp_dia_avg = sum(r[3] for r in health_data) / len(health_data)
        hr_avg = sum(r[4] for r in health_data) / len(health_data)
        sugar_avg = sum(r[5] for r in health_data) / len(health_data)
        weight_avg = sum(r[6] for r in health_data) / len(health_data)
        
        report += f"Average BP: {bp_sys_avg:.0f}/{bp_dia_avg:.0f} mmHg\n"
        report += f"Average Heart Rate: {hr_avg:.0f} BPM\n"
        report += f"Average Blood Sugar: {sugar_avg:.0f} mg/dL\n"
        report += f"Average Weight: {weight_avg:.1f} kg\n\n"
        
        # Health status
        report += "Health Status:\n"
        if bp_sys_avg > 140:
            report += "?? Blood Pressure is HIGH - Consult doctor\n"
        elif bp_sys_avg < 90:
            report += "?? Blood Pressure is LOW - Monitor closely\n"
        else:
            report += "? Blood Pressure is NORMAL\n"
        
        if hr_avg > 100:
            report += "?? Heart Rate is HIGH - May indicate stress or condition\n"
        elif hr_avg < 60:
            report += "?? Heart Rate is LOW - Monitor if symptomatic\n"
        else:
            report += "? Heart Rate is NORMAL\n"
        
        if sugar_avg > 140:
            report += "?? Blood Sugar is HIGH - Monitor diet\n"
        elif sugar_avg < 70:
            report += "?? Blood Sugar is LOW - Keep snacks handy\n"
        else:
            report += "? Blood Sugar is NORMAL\n"
        
        report += f"\nTotal records this week: {len(health_data)}"
        
        return report
    
    def log_alert(self, user_id, alert_type, results):
        """Log alert for auditing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                alert_type TEXT,
                results TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute(
            "INSERT INTO alert_logs (user_id, alert_type, results) VALUES (?, ?, ?)",
            (user_id, alert_type, json.dumps(results))
        )
        conn.commit()
        conn.close()
    
    def start_scheduled_jobs(self):
        """Start background jobs for reminders and reports"""
        # Schedule medication reminders (run every 15 minutes)
        self.scheduler.add_job(
            self.check_medication_reminders,
            'interval',
            minutes=15,
            id='medication_reminders'
        )
        
        # Schedule weekly health reports (every Monday at 9 AM)
        self.scheduler.add_job(
            self.send_weekly_reports,
            'cron',
            day_of_week='mon',
            hour=9,
            minute=0,
            id='weekly_reports'
        )
    
    def check_medication_reminders(self):
        """Check and send due medication reminders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now().strftime('%H:%M')
        current_hour = int(current_time.split(':')[0])
        
        # Map time of day to hour range
        time_map = {
            'morning': [6, 7, 8, 9, 10],
            'afternoon': [12, 13, 14],
            'evening': [17, 18, 19],
            'night': [21, 22, 23]
        }
        
        for time_slot, hours in time_map.items():
            if current_hour in hours:
                cursor.execute('''
                    SELECT m.user_id, m.name, m.dosage, u.name 
                    FROM medications m
                    JOIN users u ON m.user_id = u.id
                    WHERE m.time_of_day = ? AND m.active = 1
                ''', (time_slot,))
                
                reminders = cursor.fetchall()
                for reminder in reminders:
                    user_id, med_name, dosage, patient_name = reminder
                    self.send_medication_reminder(user_id, med_name, dosage, time_slot)
        
        conn.close()
    
    def send_weekly_reports(self):
        """Send weekly reports to all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM users")
        users = cursor.fetchall()
        
        for user_id, user_name in users:
            self.send_weekly_health_report(user_id)
        
        conn.close()

# Initialize notification service
notification_service = NotificationService()
