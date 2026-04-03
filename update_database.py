import sqlite3

conn = sqlite3.connect('health_tracker.db')
cursor = conn.cursor()

print('=' * 60)
print('🔧 UPDATING DATABASE WITH MISSING TABLES')
print('=' * 60)

# Add Notification Settings table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notification_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        browser_notifications BOOLEAN DEFAULT 1,
        email_notifications BOOLEAN DEFAULT 0,
        sms_notifications BOOLEAN DEFAULT 0,
        reminder_frequency TEXT DEFAULT 'on_time',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
print('✅ notification_settings table created')

# Add Notification Logs table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notification_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'sent',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
print('✅ notification_logs table created')

# Add Medication Stock table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS medication_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medication_id INTEGER NOT NULL,
        stock_quantity INTEGER DEFAULT 30,
        low_stock_threshold INTEGER DEFAULT 5,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (medication_id) REFERENCES medications (id)
    )
''')
print('✅ medication_stock table created')

# Add Health Alerts table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        alert_type TEXT NOT NULL,
        alert_level TEXT CHECK(alert_level IN ('info', 'warning', 'danger')),
        message TEXT NOT NULL,
        acknowledged BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
print('✅ health_alerts table created')

# Add Caregiver Notifications table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS caregiver_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caregiver_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        alert_type TEXT NOT NULL,
        message TEXT NOT NULL,
        read_status BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (caregiver_id) REFERENCES users (id),
        FOREIGN KEY (patient_id) REFERENCES users (id)
    )
''')
print('✅ caregiver_notifications table created')

conn.commit()
conn.close()

print('\n' + '=' * 60)
print('✅ Database update completed successfully!')
print('=' * 60)
