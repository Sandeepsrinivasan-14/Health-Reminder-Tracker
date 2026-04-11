import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Reuse models from backend.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend import UserDB, HealthDataDB, Base

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def seed():
    # 5 highly realistic mock patients for the demo
    patients = [
        {"name": "Robert Chen (Hypertension)", "email": "robert@example.com", "base_sys": 145, "base_dia": 90, "base_hr": 80, "base_sugar": 105, "base_wt": 82.5},
        {"name": "Sarah Jenkins (Diabetes)", "email": "sarah@example.com", "base_sys": 118, "base_dia": 78, "base_hr": 70, "base_sugar": 160, "base_wt": 68.0},
        {"name": "Michael O'Connor (Heart)", "email": "michael@example.com", "base_sys": 135, "base_dia": 85, "base_hr": 88, "base_sugar": 110, "base_wt": 91.0},
        {"name": "Emily Davis (Anemia)", "email": "emily@example.com", "base_sys": 105, "base_dia": 65, "base_hr": 65, "base_sugar": 90, "base_wt": 55.5},
        {"name": "David Kim (Checkup)", "email": "david@example.com", "base_sys": 120, "base_dia": 80, "base_hr": 72, "base_sugar": 98, "base_wt": 75.0},
    ]

    print("🚀 Connecting directly to Neon Cloud Database...")
    Base.metadata.create_all(bind=engine)

    for p in patients:
        user = db.query(UserDB).filter(UserDB.email == p["email"]).first()
        if not user:
            user = UserDB(name=p["name"], email=p["email"])
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Added user: {user.name}")
        
        # Check health records
        count = db.query(HealthDataDB).filter(HealthDataDB.user_id == user.id).count()
        if count < 5:
            records = []
            now = datetime.utcnow()
            for i in range(7): # 7 days of history
                sys_val = int(p["base_sys"] + (i % 3 * 2) - 1)
                dia_val = int(p["base_dia"] + (i % 2 * 2) - 1)
                hr_val = int(p["base_hr"] + (i % 4) - 2)
                sugar_val = int(p["base_sugar"] + (i % 3 * 5) - 5)
                wt_val = round(p["base_wt"] - (i * 0.1), 1)
                
                records.append(HealthDataDB(
                    user_id=user.id,
                    bp_systolic=sys_val,
                    bp_diastolic=dia_val,
                    heart_rate=hr_val,
                    blood_sugar=sugar_val,
                    weight=wt_val,
                    recorded_at=now - timedelta(days=6-i)
                ))
            db.add_all(records)
            db.commit()
            print(f"📈 Added 7 days of health records for {user.name}")

    # FORCE fixing Bob Johnson and old users too!
    old_users = ["Bob Johnson", "Jane Smith", "John Doe"]
    for old_name in old_users:
        user = db.query(UserDB).filter(UserDB.name == old_name).first()
        if user and db.query(HealthDataDB).filter(HealthDataDB.user_id == user.id).count() == 0:
            records = [
                HealthDataDB(user_id=user.id, bp_systolic=125, bp_diastolic=82, heart_rate=75, blood_sugar=95, weight=80.0, recorded_at=datetime.utcnow() - timedelta(days=2)),
                HealthDataDB(user_id=user.id, bp_systolic=122, bp_diastolic=80, heart_rate=72, blood_sugar=98, weight=79.5, recorded_at=datetime.utcnow() - timedelta(days=1)),
                HealthDataDB(user_id=user.id, bp_systolic=120, bp_diastolic=78, heart_rate=70, blood_sugar=92, weight=79.2, recorded_at=datetime.utcnow()),
            ]
            db.add_all(records)
            db.commit()
            print(f"🔧 Forced health records for {user.name}")

    print("🏁 Cloud database fully seeded!")

if __name__ == '__main__':
    seed()
