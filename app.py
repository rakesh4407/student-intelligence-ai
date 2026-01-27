from flask import (
    Flask, render_template, request, abort,
    redirect, url_for, session, send_file
)
import joblib
import numpy as np
import pandas as pd
import sqlite3
import os
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ===================== APP =====================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

# ===================== PATHS (🔥 FIXED) =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "student_system.db")

MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "performance_model.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "ml_model", "label_encoder.joblib")

# ===================== MODEL LOADING =====================
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# ===================== DB HELPERS =====================
def get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db_and_admin():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            roll_no INTEGER
        )
    """)

    conn.execute("""
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no INTEGER,
            predicted_label TEXT,
            date_time TEXT
        )
    """)

    admin = conn.execute(
        "SELECT * FROM users WHERE username='admin'"
    ).fetchone()

    if not admin:
        conn.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (
            "admin",
            generate_password_hash("admin123"),
            "admin"
        ))

    conn.commit()
    conn.close()

# -------------------- RISK & RECOMMENDATION --------------------
def get_risk_and_recommendation(student):
    attendance = student["attendance"]
    performance = student["performance"]
    final_score = student["final_score"]
    study_hours = student["study_hours"]

    if attendance < 60 or performance == "Poor":
        risk = "High"
    elif attendance < 75 or performance == "Average":
        risk = "Medium"
    else:
        risk = "Low"

    rec = []
    if attendance < 75:
        rec.append("Improve attendance and avoid missing classes.")
    if final_score < 60:
        rec.append("Focus on basics & past question papers.")
    if study_hours < 2:
        rec.append("Increase daily study time gradually.")
    if performance == "Poor":
        rec.append("Seek mentoring / extra coaching.")

    if not rec:
        rec.append("Good progress! Maintain consistency.")

    return risk, " ".join(rec)

# -------------------- SIMPLE CHATBOT LOGIC --------------------
def chatbot_reply(message: str) -> str:
    msg = message.lower()

    if any(word in msg for word in ["hello", "hi", "hey"]):
        return "Hi! 👋 I’m your AI assistant for the Student Performance System. Ask me about attendance, marks, risk level, or how to improve your studies."

    if "attendance" in msg:
        return "Attendance is very important. Try to keep it above 75%. If your attendance is low, focus on attending all classes for the next few weeks and avoid unnecessary absences."

    if "study" in msg or "hours" in msg or "time table" in msg:
        return "A good habit is to study 2–3 hours daily in focused blocks. Break it as: 45 minutes study + 10 minutes break. Prioritize weak subjects first and revise with short notes."

    if "exam" in msg or "exams" in msg or "test" in msg:
        return "For exams, revise previous question papers, focus on important units, and solve 3–5 problems per topic. The night before the exam, do light revision and sleep well."

    if "improve marks" in msg or "low marks" in msg or "fail" in msg:
        return "Check which area is weak: attendance, assignments, or exam preparation. Start by analysing your mistakes, practicing similar questions, and asking doubts from teachers or peers."

    if "cgpa" in msg or "grade" in msg:
        return "To improve GPA/grades, be consistent: submit assignments on time, attend classes, and maintain daily revision. Small improvements in each subject add up to a better GPA."

    if "risk" in msg or "at risk" in msg:
        return "The system marks you as 'High', 'Medium', or 'Low' risk based on attendance, performance, and study hours. If you’re High risk, increase study time, attend all classes, and seek help from teachers."

    if "project" in msg or "system" in msg or "explain" in msg:
        return "This system predicts student performance using machine learning, shows at-risk students to teachers, provides dashboards, history, and AI-generated recommendations and PDF reports."

    if "recommendation" in msg or "suggest" in msg:
        return "General recommendation: make a realistic timetable, focus on weak subjects, revise daily, take mock tests on weekends, and discuss doubts early instead of waiting till exams."

    if "who are you" in msg or "what can you do" in msg:
        return "I’m a simple AI chatbot inside the Student Performance Prediction and Recommendation System. I help with guidance on study, performance, and how to use this platform."

    return "I’m not fully sure about that, but you can ask me about attendance, study plans, exams, risk levels, GPA, or how to improve your academic performance."

# -------------------- AUTH HELPERS --------------------
def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return user

def login_required(role=None):
    if "user_id" not in session:
        return False
    if role and session.get("role") != role:
        return False
    return True

# -------------------- ROUTES --------------------

@app.route("/")
def home():
    return render_template("index.html")

# ---------- LOGIN / LOGOUT ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = get_user_by_username(username)
        if user and user["role"] == role and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            if role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif role == "teacher":
                return redirect(url_for("teacher_dashboard"))
            else:
                return redirect(url_for("student_dashboard"))
        else:
            error = "Invalid login details!"

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/predict", methods=["GET"])
def predict_form():
    return render_template("predict.html")

# ---------- PREDICT (PUBLIC FORM) ----------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        attendance = float(request.form["attendance"])
        assignments = float(request.form["assignments"])
        midterm = float(request.form["midterm"])
        final = float(request.form["final"])
        hours = float(request.form["hours"])

        features = np.array([[attendance, assignments, midterm, final, hours]])
        pred_encoded = model.predict(features)[0]
        pred_label = label_encoder.inverse_transform([pred_encoded])[0]

        # Detect logged in student to attach roll_no if available
        roll_no = None
        if "user_id" in session and session.get("role") == "student":
            user = get_user_by_username(session.get("username"))
            if user and user["roll_no"]:
                roll_no = user["roll_no"]

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO prediction_history (roll_no, predicted_label, date_time)
            VALUES (?, ?, ?)
        """, (
            roll_no,
            pred_label,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

        return render_template(
            "result.html",
            performance=pred_label,
            attendance=attendance,
            assignments=assignments,
            midterm=midterm,
            final=final,
            hours=hours
        )

    except Exception as e:
        return f"Prediction Error: {e}"

@app.route("/dashboard")
def dashboard_redirect():
    if "role" not in session:
        return redirect(url_for("login"))

    if session["role"] == "teacher":
        return redirect(url_for("teacher_dashboard"))
    elif session["role"] == "student":
        return redirect(url_for("student_dashboard"))
    elif session["role"] == "admin":
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("login"))

