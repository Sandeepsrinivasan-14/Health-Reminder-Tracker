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

print("✅ Fixed notification endpoints added!")
