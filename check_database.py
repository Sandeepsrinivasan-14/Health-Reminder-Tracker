import sqlite3

conn = sqlite3.connect('health_tracker.db')
cursor = conn.cursor()

print('=' * 60)
print('📊 DATABASE STRUCTURE')
print('=' * 60)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f'\n📁 Table: {table_name}')
    print('-' * 40)
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        print(f'   ├─ {col_name} ({col_type})')
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f'   └─ Total rows: {count}')

conn.close()
print('\n✅ Database check complete!')
