import sqlite3
import random
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('health_tracker.db')
cursor = conn.cursor()

# Clear existing users (keep Test Patient if exists)
cursor.execute("DELETE FROM users WHERE name != 'Test Patient'")
conn.commit()

# 20 diverse user profiles
users = [
    # Name, Email, Age Group, Health Conditions
    ("Rajesh Kumar", "rajesh.kumar@email.com", "Senior", "Diabetes, Hypertension"),
    ("Priya Sharma", "priya.sharma@email.com", "Adult", "Healthy"),
    ("Amit Patel", "amit.patel@email.com", "Adult", "Heart Condition"),
    ("Sunita Reddy", "sunita.reddy@email.com", "Senior", "Arthritis, Diabetes"),
    ("Vikram Singh", "vikram.singh@email.com", "Adult", "High Cholesterol"),
    ("Neha Gupta", "neha.gupta@email.com", "Young", "Asthma"),
    ("Anand Desai", "anand.desai@email.com", "Senior", "BP, Diabetes"),
    ("Kavita Nair", "kavita.nair@email.com", "Adult", "Thyroid"),
    ("Suresh Iyer", "suresh.iyer@email.com", "Senior", "Heart Disease"),
    ("Meera Joshi", "meera.joshi@email.com", "Adult", "Migraine"),
    ("Rohan Mehta", "rohan.mehta@email.com", "Young", "Healthy"),
    ("Anjali Kulkarni", "anjali.kulkarni@email.com", "Senior", "BP, Diabetes"),
    ("Deepak Saxena", "deepak.saxena@email.com", "Adult", "Obesity"),
    ("Swati Choudhary", "swati.choudhary@email.com", "Young", "Anemia"),
    ("Manoj Verma", "manoj.verma@email.com", "Adult", "Stress, Anxiety"),
    ("Pooja Malhotra", "pooja.malhotra@email.com", "Senior", "Osteoporosis"),
    ("Arjun Nair", "arjun.nair@email.com", "Young", "Healthy"),
    ("Divya Menon", "divya.menon@email.com", "Adult", "PCOS"),
    ("Sanjay Gupta", "sanjay.gupta@email.com", "Senior", "Diabetes, Kidney"),
    ("Lata Mangeshkar", "lata.mangeshkar@email.com", "Senior", "BP, Heart")
]

