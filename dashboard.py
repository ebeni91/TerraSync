import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import numpy as np

# Define farms dictionary early to avoid unresolved reference
farms = {
    'Farm_1': {'channel_id': '3132615', 'read_api_key': 'G6YRQL32254XMTOE'},
    'Farm_2': {'channel_id': '3132618', 'read_api_key': 'Y4ELEXLHUXM1D0YH'},
    'Farm_3': {'channel_id': '3132619', 'read_api_key': 'BLXEREJOHOOWP8PK'}
}

# Translation dictionaries (English, Amharic, Oromo)
translations = {
    'en': {
        'title': 'TerraSync Dashboard',
        'control_panel': 'Control Panel',
        'select_language': 'Select Language',
        'select_farm': 'Select Farms',
        'select_sensors': 'Select Sensors for Trends',
        'time_range': 'Select Time Range (hours ago)',
        'comparison': 'Farm Comparison',
        'detailed_view': 'Detailed View: {}',
        'moisture': 'Moisture',
        'ph': 'pH',
        'temperature': 'Temperature',
        'humidity': 'Humidity',
        'nitrogen': 'Nitrogen',
        'phosphorus': 'Phosphorus',
        'potassium': 'Potassium',
        'weather_temp': 'Weather Temp',
        'weather_humidity': 'Weather Humidity',
        'rain_prob': 'Rain Probability',
        'timestamp': 'Timestamp',
        'recommendation': 'Recommendation & Disease Status',
        'send_rec': 'Send Recommendation to {}',
        'trends': 'Historical Trends for {}',
        'overview': 'All Farms Overview',
        'refresh': 'Refresh Data',
        'no_data': 'No data available. Run hub.py to generate data.',
        'no_realtime': 'No real-time data for {}. Using synthetic data.',
        'no_trends': 'No historical data from ThingSpeak for {}. Showing synthetic trends.',
        'no_filtered_data': 'No data in selected range. Adjust filters.',
        'sent_rec': 'Simulated sending recommendation to {}: "{}"',
        'stats': 'Summary Statistics',
        'rec_plant_now': 'Good to plant now!',
        'rec_water': 'Water the soil (moisture too low).',
        'rec_ph': 'Adjust pH (add lime if acidic, sulfur if basic).',
        'rec_temp': 'Temperature not ideal.',
        'rec_nitrogen': 'Add nitrogen fertilizer.',
        'rec_rain': 'High rain probability—delay actions to avoid flooding.',
        'rec_wait': 'Wait (ML predicts poor conditions).',
        'rec_healthy': 'Healthy: No disease detected.',
        'rec_blight': 'Warning: Early Blight risk. Reduce moisture, improve air circulation.',
        'rec_wilt': 'Warning: Fusarium Wilt risk. Check soil drainage, adjust pH.'
    },
    'am': {
        'title': 'TerraSync Dashboard',
        'control_panel': 'የቁጥጥር ፓነል',
        'select_language': 'ቋንቋ ይምረጡ',
        'select_farm': 'አካባቢዎችን ይምረጡ',
        'select_sensors': 'የአዝዛኛ መለኪያዎችን ያስቀምጡ',
        'time_range': 'ጊዜ ወርቅ (ሰዓቶች በፊት)',
        'comparison': 'አካባቢ ንጽጽር',
        'detailed_view': 'ዝርዝር እይታ: {}',
        'moisture': 'የምድር እርጥበት',
        'ph': 'pH ደረጃ',
        'temperature': 'ሙቀት',
        'humidity': 'እርጥበት',
        'nitrogen': 'ናይትሮጅን',
        'phosphorus': 'ፎስፎረስ',
        'potassium': 'ፓታሲየም',
        'weather_temp': 'የአየር ሙቀት',
        'weather_humidity': 'የአየር እርጥበት',
        'rain_prob': 'የዝናብ አስደሳችነት',
        'timestamp': 'ጊዜ ምልክት',
        'recommendation': 'የመመከር ምክር እና የበሽታ ሁኔታ',  # Uses ' እና ' as separator
        'send_rec': 'አማራጭ ወደ {} ይላኩ',
        'trends': 'ታሪካዊ አዝዛኛዎች ለ {}',
        'overview': 'ሁሉም አካባቢዎች አጠቃላይ እይታ',
        'refresh': 'ዳግም አስጀብሩ',
        'no_data': 'ምንም ውሂብ የለም። ሃብ.py ያሂዱ።',
        'no_realtime': 'ለ {} ምንም ተግባራዊ ውሂብ የለም። ሰው ሰራሽ ውሂብ በመጠቀም።',
        'no_trends': 'ለ {} ከ ThingSpeak ምንም ታሪካዊ ውሂብ የለም። ሰው ሰራሽ አዝዛኛዎችን እያሳየ ነው።',
        'no_filtered_data': 'በተመረጠው ክልል ውስጥ ምንም ውሂብ የለም። ማጣሪያዎችን ያስተካክሉ።',
        'sent_rec': '{} ላክን፡ "{}"',
        'stats': 'የተጠቃለለ ስታቲስቲክስ',
        'rec_plant_now': 'አሁን ተባል!',
        'rec_water': 'ምድር አሟል (እርጥበት በጣም ዝቅተኛ ነው)።',
        'rec_ph': 'pH አስተካክል (አሲዳማ ከሆነ ላይም ጨምር፣ መሰረታዊ ከሆነ ሰልፈር)።',
        'rec_temp': 'ሙቀት ተስማሚ አይደለም።',
        'rec_nitrogen': 'የናይትሮጅን ማዳበሪያ ጨምር።',
        'rec_rain': 'ከፍተኛ የዝናብ እድል—ጎርፍን ለመከላከል ተግባራትን አስተካክል።',
        'rec_wait': 'ጠብቅ (ML ደካማ ሁኔታዎችን ይተነብያል)።',
        'rec_healthy': 'ጤናማ፡ ምንም በሽታ አልተገኘም።',
        'rec_blight': 'ማስጠንቀቂያ፡ የቅድመ ብላይት አደጋ። እርጥበትን ቀንስ፣ የአየር ዝውውርን አሻሽል።',
        'rec_wilt': 'ማስጠንቀቂያ፡ የፉዛሪየም ዊልት አደጋ። የምድር ፍሳሽ እና pH አስተካክል።'
    },
    'om': {
        'title': 'TerraSync Dashboard',
        'control_panel': 'Paaneelii Too’achuu',
        'select_language': 'Afaan Qopheesse',
        'select_farm': 'Addaayyaan Biyyaa',
        'select_sensors': 'Qoricha Biyyaa Biyyaa',
        'time_range': 'Ittin Gabaaba (saawwi)',
        'comparison': 'Qoricha Addaayyaan',
        'detailed_view': 'Qoricha Qorannoo: {}',
        'moisture': 'Qixxii Uummaa',
        'ph': 'pH Mata Duree',
        'temperature': 'Haala Jireenya',
        'humidity': 'Qixxummaa',
        'nitrogen': 'Niitroojiini',
        'phosphorus': 'Fosfoorasiisii',
        'potassium': 'Potaasiyami',
        'weather_temp': 'Haala Ayyanaa',
        'weather_humidity': 'Qixxummaa Ayyanaa',
        'rain_prob': 'Aadaa Barii',
        'timestamp': 'Mata Duraa',
        'recommendation': 'Qoricha Biyyaa fi Haala Dhukkuba',  # Uses ' fi ' as separator
        'send_rec': 'Qoricha Biyyaa {}',
        'trends': 'Qoricha Addaayyaan {}',
        'overview': 'Addaayyaan Biyya Biyyaa',
        'refresh': 'Dabalee Deebisuu',
        'no_data': 'Hin Barame. hub.py qopheessi.',
        'no_realtime': 'Hin barame {}-f. Data uumamaa fayyadamuu.',
        'no_trends': '{}-f ThingSpeak irraa hin barame. Data uumamaa agarsiisuu.',
        'no_filtered_data': 'Gama qoratame keessatti hin barame. Filteerota deebisuu.',
        'sent_rec': '{}-f ergamuu: "{}"',
        'stats': 'Istaatistiksii Gabaabaa',
        'rec_plant_now': 'Amma uumuu!',
        'rec_water': 'Uumaa deebisuu (qixxii uummaa gadi).',
        'rec_ph': 'pH deebisuu (asidii ta’e laayimii, basaasii ta’e salfara).',
        'rec_temp': 'Haala jireenya hin ta’u.',
        'rec_nitrogen': 'Niitroojiini kuu.',
        'rec_rain': 'Aadaa barii guddaa—lolaa irraa of qusachuu.',
        'rec_wait': 'Tarii (ML haala gadii ragaa).',
        'rec_healthy': 'Caafimaad qaba: Dhukkuba hin argamne.',
        'rec_blight': 'Akeekkachiisa: Early Blight. Qixxii uummaa gadi, qilleensa deebisuu.',
        'rec_wilt': 'Akeekkachiisa: Fusarium Wilt. Uumaa uummaa fi pH deebisuu.'
    }
}

