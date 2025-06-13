import streamlit as st
from utils.weather import fetch_pvgis_tmy
from utils.simulation import simulate_energy_output
from utils.financials import calculate_financials
from utils.report import export_to_csv, export_to_pdf
from utils.optimizer import optimize_tilt_azimuth
from utils.curves import plot_iv_pv_curves
from utils.panond_parser import parse_pan_file, parse_ond_file
from utils.project_config import save_config, load_config
from utils.visuals import plot_hourly_time_series, plot_loss_waterfall
from utils.degradation import estimate_annual_degradation, simulate_lifetime_energy
from utils.bom_validator import validate_bom  # NEW for Phase 3

import pandas as pd
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="PVSimApp - Phase 3", layout="centered")
st.title("🔆 PVSimApp – Smart Solar Simulation (Phase 3)")

modules_df = pd.read_csv("modules.csv")
inverters_df = pd.read_csv("inverters.csv")

# Location Map Picker
st.sidebar.header("🌍 Select Location")
default_coords = [40.7128, -74.0060]
m = folium.Map(location=default_coords, zoom_start=4)
marker = folium.Marker(location=default_coords, draggable=True)
marker.add_to(m)
map_data = st_folium(m, height=300, returned_objects=["last_clicked"])
latitude = map_data["last_clicked"]["lat"] if map_data["last_clicked"] else default_coords[0]
longitude = map_data["last_clicked"]["lng"] if map_data["last_clicked"] else default_coords[1]
st.sidebar.markdown(f"**Latitude**: `{latitude:.4f}`, **Longitude**: `{longitude:.4f}`")

# Panel Orientation
st.sidebar.subheader("📐 Orientation")
optimize = st.sidebar.checkbox("Auto Optimize Tilt/Azimuth", value=False)
if not optimize:
    tilt = st.sidebar.slider("Tilt (°)", 0, 60, 30)
    azimuth = st.sidebar.slider("Azimuth (°)", 90, 270, 180)
else:
    tilt = None
    azimuth = None

# PV Module Selection
st.sidebar.subheader("⚡ PV Module")
module_choice = st.sidebar.selectbox("Select Module", modules_df["Model"])
selected_module = modules_df[modules_df["Model"] == module_choice].iloc[0]
module_power_default = selected_module["Power (W)"]

# PAN/OND Upload
st.sidebar.subheader("📥 Upload PAN/OND")
pan_file = st.sidebar.file_uploader("Upload PAN (.pan)", type=["pan"])
ond_file = st.sidebar.file_uploader("Upload OND (.ond)", type=["ond"])
if pan_file:
    parsed_module = parse_pan_file(pan_file.read())
    module_power = parsed_module["Pmax"]
    vmp, imp, voc, isc = parsed_module["Vmp"], parsed_module["Imp"], parsed_module["Voc"], parsed_module["Isc"]
else:
    module_power = module_power_default
    vmp = selected_module["Vmp (V)"]
    imp = selected_module["Imp (A)"]
    voc = selected_module["Voc (V)"]
    isc = selected_module["Isc (A)"]

# System Sizing
num_modules = st.sidebar.number_input("Number of Modules", min_value=1, value=12)
system_kw = (module_power * num_modules) / 1000
st.sidebar.markdown(f"**System Size**: {system_kw:.2f} kW")

# Inverter
st.sidebar.subheader("🔌 Inverter")
inverter_choice = st.sidebar.selectbox("Select Inverter", inverters_df["Model"])
selected_inverter = inverters_df[inverters_df["Model"] == inverter_choice].iloc[0]

# Losses
st.sidebar.subheader("⚙️ Loss Factors")
soiling = st.sidebar.slider("Soiling (%)", 0, 10, 2)
shading = st.sidebar.slider("Shading (%)", 0, 20, 3)
wiring = st.sidebar.slider("Wiring (%)", 0, 5, 2)
inv_loss = st.sidebar.slider("Inverter (%)", 0, 5, 2)
loss_dict = {"Soiling": soiling, "Shading": shading, "Wiring": wiring, "Inverter": inv_loss}

# Save/Load Config
st.sidebar.subheader("💾 Save / Load Config")
load_file = st.sidebar.file_uploader("Load Config", type=["json"])
if load_file:
    cfg = load_config(load_file)
    st.session_state.update(cfg)
    st.success("Config loaded. Update UI selections manually.")

if st.sidebar.button("Save Config"):
    filename = save_config({
        "latitude": latitude,
        "longitude": longitude,
        "tilt": tilt,
        "azimuth": azimuth,
        "module": module_choice,
        "inverter": inverter_choice,
        "num_modules": num_modules,
        "losses": loss_dict
    })
    with open(filename, "rb") as f:
        st.download_button("Download JSON", f, file_name=filename)

# Run Simulation
if st.sidebar.button("Run Simulation"):
    st.info("Fetching weather and running simulation...")
    weather = fetch_pvgis_tmy(latitude, longitude)

    if isinstance(weather, pd.DataFrame):
        if optimize:
            tilt, azimuth, _ = optimize_tilt_azimuth(weather, latitude, longitude, system_kw)
        st.success(f"Using Tilt={tilt}°, Azimuth={azimuth}°")

        # 🔍 BOM Validation
        st.subheader("🔍 BOM Validation Report")
        bom_feedback, issue_count = validate_bom(
            selected_module, selected_inverter, num_modules, (latitude, longitude), weather
        )
        for item in bom_feedback:
            st.write(item)
        if issue_count > 0:
            st.warning("⚠️ Please fix BOM issues before finalizing system.")

        # ⚡ Simulate Energy
        monthly_df, hourly_df = simulate_energy_output(weather, latitude, longitude, tilt, azimuth, system_kw)
        total_loss = sum(loss_dict.values()) / 100
        monthly_df["Energy (kWh)"] *= (1 - total_loss)

        st.subheader("📊 Monthly Energy Output")
        st.dataframe(monthly_df)
        st.pyplot(plot_loss_waterfall(monthly_df["Energy (kWh)"].sum(), loss_dict))

        st.subheader("📈 POA / Temp / Efficiency Charts")
        st.pyplot(plot_hourly_time_series(hourly_df))

        st.subheader("🔋 I-V and P-V Curves")
        iv_fig, pv_fig = plot_iv_pv_curves(vmp, imp, voc, isc)
        st.pyplot(iv_fig)
        st.pyplot(pv_fig)

        st.subheader("📉 Degradation Risk Forecast (25 years)")
        deg_rate = estimate_annual_degradation(hourly_df["Module Temp (°C)"])
        deg_df = simulate_lifetime_energy(monthly_df, deg_rate)
        st.line_chart(deg_df.set_index("Year"))

        st.subheader("💰 Financial Analysis")
        cost_per_kw = st.number_input("System Cost ($/kW)", value=1200)
        rate = st.number_input("Electricity Rate ($/kWh)", value=0.12)
        fin = calculate_financials(system_kw, cost_per_kw, rate, monthly_df)
        for k, v in fin.items():
            st.write(f"**{k}**: ${v:,.2f}" if "($)" in k else f"**{k}**: {v:,.2f}")

        st.subheader("📁 Export")
        export_to_csv(monthly_df, "monthly_energy.csv")
        with open("monthly_energy.csv", "rb") as f:
            st.download_button("Download CSV", f, file_name="monthly_energy.csv")
    else:
        st.error("Failed to load weather data.")
