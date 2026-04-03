
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

print("✅ Notification endpoints added to backend.py")
