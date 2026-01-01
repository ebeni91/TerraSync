import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 100
n_farms = 3
total_samples = n_samples * n_farms

# Sensor and weather data
data = {
    'farm_id': np.repeat([f'Farm_{i+1}' for i in range(n_farms)], n_samples),
    'moisture': np.random.uniform(20, 80, total_samples),
    'ph': np.random.uniform(5, 8, total_samples),
    'temp': np.random.uniform(15, 35, total_samples),
    'humidity': np.random.uniform(40, 90, total_samples),
    'nitrogen': np.random.uniform(30, 120, total_samples),
    'phosphorus': np.random.uniform(20, 100, total_samples),
    'potassium': np.random.uniform(40, 130, total_samples),
    'weather_temp': np.random.uniform(18, 29, total_samples),
    'weather_humidity': np.random.uniform(50, 80, total_samples),
    'rain_prob': np.random.uniform(0, 100, total_samples)
}

df = pd.DataFrame(data)

# Planting label
df['planting_label'] = ((df['moisture'] > 30) &
                        (df['ph'].between(6.0, 6.8)) &
                        (df['temp'].between(18, 29)) &
                        (df['nitrogen'] > 50) &
                        (df['phosphorus'] > 30) &
                        (df['potassium'] > 50) &
                        (df['rain_prob'] < 70)).astype(int)

# Disease label: 0 = Healthy, 1 = Early Blight, 2 = Fusarium Wilt
df['disease_label'] = 0  # Default: Healthy
df.loc[(df['moisture'] > 60) & (df['humidity'] > 70) & (df['temp'].between(20, 25)) & (df['rain_prob'] > 50), 'disease_label'] = 1  # Early Blight
df.loc[(df['temp'] > 28) & (df['ph'] < 6.0) & (df['moisture'].between(40, 60)), 'disease_label'] = 2  # Fusarium Wilt

df.to_csv('farm_data_synthetic.csv', index=False)
print("Synthetic data updated with planting and disease labels.")
print(df.head())