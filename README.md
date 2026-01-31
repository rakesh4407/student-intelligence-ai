# SparkAI – Student Performance Prediction and Recommendation System

SparkAI is a full-stack, AI-powered web application designed to predict student academic performance and provide personalized recommendations.  
The system uses Machine Learning techniques to identify at-risk students and support teachers, students, and administrators with data-driven insights.

This project is developed as a **2nd Year Engineering / BCA (AI & DS) Minor Project** and follows  **industry-level** standards.

---

## 🚀 Features

### 🔐 Role-Based Access Control

**Admin**
- Add / delete users  
- Upload student data via CSV  
- Manage student and user records  

**Teacher**
- View analytics dashboard  
- Identify at-risk students  
- View prediction history  
- Download AI-generated reports  

**Student**
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

**Input Features**
- Attendance  
- Assignment score  
- Midterm score  
- Final exam score  
- Study hours per day  

**Target Variable**
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



# Clone the repository
git clone https://github.com/rakesh4407/student-intelligence-ai.git

# Navigate to project directory
cd student-intelligence-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train the Machine Learning model
python model_train.py

# Run the application
python app.py


👨‍🎓 Author
RAKESH G
Engineering Student
AI / Machine Learning Minor Project
```