# Language-specific separators for splitting recommendation string
separators = {
    'en': ' & ',
    'am': ' እና ',
    'om': ' fi '
}

# RTL for Amharic
st.markdown("<style> [lang='am'] { direction: rtl; } </style>", unsafe_allow_html=True)

# Define language and translation dictionary
lang = st.sidebar.selectbox(
    translations['en']['select_language'],  # Use English key to avoid undefined 't'
    options=['en', 'am', 'om'],
    format_func=lambda x: {'en': 'English', 'am': 'አማርኛ', 'om': 'Afaan Oromoo'}[x]
)
t = translations[lang]  # Define t after lang selection

# Sidebar
st.sidebar.header(t['control_panel'])
selected_farms = st.sidebar.multiselect(t['select_farm'], list(farms.keys()), default=[list(farms.keys())[0]])
show_sensors = st.sidebar.multiselect(t['select_sensors'],
                                      ['moisture', 'temp', 'ph', 'humidity', 'nitrogen', 'phosphorus', 'potassium',
                                       'weather_temp', 'weather_humidity', 'rain_prob'],
                                      default=['moisture', 'temp'])
date_range = st.sidebar.slider(t['time_range'], 1, 24, 12)


# Data fetch functions
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
            'weather_temp': float(data.get('field8', 0)),
            'weather_humidity': float(data.get('field9', 0)),
            'rain_prob': float(data.get('field10', 0))
        }
    except Exception as e:
        print(f"Dashboard: Error fetching data for {farm_id}: {e}")
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
        print(f"Dashboard: Error loading synthetic data for {farm_id}: {e}")
        return None


