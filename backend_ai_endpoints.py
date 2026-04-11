# Add these imports at the TOP of backend.py (after existing imports)
from ai_service import get_health_advice, get_health_tips, get_medication_suggestions
from notification_service import send_email_alert, get_push_notification_script
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add these new endpoints BEFORE the if __name__ == "__main__" block

@app.post("/api/ai/chat")
async def ai_chat(request: dict):
    """AI Chat endpoint - answers health questions"""
    question = request.get("question", "")
    user_id = request.get("user_id")
    
    # Get patient health data if user_id provided
    patient_data = None
    if user_id:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 5", (user_id,))
        rows = cursor.fetchall()
        if rows:
            patient_data = [{"bp_systolic": r[0], "bp_diastolic": r[1], "heart_rate": r[2], "blood_sugar": r[3], "weight": r[4]} for r in rows]
        conn.close()
    
    advice = get_health_advice(question, patient_data)
    return {"response": advice, "status": "success"}

@app.get("/api/ai/health-tips/{user_id}")
async def health_tips(user_id: int):
    """Get personalized health tips based on patient data"""
    # Get patient health data
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 5", (user_id,))
    rows = cursor.fetchall()
    patient_data = [{"bp_systolic": r[0], "bp_diastolic": r[1], "heart_rate": r[2], "blood_sugar": r[3], "weight": r[4]} for r in rows]
    conn.close()
    
    tips = get_health_tips(patient_data)
    return {"tips": tips, "status": "success"}

@app.post("/api/ai/medication-suggestions")
async def medication_suggestions(request: dict):
    """Get AI medication suggestions"""
    user_id = request.get("user_id")
    medications = request.get("medications", [])
    
    # Get patient health data
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 5", (user_id,))
    rows = cursor.fetchall()
    patient_data = [{"bp_systolic": r[0], "bp_diastolic": r[1], "heart_rate": r[2], "blood_sugar": r[3], "weight": r[4]} for r in rows]
    conn.close()
    
    suggestions = get_medication_suggestions(patient_data, medications)
    return {"suggestions": suggestions, "status": "success"}

@app.post("/api/send-reminder-email")
async def send_reminder_email(request: dict):
    """Send email reminder"""
    to_email = request.get("to_email")
    medication_name = request.get("medication_name", "your medication")
    dosage = request.get("dosage", "")
    
    subject = f"💊 Medication Reminder - Time to take {medication_name}"
    message = f"""Hello,

This is a reminder that it's time to take your medication:
- Medication: {medication_name}
- Dosage: {dosage}

Please take your medication on time for best results.

Stay healthy! 🏥
Health Reminder Tracker
"""
    
    result = send_email_alert(to_email, subject, message)
    return result

@app.get("/api/push-notification-script")
async def get_notification_script():
    """Get JavaScript for push notifications"""
    return {"script": get_push_notification_script("Medication Reminder", "Time to take your medication!")}
