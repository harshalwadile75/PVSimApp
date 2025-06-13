import streamlit as st
from utils.weather import fetch_pvgis_tmy
import pandas as pd

st.set_page_config(page_title="PVSimApp - Phase 1", layout="centered")
st.title("🔆 PVSimApp - Basic PV Simulation")

# Sidebar Inputs
st.sidebar.header("Location & System Settings")
latitude = st.sidebar.number_input("Latitude", value=40.7128)
longitude = st.sidebar.number_input("Longitude", value=-74.0060)
system_size_kw = st.sidebar.number_input("System Size (kW)", value=5.0)
tilt = st.sidebar.slider("Tilt Angle (°)", min_value=0, max_value=90, value=30)
azimuth = st.sidebar.slider("Azimuth (°)", min_value=0, max_value=360, value=180)

if st.sidebar.button("Run Simulation"):
    st.info("Fetching weather data from PVGIS...")
    weather_df = fetch_pvgis_tmy(latitude, longitude)
    
    if isinstance(weather_df, pd.DataFrame):

