import plotly.express as px
import streamlit as st
import pandas as pd  # <--- This was missing!

def render_trend_chart(df, farm_id, t):
    if df.empty:
        st.warning("No historical data available.")
        return

    # Convert timestamp to datetime if not already
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    sensors = ['moisture', 'temp', 'ph']
    fig = px.line(df, x='timestamp', y=sensors, 
                  title=f"Trends for {farm_id}",
                  labels={'value': 'Value', 'variable': 'Sensor'})
    st.plotly_chart(fig, use_container_width=True)