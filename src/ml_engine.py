import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from src.synthetic import generate_training_data

MODEL_DIR = "models"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

PLANTING_PATH = f"{MODEL_DIR}/planting_model.pkl"
DISEASE_PATH = f"{MODEL_DIR}/disease_model.pkl"

def train_if_missing():
    """Trains models only if they don't exist."""
    if os.path.exists(PLANTING_PATH) and os.path.exists(DISEASE_PATH):
        return

    print("Training new models...")
    df = generate_training_data()
    X = df[['moisture', 'ph', 'temp', 'humidity', 'nitrogen', 'phosphorus', 'potassium', 
            'weather_temp', 'weather_humidity', 'rain_prob']]
    
    # Train Planting
    p_model = RandomForestClassifier(n_estimators=50)
    p_model.fit(X, df['planting_label'])
    joblib.dump(p_model, PLANTING_PATH)
    
    # Train Disease
    d_model = RandomForestClassifier(n_estimators=50)
    d_model.fit(X, df['disease_label'])
    joblib.dump(d_model, DISEASE_PATH)

def predict(data):
    """Returns a recommendation string based on data."""
    train_if_missing()
    p_model = joblib.load(PLANTING_PATH)
    d_model = joblib.load(DISEASE_PATH)
    
    features = [[data['moisture'], data['ph'], data['temp'], data['humidity'],
                 data['nitrogen'], data['phosphorus'], data['potassium'],
                 data['weather_temp'], data['weather_humidity'], data['rain_prob']]]
                 
    # Logic + ML Hybrid Approach
    planting_pred = p_model.predict(features)[0]
    disease_pred = d_model.predict(features)[0]
    
    # Planting Logic
    issues = []
    if data['moisture'] < 30: issues.append("rec_water")
    if not 6.0 <= data['ph'] <= 6.8: issues.append("rec_ph")
    if data['rain_prob'] > 70: issues.append("rec_rain")
    
    if planting_pred == 1 and not issues:
        planting_msg = "rec_plant_now"
    else:
        planting_msg = issues[0] if issues else "rec_wait"

    # Disease Logic
    disease_msg = {0: "rec_healthy", 1: "rec_blight", 2: "rec_wilt"}.get(disease_pred, "rec_healthy")
    
    return f"{planting_msg} | Disease: {disease_msg}"