# ---------- TEACHER DASHBOARD ----------
@app.route("/teacher-dashboard", methods=["GET"])
def teacher_dashboard():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    if not students:
        return "No student records found in database!"

    df = pd.DataFrame([dict(row) for row in students])

    df["risk_level"] = df.apply(lambda row: get_risk_and_recommendation(row)[0], axis=1)
    df["recommendation"] = df.apply(lambda row: get_risk_and_recommendation(row)[1], axis=1)

    search_query = request.args.get("search", "").lower()
    filter_risk = request.args.get("risk", "")
    filter_perf = request.args.get("performance", "")
    sort_by = request.args.get("sort", "")

    if search_query:
        df = df[
            df["name"].str.lower().str.contains(search_query) |
            df["roll_no"].astype(str).str.contains(search_query)
        ]

    if filter_risk:
        df = df[df["risk_level"] == filter_risk]

    if filter_perf:
        df = df[df["performance"] == filter_perf]

    if sort_by == "attendance":
        df = df.sort_values(by="attendance", ascending=False)
    elif sort_by == "final_score":
        df = df.sort_values(by="final_score", ascending=False)

    total_students = len(df)
    avg_attendance = round(df["attendance"].mean(), 1) if total_students > 0 else 0
    avg_final = round(df["final_score"].mean(), 1) if total_students > 0 else 0
    perf_counts = df["performance"].value_counts().to_dict()
    at_risk_records = df.to_dict(orient="records")

    return render_template(
        "teacher_dashboard.html",
        total_students=total_students,
        avg_attendance=avg_attendance,
        avg_final=avg_final,
        perf_counts=perf_counts,
        perf_labels=list(perf_counts.keys()),
        perf_values=list(perf_counts.values()),
        at_risk_students=at_risk_records,
        search_query=search_query,
        filter_risk=filter_risk,
        filter_perf=filter_perf,
        sort_by=sort_by
    )

