import requests
import os
from dotenv import load_dotenv
from src.synthetic import generate_synthetic_sample

load_dotenv()

FARMS = {
    'Farm_1': {'channel_id': '3132615', 'key_env': 'THINGSPEAK_FARM_1_KEY'},
    'Farm_2': {'channel_id': '3132618', 'key_env': 'THINGSPEAK_FARM_2_KEY'},
    'Farm_3': {'channel_id': '3132619', 'key_env': 'THINGSPEAK_FARM_3_KEY'}
}

def fetch_weather():
    api_key = os.getenv('OWM_API_KEY')
    # Default to Addis Ababa
    url = f"https://api.openweathermap.org/data/2.5/weather?lat=9&lon=38.7&appid={api_key}&units=metric"
    try:
        resp = requests.get(url).json()
        return {
            'weather_temp': resp['main']['temp'],
            'weather_humidity': resp['main']['humidity'],
            'rain_prob': resp.get('rain', {}).get('1h', 0) * 100
        }
    except:
        return {'weather_temp': 25, 'weather_humidity': 60, 'rain_prob': 0}

def fetch_farm_data(farm_id):
    weather = fetch_weather()
    config = FARMS.get(farm_id)
    api_key = os.getenv(config['key_env'])
    
    url = f"https://api.thingspeak.com/channels/{config['channel_id']}/feeds.json?api_key={api_key}&results=1"
    
    try:
        data = requests.get(url).json()['feeds'][0]
        return {
            'farm_id': farm_id,
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
        print(f"Sensor fail for {farm_id}: {e}. Using synthetic data.")
        return generate_synthetic_sample(farm_id)