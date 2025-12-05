import sqlite3

conn = sqlite3.connect("students.db")
cur = conn.cursor()

# 1) Add email column if it does not exist yet
cur.execute("PRAGMA table_info(students)")
cols = [row[1] for row in cur.fetchall()]
if "email" not in cols:
    cur.execute("ALTER TABLE students ADD COLUMN email TEXT")

# 2) Set emails for some students
cur.execute("UPDATE students SET email = '2024ci_rohanrajukadolkar_b@nie.ac.in' WHERE student_id = 1")
cur.execute("UPDATE students SET email = 'aishwaryahiremath045@gmail.com'      WHERE student_id = 61")

conn.commit()
conn.close()

conn = sqlite3.connect("students.db")
cur = conn.cursor()

# 1) Add email column if it does not exist yet
cur.execute("PRAGMA table_info(teachers)")
cols = [row[1] for row in cur.fetchall()]
if "email" not in cols:
    cur.execute("ALTER TABLE teachers ADD COLUMN email TEXT")
if "gmail_app_password" not in cols:
    cur.execute("ALTER TABLE teachers ADD COLUMN gmail_app_password TEXT;")

# 2) Set emails for some students
cur.execute("UPDATE teachers SET email = 'rkyouthubetry2006@gmail.com' WHERE teacher_id = 1")
cur.execute("UPDATE teachers SET gmail_app_password = 'udibgebxvmczignl' WHERE teacher_id = 1")
cur.execute("UPDATE teachers SET email = 'aishwaryahiremath045@gmail.com' WHERE teacher_id = 5")
cur.execute("UPDATE teachers SET gmail_app_password = '.....' WHERE teacher_id = 5")


conn.commit()
conn.close()

print("Done updating emails.")