# ---------- STUDENT PROFILE (Teacher view) ----------
@app.route("/student/<int:roll_no>")
def student_profile(roll_no):
    if not login_required(role="teacher"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
    ).fetchone()
    conn.close()

    if student is None:
        return abort(404, "Student not found")

    risk, rec = get_risk_and_recommendation(student)

    features = np.array([[student["attendance"],
                          student["assignments_score"],
                          student["midterm_score"],
                          student["final_score"],
                          student["study_hours"]]])
    pred_encoded = model.predict(features)[0]
    predicted_label = label_encoder.inverse_transform([pred_encoded])[0]

    return render_template(
        "student_profile.html",
        roll_no=student["roll_no"],
        name=student["name"],
        attendance=student["attendance"],
        assignments=student["assignments_score"],
        midterm=student["midterm_score"],
        final=student["final_score"],
        study_hours=student["study_hours"],
        performance=student["performance"],
        predicted_performance=predicted_label,
        risk_level=risk,
        recommendation=rec
    )

# ---------- STUDENT DASHBOARD ----------
@app.route("/student-dashboard")
def student_dashboard():
    if not login_required(role="student"):
        return redirect(url_for("login"))

    username = session.get("username")
    user = get_user_by_username(username)

    if not user or not user["roll_no"]:
        return "Your account is not linked to a student record. Contact admin."

    roll_no = user["roll_no"]

    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
    ).fetchone()
    conn.close()

    if not student:
        return "Student record not found."

    risk, rec = get_risk_and_recommendation(student)

    features = np.array([[student["attendance"],
                          student["assignments_score"],
                          student["midterm_score"],
                          student["final_score"],
                          student["study_hours"]]])
    pred_encoded = model.predict(features)[0]
    predicted_label = label_encoder.inverse_transform([pred_encoded])[0]

    # Log prediction for this student (history)
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO prediction_history (roll_no, predicted_label, date_time)
        VALUES (?, ?, ?)
    """, (
        roll_no,
        predicted_label,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

    return render_template(
        "student_dashboard.html",
        name=student["name"],
        roll_no=student["roll_no"],
        attendance=student["attendance"],
        assignments=student["assignments_score"],
        midterm=student["midterm_score"],
        final=student["final_score"],
        study_hours=student["study_hours"],
        performance=student["performance"],
        predicted_performance=predicted_label,
        risk_level=risk,
        recommendation=rec,
        username=username
    )

# ---------- TEACHER: PREDICTION HISTORY ----------
@app.route("/prediction-history")
def prediction_history():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()
    label = request.args.get("label", "")
    sort = request.args.get("sort", "")

    query = """
        SELECT ph.id, ph.roll_no, ph.predicted_label, ph.date_time,
               s.name
        FROM prediction_history ph
        LEFT JOIN students s ON ph.roll_no = s.roll_no
        WHERE 1=1
    """
    params = []

    # 🔍 Search by roll no or name
    if search:
        query += " AND (CAST(ph.roll_no AS TEXT) LIKE ? OR LOWER(s.name) LIKE ?)"
        params.extend([f"%{search}%", f"%{search.lower()}%"])

    # 🏷 Filter by label
    if label:
        query += " AND ph.predicted_label = ?"
        params.append(label)

    # 🔃 Sorting
    if sort == "date_asc":
        query += " ORDER BY datetime(ph.date_time) ASC"
    else:
        query += " ORDER BY datetime(ph.date_time) DESC"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    history = [dict(r) for r in rows]

    return render_template(
        "prediction_history.html",
        history=history
    )

# ---------- STUDENT: OWN HISTORY ----------
@app.route("/student-history")
def student_history():
    if not login_required(role="student"):
        return redirect(url_for("login"))

    username = session.get("username")
    user = get_user_by_username(username)

    if not user or not user["roll_no"]:
        return "Your account is not linked to a student record. Contact admin."

    roll_no = user["roll_no"]

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, predicted_label, date_time 
        FROM prediction_history
        WHERE roll_no = ?
        ORDER BY datetime(date_time) DESC
    """, (roll_no,)).fetchall()
    conn.close()

    history = [dict(r) for r in rows]

    return render_template("student_history.html", history=history)

