import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "health_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS health_data (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, bp_systolic INTEGER, bp_diastolic INTEGER, heart_rate INTEGER, blood_sugar INTEGER, weight REAL, recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notification_settings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, browser_notifications BOOLEAN DEFAULT 1)''')
    conn.commit()
    conn.close()
    print("Database initialized")

init_db()

class User(BaseModel):
    name: str
    email: str

class HealthData(BaseModel):
    user_id: int
    bp_systolic: int
    bp_diastolic: int
    heart_rate: int
    blood_sugar: int
    weight: float

class MedicineReminderRequest(BaseModel):
    user_id: int
    medicine_name: str
    dosage: str
    time_of_day: str
    reminder_time: str

@app.get("/health")
def health():
    return {"status": "healthy"}

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
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user.name, user.email))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.execute("INSERT INTO notification_settings (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return {"id": user_id, "name": user.name, "email": user.email}

@app.post("/health-data")
def save_health_data(data: HealthData):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO health_data (user_id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight) VALUES (?, ?, ?, ?, ?, ?)", (data.user_id, data.bp_systolic, data.bp_diastolic, data.heart_rate, data.blood_sugar, data.weight))
    conn.commit()
    conn.close()
    return {"message": "Health data saved"}

@app.get("/health-data/user/{user_id}")
def get_health_data(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight, recorded_at FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC", (user_id,))
    data = [{"id": row[0], "bp_systolic": row[1], "bp_diastolic": row[2], "heart_rate": row[3], "blood_sugar": row[4], "weight": row[5], "recorded_at": row[6]} for row in cursor.fetchall()]
    conn.close()
    return data

@app.get("/health-tips")
def get_health_tips():
    return ["Check BP regularly", "Exercise 30 mins daily", "Stay hydrated", "Get good sleep", "Take meds on time"]

@app.post("/api/ai/chat")
async def ai_chat(request: dict):
    query = request.get('query', '').lower()
    if 'bp' in query:
        return {"response": "Normal BP is 120/80 mmHg. Maintain with exercise and low salt.", "provider": "AI"}
    if 'sugar' in query:
        return {"response": "Normal blood sugar is 70-100 mg/dL fasting. Monitor regularly.", "provider": "AI"}
    return {"response": "I can help with BP, sugar, heart rate, medications. What would you like to know?", "provider": "AI"}

@app.post("/api/ai/health-risk")
async def predict_health_risk(request: dict):
    data = request.get('health_data', {})
    risks = []
    if data.get('bp_systolic', 120) > 140:
        risks.append("High BP")
    if data.get('blood_sugar', 100) > 140:
        risks.append("High Sugar")
    level = "HIGH" if len(risks) > 1 else "LOW"
    return {"risk_level": level, "risks": risks, "recommendations": ["Consult doctor", "Monitor regularly"]}

@app.get("/api/ai/status")
async def ai_status():
    return {"gemini_available": False, "status": "active"}

@app.post("/sos")
def sos_alert():
    try:
        from plyer import notification
        import winsound
        notification.notify(title="SOS ALERT!", message="Patient needs immediate medical attention!", timeout=10)
        for i in range(3):
            winsound.Beep(1000, 500)
        print("Desktop SOS Alert Displayed!")
        return {"status": "sent", "method": "desktop_notification"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@app.get("/api/notifications/alerts/{user_id}")
def get_alerts(user_id: int):
    return []

@app.put("/api/notifications/alerts/{alert_id}/acknowledge")
def acknowledge(alert_id: int):
    return {"message": "ok"}

@app.get("/export-pdf/{user_id}")
async def export_pdf(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight, recorded_at FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 20", (user_id,))
    records = cursor.fetchall()
    conn.close()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"Health Report - {user[0] if user else 'Patient'}", styles['Title']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    if records:
        story.append(Paragraph("Health Records", styles['Heading2']))
        table_data = [["Date", "BP Sys", "BP Dia", "HR", "Sugar", "Weight"]]
        for r in records[:10]:
            date = r[5][:10] if r[5] else "N/A"
            table_data.append([date, str(r[0]), str(r[1]), str(r[2]), str(r[3]), str(r[4])])
        table = Table(table_data)
        table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
        story.append(table)
    else:
        story.append(Paragraph("No health records found", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=health_report_{user[0] if user else 'patient'}.pdf"})

# ============ MEDICINE REMINDER ENDPOINTS ============
from medicine_reminder import add_medicine_reminder, get_reminders_for_user, test_reminder

@app.post("/api/medicine-reminder/add")
def api_add_reminder(req: MedicineReminderRequest):
    result = add_medicine_reminder(req.user_id, req.medicine_name, req.dosage, req.time_of_day, req.reminder_time)
    return {"status": "added", "reminder": result}

@app.get("/api/medicine-reminder/list/{user_id}")
def api_list_reminders(user_id: int):
    reminders = get_reminders_for_user(user_id)
    return {"reminders": reminders}

@app.post("/api/medicine-reminder/test/{user_id}")
def api_test_reminder(user_id: int):
    return test_reminder(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
