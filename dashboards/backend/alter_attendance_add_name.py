import sqlite3

conn = sqlite3.connect("students.db")
cur = conn.cursor()

# 1) Add the column
cur.execute("ALTER TABLE attendance ADD COLUMN student_name TEXT;")

# 2) Optional: fill it for existing rows from students table
cur.execute("""
UPDATE attendance
SET student_name = (
  SELECT full_name
  FROM students
  WHERE students.student_id = attendance.student_id
)
""")

conn.commit()
conn.close()
