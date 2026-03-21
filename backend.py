from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

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

# Initialize database
init_db()

# Pydantic models
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

# Health check
@app.get("/health")
def health():
    return {"status": "healthy", "phase": 5, "project": "HealthReminderTracker"}

# User endpoints
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

# Medication endpoints
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

# Vaccination endpoints
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

# Health tips
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
