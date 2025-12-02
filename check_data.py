# check_data.py
import sqlite3

conn = sqlite3.connect('dashboards/backend/students.db')
cursor = conn.cursor()

print("=" * 60)
print("🔍 CHECKING DATABASE STRUCTURE")
print("=" * 60)

# Check teachers table
print("\n1️⃣ TEACHERS TABLE:")
cursor.execute("SELECT * FROM teachers LIMIT 3")
columns = [desc[0] for desc in cursor.description]
print(f"   Columns: {columns}")
rows = cursor.fetchall()
print(f"   Sample data: {rows[0] if rows else 'EMPTY'}")

# Check student_teacher_mapping
print("\n2️⃣ STUDENT_TEACHER_MAPPING TABLE:")
cursor.execute("SELECT * FROM student_teacher_mapping LIMIT 3")
columns = [desc[0] for desc in cursor.description]
print(f"   Columns: {columns}")
rows = cursor.fetchall()
print(f"   Sample data: {rows[0] if rows else 'EMPTY'}")

# Check if teacher_id 1 exists
print("\n3️⃣ CHECKING TEACHER_ID=1:")
cursor.execute("SELECT * FROM teachers WHERE teacher_id = 1")
teacher = cursor.fetchone()
if teacher:
    print(f"   ✅ Teacher 1 exists: {teacher}")
else:
    print(f"   ❌ Teacher 1 NOT FOUND")

# Check mappings for teacher 1
print("\n4️⃣ STUDENTS FOR TEACHER_ID=1:")
cursor.execute("""
    SELECT COUNT(*) FROM student_teacher_mapping 
    WHERE teacher_id = 1
""")
count = cursor.fetchone()[0]
print(f"   Students assigned: {count}")

# Check if students table has matching IDs
print("\n5️⃣ CHECKING STUDENT DATA:")
cursor.execute("""
    SELECT s.student_id, s.full_name, stm.teacher_id
    FROM students s
    JOIN student_teacher_mapping stm ON s.student_id = stm.student_id
    WHERE stm.teacher_id = 1
    LIMIT 3
""")
rows = cursor.fetchall()
print(f"   Sample joined data: {rows}")

conn.close()
print("\n" + "=" * 60)