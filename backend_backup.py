import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_service import ai_service

# Initialize FastAPI app
app = FastAPI(title="Health Reminder Tracker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_PATH = "health_tracker.db"

# ============ DATABASE INITIALIZATION ============
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Medications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            dosage TEXT,
            time_of_day TEXT,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Medication logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medication_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('taken', 'missed')),
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medication_id) REFERENCES medications (id)
        )
    ''')
    
    # Vaccinations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            due_date DATE,
            completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Health data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bp_systolic INTEGER,
            bp_diastolic INTEGER,
            heart_rate INTEGER,
            blood_sugar INTEGER,
            weight REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Notification settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            browser_notifications BOOLEAN DEFAULT 1,
            email_notifications BOOLEAN DEFAULT 0,
            sms_notifications BOOLEAN DEFAULT 0,
            reminder_frequency TEXT DEFAULT 'on_time',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Notification logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'sent',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Medication stock table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medication_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            stock_quantity INTEGER DEFAULT 30,
            low_stock_threshold INTEGER DEFAULT 5,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medication_id) REFERENCES medications (id)
        )
    ''')
    
    # Health alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            alert_level TEXT CHECK(alert_level IN ('info', 'warning', 'danger')),
            message TEXT NOT NULL,
            acknowledged BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Caregiver notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caregiver_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caregiver_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            read_status BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (caregiver_id) REFERENCES users (id),
            FOREIGN KEY (patient_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("? Database initialized with all tables")

# Initialize database on startup
init_db()

# ============ PYDANTIC MODELS ============
class User(BaseModel):
    name: str
    email: str

class Medication(BaseModel):
    user_id: int
    name: str
    dosage: str
    time_of_day: str
    active: bool = True

class Vaccination(BaseModel):
    user_id: int
    name: str
    due_date: str

class HealthData(BaseModel):
    user_id: int
    bp_systolic: int
    bp_diastolic: int
    heart_rate: int
    blood_sugar: int
    weight: float

class NotificationSettings(BaseModel):
    user_id: int
    browser_notifications: bool = True
    email_notifications: bool = False
    sms_notifications: bool = False
    reminder_frequency: str = "on_time"

class HealthAlert(BaseModel):
    user_id: int
    alert_type: str
    alert_level: str
    message: str

# ============ BASIC ENDPOINTS ============
@app.get("/health")
def health():
    return {"status": "healthy", "phase": 5, "project": "HealthReminderTracker"}

@app.get("/users")
def get_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in cursor.fetchall()]
    conn.close()
    return users

@app.post("/users")
def create_user(user: User):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                      (user.name, user.email))
        conn.commit()
        user_id = cursor.lastrowid
        
        # Create default notification settings for user
        cursor.execute("INSERT INTO notification_settings (user_id) VALUES (?)", (user_id,))
        conn.commit()
        
        conn.close()
        return {"id": user_id, "name": user.name, "email": user.email}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")

# ============ MEDICATION ENDPOINTS ============
@app.get("/medications/user/{user_id}")
def get_medications(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, dosage, time_of_day, active 
        FROM medications 
        WHERE user_id = ?
    """, (user_id,))
    meds = [{"id": row[0], "name": row[1], "dosage": row[2], 
             "time_of_day": row[3], "active": row[4]} for row in cursor.fetchall()]
    conn.close()
    return meds

@app.post("/medications")
def add_medication(med: Medication):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medications (user_id, name, dosage, time_of_day, active) 
        VALUES (?, ?, ?, ?, ?)
    """, (med.user_id, med.name, med.dosage, med.time_of_day, med.active))
    conn.commit()
    med_id = cursor.lastrowid
    
    # Initialize medication stock
    cursor.execute("""
        INSERT INTO medication_stock (medication_id, stock_quantity) 
        VALUES (?, ?)
    """, (med_id, 30))
    conn.commit()
    conn.close()
    return {"id": med_id, "message": "Medication added"}

