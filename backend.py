import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from ai_service import ai_service

app = FastAPI(title="Health Reminder Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "health_tracker.db"

# ============ INIT DATABASE ============
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS medications (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, name TEXT NOT NULL, dosage TEXT, time_of_day TEXT, active BOOLEAN DEFAULT 1, FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS medication_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, medication_id INTEGER NOT NULL, status TEXT, logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (medication_id) REFERENCES medications (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS vaccinations (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, name TEXT NOT NULL, due_date DATE, completed BOOLEAN DEFAULT 0, FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS health_data (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, bp_systolic INTEGER, bp_diastolic INTEGER, heart_rate INTEGER, blood_sugar INTEGER, weight REAL, recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notification_settings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, browser_notifications BOOLEAN DEFAULT 1, email_notifications BOOLEAN DEFAULT 0, sms_notifications BOOLEAN DEFAULT 0, reminder_frequency TEXT DEFAULT 'on_time', FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notification_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, type TEXT NOT NULL, message TEXT NOT NULL, sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT 'sent', FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS medication_stock (id INTEGER PRIMARY KEY AUTOINCREMENT, medication_id INTEGER NOT NULL, stock_quantity INTEGER DEFAULT 30, low_stock_threshold INTEGER DEFAULT 5, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (medication_id) REFERENCES medications (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS health_alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, alert_type TEXT NOT NULL, alert_level TEXT CHECK(alert_level IN ('info', 'warning', 'danger')), message TEXT NOT NULL, acknowledged BOOLEAN DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS caregiver_notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, caregiver_id INTEGER NOT NULL, patient_id INTEGER NOT NULL, alert_type TEXT NOT NULL, message TEXT NOT NULL, read_status BOOLEAN DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (caregiver_id) REFERENCES users (id), FOREIGN KEY (patient_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()
    print("? Database initialized")

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
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user.name, user.email))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO notification_settings (user_id) VALUES (?)", (user_id,))
        conn.commit()
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
    cursor.execute("INSERT INTO medications (user_id, name, dosage, time_of_day, active) VALUES (?, ?, ?, ?, ?)", (med.user_id, med.name, med.dosage, med.time_of_day, med.active))
    conn.commit()
    med_id = cursor.lastrowid
    cursor.execute("INSERT INTO medication_stock (medication_id, stock_quantity) VALUES (?, ?)", (med_id, 30))
    conn.commit()
    conn.close()
    return {"id": med_id, "message": "Medication added"}

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
    cursor.execute("INSERT INTO vaccinations (user_id, name, due_date) VALUES (?, ?, ?)", (vax.user_id, vax.name, vax.due_date))
    conn.commit()
    vax_id = cursor.lastrowid
    conn.close()
    return {"id": vax_id, "message": "Vaccination added"}

@app.post("/health-data")
def save_health_data(data: HealthData):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO health_data (user_id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight) VALUES (?, ?, ?, ?, ?, ?)", (data.user_id, data.bp_systolic, data.bp_diastolic, data.heart_rate, data.blood_sugar, data.weight))
    conn.commit()
    conn.close()
    return {"message": "Health data saved"}

@app.get("/health-data/user/{user_id}")
def get_health_data(user_id: int, limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight, recorded_at FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT ?", (user_id, limit))
    data = [{"id": row[0], "bp_systolic": row[1], "bp_diastolic": row[2], "heart_rate": row[3], "blood_sugar": row[4], "weight": row[5], "recorded_at": row[6]} for row in cursor.fetchall()]
    conn.close()
    return data

@app.get("/health-tips")
def get_health_tips():
    return ["Check your blood sugar regularly", "Walk 30 minutes daily", "Drink enough water", "Take medication on time", "Get 7-8 hours of sleep", "Regular exercise helps"]

# ============ AI-POWERED PERSONALIZED HEALTH TIPS ============
@app.post("/api/ai/health-tips")
async def get_ai_health_tips(request: dict):
    """Generate personalized health tips based on patient's health data"""
    
    health_data = request.get('health_data', {})
    user_id = request.get('user_id')
    user_name = request.get('user_name', 'Patient')
    
    # Get user's latest health data from database
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
    if hr > 100:
        conditions.append("High Heart Rate")
    if hr < 60:
        conditions.append("Low Heart Rate")
    if sugar > 140:
        conditions.append("High Blood Sugar")
    if sugar < 70:
        conditions.append("Low Blood Sugar")
    if weight > 90:
        conditions.append("Overweight")
    
    if not conditions:
        conditions = ["Generally Healthy"]
    
    # Generate personalized tips based on conditions
    tips = []
    
    for condition in conditions:
        if condition == "High Blood Pressure":
            tips.append(f"?? Your BP is {bp_sys}/{bp_dia}. Reduce salt intake - aim for less than 1500mg daily.")
            tips.append("?? Walk for 30 minutes daily to help lower your blood pressure naturally.")
            tips.append("?? Eat more potassium-rich foods like bananas, spinach, and sweet potatoes.")
        elif condition == "High Blood Sugar":
            tips.append(f"?? Your blood sugar is {sugar} mg/dL. Avoid sugary drinks and refined carbs.")
            tips.append("?? Eat protein and fiber with every meal to stabilize blood sugar.")
            tips.append("?? Take a 15-minute walk after meals to help lower blood sugar.")
        elif condition == "High Heart Rate":
            tips.append(f"?? Your heart rate is {hr} BPM. Practice deep breathing: inhale 4 sec, hold 4, exhale 6.")
            tips.append("? Reduce caffeine and alcohol intake to help lower heart rate.")
        elif condition == "Low Heart Rate":
            tips.append(f"?? Your heart rate is {hr} BPM. If you feel dizzy, consult your doctor.")
        elif condition == "Low Blood Sugar":
            tips.append(f"?? Your blood sugar is {sugar} mg/dL. Keep glucose tablets or candy handy.")
            tips.append("?? Eat small, frequent meals to maintain stable blood sugar.")
        elif condition == "Overweight":
            tips.append(f"?? Your weight is {weight} kg. Start with small changes - walk 10 mins after each meal.")
            tips.append("?? Replace one meal a day with a healthy salad or vegetable dish.")
        elif condition == "Generally Healthy":
            tips.append("? Your health numbers look good! Maintain with regular checkups.")
            tips.append("?? Eat a rainbow of vegetables daily for optimal nutrition.")
            tips.append("?? Drink 8 glasses of water to stay hydrated.")
            tips.append("?? Get 7-8 hours of quality sleep for recovery.")
            tips.append("?? Take 5-minute stress breaks throughout your day.")
    
    # Remove duplicates and limit to 5 tips
    unique_tips = []
    for tip in tips:
        if tip not in unique_tips:
            unique_tips.append(tip)
    
    return {"tips": unique_tips[:5], "conditions": conditions}

# ============ AI CHAT ============
@app.post("/api/ai/chat")
async def ai_chat(request: dict):
    query = request.get('query', '')
    session_id = request.get('session_id', 'default')
    result = ai_service.get_health_advice(query, None, session_id)
    return result

@app.post("/api/ai/health-risk")
async def predict_health_risk(request: dict):
    result = ai_service.predict_health_risk(request.get('health_data', {}))
    return result

@app.get("/api/ai/status")
async def ai_status():
    return {'gemini_available': ai_service.gemini_key is not None, 'provider': ai_service.provider, 'status': 'active' if ai_service.gemini_key else 'fallback'}

# ============ SOS ENDPOINT ============
from twilio_service import send_sos_alert

@app.post("/sos")
def sos_alert():
    result = send_sos_alert()
    return result

# ============ NOTIFICATION ENDPOINTS ============
@app.get("/api/notifications/alerts/{user_id}")
def get_user_alerts(user_id: int, unread_only: bool = False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if unread_only:
        cursor.execute("SELECT id, alert_type, alert_level, message, acknowledged, created_at FROM health_alerts WHERE user_id = ? AND acknowledged = 0 ORDER BY created_at DESC", (user_id,))
    else:
        cursor.execute("SELECT id, alert_type, alert_level, message, acknowledged, created_at FROM health_alerts WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", (user_id,))
    alerts = [{"id": row[0], "type": row[1], "level": row[2], "message": row[3], "acknowledged": bool(row[4]), "created_at": row[5]} for row in cursor.fetchall()]
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

# ============ PDF EXPORT ============
@app.get("/export-pdf/{user_id}")
async def export_pdf(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {"error": "User not found"}
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"Health Report for {user[0]}", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=health_report_{user[0]}.pdf"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# ============ EMAIL REPORT ENDPOINT ============
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

@app.post("/api/send-email-report/{user_id}")
async def send_email_report(user_id: int, recipient_email: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get user data
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {"error": "User not found"}
    
    # Get health data
    cursor.execute("""
        SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight, recorded_at 
        FROM health_data 
        WHERE user_id = ? 
        ORDER BY recorded_at DESC LIMIT 5
    """, (user_id,))
    health_records = cursor.fetchall()
    conn.close()
    
    # Create email HTML
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; }}
            .record {{ border-bottom: 1px solid #ddd; padding: 10px; }}
            .footer {{ text-align: center; padding: 20px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>?? Health Report</h2>
                <p>Patient: {user[0]}</p>
            </div>
            <h3>Recent Health Records</h3>
    """
    
    for record in health_records:
        html += f"""
            <div class="record">
                <strong>{record[5]}</strong><br>
                BP: {record[0]}/{record[1]} | HR: {record[2]} | Sugar: {record[3]} | Weight: {record[4]} kg
            </div>
        """
    
    html += f"""
            <div class="footer">
                <p>Generated by Medical Health Reminder Tracker</p>
                <p>Please consult a doctor for medical advice</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # For demo, just return the HTML (actual email sending requires SMTP config)
    return {"message": "Report generated", "html": html, "recipient": recipient_email or user[1]}

print("? Email report endpoint added")
# ============ EMAIL SERVICE ============
import os
from dotenv import load_dotenv

load_dotenv()

def send_health_report_email(recipient_email, patient_name, health_data, risk_level, tips):
    """Send actual email with health report"""
    try:
        sender_email = os.getenv('EMAIL_SENDER')
        sender_password = os.getenv('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            print("Email not configured. Set EMAIL_SENDER and EMAIL_PASSWORD in .env")
            return False
        
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; border-radius: 10px; }}
                .content {{ padding: 20px; }}
                .metric {{ background: #f3f4f6; padding: 10px; margin: 10px 0; border-radius: 8px; }}
                .risk-high {{ color: #dc2626; font-weight: bold; }}
                .risk-low {{ color: #10b981; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #6b7280; }}
                button {{ background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>?? Medical Health Report</h2>
                    <p>Patient: {patient_name}</p>
                </div>
                <div class="content">
                    <h3>?? Health Summary</h3>
                    <div class="metric">
                        <strong>Blood Pressure:</strong> {health_data.get('bp_systolic', 'N/A')}/{health_data.get('bp_diastolic', 'N/A')} mmHg
                    </div>
                    <div class="metric">
                        <strong>Heart Rate:</strong> {health_data.get('heart_rate', 'N/A')} BPM
                    </div>
                    <div class="metric">
                        <strong>Blood Sugar:</strong> {health_data.get('blood_sugar', 'N/A')} mg/dL
                    </div>
                    <div class="metric">
                        <strong>Weight:</strong> {health_data.get('weight', 'N/A')} kg
                    </div>
                    
                    <h3>?? Risk Assessment</h3>
                    <div class="metric">
                        <strong>Risk Level:</strong> <span class="risk-{risk_level.lower()}">{risk_level}</span>
                    </div>
                    
                    <h3>?? Health Tips</h3>
                    <div class="metric">
                        <ul>
                            {''.join([f'<li>{tip}</li>' for tip in tips[:5]])}
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://localhost:5173" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px;">View Dashboard</a>
                    </div>
                </div>
                <div class="footer">
                    <p>This report was generated automatically by Medical Health Reminder Tracker.</p>
                    <p>Please consult a healthcare provider for medical advice.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        # Email disabled
        yag.send(
            to=recipient_email,
            subject=f"Health Report for {patient_name} - {datetime.now().strftime('%Y-%m-%d')}",
            contents=html_content
        )
        yag.close()
        
        print(f"? Email sent to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"? Email failed: {e}")
        return False

# Update the email report endpoint
@app.post("/api/send-email-report/{user_id}")
async def send_email_report_endpoint(user_id: int, recipient_email: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get user data
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {"error": "User not found"}
    
    patient_name, user_email = user
    to_email = recipient_email or user_email
    
    # Get latest health data
    cursor.execute("""
        SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight 
        FROM health_data 
        WHERE user_id = ? 
        ORDER BY recorded_at DESC LIMIT 1
    """, (user_id,))
    latest = cursor.fetchone()
    
    health_data = {}
    risk_level = "LOW"
    tips = ["Monitor your health regularly", "Stay hydrated", "Exercise daily", "Eat balanced diet", "Get good sleep"]
    
    if latest:
        health_data = {
            'bp_systolic': latest[0],
            'bp_diastolic': latest[1],
            'heart_rate': latest[2],
            'blood_sugar': latest[3],
            'weight': latest[4]
        }
        
        # Calculate risk level
        risks = 0
        if latest[0] > 140 or latest[1] > 90: risks += 1
        if latest[2] > 100: risks += 1
        if latest[3] > 140: risks += 1
        risk_level = "HIGH" if risks > 1 else "MODERATE" if risks == 1 else "LOW"
        
        # Get AI tips
        try:
            tips_response = await get_ai_health_tips({'user_id': user_id, 'user_name': patient_name, 'health_data': health_data})
            tips = tips_response.get('tips', tips)
        except:
            pass
    
    conn.close()
    
    # Send actual email
    success = send_health_report_email(to_email, patient_name, health_data, risk_level, tips)
    
    if success:
        return {"message": "Email sent successfully", "recipient": to_email}
    else:
        return {"message": "Email configuration missing. Check .env file", "recipient": to_email, "html": "Email would be sent here"}
# ============ DEMO EMAIL SIMULATION (No actual email needed) ============
@app.post("/api/send-email-report/{user_id}")
async def send_email_report_endpoint(user_id: int, recipient_email: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get user data
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {"error": "User not found"}
    
    patient_name, user_email = user
    to_email = recipient_email or user_email
    
    # Get latest health data
    cursor.execute("""
        SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight 
        FROM health_data 
        WHERE user_id = ? 
        ORDER BY recorded_at DESC LIMIT 1
    """, (user_id,))
    latest = cursor.fetchone()
    
    health_data = {}
    risk_level = "LOW"
    tips = ["Monitor your health regularly", "Stay hydrated", "Exercise daily", "Eat balanced diet", "Get good sleep"]
    
    if latest:
        health_data = {
            'bp_systolic': latest[0],
            'bp_diastolic': latest[1],
            'heart_rate': latest[2],
            'blood_sugar': latest[3],
            'weight': latest[4]
        }
        
        # Calculate risk level
        risks = 0
        if latest[0] > 140 or latest[1] > 90: risks += 1
        if latest[2] > 100: risks += 1
        if latest[3] > 140: risks += 1
        risk_level = "HIGH" if risks > 1 else "MODERATE" if risks == 1 else "LOW"
        
        # Get AI tips
        try:
            tips_response = await get_ai_health_tips({'user_id': user_id, 'user_name': patient_name, 'health_data': health_data})
            tips = tips_response.get('tips', tips)
        except:
            pass
    
    conn.close()
    
    # Generate email HTML preview
    html_preview = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; border-radius: 10px; }}
            .content {{ padding: 20px; }}
            .metric {{ background: #f3f4f6; padding: 10px; margin: 10px 0; border-radius: 8px; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #6b7280; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>?? Medical Health Report</h2>
                <p>Patient: {patient_name}</p>
            </div>
            <div class="content">
                <h3>?? Health Summary</h3>
                <div class="metric"><strong>Blood Pressure:</strong> {health_data.get('bp_systolic', 'N/A')}/{health_data.get('bp_diastolic', 'N/A')} mmHg</div>
                <div class="metric"><strong>Heart Rate:</strong> {health_data.get('heart_rate', 'N/A')} BPM</div>
                <div class="metric"><strong>Blood Sugar:</strong> {health_data.get('blood_sugar', 'N/A')} mg/dL</div>
                <div class="metric"><strong>Weight:</strong> {health_data.get('weight', 'N/A')} kg</div>
                <h3>?? Risk Level: {risk_level}</h3>
                <h3>?? Health Tips</h3>
                {''.join([f'<div class="metric">? {tip}</div>' for tip in tips[:5]])}
            </div>
            <div class="footer">
                <p>Generated by Medical Health Reminder Tracker</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return {
        "message": "?? Report Generated (Demo Mode - Email not actually sent)",
        "recipient": to_email,
        "html_preview": html_preview,
        "demo_mode": True
    }
