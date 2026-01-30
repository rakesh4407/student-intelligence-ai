
# SparkAI – Student Performance Prediction and Recommendation System

SparkAI is a full-stack AI-powered web application designed to predict student academic performance and provide personalized recommendations. The system leverages Machine Learning techniques to identify at-risk students and assist teachers, students, and administrators with data-driven insights.

This project is developed as a **2nd Year Engineering Project** and follows both **academic (IEEE)** and **industry-level** standards.

---

## 🚀 Features

### 🔐 Role-Based Access Control

- **Admin**
  - Add / delete users
  - Upload student data via CSV
  - Manage student and user records
- **Teacher**
  - View analytics dashboard
  - Identify at-risk students
  - View prediction history
  - Download AI-generated reports
- **Student**
  - View personal academic dashboard
  - Receive AI-based recommendations
  - Track prediction history
  - Download performance PDF report

---

### 🤖 Artificial Intelligence & Machine Learning

- Student performance prediction using **Random Forest Classifier**
- Performance categories:
  - Excellent
  - Good
  - Average
  - Poor
- Risk level classification:
  - High
  - Medium
  - Low
- Personalized academic recommendations based on performance metrics

---

### 📊 Dashboards & Analytics

- Teacher analytics dashboard
- Student performance dashboard
- Prediction history logs
- CSV-based bulk student upload

---

### 💬 AI Chatbot

- Rule-based AI academic assistant
- Provides guidance on:
  - Attendance improvement
  - Study planning
  - Exam preparation
  - CGPA enhancement
- Integrated clean and modern UI

---

### 📄 PDF Report Generation

- AI-generated student progress report
- Includes:
  - Academic metrics
  - Predicted performance
  - Risk level
  - Personalized recommendations

---

## 🧠 Machine Learning Model Details

- **Algorithm**: Random Forest Classifier
- **Library**: Scikit-learn
- **Input Features**:
  - Attendance
  - Assignment score
  - Midterm score
  - Final exam score
  - Study hours per day
- **Target Variable**:
  - Performance category

The trained model and label encoder are serialized using `joblib`.

---

## 🗂 Project Structure

SparkAI-Student-Performance-Prediction/
│
├── app.py # Main Flask application
├── model_train.py # Model training & evaluation
├── create_admin.py # Admin creation script
├── student_data.csv # Sample dataset
├── requirements.txt # Python dependencies
│
├── ml_model/
│ ├── performance_model.joblib
│ └── label_encoder.joblib
│
├── database/
│ └── student_system.db
│
├── templates/
│ ├── index.html
│ ├── login.html
│ ├── teacher_dashboard.html
│ ├── student_dashboard.html
│ ├── admin_dashboard.html
│ ├── result.html
│ ├── chatbot.html
│ └── other templates
│
├── static/
│ ├── css/
│ ├── js/
│ └── images/
│
└── .gitignore

yaml
Copy code

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/omdhanwat368-create/EduAI-Student-Performance-Prediction.git
cd EduAI-Student-Performance-Prediction
2️⃣ Create Virtual Environment
bash
Copy code
python -m venv venv
Activate the environment:

Windows

bash
Copy code
venv\Scripts\activate
macOS / Linux

bash
Copy code
source venv/bin/activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Train the Machine Learning Model
bash
Copy code
python model_train.py
5️⃣ Run the Application
bash
Copy code
python app.py
Open your browser and visit:

cpp
Copy code
http://127.0.0.1:5000
📂 Dataset
The project uses a synthetic student dataset (student_data.csv) created for academic and research purposes.

Dataset Columns
roll_no

name

attendance

assignments_score

midterm_score

final_score

study_hours

performance

🧪 Model Evaluation Metrics
Accuracy

Precision

Recall

F1-Score

Confusion Matrix

(Model evaluation results are displayed during training.)

📌 Use Cases
Early identification of at-risk students

Personalized academic guidance

Decision support for teachers

Educational data analytics

🔮 Future Enhancements
Deep Learning-based models

Large Language Model (LLM) powered chatbot

Real-time analytics

Cloud deployment

Mobile-first responsive UI

👨‍🎓 Author
RAKESH G
Engineering Student
AI / Machine Learning Minor Project
```