@app.post("/medications/{med_id}/log")
def log_medication(med_id: int, status: str):
    if status not in ['taken', 'missed']:
        raise HTTPException(status_code=400, detail="Invalid status")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medication_logs (medication_id, status) 
        VALUES (?, ?)
    """, (med_id, status))
    conn.commit()
    conn.close()
    return {"message": f"Medication marked as {status}"}

# ============ VACCINATION ENDPOINTS ============
@app.get("/vaccinations/user/{user_id}")
def get_vaccinations(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, due_date, completed 
        FROM vaccinations 
        WHERE user_id = ?
    """, (user_id,))
    vax = [{"id": row[0], "name": row[1], "due_date": row[2], 
            "completed": row[3]} for row in cursor.fetchall()]
    conn.close()
    return vax

@app.post("/vaccinations")
def add_vaccination(vax: Vaccination):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vaccinations (user_id, name, due_date) 
        VALUES (?, ?, ?)
    """, (vax.user_id, vax.name, vax.due_date))
    conn.commit()
    vax_id = cursor.lastrowid
    conn.close()
    return {"id": vax_id, "message": "Vaccination added"}

@app.put("/vaccinations/{vax_id}/complete")
def complete_vaccination(vax_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE vaccinations SET completed = 1 WHERE id = ?", (vax_id,))
    conn.commit()
    conn.close()
    return {"message": "Vaccination marked as completed"}

# ============ HEALTH DATA ENDPOINTS ============
@app.post("/health-data")
def save_health_data(data: HealthData):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO health_data (user_id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data.user_id, data.bp_systolic, data.bp_diastolic, 
          data.heart_rate, data.blood_sugar, data.weight))
    conn.commit()
    data_id = cursor.lastrowid
    conn.close()
    
    # Check for health alerts after saving
    check_and_create_alerts(data.user_id, data)
    
    return {"id": data_id, "message": "Health data saved"}

@app.get("/health-data/user/{user_id}")
def get_health_data(user_id: int, limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight, recorded_at
        FROM health_data
        WHERE user_id = ?
        ORDER BY recorded_at DESC
        LIMIT ?
    """, (user_id, limit))
    data = [{"id": row[0], "bp_systolic": row[1], "bp_diastolic": row[2],
             "heart_rate": row[3], "blood_sugar": row[4], "weight": row[5],
             "recorded_at": row[6]} for row in cursor.fetchall()]
    conn.close()
    return data

