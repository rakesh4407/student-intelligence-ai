import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# ---------------- LOAD DATA ----------------
df = pd.read_csv("student_data.csv")

# ---------------- DATA CLEANING ----------------
# Remove missing / invalid labels
df = df.dropna(subset=["performance"])
df = df[df["performance"].astype(str).str.strip() != ""]

# Normalize labels
df["performance"] = df["performance"].str.strip().str.title()


print("Class distribution:\n", df["performance"].value_counts())

np.random.seed(42)

# 1️⃣ Score noise (students don't perform identically every time)
score_cols = [
    "assignments_score",
    "midterm_score",
    "final_score"
]

for col in score_cols:
    noise = np.random.normal(loc=0, scale=3, size=len(df))
    df[col] = (df[col] + noise).clip(0, 100).round()

noise_fraction = 0.05
n_noisy = int(len(df) * noise_fraction)

indices = np.random.choice(df.index, n_noisy, replace=False)
labels = df["performance"].unique()

for idx in indices:
    current_label = df.at[idx, "performance"]
    df.at[idx, "performance"] = np.random.choice(
        [l for l in labels if l != current_label]
    )

# ---------------- FEATURES & TARGET ----------------
X = df[
    ["attendance", "assignments_score", "midterm_score", "final_score", "study_hours"]
]

le = LabelEncoder()
y = le.fit_transform(df["performance"])

# ---------------- STRATIFIED SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

# ---------------- MODEL ----------------
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# ---------------- EVALUATION ----------------
y_pred = model.predict(X_test)

print(f"\nAccuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=le.classes_,
    zero_division=0
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ---------------- FEATURE IMPORTANCE ----------------
feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

print("\nFeature Importance:")
print(feature_importance)

# ---------------- SAVE MODEL ----------------
joblib.dump(model, "ml_model/performance_model.joblib")
joblib.dump(le, "ml_model/label_encoder.joblib")

print("\n✔ model trained and saved successfully!")
