# init_attendance_table.py
import sqlite3

conn = sqlite3.connect("students.db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS resources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  teacher_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  type TEXT NOT NULL,           -- 'link', 'pdf', 'note', 'assignment'
  url TEXT,                     -- for links / hosted files
  file_path TEXT,               -- optional, if you store files on disk
  created_at TEXT NOT NULL      -- ISO datetime string
);""")
conn.commit()
conn.close()
print("Resources table ready.")