# ---------- PDF REPORT: STUDENT ----------
@app.route("/student-report/<int:roll_no>")
def student_report(roll_no):
    # both teacher & student can use, but student only for own roll_no
    if not login_required():
        return redirect(url_for("login"))

    username = session.get("username")
    role = session.get("role")
    user = get_user_by_username(username)

    if role == "student":
        if not user or not user["roll_no"] or int(user["roll_no"]) != roll_no:
            return "You are not allowed to download this report."

    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
    ).fetchone()
    conn.close()

    if student is None:
        return "Student not found."

    risk, rec = get_risk_and_recommendation(student)

    # model prediction
    features = np.array([[student["attendance"],
                          student["assignments_score"],
                          student["midterm_score"],
                          student["final_score"],
                          student["study_hours"]]])
    pred_encoded = model.predict(features)[0]
    predicted_label = label_encoder.inverse_transform([pred_encoded])[0]

    # --------- Build PDF (AI progress card style) ---------
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # header band
    c.setFillColor(colors.HexColor("#2563eb"))
    c.rect(0, height-80, width, 80, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, height-50, "AI Progress Report")

    # Student info
    c.setFillColor(colors.black)
    y = height - 110
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, f"Student: {student['name']}  (Roll: {student['roll_no']})")
    y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 30

    # Academic metrics
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Academic Metrics")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Attendance: {student['attendance']}%")
    y -= 16
    c.drawString(50, y, f"Assignments Score: {student['assignments_score']}")
    y -= 16
    c.drawString(50, y, f"Midterm Score: {student['midterm_score']}")
    y -= 16
    c.drawString(50, y, f"Final Exam Score: {student['final_score']}")
    y -= 16
    c.drawString(50, y, f"Study Hours/Day: {student['study_hours']}")
    y -= 28

    # Performance section
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Performance Summary")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Actual Performance: {student['performance']}")
    y -= 16
    c.drawString(50, y, f"AI Predicted Performance: {predicted_label}")
    y -= 16
    c.drawString(50, y, f"Risk Level: {risk}")
    y -= 28

    # Recommendations
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "AI Recommendations")
    y -= 18
    c.setFont("Helvetica", 11)

    from reportlab.lib.utils import simpleSplit
    lines = simpleSplit(rec, "Helvetica", 11, width - 80)
    for line in lines:
        c.drawString(50, y, "• " + line)
        y -= 14
        if y < 80:
            c.showPage()
            y = height - 80
            c.setFont("Helvetica", 11)

    c.showPage()
    c.save()
    buffer.seek(0)

    filename = f"Student_Report_{student['roll_no']}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

# ---------- CHATBOT ROUTE ----------
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    # optional: allow both logged-in teacher & student or even guests
    history = session.get("chat_history", [])

    if request.method == "POST":
        user_msg = request.form.get("message", "").strip()
        if user_msg:
            bot_msg = chatbot_reply(user_msg)
            history.append({"sender": "user", "text": user_msg})
            history.append({"sender": "bot", "text": bot_msg})
            session["chat_history"] = history

    return render_template("chatbot.html", history=history)

# ---------- ADMIN DASHBOARD ----------
@app.route("/admin-dashboard")
def admin_dashboard():
    if not login_required(role="admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()

    users = conn.execute("""
        SELECT id, username, role, roll_no
        FROM users
        ORDER BY role
    """).fetchall()

    students = conn.execute("SELECT * FROM students").fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        students=students
    )

