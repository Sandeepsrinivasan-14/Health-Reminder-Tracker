"""Load demo patients, readings and medications.

Usage:  python -m app.seed          (uses DATABASE_URL from the environment / .env)
Idempotent: patients are matched by email and only get demo data if they have none.
"""

from datetime import timedelta

from sqlalchemy import select

from .config import get_settings
from .database import Database
from .models import Medication, User, VitalReading, utcnow

DEMO_PATIENTS = [
    # name, email, height, (sys, dia, hr, glucose, weight), medications
    ("Ravi Kumar", "ravi.kumar@example.com", 170, (146, 92, 82, 108, 82.0), [("Amlodipine", "5 mg", "08:00", "BP", 20)]),
    (
        "Meena Iyer",
        "meena.iyer@example.com",
        158,
        (122, 78, 74, 162, 68.0),
        [("Metformin", "500 mg", "08:30", "Diabetes", 45), ("Metformin", "500 mg", "20:30", "Diabetes", 45)],
    ),
    ("Arjun Rao", "arjun.rao@example.com", 178, (116, 74, 66, 92, 72.5), [("Vitamin D3", "1000 IU", "09:00", "Vitamin", 4)]),
]


def seed(db_url: str | None = None) -> int:
    database = Database(db_url or get_settings().database_url)
    database.create_all()
    added = 0
    with database.session_factory() as db:
        for name, email, height, (sys_, dia, hr, glu, wt), meds in DEMO_PATIENTS:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(name=name, email=email, height_cm=height)
                db.add(user)
                db.flush()
                added += 1
            if not user.vitals:
                now = utcnow()
                for day in range(14):
                    wobble = (day % 4) - 1
                    db.add(
                        VitalReading(
                            user_id=user.id,
                            systolic=sys_ + wobble * 2,
                            diastolic=dia + wobble,
                            heart_rate=hr + wobble,
                            blood_glucose=glu + wobble * 4,
                            glucose_context="fasting",
                            weight_kg=round(wt - day * 0.05, 1),
                            recorded_at=now - timedelta(days=13 - day, hours=1),
                        )
                    )
            if not user.medications:
                for med_name, dose, at, category, stock in meds:
                    db.add(
                        Medication(user_id=user.id, name=med_name, dosage=dose, schedule_time=at, category=category, stock=stock)
                    )
        db.commit()
    return added


if __name__ == "__main__":
    print(f"Seeded {seed()} new demo patient(s).")