def fetch_historical_data(farm_id, channel_id, api_key, results=50):
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}&results={results}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        hist_data = response.json()['feeds']
        hist_df = pd.DataFrame(hist_data)
        hist_df['moisture'] = pd.to_numeric(hist_df['field1'], errors='coerce')
        hist_df['temp'] = pd.to_numeric(hist_df['field3'], errors='coerce')
        hist_df['ph'] = pd.to_numeric(hist_df['field2'], errors='coerce')
        hist_df['humidity'] = pd.to_numeric(hist_df['field4'], errors='coerce')
        hist_df['nitrogen'] = pd.to_numeric(hist_df['field5'], errors='coerce')
        hist_df['phosphorus'] = pd.to_numeric(hist_df['field6'], errors='coerce')
        hist_df['potassium'] = pd.to_numeric(hist_df['field7'], errors='coerce')
        hist_df['weather_temp'] = pd.to_numeric(hist_df.get('field8', 0), errors='coerce')
        hist_df['weather_humidity'] = pd.to_numeric(hist_df.get('field9', 0), errors='coerce')
        hist_df['rain_prob'] = pd.to_numeric(hist_df.get('field10', 0), errors='coerce')
        hist_df['created_at'] = pd.to_datetime(hist_df['created_at'])
        return hist_df
    except:
        hist_df = pd.read_csv('farm_data_synthetic.csv')
        hist_df = hist_df[hist_df['farm_id'] == farm_id].tail(50)
        hist_df['created_at'] = pd.date_range(end=datetime.now(), periods=len(hist_df), freq='10min')
        return hist_df


# Main dashboard
st.title(t['title'])

# Load latest data
try:
    df = pd.read_csv('latest_farm_data.csv')
except:
    df = pd.DataFrame()
    st.warning(t['no_data'])

# Farm Comparison
st.subheader(t['comparison'])
if selected_farms and not df.empty:
    comparison_df = df[df['farm_id'].isin(selected_farms)][['farm_id', 'moisture', 'ph', 'temp', 'humidity',
                                                            'nitrogen', 'phosphorus', 'potassium', 'weather_temp',
                                                            'weather_humidity', 'rain_prob', 'recommendation']]
    st.dataframe(comparison_df.rename(columns={k: t[k] for k in comparison_df.columns if k in t}), width='stretch')
else:
    st.info(t['no_data'])

