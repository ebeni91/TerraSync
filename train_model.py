import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv('farm_data_synthetic.csv')

# Features
X = df[['moisture', 'ph', 'temp', 'humidity', 'nitrogen', 'phosphorus', 'potassium',
        'weather_temp', 'weather_humidity', 'rain_prob']]

# Planting model
y_planting = df['planting_label']
X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(X, y_planting, test_size=0.2, random_state=42)
planting_model = RandomForestClassifier(n_estimators=50, random_state=42)
planting_model.fit(X_train_p, y_train_p)
planting_acc = accuracy_score(y_test_p, planting_model.predict(X_test_p))
print(f"Planting Model Accuracy: {planting_acc:.2f}")

# Disease model
y_disease = df['disease_label']
X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X, y_disease, test_size=0.2, random_state=42)
disease_model = RandomForestClassifier(n_estimators=50, random_state=42)
disease_model.fit(X_train_d, y_train_d)
disease_acc = accuracy_score(y_test_d, disease_model.predict(X_test_d))
print(f"Disease Model Accuracy: {disease_acc:.2f}")

# Save models
joblib.dump(planting_model, 'planting_model.pkl')
joblib.dump(disease_model, 'disease_model.pkl')
# print("Models saved: planting_model.pkl, disease_model.pkl")