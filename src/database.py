import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "terrasync.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table for sensor readings
    c.execute('''CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id TEXT,
                    timestamp DATETIME,
                    moisture REAL, ph REAL, temp REAL, humidity REAL,
                    nitrogen REAL, phosphorus REAL, potassium REAL,
                    weather_temp REAL, weather_humidity REAL, rain_prob REAL,
                    recommendation TEXT
                )''')
    conn.commit()
    conn.close()

def save_reading(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO readings 
                 (farm_id, timestamp, moisture, ph, temp, humidity, nitrogen, phosphorus, potassium, 
                  weather_temp, weather_humidity, rain_prob, recommendation)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['farm_id'], datetime.now(), data['moisture'], data['ph'], data['temp'], 
               data['humidity'], data['nitrogen'], data['phosphorus'], data['potassium'],
               data['weather_temp'], data['weather_humidity'], data['rain_prob'], data['recommendation']))
    conn.commit()
    conn.close()

def get_latest_data():
    conn = sqlite3.connect(DB_NAME)
    # Get the most recent row for each unique farm_id
    query = '''SELECT * FROM readings 
               WHERE id IN (SELECT MAX(id) FROM readings GROUP BY farm_id)'''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_historical_data(farm_id, hours=24):
    conn = sqlite3.connect(DB_NAME)
    query = f"SELECT * FROM readings WHERE farm_id = ? ORDER BY timestamp DESC LIMIT ?"
    # Rough estimate: 6 readings per hour * hours
    limit = 6 * hours 
    df = pd.read_sql_query(query, conn, params=(farm_id, limit))
    conn.close()
    return df