# Add users
for name, email, age_group, conditions in users:
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        user_id = cursor.lastrowid
        print(f"✅ Added: {name} (ID: {user_id}) - {age_group} - {conditions}")
        
        # Add default notification settings
        cursor.execute("INSERT INTO notification_settings (user_id) VALUES (?)", (user_id,))
        
        # Add health data based on conditions
        health_data = []
        
        if "Diabetes" in conditions:
            # Diabetic patient
            health_data.append((user_id, random.randint(140, 180), random.randint(85, 95), 
                               random.randint(75, 90), random.randint(150, 220), random.randint(70, 85)))
        elif "Hypertension" in conditions or "BP" in conditions:
            # High BP patient
            health_data.append((user_id, random.randint(145, 165), random.randint(90, 105), 
                               random.randint(70, 85), random.randint(90, 110), random.randint(65, 80)))
        elif "Heart" in conditions:
            # Heart condition
            health_data.append((user_id, random.randint(130, 150), random.randint(85, 95), 
                               random.randint(85, 110), random.randint(95, 120), random.randint(70, 90)))
        elif "Healthy" in conditions:
            # Healthy individual
            health_data.append((user_id, random.randint(110, 125), random.randint(70, 80), 
                               random.randint(65, 75), random.randint(80, 100), random.randint(60, 75)))
        elif "Obesity" in conditions:
            # Overweight
            health_data.append((user_id, random.randint(125, 140), random.randint(80, 90), 
                               random.randint(70, 85), random.randint(100, 130), random.randint(90, 110)))
        else:
            # Average
            health_data.append((user_id, random.randint(115, 135), random.randint(75, 85), 
                               random.randint(68, 82), random.randint(85, 115), random.randint(65, 85)))
        
        # Add 3 months of historical data
        for i in range(12):  # 12 weeks of data
            date = (datetime.now() - timedelta(days=i*7)).strftime('%Y-%m-%d')
            bp_sys = health_data[0][1] + random.randint(-15, 15)
            bp_dia = health_data[0][2] + random.randint(-10, 10)
            hr = health_data[0][3] + random.randint(-10, 15)
            sugar = health_data[0][4] + random.randint(-30, 40)
            weight = health_data[0][5] + random.randint(-3, 3)
            
            cursor.execute("""
                INSERT INTO health_data (user_id, bp_systolic, bp_diastolic, heart_rate, blood_sugar, weight, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, bp_sys, bp_dia, hr, sugar, weight, date))
        
        # Add medications based on conditions
        if "Diabetes" in conditions:
            cursor.execute("INSERT INTO medications (user_id, name, dosage, time_of_day, active) VALUES (?, ?, ?, ?, ?)",
                          (user_id, "Metformin", "500mg", "morning", 1))
            cursor.execute("INSERT INTO medications (user_id, name, dosage, time_of_day, active) VALUES (?, ?, ?, ?, ?)",
                          (user_id, "Insulin", "10 units", "evening", 1))
        elif "Hypertension" in conditions or "BP" in conditions:
            cursor.execute("INSERT INTO medications (user_id, name, dosage, time_of_day, active) VALUES (?, ?, ?, ?, ?)",
                          (user_id, "Amlodipine", "5mg", "morning", 1))
        elif "Heart" in conditions:
            cursor.execute("INSERT INTO medications (user_id, name, dosage, time_of_day, active) VALUES (?, ?, ?, ?, ?)",
                          (user_id, "Aspirin", "75mg", "morning", 1))
            cursor.execute("INSERT INTO medications (user_id, name, dosage, time_of_day, active) VALUES (?, ?, ?, ?, ?)",
                          (user_id, "Atorvastatin", "20mg", "evening", 1))
        
        # Add vaccinations
        vaccines = ["Flu Vaccine", "COVID-19 Booster", "Pneumococcal", "Hepatitis B"]
        for vaccine in random.sample(vaccines, random.randint(1, 2)):
            due_date = (datetime.now() + timedelta(days=random.randint(7, 180))).strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO vaccinations (user_id, name, due_date, completed) VALUES (?, ?, ?, ?)",
                          (user_id, vaccine, due_date, 0))
        
        # Add some health alerts
        if "Diabetes" in conditions:
            cursor.execute("INSERT INTO health_alerts (user_id, alert_type, alert_level, message) VALUES (?, ?, ?, ?)",
                          (user_id, "Blood Sugar", "warning", "High blood sugar detected. Monitor diet."))
        if "Hypertension" in conditions:
            cursor.execute("INSERT INTO health_alerts (user_id, alert_type, alert_level, message) VALUES (?, ?, ?, ?)",
                          (user_id, "Blood Pressure", "warning", "BP reading above normal range."))
        
        # Add medication stock
        meds = cursor.execute("SELECT id FROM medications WHERE user_id = ?", (user_id,)).fetchall()
        for med in meds:
            cursor.execute("INSERT INTO medication_stock (medication_id, stock_quantity) VALUES (?, ?)",
                          (med[0], random.randint(10, 60)))
            
    except sqlite3.IntegrityError:
        print(f"⚠️ {name} already exists, skipping")

conn.commit()
conn.close()

print("\n" + "="*60)
print("✅ 20 DIVERSE TEST USERS ADDED SUCCESSFULLY!")
print("="*60)
print("\nUser Categories Added:")
print("• Seniors with chronic conditions (Diabetes, BP, Heart)")
print("• Adults with specific conditions (Thyroid, Asthma, Migraine)")
print("• Young healthy individuals")
print("• Patients with obesity, stress, anemia")
print("• Complete with medications, health data, alerts")
print("\nAll users have:")
print("✓ 3 months of health history")
print("✓ Relevant medications")
print("✓ Upcoming vaccinations")
print("✓ Custom health alerts")
print("✓ Medication stock tracking")