# Detailed View
if selected_farms:
    farm_id = selected_farms[0]
    st.subheader(t['detailed_view'].format(farm_id))

    data = fetch_farm_data(farm_id, farms[farm_id]['channel_id'], farms[farm_id]['read_api_key'])
    if data is None:
        st.warning(t['no_realtime'].format(farm_id))
        data = get_synthetic_data(farm_id)

    if data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t['moisture'], f"{data['moisture']:.1f}%")
            st.metric(t['ph'], f"{data['ph']:.1f}")
        with col2:
            st.metric(t['temperature'], f"{data['temp']:.1f}°C")
            st.metric(t['humidity'], f"{data['humidity']:.1f}%")
        with col3:
            st.metric(t['nitrogen'], f"{data['nitrogen']:.1f}")
            st.metric(t['phosphorus'], f"{data['phosphorus']:.1f}")
        with col4:
            st.metric(t['potassium'], f"{data['potassium']:.1f}")
            st.metric(t['weather_temp'], f"{data['weather_temp']:.1f}°C")
            st.metric(t['weather_humidity'], f"{data['weather_humidity']:.1f}%")
            st.metric(t['rain_prob'], f"{data['rain_prob']:.1f}%")
        st.write(f"{t['timestamp']}: {data['timestamp']}")

        # Recommendation with translation
        if not df.empty and farm_id in df['farm_id'].values:
            rec = df[df['farm_id'] == farm_id]['recommendation'].iloc[0]
            # Split and translate planting and disease parts
            planting_part, disease_part = rec.split(' | Disease: ')
            planting_key = next((k for k in t if k.startswith('rec_') and t[k] in planting_part), 'rec_wait')
            disease_key = next((k for k in t if k.startswith('rec_') and t[k] in disease_part), 'rec_healthy')
            try:
                # Use language-specific separator
                separator = separators[lang]
                rec_label = t['recommendation'].split(separator)[1] if len(
                    t['recommendation'].split(separator)) > 1 else t['recommendation']
                rec_trans = f"{t[planting_key]} | {rec_label}: {t[disease_key]}"
            except (KeyError, IndexError) as e:
                st.error(f"Translation error for {farm_id}: {e}. Using fallback recommendation.")
                rec_trans = f"{planting_part} | Disease: {disease_part}"  # Fallback to English
            st.success(f"{t['recommendation']}: {rec_trans}")
            if st.button(t['send_rec'].format(farm_id), key=f"send_{farm_id}"):
                st.info(t['sent_rec'].format(farm_id, rec_trans))
        else:
            st.info(t['no_data'])

# Historical Trends
st.subheader(t['trends'].format(farm_id if selected_farms else 'Selected Farms'))
if selected_farms:
    for farm_id in selected_farms:
        with st.expander(t['trends'].format(farm_id), expanded=farm_id == selected_farms[0]):
            hist_df = fetch_historical_data(farm_id, farms[farm_id]['channel_id'], farms[farm_id]['read_api_key'])
            time_threshold = datetime.now() - timedelta(hours=date_range)
            hist_df = hist_df[hist_df['created_at'] >= time_threshold]

            col1, col2 = st.columns(2)
            with col1:
                moisture_range = st.slider(f"{t['moisture']} Range (%)", 0, 100, (20, 80), key=f"moisture_{farm_id}")
                temp_range = st.slider(f"{t['temperature']} Range (°C)", 0, 50, (15, 35), key=f"temp_{farm_id}")
            with col2:
                ph_range = st.slider(f"{t['ph']} Range", 0.0, 14.0, (5.0, 8.0), key=f"ph_{farm_id}")

            filtered_df = hist_df[
                (hist_df['moisture'].between(moisture_range[0], moisture_range[1])) &
                (hist_df['temp'].between(temp_range[0], temp_range[1])) &
                (hist_df['ph'].between(ph_range[0], ph_range[1]))
                ]

            if not filtered_df.empty:
                fig = px.line(filtered_df, x='created_at', y=show_sensors, title=t['trends'].format(farm_id),
                              labels={'created_at': t['timestamp'], 'value': 'Value', 'variable': 'Sensor'})
                fig.update_layout(yaxis_title="Value")
                st.plotly_chart(fig)

                stats = filtered_df[show_sensors].describe().transpose()[['mean', 'min', 'max']]
                st.write(t['stats'])
                st.dataframe(stats.rename(columns={'mean': 'Average', 'min': 'Minimum', 'max': 'Maximum'}),
                             width='stretch')
            else:
                st.warning(t['no_filtered_data'])

# All Farms Overview
st.subheader(t['overview'])
if not df.empty:
    st.dataframe(df[['farm_id', 'moisture', 'ph', 'temp', 'humidity', 'nitrogen', 'phosphorus', 'potassium',
                     'weather_temp', 'weather_humidity', 'rain_prob', 'recommendation']]
                 .rename(columns={k: t[k] for k in df.columns if k in t}), width='stretch')
else:
    st.warning(t['no_data'])

# Refresh
if st.button(t['refresh']):
    st.rerun()