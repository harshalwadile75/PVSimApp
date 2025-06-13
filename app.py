import streamlit as st
from utils.weather import fetch_pvgis_tmy
from utils.simulation import simulate_energy_output
from utils.financials import calculate_financials
from utils.report import export_to_csv, export_to_pdf
from utils.optimizer import optimize_tilt_azimuth
from utils.curves import plot_iv_pv_curves
from utils.panond_parser import parse_pan_file, parse_ond_file

import pandas as pd
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="PVSimApp - PAN Support", layout="centered")
st.title("🔆 PVSimApp - PV Simulation Tool")

modules_df = pd.read_csv("modules.csv")
inverters_df = pd.read_csv("inverters.csv")

# Location Map Picker
st.sidebar.header("🌍 Select Location on Map")
default_coords = [40.7128, -74.0060]
m = folium.Map(location=default_coords, zoom_start=4)
marker = folium.Marker(location=default_coords, draggable=True)
marker.add_to(m)

map_data = st_folium(m, height=300, returned_objects=["last_clicked"])
latitude = map_data["last_clicked"]["lat"] if map_data["last_clicked"] else default_coords[0]
longitude = map_data["last_clicked"]["lng"] if map_data["last_clicked"] else default_coords[1]

st.sidebar.markdown(f"**Latitude**: `{latitude:.4f}`")
st.sidebar.markdown(f"**Longitude**: `{longitude:.4f}`")

# Orientation
st.sidebar.subheader("📐 Panel Orientation")
optimize = st.sidebar.checkbox("Auto-optimize Tilt & Azimuth", value=False)

if not optimize:
    tilt = st.sidebar.slider("Tilt Angle (°)", 0, 60, 30)
    azimuth = st.sidebar.slider("Azimuth (°)", 90, 270, 180)
else:
    tilt = None
    azimuth = None

# Module Picker
st.sidebar.subheader("⚡ Select PV Module")
module_choice = st.sidebar.selectbox("Module", modules_df["Model"])
selected_module = modules_df[modules_df["Model"] == module_choice].iloc[0]
module_power_default = selected_module["Power (W)"]

# Upload PAN and OND
st.sidebar.subheader("📥 Upload PAN/OND Files")
pan_file = st.sidebar.file_uploader("Upload PAN (module)", type=["pan"])
ond_file = st.sidebar.file_uploader("Upload OND (inverter)", type=["ond"])

if pan_file:
    parsed_module = parse_pan_file(pan_file.read())
    module_power = parsed_module["Pmax"]
    vmp = parsed_module["Vmp"]
    imp = parsed_module["Imp"]
    voc = parsed_module["Voc"]
    isc = parsed_module["Isc"]
else:
    parsed_module = None
    module_power = module_power_default
    vmp = selected_module["Vmp (V)"]
    imp = selected_module["Imp (A)"]
    voc = selected_module["Voc (V)"]
    isc = selected_module["Isc (A)"]

if ond_file:
    parsed_inverter = parse_ond_file(ond_file.read())
else:
    parsed_inverter = None

# System Size
num_modules = st.sidebar.number_input("Modules in Array", min_value=1, value=12)
system_size_kw = (module_power * num_modules) / 1000
st.sidebar.markdown(f"**System Size**: {system_size_kw:.2f} kW")

# Inverter Picker
st.sidebar.subheader("🔌 Select Inverter")
inverter_choice = st.sidebar.selectbox("Inverter", inverters_df["Model"])
selected_inverter = inverters_df[inverters_df["Model"] == inverter_choice].iloc[0]

# Loss Factors
st.sidebar.header("⚙️ Loss Factors")
region = st.sidebar.selectbox("Site Region Type", [
    "Urban (Clean Roofs)", "Rural (Moderate Soiling)", "Coastal (High Salt Exposure)",
    "Desert (Heavy Dust)", "Forested/Shady"
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

# Run Simulation
if st.sidebar.button("Run Simulation"):
    st.info("Fetching weather data...")
    weather_df = fetch_pvgis_tmy(latitude, longitude)

    if isinstance(weather_df, pd.DataFrame):
        st.success("Weather data fetched!")

        if optimize:
            tilt, azimuth, _ = optimize_tilt_azimuth(weather_df, latitude, longitude, system_size_kw)
            st.success(f"Optimal Tilt: {tilt}°, Azimuth: {azimuth}°")

        monthly_energy, _ = simulate_energy_output(
            weather_df, latitude, longitude, tilt, azimuth, system_size_kw
        )

        loss_pct = (soiling_loss + shading_loss + wiring_loss + inverter_loss) / 100.0
        monthly_energy["Energy (kWh)"] *= (1 - loss_pct)

        st.subheader("📊 Monthly Energy Output")
        st.dataframe(monthly_energy)

        fig, ax = plt.subplots()
        monthly_energy.plot(kind="bar", ax=ax)
        ax.set_ylabel("Energy (kWh)")
        ax.set_title("Monthly Energy Production (After Losses)")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.subheader("📁 Export Results")
        export_to_csv(monthly_energy, "monthly_energy.csv")
        export_to_pdf(monthly_energy, "monthly_energy.pdf")

        with open("monthly_energy.csv", "rb") as f:
            st.download_button("Download CSV", f, file_name="monthly_energy.csv")

        with open("monthly_energy.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="monthly_energy.pdf")

        st.subheader("💰 Financial Analysis")
        cost_per_kw = st.number_input("System Cost ($/kW)", value=1200)
        energy_price = st.number_input("Electricity Rate ($/kWh)", value=0.12)

        results = calculate_financials(system_size_kw, cost_per_kw, energy_price, monthly_energy)
        for k, v in results.items():
            st.write(f"**{k}**: ${v:,.2f}" if "($)" in k else f"**{k}**: {v:,.2f}")

        st.subheader("🔋 I-V and P-V Curves")
        fig_iv, fig_pv = plot_iv_pv_curves(vmp, imp, voc, isc)
        st.pyplot(fig_iv)
        st.pyplot(fig_pv)

    else:
        st.error("Failed to fetch weather data.")
