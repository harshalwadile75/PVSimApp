import streamlit as st
from utils.weather import fetch_pvgis_tmy
from utils.simulation import simulate_energy_output
from utils.financials import calculate_financials
from utils.report import export_to_csv, export_to_pdf

import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="PVSimApp - Phase 1", layout="centered")
st.title("🔆 PVSimApp - Basic PV Simulation")

# Sidebar Inputs
st.sidebar.header("📍 Location & System Settings")
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

        st.subheader("📁 Export Results")

        csv_file = "monthly_energy.csv"
        pdf_file = "monthly_energy.pdf"

        export_to_csv(monthly_energy, csv_file)
        export_to_pdf(monthly_energy, pdf_file)

        with open(csv_file, "rb") as f:
            st.download_button("Download CSV", f, file_name=csv_file, mime="text/csv")

        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, file_name=pdf_file, mime="application/pdf")

        st.subheader("💰 Financial Calculator")

        cost_per_kw = st.number_input("System Cost ($/kW)", value=1200)
        energy_price = st.number_input("Energy Price ($/kWh)", value=0.12)

        results = calculate_financials(system_size_kw, cost_per_kw, energy_price, monthly_energy)

        st.write("### Financial Summary")
        for key, value in results.items():
            st.write(f"**{key}**: ${value:,.2f}" if "($)" in key else f"**{key}**: {value:,.2f}")

    else:
        st.error("Failed to fetch weather data. Please try a different location.")
