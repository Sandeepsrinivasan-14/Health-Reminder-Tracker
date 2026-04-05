from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime
import os

app = FastAPI(title="Health Tracker API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
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
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bp_systolic INTEGER,
            bp_diastolic INTEGER,
            heart_rate INTEGER,
            blood_sugar INTEGER,
            weight REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# Models
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

# ========== ROUTES ==========

@app.get("/")
def root():
    return {"message": "Health Tracker API", "status": "running"}

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
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user.name, user.email))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "name": user.name, "email": user.email}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

@app.post("/health-data")
def save_health_data(data: HealthData):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_data (user_id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.user_id, data.bp_systolic, data.bp_diastolic, data.heart_rate, data.blood_sugar, data.weight))
    conn.commit()
    conn.close()
    return {"message": "Health data saved"}

@app.get("/health-data/user/{user_id}")
def get_user_health_data(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight, recorded_at
        FROM health_data WHERE user_id = ? ORDER BY recorded_at DESC
    ''', (user_id,))
    data = [{
        "id": row[0],
        "bp_systolic": row[1],
        "bp_diastolic": row[2],
        "heart_rate": row[3],
        "blood_sugar": row[4],
        "weight": row[5],
        "recorded_at": row[6]
    } for row in cursor.fetchall()]
    conn.close()
    return data

@app.post("/sos")
def send_sos(payload: dict):
    # Simplified SOS - just log for now
    return {"message": "SOS alert triggered", "user_id": payload.get("user_id")}

# Add sample users if none exist
def add_sample_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_users = [
            ("John Doe", "john@example.com"),
            ("Jane Smith", "jane@example.com"),
            ("Bob Johnson", "bob@example.com"),
            ("Alice Williams", "alice@example.com"),
            ("Charlie Brown", "charlie@example.com"),
        ]
        for name, email in sample_users:
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        print(f"✅ Added {len(sample_users)} sample users")
    conn.close()

add_sample_users()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