# ============ NOTIFICATION ENDPOINTS ============
@app.get("/api/notifications/settings/{user_id}")
def get_notification_settings(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT browser_notifications, email_notifications, sms_notifications, reminder_frequency 
        FROM notification_settings WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "browser_notifications": bool(row[0]),
            "email_notifications": bool(row[1]),
            "sms_notifications": bool(row[2]),
            "reminder_frequency": row[3]
        }
    else:
        # Create default settings
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notification_settings (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return {
            "browser_notifications": True,
            "email_notifications": False,
            "sms_notifications": False,
            "reminder_frequency": "on_time"
        }

@app.post("/api/notifications/settings")
def update_notification_settings(settings: NotificationSettings):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notification_settings 
        SET browser_notifications = ?, email_notifications = ?, 
            sms_notifications = ?, reminder_frequency = ?
        WHERE user_id = ?
    """, (settings.browser_notifications, settings.email_notifications, 
          settings.sms_notifications, settings.reminder_frequency, settings.user_id))
    conn.commit()
    conn.close()
    return {"message": "Settings updated"}

@app.get("/api/notifications/medication-reminders/{user_id}")
def get_due_medications(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        current_hour = datetime.now().hour
        
        # Determine time of day
        if 5 <= current_hour < 12:
            time_of_day = 'morning'
        elif 12 <= current_hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= current_hour < 22:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        
        cursor.execute("""
            SELECT m.id, m.name, m.dosage, m.time_of_day, COALESCE(ms.stock_quantity, 30) as stock
            FROM medications m
            LEFT JOIN medication_stock ms ON m.id = ms.medication_id
            WHERE m.user_id = ? AND m.active = 1 AND m.time_of_day = ?
        """, (user_id, time_of_day))
        
        medications = [{"id": row[0], "name": row[1], "dosage": row[2], 
                        "time": row[3], "stock": row[4]} for row in cursor.fetchall()]
        conn.close()
        return {"medications": medications, "time_of_day": time_of_day}
    except Exception as e:
        print(f"Error in get_due_medications: {e}")
        return {"medications": [], "time_of_day": "unknown", "error": str(e)}

@app.get("/api/notifications/vaccination-due/{user_id}")
def get_due_vaccinations(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        cursor.execute("""
            SELECT id, name, due_date, completed 
            FROM vaccinations 
            WHERE user_id = ? AND completed = 0 
            AND due_date BETWEEN ? AND ?
        """, (user_id, today.isoformat(), next_week.isoformat()))
        
        vaccinations = [{"id": row[0], "name": row[1], "due_date": row[2], 
                         "completed": bool(row[3])} for row in cursor.fetchall()]
        conn.close()
        return {"vaccinations": vaccinations}
    except Exception as e:
        print(f"Error in get_due_vaccinations: {e}")
        return {"vaccinations": [], "error": str(e)}

@app.get("/api/notifications/alerts/{user_id}")
def get_user_alerts(user_id: int, unread_only: bool = False):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if unread_only:
            cursor.execute("""
                SELECT id, alert_type, alert_level, message, acknowledged, created_at
                FROM health_alerts
                WHERE user_id = ? AND acknowledged = 0
                ORDER BY created_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT id, alert_type, alert_level, message, acknowledged, created_at
                FROM health_alerts
                WHERE user_id = ?
                ORDER BY created_at DESC LIMIT 50
            """, (user_id,))
        
        alerts = [{"id": row[0], "type": row[1], "level": row[2], 
                   "message": row[3], "acknowledged": bool(row[4]), 
                   "created_at": row[5]} for row in cursor.fetchall()]
        conn.close()
        return alerts
    except Exception as e:
        print(f"Error in get_user_alerts: {e}")
        return []

@app.post("/api/notifications/health-alert")
def create_health_alert(alert: HealthAlert):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO health_alerts (user_id, alert_type, alert_level, message)
            VALUES (?, ?, ?, ?)
        """, (alert.user_id, alert.alert_type, alert.alert_level, alert.message))
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        
        # Also log to caregiver notifications if needed
        if alert.alert_level in ['warning', 'danger']:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO caregiver_notifications (caregiver_id, patient_id, alert_type, message)
                SELECT id, ?, ?, ? FROM users WHERE id != ?
            """, (alert.user_id, alert.alert_type, alert.message, alert.user_id))
            conn.commit()
            conn.close()
        
        return {"id": alert_id, "message": "Health alert created"}
    except Exception as e:
        print(f"Error in create_health_alert: {e}")
        return {"error": str(e)}

@app.put("/api/notifications/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE health_alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return {"message": "Alert acknowledged"}

@app.post("/api/notifications/medication-stock/{medication_id}")
def update_medication_stock(medication_id: int, stock: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO medication_stock (medication_id, stock_quantity, last_updated)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (medication_id, stock))
    conn.commit()
    conn.close()
    
    # Check for low stock alert
    if stock <= 5:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name FROM medications WHERE id = ?", (medication_id,))
        result = cursor.fetchone()
        if result:
            user_id, med_name = result
            alert_message = f"Low stock alert: {med_name} has only {stock} doses remaining"
            cursor.execute("""
                INSERT INTO health_alerts (user_id, alert_type, alert_level, message)
                VALUES (?, 'Low Stock', 'warning', ?)
            """, (user_id, alert_message))
            conn.commit()
        conn.close()
    
    return {"message": "Stock updated"}

@app.post("/api/notifications/log")
def log_notification(data: dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notification_logs (user_id, type, message, status)
            VALUES (?, ?, ?, ?)
        """, (data['user_id'], data['type'], data['message'], data.get('status', 'sent')))
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return {"id": log_id, "message": "Notification logged"}
    except Exception as e:
        print(f"Error in log_notification: {e}")
        return {"error": str(e)}

