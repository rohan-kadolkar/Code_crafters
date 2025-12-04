# init_attendance_table.py
import sqlite3

conn = sqlite3.connect("students.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL  -- 'Present' or 'Absent'
)
""")
conn.commit()
conn.close()
print("Attendance table ready.")
