import streamlit as st
import numpy as np
from datetime import datetime
import requests
import folium
from streamlit_folium import st_folium
import pickle

model_path = 'climatemodel.pkl'
with open(model_path, 'rb') as file:
    model = pickle.load(file)

def get_weather_data(api_key, city):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# CSS styling for the application
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #00cc66;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stSuccess {
        color: #28a745;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .stTitle {
        color: #007bff;
        font-weight: bold;
    }
    .stHeader {
        font-size: 1.2rem;
        color: #343a40;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Climate Change Impact Prediction")

# Sidebar with function options
st.sidebar.title("Function Options")
option = st.sidebar.radio("Select a Function:", ['Predict Climate Impact', 'Live Weather Data', 'Interactive Climate Risk Map'])

# API key for weather data
api_key = '94902f02069c45bd81d61215241109'

if option == 'Predict Climate Impact':
    st.header("📝 Enter Weather Data for Impact Prediction")
    
    # Input form for prediction
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_input = st.date_input("📅 Date", value=datetime.today())
        dew_point = st.number_input("💧 Dew Point Temperature (°C)", step=0.1)
        fog = st.selectbox("🌫️ Fog (0 or 1)", [0, 1])
    
    with col2:
        hail = st.selectbox("🌨️ Hail (0 or 1)", [0, 1])
        heat_index = st.number_input("🔥 Heat Index (°C)", step=0.1)
    
    with col3:
        humidity = st.number_input("💦 Humidity (%)", step=0.1)
        pressure = st.number_input("⚖️ Pressure (mbar)", step=0.1)
        temperature = st.number_input("🌡️ Temperature (°C)", step=0.1)
    
    year = date_input.year
    month = date_input.month
    day = date_input.day
    
    if st.button("🔮 Predict Climate Impact", key="predict_impact"):
        # Prepare input data for prediction
        new = np.array([[dew_point, fog, hail, heat_index, humidity, pressure, temperature, year, month, day]])
        prediction = model.predict(new)
        st.success(f"Predicted Climate Change Impact: {prediction[0]}")

elif option == 'Live Weather Data':
    st.header("🌤️ Live Weather Data")
    city = st.text_input("🏙️ Enter City Name", "Delhi")
    
    if st.button("Get Live Weather Data", key="live_weather"):
        weather_data = get_weather_data(api_key, city)
        if weather_data:
            temperature = weather_data['current']['temp_c']
            humidity = weather_data['current']['humidity']
            precipitation = weather_data.get('current', {}).get('precip_mm', 0)
            
            st.subheader(f"Current Weather Data for {city}")
            st.write(f"Temperature: {temperature} °C")
            st.write(f"Humidity: {humidity} %")
            st.write(f"Precipitation: {precipitation} mm")
        else:
            st.error("City not found or API call failed. Please try again.")

elif option == 'Interactive Climate Risk Map':
    def create_map():
        india_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='OpenStreetMap')
        cities = {
            "Delhi": {"coords": [28.6139, 77.2090], "risk_level": "High", "temp_rise": 2.5},
            "Mumbai": {"coords": [19.0760, 72.8777], "risk_level": "Medium", "sea_level_rise": 0.7},
            "Kolkata": {"coords": [22.5726, 88.3639], "risk_level": "High", "flood_risk": "Severe"},
            "Chennai": {"coords": [13.0827, 80.2707], "risk_level": "Medium", "drought_risk": "Moderate"},
            "Bangalore": {"coords": [12.9716, 77.5946], "risk_level": "Low", "heatwave_risk": "Mild"}
        }
        risk_colors = {"High": "red", "Medium": "orange", "Low": "green"}
        for city, data in cities.items():
            folium.CircleMarker(
                location=data["coords"],
                radius=10,
                color=risk_colors[data["risk_level"]],
                fill=True,
                fill_opacity=0.6,
                popup=(f"{city}<br>"
                       f"Risk Level: {data['risk_level']}<br>"
                       f"Temp Rise: {data.get('temp_rise', 'N/A')}°C<br>"
                       f"Sea Level Rise: {data.get('sea_level_rise', 'N/A')} meters<br>"
                       f"Flood Risk: {data.get('flood_risk', 'N/A')}<br>"
                       f"Drought Risk: {data.get('drought_risk', 'N/A')}<br>"
                       f"Heatwave Risk: {data.get('heatwave_risk', 'N/A')}")
            ).add_to(india_map)
        return india_map

    st.header("🗺️ Interactive Climate Risk Map of India")
    india_map = create_map()
    st_folium(india_map, width=700, height=500)
