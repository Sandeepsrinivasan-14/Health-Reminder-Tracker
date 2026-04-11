from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from ai_service import get_health_advice, get_health_tips, get_medication_suggestions
from twilio_service import send_sos_alert
from notification_service import send_email_alert

app = FastAPI(title="Health Tracker API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
# DATABASE_URL should be set in Render environment variables for Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./health_tracker.db")

# Fix for Render (some Postgres URLs start with postgres:// instead of postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ========== DATABASE MODELS ==========

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

class HealthDataDB(Base):
    __tablename__ = "health_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bp_systolic = Column(Integer)
    bp_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    blood_sugar = Column(Integer)
    weight = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== PYDANTIC MODELS ==========

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True

class HealthDataCreate(BaseModel):
    user_id: int
    bp_systolic: int
    bp_diastolic: int
    heart_rate: int
    blood_sugar: int
    weight: float

class HealthDataResponse(BaseModel):
    id: int
    bp_systolic: int
    bp_diastolic: int
    heart_rate: int
    blood_sugar: int
    weight: float
    recorded_at: datetime
    class Config:
        from_attributes = True

class NotifyPayload(BaseModel):
    user_id: int
    message: str
    delivery_type: str # "sms", "whatsapp", "email"

# ========== ROUTES ==========

@app.get("/")
def root():
    return {"message": "Health Tracker API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        return db_user
    new_user = UserDB(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/health-data")
def save_health_data(data: HealthDataCreate, db: Session = Depends(get_db)):
    new_data = HealthDataDB(**data.dict())
    db.add(new_data)
    db.commit()
    return {"message": "Health data saved"}

@app.get("/health-data/user/{user_id}", response_model=List[HealthDataResponse])
def get_user_health_data(user_id: int, db: Session = Depends(get_db)):
    return db.query(HealthDataDB).filter(HealthDataDB.user_id == user_id).order_by(HealthDataDB.recorded_at.desc()).all()

@app.post("/api/notify")
def handle_notification(payload: NotifyPayload):
    alerts = {}
    if payload.delivery_type in ["sms", "whatsapp"]:
        resp = send_sos_alert(payload.message, delivery_type=payload.delivery_type)
        alerts["phone"] = resp
    elif payload.delivery_type == "email":
        caretaker_email = os.getenv("CARETAKER_EMAIL", os.getenv("EMAIL_ADDRESS", "test@example.com"))
        resp = send_email_alert(caretaker_email, "Medical Reminder/Alert", payload.message)
        alerts["email"] = resp
    return {"status": "processed", "alerts": alerts}

@app.post("/sos")
def send_sos(payload: dict):
    resp = send_sos_alert("🚨 EMERGENCY SOS ALERT! Patient needs immediate medical attention!")
    return {"message": "SOS alert triggered", "user_id": payload.get("user_id"), "twilio_response": resp}

@app.post("/api/ai/chat")
async def ai_chat(request: dict, db: Session = Depends(get_db)):
    question = request.get("question", "")
    user_id = request.get("user_id")
    
    patient_data = None
    if user_id:
        rows = db.query(HealthDataDB).filter(HealthDataDB.user_id == user_id).order_by(HealthDataDB.recorded_at.desc()).limit(5).all()
        if rows:
            patient_data = [{"bp_systolic": r.bp_systolic, "bp_diastolic": r.bp_diastolic, "heart_rate": r.heart_rate, "blood_sugar": r.blood_sugar, "weight": r.weight} for r in rows]
    
    advice = get_health_advice(question, patient_data)
    return {"response": advice}

@app.get("/api/ai/health-tips/{user_id}")
async def health_tips(user_id: int, db: Session = Depends(get_db)):
    rows = db.query(HealthDataDB).filter(HealthDataDB.user_id == user_id).order_by(HealthDataDB.recorded_at.desc()).limit(5).all()
    patient_data = [{"bp_systolic": r.bp_systolic, "bp_diastolic": r.bp_diastolic, "heart_rate": r.heart_rate, "blood_sugar": r.blood_sugar, "weight": r.weight} for r in rows]
    
    tips = get_health_tips(patient_data)
    return {"tips": tips}

@app.post("/api/ai/medication-suggestions")
async def medication_suggestions(request: dict, db: Session = Depends(get_db)):
    user_id = request.get("user_id")
    medications = request.get("medications", [])
    
    rows = db.query(HealthDataDB).filter(HealthDataDB.user_id == user_id).order_by(HealthDataDB.recorded_at.desc()).limit(5).all()
    patient_data = [{"bp_systolic": r.bp_systolic, "bp_diastolic": r.bp_diastolic, "heart_rate": r.heart_rate, "blood_sugar": r.blood_sugar, "weight": r.weight} for r in rows]
    
    suggestions = get_medication_suggestions(patient_data, medications)
    return {"suggestions": suggestions}

# Auto-provision sample users if database is empty
def add_sample_users():
    db = SessionLocal()
    try:
        if db.query(UserDB).count() == 0:
            sample_users = [
                UserDB(name="John Doe", email="john@example.com"),
                UserDB(name="Jane Smith", email="jane@example.com"),
                UserDB(name="Bob Johnson", email="bob@example.com"),
            ]
            db.add_all(sample_users)
            db.commit()
            print(f"✅ Added {len(sample_users)} sample users")
            
        # Check if John Doe has health records; if not, add some
        user = db.query(UserDB).filter(UserDB.name == "John Doe").first()
        if user and db.query(HealthDataDB).filter(HealthDataDB.user_id == user.id).count() == 0:
            sample_data = [
                HealthDataDB(user_id=user.id, bp_systolic=120, bp_diastolic=80, heart_rate=72, blood_sugar=95, weight=70.0),
                HealthDataDB(user_id=user.id, bp_systolic=125, bp_diastolic=82, heart_rate=75, blood_sugar=98, weight=70.2),
                HealthDataDB(user_id=user.id, bp_systolic=118, bp_diastolic=78, heart_rate=70, blood_sugar=92, weight=69.8),
                HealthDataDB(user_id=user.id, bp_systolic=122, bp_diastolic=80, heart_rate=73, blood_sugar=96, weight=70.1),
                HealthDataDB(user_id=user.id, bp_systolic=128, bp_diastolic=84, heart_rate=78, blood_sugar=102, weight=70.5),
            ]
            db.add_all(sample_data)
            db.commit()
            print(f"✅ Added sample health records for {user.name}")
    finally:
        db.close()

add_sample_users()
