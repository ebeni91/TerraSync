import requests
import pandas as pd
import joblib
from datetime import datetime

# OpenWeatherMap API key
OWM_API_KEY = '13a9ce830a49cb77737bd918139c0363'
LOCATION = 'lat=9&lon=38.7'  # Addis Ababa for testing

farms = {
    'Farm_1': {'channel_id': '3132615', 'read_api_key': 'G6YRQL32254XMTOE'},
    'Farm_2': {'channel_id': '3132618', 'read_api_key': 'Y4ELEXLHUXM1D0YH'},
    'Farm_3': {'channel_id': '3132619', 'read_api_key': 'BLXEREJOHOOWP8PK'}
}

# Load models
planting_model = joblib.load('planting_model.pkl')
disease_model = joblib.load('disease_model.pkl')


def fetch_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?{LOCATION}&appid={OWM_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        return {
            'weather_temp': response['main']['temp'],
            'weather_humidity': response['main']['humidity'],
            'rain_prob': response.get('rain', {}).get('1h', 0) * 100
        }
    except Exception as e:
        print(f"Weather fetch error: {e}. Using defaults.")
        return {'weather_temp': 25, 'weather_humidity': 60, 'rain_prob': 0}


weather = fetch_weather()


def fetch_farm_data(farm_id, channel_id, api_key):
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}&results=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['feeds']
        if not data:
            return None
        data = data[0]
        return {
            'farm_id': farm_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'moisture': float(data.get('field1', 0)),
            'ph': float(data.get('field2', 0)),
            'temp': float(data.get('field3', 0)),
            'humidity': float(data.get('field4', 0)),
            'nitrogen': float(data.get('field5', 0)),
            'phosphorus': float(data.get('field6', 0)),
            'potassium': float(data.get('field7', 0)),
            **weather
        }
    except Exception as e:
        print(f"Error fetching data for {farm_id}: {e}")
        return None


def get_synthetic_data(farm_id):
    try:
        df = pd.read_csv('farm_data_synthetic.csv')
        farm_data = df[df['farm_id'] == farm_id].sample(n=1, random_state=None).iloc[0]
        return {
            'farm_id': farm_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'moisture': float(farm_data['moisture']),
            'ph': float(farm_data['ph']),
            'temp': float(farm_data['temp']),
            'humidity': float(farm_data['humidity']),
            'nitrogen': float(farm_data['nitrogen']),
            'phosphorus': float(farm_data['phosphorus']),
            'potassium': float(farm_data['potassium']),
            'weather_temp': float(farm_data['weather_temp']),
            'weather_humidity': float(farm_data['weather_humidity']),
            'rain_prob': float(farm_data['rain_prob'])
        }
    except Exception as e:
        print(f"Error loading synthetic data for {farm_id}: {e}")
        return None


def get_recommendation(data, planting_model, disease_model):
    features = [[data['moisture'], data['ph'], data['temp'], data['humidity'],
                 data['nitrogen'], data['phosphorus'], data['potassium'],
                 data['weather_temp'], data['weather_humidity'], data['rain_prob']]]

    # Planting prediction
    planting_pred = planting_model.predict(features)[0]
    issues = []
    if data['moisture'] < 30:
        issues.append("Water the soil (moisture too low).")
    if not 6.0 <= data['ph'] <= 6.8:
        issues.append("Adjust pH (add lime if acidic, sulfur if basic).")
    if not 18 <= data['temp'] <= 29:
        issues.append("Temperature not ideal.")
    if data['nitrogen'] < 50:
        issues.append("Add nitrogen fertilizer.")
    if data['rain_prob'] > 70:
        issues.append("High rain probability—delay actions to avoid flooding.")

    planting_rec = "Good to plant now!" if planting_pred == 1 and not issues else "Wait and fix: " + "; ".join(
        issues) if issues else "Wait (ML predicts poor conditions)."

    # Disease prediction
    disease_pred = disease_model.predict(features)[0]
    disease_rec = {
        0: "Healthy: No disease detected.",
        1: "Warning: Early Blight risk. Reduce moisture, improve air circulation.",
        2: "Warning: Fusarium Wilt risk. Check soil drainage, adjust pH."
    }[disease_pred]

    return f"{planting_rec} | Disease: {disease_rec}"


# Main loop
all_data = []
for farm_id, info in farms.items():
    data = fetch_farm_data(farm_id, info['channel_id'], info['read_api_key'])
    if data is None:
        print(f"Using synthetic data for {farm_id}")
        data = get_synthetic_data(farm_id)

    if data:
        data['recommendation'] = get_recommendation(data, planting_model, disease_model)
        all_data.append(data)
        print(f"{farm_id}: {data['recommendation']}")

if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv('latest_farm_data.csv', index=False)
    print("Data saved with planting and disease recommendations.")