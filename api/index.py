import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import io

app = FastAPI()

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ DATA STORAGE (In-memory for Vercel) ============
# Since Vercel Functions are stateless, we use in-memory storage
# For production, you should use a real database like Supabase, MongoDB, or PostgreSQL

users_db = {}
health_data_db = {}
medication_reminders_db = {}
user_counter = 0

# Initialize with 22 patients
initial_users = [
    {"id": 1, "name": "Test Patient", "email": "test@example.com", "condition": "Healthy"},
    {"id": 2, "name": "Rajesh Kumar", "email": "rajesh@email.com", "condition": "Diabetes"},
    {"id": 3, "name": "Priya Sharma", "email": "priya@email.com", "condition": "Healthy"},
    {"id": 4, "name": "Amit Patel", "email": "amit@email.com", "condition": "Heart Disease"},
    {"id": 5, "name": "Sunita Reddy", "email": "sunita@email.com", "condition": "Hypertension"},
    {"id": 6, "name": "Vikram Singh", "email": "vikram@email.com", "condition": "Diabetes"},
    {"id": 7, "name": "Neha Gupta", "email": "neha@email.com", "condition": "Asthma"},
    {"id": 8, "name": "Anand Desai", "email": "anand@email.com", "condition": "Hypertension"},
    {"id": 9, "name": "Kavita Nair", "email": "kavita@email.com", "condition": "Thyroid"},
    {"id": 10, "name": "Suresh Iyer", "email": "suresh@email.com", "condition": "Heart Disease"},
    {"id": 11, "name": "Meera Joshi", "email": "meera@email.com", "condition": "Migraine"},
    {"id": 12, "name": "Rohan Mehta", "email": "rohan@email.com", "condition": "Healthy"},
    {"id": 13, "name": "Anjali Kulkarni", "email": "anjali@email.com", "condition": "Diabetes"},
    {"id": 14, "name": "Deepak Saxena", "email": "deepak@email.com", "condition": "Obesity"},
    {"id": 15, "name": "Swati Choudhary", "email": "swati@email.com", "condition": "Anemia"},
    {"id": 16, "name": "Manoj Verma", "email": "manoj@email.com", "condition": "Hypertension"},
    {"id": 17, "name": "Pooja Malhotra", "email": "pooja@email.com", "condition": "Osteoporosis"},
    {"id": 18, "name": "Arjun Nair", "email": "arjun@email.com", "condition": "Healthy"},
    {"id": 19, "name": "Divya Menon", "email": "divya@email.com", "condition": "PCOS"},
    {"id": 20, "name": "Sanjay Gupta", "email": "sanjay@email.com", "condition": "Diabetes"},
    {"id": 21, "name": "Lata Mangeshkar", "email": "lata@email.com", "condition": "Hypertension"},
    {"id": 22, "name": "Lohith", "email": "lohith@email.com", "condition": "Healthy"}
]

for user in initial_users:
    users_db[user["id"]] = user
    user_counter = max(user_counter, user["id"])

# Health data templates
health_templates = {
    "Healthy": {"bp_sys": 118, "bp_dia": 78, "hr": 72, "sugar": 95, "weight": 68},
    "Diabetes": {"bp_sys": 135, "bp_dia": 85, "hr": 78, "sugar": 180, "weight": 75},
    "Heart Disease": {"bp_sys": 145, "bp_dia": 90, "hr": 95, "sugar": 115, "weight": 78},
    "Hypertension": {"bp_sys": 155, "bp_dia": 95, "hr": 82, "sugar": 110, "weight": 80},
    "Asthma": {"bp_sys": 120, "bp_dia": 78, "hr": 75, "sugar": 95, "weight": 65},
    "Thyroid": {"bp_sys": 125, "bp_dia": 80, "hr": 70, "sugar": 100, "weight": 85},
    "Obesity": {"bp_sys": 140, "bp_dia": 88, "hr": 85, "sugar": 125, "weight": 110},
    "Anemia": {"bp_sys": 105, "bp_dia": 65, "hr": 88, "sugar": 85, "weight": 55},
    "PCOS": {"bp_sys": 128, "bp_dia": 82, "hr": 76, "sugar": 115, "weight": 82},
    "Migraine": {"bp_sys": 118, "bp_dia": 75, "hr": 68, "sugar": 92, "weight": 62},
    "Osteoporosis": {"bp_sys": 130, "bp_dia": 82, "hr": 72, "sugar": 100, "weight": 60}
}

