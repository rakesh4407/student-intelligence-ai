import sqlite3

# Create database connection
conn = sqlite3.connect("database/student_system.db")
cur = conn.cursor()

# ------------------ USERS TABLE (LOGIN) ------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT CHECK(role IN ('admin', 'teacher', 'student')),
    roll_no INTEGER
)
""")

# ------------------ STUDENTS TABLE ------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_no INTEGER PRIMARY KEY,
    name TEXT,
    attendance REAL,
    assignments_score REAL,
    midterm_score REAL,
    final_score REAL,
    study_hours REAL,
    performance TEXT
)
""")

# ------------------ PREDICTION HISTORY ------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS prediction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no INTEGER,
    predicted_label TEXT,
    date_time TEXT,
    FOREIGN KEY (roll_no) REFERENCES students(roll_no)
)
""")

conn.commit()
conn.close()

print("Database & tables created successfully!")
