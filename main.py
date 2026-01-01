import streamlit as st
import pandas as pd
from src.database import get_latest_data, get_historical_data
from app.utils.locales import TRANSLATIONS
from app.components.charts import render_trend_chart

# 1. Setup & Language
st.set_page_config(page_title="TerraSync", layout="wide")

lang = st.sidebar.selectbox("Language / ቋንቋ / Afaan", ['en', 'am', 'om'])
t = TRANSLATIONS[lang]

if lang == 'am':
    st.markdown("<style> [lang='am'] { direction: rtl; } </style>", unsafe_allow_html=True)

st.title(t['title'])

# 2. Sidebar Controls
st.sidebar.header(t['control_panel'])
if st.sidebar.button(t['refresh']):
    st.rerun()

# 3. Load Data
df = get_latest_data()

if df.empty:
    st.error("No data found. Please run 'python run_hub.py' to generate data.")
else:
    # 4. Overview Metrics
    for _, row in df.iterrows():
        with st.expander(f"{row['farm_id']} - Status", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t['moisture'], f"{row['moisture']:.1f}%")
            c2.metric(t['ph'], f"{row['ph']:.1f}")
            c3.metric(t['temp'], f"{row['temp']:.1f}°C")
            
            # Translate Recommendation
            raw_rec = row['recommendation'] # e.g. "rec_plant_now | Disease: rec_healthy"
            try:
                plant_key, disease_part = raw_rec.split(" | Disease: ")
                plant_msg = t.get(plant_key, plant_key)
                disease_msg = t.get(disease_part, disease_part)
                final_rec = f"{plant_msg} | {disease_msg}"
            except:
                final_rec = raw_rec
                
            c4.success(f"Recommendation: {final_rec}")

            # 5. Charts
            history_df = get_historical_data(row['farm_id'])
            render_trend_chart(history_df, row['farm_id'], t)