@app.get("/api/notifications/caregiver/{caregiver_id}")
def get_caregiver_notifications(caregiver_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cn.id, cn.patient_id, u.name as patient_name, 
               cn.alert_type, cn.message, cn.read_status, cn.created_at
        FROM caregiver_notifications cn
        JOIN users u ON cn.patient_id = u.id
        WHERE cn.caregiver_id = ?
        ORDER BY cn.created_at DESC LIMIT 50
    """, (caregiver_id,))
    
    notifications = [{"id": row[0], "patient_id": row[1], "patient_name": row[2],
                      "alert_type": row[3], "message": row[4], "read_status": bool(row[5]),
                      "created_at": row[6]} for row in cursor.fetchall()]
    conn.close()
    return notifications

@app.put("/api/notifications/caregiver/{notification_id}/read")
def mark_notification_read(notification_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE caregiver_notifications SET read_status = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()
    return {"message": "Notification marked as read"}

# ============ HELPER FUNCTIONS ============
def check_and_create_alerts(user_id: int, health_data: HealthData):
    """Check health data and create alerts if values are abnormal"""
    alerts = []
    
    # Check Blood Pressure
    if health_data.bp_systolic > 140 or health_data.bp_diastolic > 90:
        alert_msg = f"High Blood Pressure: {health_data.bp_systolic}/{health_data.bp_diastolic} mmHg"
        create_health_alert_internal(user_id, 'Blood Pressure', 'warning', alert_msg)
        alerts.append(alert_msg)
    elif health_data.bp_systolic < 90 or health_data.bp_diastolic < 60:
        alert_msg = f"Low Blood Pressure: {health_data.bp_systolic}/{health_data.bp_diastolic} mmHg"
        create_health_alert_internal(user_id, 'Blood Pressure', 'warning', alert_msg)
        alerts.append(alert_msg)
    
    # Check Heart Rate
    if health_data.heart_rate > 100:
        alert_msg = f"High Heart Rate: {health_data.heart_rate} BPM"
        create_health_alert_internal(user_id, 'Heart Rate', 'warning', alert_msg)
        alerts.append(alert_msg)
    elif health_data.heart_rate < 60:
        alert_msg = f"Low Heart Rate: {health_data.heart_rate} BPM"
        create_health_alert_internal(user_id, 'Heart Rate', 'warning', alert_msg)
        alerts.append(alert_msg)
    
    # Check Blood Sugar
    if health_data.blood_sugar > 140:
        alert_msg = f"High Blood Sugar: {health_data.blood_sugar} mg/dL"
        create_health_alert_internal(user_id, 'Blood Sugar', 'danger', alert_msg)
        alerts.append(alert_msg)
    elif health_data.blood_sugar < 70:
        alert_msg = f"Low Blood Sugar: {health_data.blood_sugar} mg/dL"
        create_health_alert_internal(user_id, 'Blood Sugar', 'danger', alert_msg)
        alerts.append(alert_msg)
    
    return alerts

def create_health_alert_internal(user_id: int, alert_type: str, level: str, message: str):
    """Internal function to create health alerts"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO health_alerts (user_id, alert_type, alert_level, message)
            VALUES (?, ?, ?, ?)
        """, (user_id, alert_type, level, message))
        conn.commit()
        
        # Also notify caregivers for warning/danger alerts
        if level in ['warning', 'danger']:
            cursor.execute("""
                INSERT INTO caregiver_notifications (caregiver_id, patient_id, alert_type, message)
                SELECT id, ?, ?, ? FROM users WHERE id != ?
            """, (user_id, alert_type, message, user_id))
            conn.commit()
        
        conn.close()
    except Exception as e:
        print(f"Error creating internal alert: {e}")

# ============ AI ENDPOINTS ============
@app.post("/api/ai/chat")
async def ai_chat(request: dict):
    result = ai_service.get_health_advice(request.get('query', ''), request.get('health_data'))
    return result

@app.post("/api/ai/health-risk")
async def predict_health_risk(request: dict):
    result = ai_service.predict_health_risk(request.get('health_data', {}))
    return result

@app.get("/api/ai/status")
async def ai_status():
    return {
        'gemini_available': ai_service.gemini_key is not None,
        'provider': ai_service.provider,
        'status': 'active' if ai_service.gemini_key else 'fallback'
    }

# ============ HEALTH TIPS ============
@app.get("/health-tips")
def get_health_tips():
    tips = [
        "Check your blood sugar regularly and take medicines on time",
        "Walk at least 30 minutes a day, 5 days a week",
        "Drink enough water and include fruits/vegetables in every meal",
        "Take medication at the same time each day for better adherence",
        "Get 7-8 hours of sleep for better immunity",
        "Regular exercise helps manage chronic conditions"
    ]
    return tips

# ============ MAIN ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

print("? Backend server ready with full notification system!")

from twilio_service import send_sos_alert

@app.post("/sos")
def sos_alert():
    result = send_sos_alert()
    return result
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io
from fastapi.responses import StreamingResponse

@app.get("/export-pdf/{user_id}")
async def export_pdf(user_id: int):
    # Get user info
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {"error": "User not found"}
    
    user_name, user_email = user
    
    # Get health data
    cursor.execute("""
        SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight, recorded_at 
        FROM health_data 
        WHERE user_id = ? 
        ORDER BY recorded_at DESC LIMIT 10
    """, (user_id,))
    health_records = cursor.fetchall()
    
    # Get medications
    cursor.execute("""
        SELECT name, dosage, time_of_day, active 
        FROM medications 
        WHERE user_id = ?
    """, (user_id,))
    medications = cursor.fetchall()
    
    # Get vaccinations
    cursor.execute("""
        SELECT name, due_date, completed 
        FROM vaccinations 
        WHERE user_id = ?
    """, (user_id,))
    vaccinations = cursor.fetchall()
    
    # Get alerts
    cursor.execute("""
        SELECT alert_type, alert_level, message, created_at 
        FROM health_alerts 
        WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 5
    """, (user_id,))
    alerts = cursor.fetchall()
    
    conn.close()
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2c3e50'))
    story.append(Paragraph("Medical Health Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # User Info
    story.append(Paragraph(f"<b>Patient:</b> {user_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Email:</b> {user_email}", styles['Normal']))
    story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Health Data Section
    if health_records:
        story.append(Paragraph("<b>Recent Health Data</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        data_table = [["Date", "BP", "HR", "Sugar", "Weight"]]
        for record in health_records[:5]:
            data_table.append([
                record[5][:10] if record[5] else "N/A",
                f"{record[0]}/{record[1]}",
                str(record[2]),
                str(record[3]),
                str(record[4])
            ])
        
        table = Table(data_table, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
    
    # Medications Section
    if medications:
        story.append(Paragraph("<b>Current Medications</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        med_table = [["Medication", "Dosage", "Time", "Status"]]
        for med in medications:
            med_table.append([med[0], med[1], med[2], "Active" if med[3] else "Inactive"])
        med_table_obj = Table(med_table, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        med_table_obj.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(med_table_obj)
        story.append(Spacer(1, 0.3*inch))
    
    # Vaccinations Section
    if vaccinations:
        story.append(Paragraph("<b>Vaccinations</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        vax_table = [["Vaccine", "Due Date", "Status"]]
        for vax in vaccinations:
            status = "Completed" if vax[2] else "Pending"
            vax_table.append([vax[0], vax[1], status])
        vax_table_obj = Table(vax_table, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        vax_table_obj.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(vax_table_obj)
        story.append(Spacer(1, 0.3*inch))
    
    # Alerts Section
    if alerts:
        story.append(Paragraph("<b>Recent Alerts</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        for alert in alerts:
            alert_color = '#e74c3c' if alert[1] == 'danger' else '#f39c12' if alert[1] == 'warning' else '#3498db'
            alert_style = ParagraphStyle('Alert', parent=styles['Normal'], textColor=colors.HexColor(alert_color))
            story.append(Paragraph(f"<b>{alert[0]}</b> - {alert[2]}", alert_style))
            story.append(Paragraph(f"<i>{alert[3][:10]}</i>", styles['Italic']))
            story.append(Spacer(1, 0.1*inch))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<i>This report is generated automatically by Medical Health Reminder Tracker. Please consult a healthcare provider for medical advice.</i>", styles['Italic']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=health_report_{user_name}_{datetime.now().strftime('%Y%m%d')}.pdf"})
async def get_ai_health_tips(request: dict):
    """Generate personalized health tips based on patient's health data"""
    health_data = request.get('health_data', {})
    user_id = request.get('user_id')
    user_name = request.get('user_name', 'Patient')
    
    # Get user's health data from database if user_id provided
    if user_id:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight 
            FROM health_data 
            WHERE user_id = ? 
            ORDER BY recorded_at DESC LIMIT 1
        """, (user_id,))
        latest = cursor.fetchone()
        if latest:
            health_data = {
                'bp_systolic': latest[0],
                'bp_diastolic': latest[1],
                'heart_rate': latest[2],
                'blood_sugar': latest[3],
                'weight': latest[4]
            }
        conn.close()
    
    # Build personalized prompt
    bp_sys = health_data.get('bp_systolic', 120)
    bp_dia = health_data.get('bp_diastolic', 80)
    hr = health_data.get('heart_rate', 75)
    sugar = health_data.get('blood_sugar', 100)
    weight = health_data.get('weight', 70)
    
    # Identify health conditions
    conditions = []
    if bp_sys > 140 or bp_dia > 90:
        conditions.append("High Blood Pressure")
    elif bp_sys < 90 or bp_dia < 60:
        conditions.append("Low Blood Pressure")
    
    if hr > 100:
        conditions.append("High Heart Rate")
    elif hr < 60:
        conditions.append("Low Heart Rate")
    
    if sugar > 140:
        conditions.append("High Blood Sugar")
    elif sugar < 70:
        conditions.append("Low Blood Sugar")
    
    if weight > 90:
        conditions.append("Overweight/Obesity")
    
    prompt = f"""You are a caring, professional health advisor. Based on the patient's health data below, provide 5 personalized, actionable health tips.

Patient: {user_name}
Health Data:
- Blood Pressure: {bp_sys}/{bp_dia} mmHg
- Heart Rate: {hr} BPM
- Blood Sugar: {sugar} mg/dL
- Weight: {weight} kg

Detected Conditions: {', '.join(conditions) if conditions else 'Generally healthy'}

Provide 5 SPECIFIC, PERSONALIZED tips that address their conditions. Each tip should be:
1. Actionable (they can do it today)
2. Specific to their numbers
3. Friendly and encouraging

Format as JSON array of strings.

Example format: ["Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5"]"""

    try:
        if ai_service.gemini_key and GEMINI_AVAILABLE:
            response = ai_service.model.generate_content(prompt)
            import json
            tips = json.loads(response.text)
        else:
            # Smart fallback based on conditions
            tips = []
            if "High Blood Pressure" in conditions:
                tips.append(f"?? Your BP is {bp_sys}/{bp_dia}. Reduce salt intake - aim for less than 1500mg daily.")
                tips.append("?? Walk for 30 minutes daily to help lower your blood pressure naturally.")
            if "High Blood Sugar" in conditions:
                tips.append(f"?? Your blood sugar is {sugar} mg/dL. Avoid sugary drinks and refined carbs.")
                tips.append("?? Eat protein and fiber with every meal to stabilize blood sugar.")
            if "High Heart Rate" in conditions:
                tips.append(f"?? Your heart rate is {hr} BPM. Practice deep breathing: inhale 4 sec, hold 4, exhale 6.")
            if "Overweight/Obesity" in conditions:
                tips.append(f"?? Your weight is {weight} kg. Start with small changes - walk 10 mins after each meal.")
            if not conditions:
                tips = [
                    "? Your health numbers look good! Maintain with regular checkups.",
                    "?? Eat a rainbow of vegetables daily for optimal nutrition.",
                    "?? Drink 8 glasses of water to stay hydrated.",
                    "?? Get 7-8 hours of quality sleep for recovery.",
                    "?? Take 5-minute stress breaks throughout your day."
                ]
            while len(tips) < 5:
                tips.append("?? Stay consistent with your health routine - small daily actions add up!")
        
        return {"tips": tips[:5], "conditions": conditions}
    except Exception as e:
        return {"tips": [
            "?? Monitor your blood pressure regularly",
            "?? Eat a balanced diet rich in vegetables",
            "?? Stay active with daily walks",
            "?? Drink plenty of water",
            "?? Get adequate sleep each night"
        ], "conditions": conditions}
@app.post("/api/ai/health-tips")
async def get_ai_health_tips(request: dict):
    """Generate personalized health tips based on patient's health data"""
    from ai_service import ai_service
    
    health_data = request.get('health_data', {})
    user_id = request.get('user_id')
    user_name = request.get('user_name', 'Patient')
    
    # Get user's latest health data from database if user_id provided
    if user_id:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight 
            FROM health_data 
            WHERE user_id = ? 
            ORDER BY recorded_at DESC LIMIT 1
        """, (user_id,))
        latest = cursor.fetchone()
        if latest:
            health_data = {
                'bp_systolic': latest[0],
                'bp_diastolic': latest[1],
                'heart_rate': latest[2],
                'blood_sugar': latest[3],
                'weight': latest[4]
            }
        conn.close()
    
    # Get values with defaults
    bp_sys = health_data.get('bp_systolic', 120)
    bp_dia = health_data.get('bp_diastolic', 80)
    hr = health_data.get('heart_rate', 75)
    sugar = health_data.get('blood_sugar', 100)
    weight = health_data.get('weight', 70)
    
    # Identify health conditions
    conditions = []
    if bp_sys > 140 or bp_dia > 90:
        conditions.append("High Blood Pressure")
    elif bp_sys < 90 or bp_dia < 60:
        conditions.append("Low Blood Pressure")
    
    if hr > 100:
        conditions.append("High Heart Rate")
    elif hr < 60:
        conditions.append("Low Heart Rate")
    
    if sugar > 140:
        conditions.append("High Blood Sugar")
    elif sugar < 70:
        conditions.append("Low Blood Sugar")
    
    if weight > 90:
        conditions.append("Overweight")
    
    # Generate smart tips based on conditions
    tips = []
    
    if "High Blood Pressure" in conditions:
        tips.append(f"🔴 Your BP is {bp_sys}/{bp_dia}. Reduce salt intake - aim for less than 1500mg daily.")
        tips.append("🚶 Walk for 30 minutes daily to help lower your blood pressure naturally.")
        tips.append("🥗 Eat more potassium-rich foods like bananas, spinach, and sweet potatoes.")
    elif "Low Blood Pressure" in conditions:
        tips.append(f"📉 Your BP is {bp_sys}/{bp_dia}. Stay hydrated and increase salt slightly if advised.")
        tips.append("🪑 Stand up slowly to avoid dizziness from low blood pressure.")
    
    if "High Blood Sugar" in conditions:
        tips.append(f"🩸 Your blood sugar is {sugar} mg/dL. Avoid sugary drinks and refined carbs.")
        tips.append("🥗 Eat protein and fiber with every meal to stabilize blood sugar.")
        tips.append("🚶 Take a 15-minute walk after meals to help lower blood sugar.")
    elif "Low Blood Sugar" in conditions:
        tips.append(f"📉 Your blood sugar is {sugar} mg/dL. Keep glucose tablets or candy handy.")
        tips.append("🍎 Eat small, frequent meals to maintain stable blood sugar.")
    
    if "High Heart Rate" in conditions:
        tips.append(f"💓 Your heart rate is {hr} BPM. Practice deep breathing: inhale 4 sec, hold 4, exhale 6.")
        tips.append("☕ Reduce caffeine and alcohol intake to help lower heart rate.")
    elif "Low Heart Rate" in conditions:
        tips.append(f"💓 Your heart rate is {hr} BPM. If you feel dizzy, consult your doctor.")
    
    if "Overweight" in conditions:
        tips.append(f"⚖️ Your weight is {weight} kg. Start with small changes - walk 10 mins after each meal.")
        tips.append("🥗 Replace one meal a day with a healthy salad or vegetable dish.")
    
    # Add general tips if not enough condition-specific tips
    general_tips = [
        "💧 Drink 8-10 glasses of water daily for overall health.",
        "😴 Get 7-8 hours of quality sleep for better recovery.",
        "🧘 Take 5-minute stress breaks throughout your day.",
        "📊 Monitor your health numbers weekly to track progress.",
        "💪 Small consistent actions create big health improvements."
    ]
    
    # Combine tips
    while len(tips) < 5:
        for tip in general_tips:
            if tip not in tips and len(tips) < 5:
                tips.append(tip)
    
    # If no conditions detected, provide maintenance tips
    if not conditions:
        tips = [
            "✅ Your health numbers look good! Maintain with regular checkups.",
            "🥗 Eat a rainbow of vegetables daily for optimal nutrition.",
            "💧 Drink 8 glasses of water to stay hydrated.",
            "😴 Get 7-8 hours of quality sleep for recovery.",
            "🧘 Take 5-minute stress breaks throughout your day."
        ]
    
    return {"tips": tips[:5], "conditions": conditions}
