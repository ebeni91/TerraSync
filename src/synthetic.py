import pandas as pd
import numpy as np

def generate_synthetic_sample(farm_id):
    """Generates a single realistic data point for fallback."""
    return {
        'farm_id': farm_id,
        'moisture': np.random.uniform(20, 80),
        'ph': np.random.uniform(5, 8),
        'temp': np.random.uniform(15, 35),
        'humidity': np.random.uniform(40, 90),
        'nitrogen': np.random.uniform(30, 120),
        'phosphorus': np.random.uniform(20, 100),
        'potassium': np.random.uniform(40, 130),
        'weather_temp': np.random.uniform(18, 29),
        'weather_humidity': np.random.uniform(50, 80),
        'rain_prob': np.random.uniform(0, 100)
    }

def generate_training_data(n_samples=300):
    """Generates bulk data for training models."""
    np.random.seed(42)
    data = {
        'moisture': np.random.uniform(20, 80, n_samples),
        'ph': np.random.uniform(5, 8, n_samples),
        'temp': np.random.uniform(15, 35, n_samples),
        'humidity': np.random.uniform(40, 90, n_samples),
        'nitrogen': np.random.uniform(30, 120, n_samples),
        'phosphorus': np.random.uniform(20, 100, n_samples),
        'potassium': np.random.uniform(40, 130, n_samples),
        'weather_temp': np.random.uniform(18, 29, n_samples),
        'weather_humidity': np.random.uniform(50, 80, n_samples),
        'rain_prob': np.random.uniform(0, 100, n_samples)
    }
    df = pd.DataFrame(data)
    
    # Apply Logic Labels
    df['planting_label'] = ((df['moisture'] > 30) & (df['ph'].between(6.0, 6.8)) & 
                            (df['temp'].between(18, 29)) & (df['nitrogen'] > 50) & 
                            (df['rain_prob'] < 70)).astype(int)
                            
    df['disease_label'] = 0 # Healthy
    df.loc[(df['moisture'] > 60) & (df['humidity'] > 70) & (df['temp'].between(20, 25)), 'disease_label'] = 1 # Blight
    df.loc[(df['temp'] > 28) & (df['ph'] < 6.0), 'disease_label'] = 2 # Wilt
    
    return df