import streamlit as st
from utils.weather import fetch_pvgis_tmy
from utils.simulation import simulate_energy_output
from utils.financials import calculate_financials
from utils.report import export_to_csv, export_to_pdf

import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="PVSimApp - Phase 2", layout="centered")
st.title("🔆 PVSimApp - PV Simulation Tool")

# Load module & inverter data
modules_df = pd.read_csv("modules.csv")
inverters_df = pd.read_csv("inverters.csv")

# Sidebar Inputs
st.sidebar.header("📍 Location & System Settings")
latitude = st.sidebar.number_input("Latitude", value=40.7128)
longitude = st.sidebar.number_input("Longitude", value=-74.0060)
tilt = st.sidebar.slider("Tilt Angle (°)", min_value=0, max_value=90, value=30)
azimuth = st.sidebar.slider("Azimuth (°)", min_value=0, max_value=360, value=180)

# Module Picker
st.sidebar.subheader("⚡ Select PV Module")
module_choice = st.sidebar.selectbox("Module", modules_df["Model"])
selected_module = modules_df[modules_df["Model"] == module_choice].iloc[0]
module_power = selected_module["Power (W)"]

num_modules = st.sidebar.number_input("Modules in Array", min_value=1, value=12)
system_size_kw = (module_power * num_modules) / 1000
st.sidebar.markdown(f"**System Size**: {system_size_kw:.2f} kW")

# Inverter Picker
st.sidebar.subheader("🔌 Select Inverter")
inverter_choice = st.sidebar.selectbox("Inverter", inverters_df["Model"])
selected_inverter = inverters_df[inverters_df["Model"] == inverter_choice].iloc[0]

# Region-based Loss Inputs
st.sidebar.header("⚙️ Loss Factors")

region = st.sidebar.selectbox("Site Region Type", [
    "Urban (Clean Roofs)",
    "Rural (Moderate Soiling)",
    "Coastal (High Salt Exposure)",
    "Desert (Heavy Dust)",
    "Forested/Shady"
])

region_presets = {
    "Urban (Clean Roofs)": {"soiling": 1, "shading": 2},
    "Rural (Moderate Soiling)": {"soiling": 3, "shading": 3},
    "Coastal (High Salt Exposure)": {"soiling": 4, "shading": 3},
    "Desert (Heavy Dust)": {"soiling": 6, "shading": 2},
    "Forested/Shady": {"soiling": 2, "shading": 10}
}

preset = region_presets[region]
soiling_loss = st.sidebar.slider("Soiling Loss (%)", 0, 10, preset["soiling"])
shading_loss = st.sidebar.slider("Shading Loss (%)", 0, 20, preset["shading"])
wiring_loss = st.sidebar.slider("Wiring Loss (%)", 0, 5, 2)
inverter_loss = st.sidebar.slider("Inverter Loss (%)", 0, 5, 2)

# Simulation Trigger
if st.sidebar.button("Run Simulation"):
    st.info("Fetching weather data from PVGIS...")
    weather_df = fetch_pvgis_tmy(latitude, longitude)

    if isinstance(weather_df, pd.DataFrame):
        st.success("Weather data fetched successfully!")

        st.info("Running energy simulation...")
        monthly_energy, processed_weather = simulate_energy_output(
            weather_df, latitude, longitude, tilt, azimuth, system_size_kw
        )

        # Apply losses
        total_loss_pct = (
            soiling_loss + shading_loss + wiring_loss + inverter_loss
        ) / 100.0
        monthly_energy["Energy (kWh)"] *= (1 - total_loss_pct)

        # Output
        st.subheader("📊 Monthly Energy Output")
        st.dataframe(monthly_energy)

        fig, ax = plt.subplots()
        monthly_energy.plot(kind='bar', legend=False, ax=ax)
        ax.set_ylabel("Energy (kWh)")
        ax.set_title("Monthly AC Energy Production (After Losses)")
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