from werkzeug.security import generate_password_hash

@app.route("/admin-add-student", methods=["POST"])
def admin_add_student():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    roll_no = int(request.form["roll_no"])
    name = request.form["name"]
    username = request.form["username"]
    password = request.form["password"]

    attendance = float(request.form["attendance"])
    assignments = float(request.form["assignments"])
    midterm = float(request.form["midterm"])
    final = float(request.form["final"])
    study_hours = float(request.form["study_hours"])
    performance = request.form["performance"]

    conn = get_db_connection()
    cur = conn.cursor()

    # 1️⃣ Insert into USERS (login)
    cur.execute("""
        INSERT INTO users (username, password, role, roll_no)
        VALUES (?, ?, 'student', ?)
    """, (
        username,
        generate_password_hash(password),
        roll_no
    ))

    # 2️⃣ Insert into STUDENTS (academic)
    cur.execute("""
        INSERT INTO students
        (roll_no, name, attendance, assignments_score, midterm_score, final_score, study_hours, performance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        roll_no, name, attendance, assignments, midterm, final, study_hours, performance
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


@app.route("/admin-add-user", methods=["POST"])
def admin_add_user():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    username = request.form["username"].strip()
    password = request.form["password"].strip()
    role = request.form["role"]
    roll_no = request.form.get("roll_no")

    from werkzeug.security import generate_password_hash
    hashed_pw = generate_password_hash(password)

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO users (username, password, role, roll_no)
            VALUES (?, ?, ?, ?)
        """, (
            username,
            hashed_pw,
            role,
            int(roll_no) if roll_no else None
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        return f"Error adding user: {e}"

    conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin-delete-user/<int:user_id>")
def admin_delete_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))

    
# ---------- ADMIN: UPLOAD CSV ----------
@app.route("/admin-upload-csv", methods=["POST"])
def admin_upload_csv():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    file = request.files.get("csv_file")
    if not file or not file.filename.endswith(".csv"):
        return "Invalid file. Please upload a CSV."

    try:
        df = pd.read_csv(file)

        required_cols = [
            "roll_no", "name", "attendance",
            "assignments_score", "midterm_score",
            "final_score", "study_hours", "performance"
        ]

        for col in required_cols:
            if col not in df.columns:
                return f"Missing column: {col}"

        # ===================== ADD THIS BLOCK =====================

        # 1. Remove empty strings (Excel CSV issue)
        df = df.replace(r'^\s*$', None, regex=True)

        # 2. Convert numeric columns safely
        numeric_cols = [
            "roll_no", "attendance",
            "assignments_score", "midterm_score",
            "final_score", "study_hours"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 3. Drop rows with invalid numeric data
        df = df.dropna(subset=numeric_cols)

        # 4. Final type casting (NOW SAFE)
        df["roll_no"] = df["roll_no"].astype(int)
        df["attendance"] = df["attendance"].astype(float)
        df["assignments_score"] = df["assignments_score"].astype(float)
        df["midterm_score"] = df["midterm_score"].astype(float)
        df["final_score"] = df["final_score"].astype(float)
        df["study_hours"] = df["study_hours"].astype(float)

        # Clean performance label
        df["performance"] = df["performance"].astype(str).str.strip().str.title()

        # ==========================================================

        conn = get_db_connection()

        for _, row in df.iterrows():
            conn.execute("""
                INSERT OR REPLACE INTO students
                (roll_no, name, attendance, assignments_score,
                 midterm_score, final_score, study_hours, performance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["roll_no"],
                row["name"],
                row["attendance"],
                row["assignments_score"],
                row["midterm_score"],
                row["final_score"],
                row["study_hours"],
                row["performance"]
            ))

        conn.commit()
        conn.close()

        return redirect(url_for("admin_dashboard"))

    except Exception as e:
        return f"CSV Upload Error: {e}"

if __name__ == "__main__":
    init_db_and_admin()
    app.run(host="0.0.0.0", port=5000)

