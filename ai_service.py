import os
from groq import Groq

# Read GROQ_API_KEY directly from .env file
try:
    with open(".env", "r", encoding="utf-8-sig") as f:
        for line in f:
            if "GROQ_API_KEY=" in line:
                os.environ["GROQ_API_KEY"] = line.split("GROQ_API_KEY=", 1)[1].strip()
except Exception:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def _chat(messages):
    """Internal helper: call Groq with a list of messages."""
    if not GROQ_API_KEY or GROQ_API_KEY == "PASTE_YOUR_GROQ_KEY_HERE":
        return "Groq API key not configured. Please add GROQ_API_KEY to your .env file."
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content

def get_health_advice(question, patient_data=None):
    """Get AI health advice based on question and patient data."""
    system = """You are a highly experienced medical doctor and clinical health advisor integrated into a patient health tracker.

Your job is to:
1. ANALYZE the patient's actual health data critically — identify abnormal values, trends, and risks.
2. DIAGNOSE possible conditions based on the data (e.g., hypertension, prediabetes, arrhythmia, obesity).
3. Give SPECIFIC, ACTIONABLE medical advice — not vague or generic statements.
4. WARN the patient clearly if any values are in a dangerous range (e.g., BP > 140/90, blood sugar > 126 mg/dL fasting, heart rate > 100 bpm at rest).
5. Suggest lifestyle changes, dietary modifications, medications to discuss with their doctor, and follow-up tests if needed.
6. Be direct, clinical, and genuinely helpful — like a real doctor reviewing a chart.

IMPORTANT: Never say "everything looks normal" unless you've explicitly checked each value. Always provide medical insights relative to clinical thresholds.

Clinical reference ranges:
- Blood Pressure: Normal <120/80, Elevated 120-129/<80, Stage 1 HTN 130-139/80-89, Stage 2 HTN ≥140/90
- Heart Rate: Normal 60-100 bpm at rest
- Blood Sugar (fasting): Normal <100 mg/dL, Prediabetes 100-125, Diabetes ≥126
- BMI: Underweight <18.5, Normal 18.5-24.9, Overweight 25-29.9, Obese ≥30"""

    if patient_data:
        system += f"\n\nPatient's recent health records (latest first): {patient_data}\n\nAnalyze this data carefully before responding."

    try:
        return _chat([
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ])
    except Exception as e:
        return f"AI service error: {str(e)}"

def get_health_tips(patient_data):
    """Get 5 personalised health tips based on patient data."""
    try:
        prompt = (
            f"Based on this patient's health data: {patient_data}\n\n"
            "Provide exactly 5 personalised health tips covering:\n"
            "1. 💊 Medication adherence\n"
            "2. 🥗 Diet recommendation\n"
            "3. 🏃 Exercise suggestion\n"
            "4. 😴 Sleep improvement\n"
            "5. 🧘 Stress management\n\n"
            "Keep each tip concise (1-2 sentences) and actionable."
        )
        result = _chat([
            {"role": "system", "content": "You are a helpful medical health assistant."},
            {"role": "user", "content": prompt},
        ])
        return result.split("\n") if result else ["No tips available."]
    except Exception as e:
        return [f"Error generating tips: {str(e)}"]

def get_medication_suggestions(patient_data, medications):
    """Get AI-driven medication adherence and safety advice."""
    try:
        prompt = (
            f"Patient's latest health data: {patient_data}\n"
            f"Current medications: {medications}\n\n"
            "As a clinical pharmacist and medical advisor, provide a detailed review:\n"
            "1. ⚠️ Flag any potential drug interactions or contraindications\n"
            "2. 💊 Optimal timing and conditions for each medication (with food? morning/night?)\n"
            "3. 🩺 How does each medication relate to the patient's current health numbers?\n"
            "4. 🔴 Are there any alarming signs in the health data that suggest the current medication regimen needs adjustment?\n"
            "5. 🥗 Lifestyle and dietary changes that improve medication effectiveness\n"
            "6. 📋 Recommended follow-up tests or monitoring based on the medications and data\n\n"
            "Be specific, reference actual values from the health data, and give real clinical guidance."
        )
        return _chat([
            {"role": "system", "content": "You are a senior clinical pharmacist and medical advisor with 20 years of experience. Be specific, direct, and genuinely helpful using the patient's actual data."},
            {"role": "user", "content": prompt},
        ])
    except Exception as e:
        return f"Medication suggestion error: {str(e)}"
