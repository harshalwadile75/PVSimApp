import streamlit as st
from utils.weather import fetch_pvgis_tmy
from utils.simulation import simulate_energy_output
import pandas as pd
import matplotlib.pyplot as plt

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
        st.success("Weather data fetched successfully!")

        st.info("Running energy simulation...")
        monthly_energy, processed_weather = simulate_energy_output(
            weather_df, latitude, longitude, tilt, azimuth, system_size_kw
        )

        st.subheader("📊 Monthly Energy Output")
        st.dataframe(monthly_energy)

        # Plotting
        fig, ax = plt.subplots()
        monthly_energy.plot(kind='bar', legend=False, ax=ax)
        ax.set_ylabel("Energy (kWh)")
        ax.set_title("Monthly AC Energy Production")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    else:
        st.error("Failed to fetch weather data. Please try a different location.")