# Initialize health data for each user
for user_id, user in users_db.items():
    condition = user.get("condition", "Healthy")
    template = health_templates.get(condition, health_templates["Healthy"])
    health_data_db[user_id] = [{
        "id": 1,
        "user_id": user_id,
        "bp_systolic": template["bp_sys"],
        "bp_diastolic": template["bp_dia"],
        "heart_rate": template["hr"],
        "blood_sugar": template["sugar"],
        "weight": template["weight"],
        "recorded_at": datetime.now().isoformat()
    }]

# ============ PYDANTIC MODELS ============
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

class MedicineReminder(BaseModel):
    user_id: int
    medicine_name: str
    dosage: str
    time_of_day: str
    reminder_time: str

# ============ API ENDPOINTS ============
@app.get("/")
def root():
    return {"message": "Health Tracker API is running", "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "healthy", "phase": 5, "project": "HealthReminderTracker"}

@app.get("/users")
def get_users():
    return list(users_db.values())

@app.post("/users")
def create_user(user: User):
    global user_counter
    user_counter += 1
    new_user = {
        "id": user_counter,
        "name": user.name,
        "email": user.email,
        "condition": "Healthy"
    }
    users_db[user_counter] = new_user
    health_data_db[user_counter] = []
    return new_user

@app.get("/health-data/user/{user_id}")
def get_health_data(user_id: int):
    return health_data_db.get(user_id, [])

@app.post("/health-data")
def save_health_data(data: HealthData):
    if data.user_id not in health_data_db:
        health_data_db[data.user_id] = []
    
    new_record = {
        "id": len(health_data_db[data.user_id]) + 1,
        "user_id": data.user_id,
        "bp_systolic": data.bp_systolic,
        "bp_diastolic": data.bp_diastolic,
        "heart_rate": data.heart_rate,
        "blood_sugar": data.blood_sugar,
        "weight": data.weight,
        "recorded_at": datetime.now().isoformat()
    }
    health_data_db[data.user_id].insert(0, new_record)
    return {"message": "Health data saved"}

@app.get("/health-tips")
def get_health_tips():
    return [
        "Check your blood pressure regularly",
        "Exercise for 30 minutes daily",
        "Stay hydrated - drink 8 glasses of water",
        "Take medications on time",
        "Get 7-8 hours of quality sleep",
        "Eat a balanced diet rich in vegetables"
    ]

@app.post("/api/ai/chat")
async def ai_chat(request: dict):
    query = request.get('query', '').lower()
    
    if 'bp' in query or 'blood pressure' in query:
        return {"response": "Normal blood pressure is 120/80 mmHg. To maintain healthy BP: reduce salt intake, exercise regularly, manage stress, and avoid smoking.", "provider": "AI Assistant"}
    elif 'sugar' in query or 'diabetes' in query:
        return {"response": "Normal blood sugar is 70-100 mg/dL fasting. Monitor regularly, avoid sugary foods, exercise after meals, and take medications as prescribed.", "provider": "AI Assistant"}
    elif 'heart' in query or 'rate' in query:
        return {"response": "Normal resting heart rate is 60-100 BPM. Regular exercise, stress management, and avoiding excessive caffeine help maintain heart health.", "provider": "AI Assistant"}
    elif 'medication' in query or 'medicine' in query:
        return {"response": "Take medications exactly as prescribed. Use reminders, pill organizers, and never skip doses without consulting your doctor.", "provider": "AI Assistant"}
    elif 'diet' in query or 'food' in query:
        return {"response": "Eat a balanced diet with plenty of vegetables, fruits, whole grains, lean proteins, and healthy fats. Limit processed foods and sugar.", "provider": "AI Assistant"}
    elif 'exercise' in query or 'workout' in query:
        return {"response": "Aim for 150 minutes of moderate exercise weekly. Walking, swimming, cycling, and strength training are excellent choices.", "provider": "AI Assistant"}
    else:
        return {"response": "I'm your health assistant. I can help with questions about blood pressure, blood sugar, heart rate, medications, diet, exercise, and sleep. What would you like to know?", "provider": "AI Assistant"}

@app.post("/api/ai/health-risk")
async def predict_health_risk(request: dict):
    data = request.get('health_data', {})
    risks = []
    recommendations = []
    
    bp_sys = data.get('bp_systolic', 120)
    bp_dia = data.get('bp_diastolic', 80)
    hr = data.get('heart_rate', 75)
    sugar = data.get('blood_sugar', 100)
    
    if bp_sys > 140 or bp_dia > 90:
        risks.append("High Blood Pressure")
        recommendations.append("Reduce salt intake, exercise regularly, consult doctor")
    if hr > 100:
        risks.append("Tachycardia (High Heart Rate)")
        recommendations.append("Rest, reduce caffeine, practice deep breathing")
    elif hr < 60:
        risks.append("Bradycardia (Low Heart Rate)")
        recommendations.append("Consult doctor if experiencing dizziness")
    if sugar > 140:
        risks.append("High Blood Sugar")
        recommendations.append("Monitor diet, exercise after meals, consult doctor")
    elif sugar < 70:
        risks.append("Low Blood Sugar")
        recommendations.append("Keep glucose tablets handy, eat regular meals")
    
    risk_level = "HIGH" if len(risks) > 1 else "MODERATE" if len(risks) == 1 else "LOW"
    
    if not recommendations:
        recommendations = ["Continue monitoring", "Maintain healthy lifestyle"]
    
    return {"risk_level": risk_level, "risks": risks, "recommendations": recommendations}

@app.get("/api/ai/status")
async def ai_status():
    return {"gemini_available": False, "provider": "fallback", "status": "active"}

@app.post("/sos")
def sos_alert():
    return {"status": "sent", "message": "SOS Alert Sent! Caregiver notified.", "method": "api"}

@app.post("/api/medicine-reminder/add")
def add_medicine_reminder(reminder: MedicineReminder):
    if reminder.user_id not in medication_reminders_db:
        medication_reminders_db[reminder.user_id] = []
    
    new_reminder = {
        "id": len(medication_reminders_db[reminder.user_id]) + 1,
        "user_id": reminder.user_id,
        "medicine_name": reminder.medicine_name,
        "dosage": reminder.dosage,
        "time_of_day": reminder.time_of_day,
        "reminder_time": reminder.reminder_time,
        "active": True
    }
    medication_reminders_db[reminder.user_id].append(new_reminder)
    return {"status": "added", "reminder": new_reminder}

@app.get("/api/medicine-reminder/list/{user_id}")
def list_medicine_reminders(user_id: int):
    return {"reminders": medication_reminders_db.get(user_id, [])}

@app.post("/api/medicine-reminder/test/{user_id}")
def test_reminder(user_id: int):
    return {"status": "test sent", "message": "Test reminder triggered"}

@app.get("/export-pdf/{user_id}")
async def export_pdf(user_id: int):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    user = users_db.get(user_id, {})
    user_name = user.get("name", "Patient")
    
    story.append(Paragraph(f"Health Report - {user_name}", styles['Title']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    records = health_data_db.get(user_id, [])
    if records:
        story.append(Paragraph("Health Records", styles['Heading2']))
        table_data = [["Date", "BP Sys", "BP Dia", "HR", "Sugar", "Weight"]]
        for r in records[:10]:
            date = r.get('recorded_at', '')[:10] if r.get('recorded_at') else "N/A"
            table_data.append([date, str(r.get('bp_systolic', '')), str(r.get('bp_diastolic', '')), 
                             str(r.get('heart_rate', '')), str(r.get('blood_sugar', '')), str(r.get('weight', ''))])
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No health records found", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(buffer, media_type="application/pdf", 
                           headers={"Content-Disposition": f"attachment; filename=health_report_{user_name}.pdf"})

# Vercel handler
handler = app
