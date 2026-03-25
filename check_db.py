import sqlite3
import os

db_path = os.path.join('instance', 'database_v2.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic, status, admin_comment FROM complaint WHERE status='Resolved'")
    rows = cursor.fetchall()
    print("Resolved Complaints:")
    for row in rows:
        print(row)
    conn.close()
else:
    print("DB not found")
