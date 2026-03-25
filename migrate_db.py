import sqlite3
import os

db_path = os.path.join('instance', 'database_v2.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(complaint)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_feedback' not in columns:
            print("Adding 'user_feedback' column to 'complaint' table...")
            cursor.execute("ALTER TABLE complaint ADD COLUMN user_feedback TEXT")
            conn.commit()
            print("Migration successful.")
        else:
            print("'user_feedback' column already exists.")
            
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")
