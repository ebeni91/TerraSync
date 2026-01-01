# Import libraries: These are like including tools
import requests  # Helps talk to the internet
import pandas as pd  # Helps handle data like a table
#import numpy as np
# Your ThingSpeak details (replace with yours)
channel_id = '3132136'  # e.g., '123456'
read_api_key = 'H1EG3TY7FE8TR9VS'  # e.g., 'ABCDEF1234567890'
num_results = 10  # How many data points to fetch (e.g., last 10 readings)

# Build the URL to ask ThingSpeak for data
url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_api_key}&results={num_results}"
# Send a request to get the data (like visiting a webpage)
response = requests.get(url)
# Turn the response into usable data (JSON is like a dictionary)
data = response.json()
# Get the 'feeds' part, which has the sensor readings
feeds = data['feeds']
# Turn it into a table (DataFrame) with pandas
df = pd.DataFrame(feeds)
# Clean the data: Make numbers actual numbers (not text)
# Assuming fields: field1=moisture, field2=ph, field3=temp, field4=humidity, field5=nitrogen, etc.
df['moisture'] = pd.to_numeric(df['field1'], errors='coerce')  # 'coerce' means ignore bad data
df['ph'] = pd.to_numeric(df['field2'], errors='coerce')
df['temp'] = pd.to_numeric(df['field3'], errors='coerce')
df['humidity'] = pd.to_numeric(df['field4'], errors='coerce')
df['nitrogen'] = pd.to_numeric(df['field5'], errors='coerce')
df['phosphorus'] = pd.to_numeric(df['field6'], errors='coerce')
df['potassium'] = pd.to_numeric(df['field7'], errors='coerce')

# Drop rows with missing data
df = df.dropna(subset=['moisture', 'ph', 'temp'])  # Add more columns as needed
# Print the data to see it
print(df[['moisture', 'ph', 'temp', 'humidity', 'nitrogen', 'phosphorus', 'potassium']])
# Save to a file for later (optional)
df.to_csv('farm_data.csv', index=False)  # Creates a CSV file like Excel

#             #Simple Rule-Based Analysis
# # Get the latest reading (last row in the table)
latest = df.iloc[-1]  # iloc[-1] means the last row
#
# #Define rules for a crop like tomatoes (adjust based on research)
# if latest['moisture'] < 40:
#     recommendation = "Soil is too dry. Water the farm!"
# elif latest['ph'] < 6 or latest['ph'] > 7:
#     recommendation = "pH is off. Add lime if too acidic or sulfur if too basic."
# elif latest['temp'] < 20 or latest['temp'] > 30:
#     recommendation = "Temperature not ideal. Wait for better weather."
# else:
#     recommendation = "Conditions good! Best time to plant."
#
# # For seasons: Simple example based on temp (real would use date or weather API)
# if latest['temp'] > 15:
#     season_advice = "Spring/Summer: Good for warm-season crops like tomatoes."
# else:
#     season_advice = "Fall/Winter: Try cold-season crops like lettuce."
# #
# # Print recommendations
# print("\nRecommendation:", recommendation)
# print("Season Advice:", season_advice)

#################################################################
                #ADDING RANDOM SAMPLE DATA
#################################################################


#################################################################
#################################################################






                        #DATA TRAINING
#################################################################
                       #DATA TRAINING 01
#################################################################

# Import ML tools
from sklearn.model_selection import train_test_split  # Splits data for training/testing
from sklearn.ensemble import RandomForestClassifier  # A simple ML model (like a smart decision tree)
from sklearn.metrics import accuracy_score  # Checks how good the model is

# Create labels for training: 1 = good for planting, 0 = bad
# Based on rules (for demo; in real, collect more data)
df['label'] = ((df['moisture'] > 40) &
               (df['ph'].between(6, 7)) &
               (df['temp'].between(20, 30)) &
               (df['nitrogen'] > 50)).astype(int)  # astype(int) makes it 0/1

# Features (inputs): The sensor data
X = df[['moisture', 'ph', 'temp', 'humidity', 'nitrogen', 'phosphorus', 'potassium']]

# Labels (output): The good/bad
y = df['label']

# Split data: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)  # random_state for reproducibility

# Create and train model
model = RandomForestClassifier(n_estimators=10)  # 10 trees; simple
model.fit(X_train, y_train)  # Fit means train

# Test it
predictions = model.predict(X_test)
print("Model Accuracy:", accuracy_score(y_test, predictions))  # Should be high if data is simple

# Predict on latest data
latest_data = latest[['moisture', 'ph', 'temp', 'humidity', 'nitrogen', 'phosphorus', 'potassium']].values.reshape(1, -1)  # Reshape for single row
ml_prediction = model.predict(latest_data)[0]

if ml_prediction == 1:
    ml_recommendation = "ML says: Good to plant!"
else:
    ml_recommendation = "ML says: Wait and improve conditions."

print(ml_recommendation)



                        #DATA TRAINING 02
#################################################################
