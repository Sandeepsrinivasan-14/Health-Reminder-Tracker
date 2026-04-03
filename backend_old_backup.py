from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import os
from ai_service import ai_service
from notification_service import notification_service

app = FastAPI(title="Health Reminder Tracker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "health_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medication_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('taken', 'missed')),
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medication_id) REFERENCES medications (id)
        )
    ''')
    
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
    
    conn.commit()
    conn.close()

init_db()

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

# AI Models
class AIQuery(BaseModel):
    query: str
    health_data: Optional[Dict[str, Any]] = None

class HealthRiskRequest(BaseModel):
    health_data: Dict[str, Any]

class TrendAnalysisRequest(BaseModel):
    health_history: List[Dict[str, Any]]

class MedicationSuggestRequest(BaseModel):
    medications: List[Dict[str, Any]]

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
        conn.close()
        return {"id": user_id, "name": user.name, "email": user.email}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")

@app.get("/medications/user/{user_id}")
def get_medications(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, dosage, time_of_day, active FROM medications WHERE user_id = ?", (user_id,))
    meds = [{"id": row[0], "name": row[1], "dosage": row[2], "time_of_day": row[3], "active": row[4]} for row in cursor.fetchall()]
    conn.close()
    return meds

@app.post("/medications")
def add_medication(med: Medication):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medications (user_id, name, dosage, time_of_day, active) VALUES (?, ?, ?, ?, ?)",
                  (med.user_id, med.name, med.dosage, med.time_of_day, med.active))
    conn.commit()
    med_id = cursor.lastrowid
    conn.close()
    return {"id": med_id, "message": "Medication added"}

@app.post("/medications/{med_id}/log")
def log_medication(med_id: int, status: str):
    if status not in ['taken', 'missed']:
        raise HTTPException(status_code=400, detail="Invalid status")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medication_logs (medication_id, status) VALUES (?, ?)", (med_id, status))
    conn.commit()
    conn.close()
    return {"message": f"Medication marked as {status}"}

@app.get("/vaccinations/user/{user_id}")
def get_vaccinations(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, due_date, completed FROM vaccinations WHERE user_id = ?", (user_id,))
    vax = [{"id": row[0], "name": row[1], "due_date": row[2], "completed": row[3]} for row in cursor.fetchall()]
    conn.close()
    return vax

@app.post("/vaccinations")
def add_vaccination(vax: Vaccination):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vaccinations (user_id, name, due_date) VALUES (?, ?, ?)",
                  (vax.user_id, vax.name, vax.due_date))
    conn.commit()
    vax_id = cursor.lastrowid
    conn.close()
    return {"id": vax_id, "message": "Vaccination added"}

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

# AI Endpoints
@app.post("/api/ai/chat")
async def ai_chat(request: AIQuery):
    result = ai_service.get_health_advice(request.query, request.health_data)
    return result

@app.post("/api/ai/health-risk")
async def predict_health_risk(request: HealthRiskRequest):
    result = ai_service.predict_health_risk(request.health_data)
    return result

@app.post("/api/ai/trend-analysis")
async def analyze_trends(request: TrendAnalysisRequest):
    result = ai_service.analyze_health_trends(request.health_history)
    return result

@app.post("/api/ai/medication-suggest")
async def suggest_medications(request: MedicationSuggestRequest):
    result = ai_service.suggest_medication_reminder(request.medications)
    return result

@app.get("/api/ai/status")
async def ai_status():
    return {
        'gemini_available': ai_service.gemini_key is not None,
        'provider': ai_service.provider,
        'status': 'active' if ai_service.gemini_key else 'fallback'
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============ NOTIFICATION ENDPOINTS ============

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

@app.get("/api/notifications/settings/{user_id}")
def get_notification_settings(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT browser_notifications, email_notifications, sms_notifications, reminder_frequency FROM notification_settings WHERE user_id = ?", (user_id,))
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
        SET browser_notifications = ?, email_notifications = ?, sms_notifications = ?, reminder_frequency = ?
        WHERE user_id = ?
    """, (settings.browser_notifications, settings.email_notifications, 
          settings.sms_notifications, settings.reminder_frequency, settings.user_id))
    conn.commit()
    conn.close()
    return {"message": "Settings updated"}

@app.get("/api/notifications/medication-reminders/{user_id}")
def get_due_medications(user_id: int):
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

@app.get("/api/notifications/vaccination-due/{user_id}")
def get_due_vaccinations(user_id: int):
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

@app.post("/api/notifications/log")
def log_notification(data: dict):
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

@app.post("/api/notifications/health-alert")
def create_health_alert(alert: HealthAlert):
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

@app.get("/api/notifications/alerts/{user_id}")
def get_user_alerts(user_id: int, unread_only: bool = False):
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
        cursor.execute("SELECT user_id FROM medications WHERE id = ?", (medication_id,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            cursor.execute("SELECT name FROM medications WHERE id = ?", (medication_id,))
            med_name = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO health_alerts (user_id, alert_type, alert_level, message)
                VALUES (?, 'Low Stock', 'warning', ?)
            """, (user_id, f"Low stock alert: {med_name} has only {stock} doses remaining"))
            conn.commit()
        conn.close()
    
    return {"message": "Stock updated"}

@app.get("/api/notifications/caregiver/{caregiver_id}")
def get_caregiver_notifications(caregiver_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cn.id, cn.patient_id, u.name as patient_name, cn.alert_type, cn.message, cn.read_status, cn.created_at
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

print("? Notification endpoints added to backend.py")
# Add these imports at the top of backend.py if not already present
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import sqlite3
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_service import ai_service

# Make sure your app is defined
app = FastAPI(title="Health Reminder Tracker API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "health_tracker.db"

# Fix the get_due_medications function - it was missing datetime import
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

# Fix the get_due_vaccinations function
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

# Fix the get_user_alerts function
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

# Fix the health-alert endpoint
@app.post("/api/notifications/health-alert")
def create_health_alert(alert: dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO health_alerts (user_id, alert_type, alert_level, message)
            VALUES (?, ?, ?, ?)
        """, (alert['user_id'], alert['alert_type'], alert['alert_level'], alert['message']))
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        
        # Also log to caregiver notifications if needed
        if alert['alert_level'] in ['warning', 'danger']:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO caregiver_notifications (caregiver_id, patient_id, alert_type, message)
                SELECT id, ?, ?, ? FROM users WHERE id != ?
            """, (alert['user_id'], alert['alert_type'], alert['message'], alert['user_id']))
            conn.commit()
            conn.close()
        
        return {"id": alert_id, "message": "Health alert created"}
    except Exception as e:
        print(f"Error in create_health_alert: {e}")
        return {"error": str(e)}

# Fix the notification log endpoint
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

print("? Fixed notification endpoints added!")
