import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import folium

from utils.weather import fetch_pvgis_tmy
from utils.simulation import simulate_energy_output
from utils.financials import calculate_financials
from utils.report import export_to_csv
from utils.optimizer import optimize_tilt_azimuth
from utils.curves import plot_iv_pv_curves
from utils.panond_parser import parse_pan_file
from utils.project_config import save_config, load_config
from utils.visuals import plot_hourly_time_series, plot_loss_waterfall
from utils.degradation import estimate_annual_degradation, simulate_lifetime_energy
from utils.bom_validator import validate_bom
from utils.risk_classifier import classify_degradation_risk, explain_risk_factors
from utils.failure_predictor import predict_failure_modes
from utils.test_recommender import recommend_tests
from utils.ai_recommender import recommend_bom
from utils.risk_scorer import compute_risk_score
from utils.report_generator import generate_pdf_report

st.set_page_config(page_title="PVSimApp - Phase 6", layout="centered")
st.title("🔆 PVSimApp – Smart Solar Simulation (Phase 6)")

modules_df = pd.read_csv("modules.csv")
inverters_df = pd.read_csv("inverters.csv")

if 'bom_b_data' not in st.session_state:
    st.session_state['bom_b_data'] = None

st.sidebar.header("🌍 Select Location")
default_coords = [40.7128, -74.0060]
m = folium.Map(location=default_coords, zoom_start=4)
marker = folium.Marker(location=default_coords, draggable=True)
marker.add_to(m)
map_data = st_folium(m, height=300, returned_objects=["last_clicked"])
latitude = map_data["last_clicked"]["lat"] if map_data["last_clicked"] else default_coords[0]
longitude = map_data["last_clicked"]["lng"] if map_data["last_clicked"]["lng"] else default_coords[1]
st.sidebar.markdown(f"**Latitude**: `{latitude:.4f}`, **Longitude**: `{longitude:.4f}`")

st.sidebar.subheader("📐 Orientation")
optimize = st.sidebar.checkbox("Auto Optimize Tilt/Azimuth", value=False)
if not optimize:
    tilt = st.sidebar.slider("Tilt (°)", 0, 60, 30)
    azimuth = st.sidebar.slider("Azimuth (°)", 90, 270, 180)
else:
    tilt = azimuth = None

st.sidebar.subheader("⚡ PV Module")
module_choice = st.sidebar.selectbox("Select Module", modules_df["Model"])
selected_module = modules_df[modules_df["Model"] == module_choice].iloc[0]
module_power = selected_module["Power (W)"]

st.sidebar.subheader("🔌 Inverter")
inverter_choice = st.sidebar.selectbox("Select Inverter", inverters_df["Model"])
selected_inverter = inverters_df[inverters_df["Model"] == inverter_choice].iloc[0]

st.sidebar.subheader("📦 Encapsulant")
encapsulant = st.sidebar.selectbox("Encapsulant Type", ["EVA", "POE"])
num_modules = st.sidebar.number_input("Number of Modules", min_value=1, value=12)
system_kw = (module_power * num_modules) / 1000

st.sidebar.subheader("⚙️ Loss Factors")
loss_dict = {
    "Soiling": st.sidebar.slider("Soiling (%)", 0, 10, 2),
    "Shading": st.sidebar.slider("Shading (%)", 0, 20, 3),
    "Wiring": st.sidebar.slider("Wiring (%)", 0, 5, 2),
    "Inverter": st.sidebar.slider("Inverter (%)", 0, 5, 2)
}

if st.sidebar.button("Run Simulation"):
    weather = fetch_pvgis_tmy(latitude, longitude)
    if isinstance(weather, pd.DataFrame):
        if optimize:
            tilt, azimuth, _ = optimize_tilt_azimuth(weather, latitude, longitude, system_kw)
        st.success(f"Using Tilt={tilt}°, Azimuth={azimuth}°")

        bom_feedback, issue_count = validate_bom(selected_module, selected_inverter, num_modules, (latitude, longitude), weather)
        for item in bom_feedback:
            st.write(item)

        monthly_df, hourly_df = simulate_energy_output(weather, latitude, longitude, tilt, azimuth, system_kw)
        monthly_df["Energy (kWh)"] *= (1 - sum(loss_dict.values()) / 100)

        st.subheader("📊 Monthly Energy Output")
        st.dataframe(monthly_df)
        st.pyplot(plot_loss_waterfall(monthly_df["Energy (kWh)"].sum(), loss_dict))

        st.subheader("📉 Degradation & Risk")
        deg_rate = estimate_annual_degradation(hourly_df["Module Temp (°C)"])
        risk_label = classify_degradation_risk(deg_rate)
        explanation = explain_risk_factors(hourly_df["Module Temp (°C)"])
        st.write(f"Estimated Annual Degradation: {deg_rate:.2f}%")
        st.write(f"Risk: {risk_label}")
        st.info(explanation)

        st.subheader("⚠️ Failure & Testing")
        failures = predict_failure_modes(selected_module, weather, encapsulant)
        for f in failures:
            st.write(f)
        test_plan, rationale = recommend_tests(weather, encapsulant)
        for k, v in test_plan.items():
            st.write(f"{k}: {v}")

        st.subheader("📊 Risk Scoring & Financials")
        risk_score, risk_rating = compute_risk_score(deg_rate, test_plan, failures)
        cost_per_kw = st.number_input("System Cost ($/kW)", value=1200)
        rate = st.number_input("Electricity Rate ($/kWh)", value=0.12)
        fin = calculate_financials(system_kw, cost_per_kw, rate, monthly_df)
        for k, v in fin.items():
            st.write(f"{k}: ${v:,.2f}" if "($)" in k else f"{k}: {v:.2f}")

        st.subheader("📁 Export Options")
        export_to_csv(monthly_df, "monthly_energy.csv")
        with open("monthly_energy.csv", "rb") as f:
            st.download_button("Download CSV", f, file_name="monthly_energy.csv")

        if st.button("📄 Export PDF Report"):
            config = {
                "Latitude": latitude,
                "Longitude": longitude,
                "Tilt": tilt,
                "Azimuth": azimuth,
                "Module": module_choice,
                "Inverter": inverter_choice,
                "Encapsulant": encapsulant,
                "System Size (kW)": f"{system_kw:.2f}"
            }

            pdf_filename = "PVSim_Report.pdf"
            generate_pdf_report(
                filename=pdf_filename,
                config=config,
                monthly_df=monthly_df,
                deg_rate=deg_rate,
                risk_score=risk_score,
                risk_label=risk_label,
                failures=failures,
                test_plan=test_plan,
                financials=fin,
                bom_b=st.session_state['bom_b_data']
            )

            with open(pdf_filename, "rb") as f:
                st.download_button("📥 Download PDF Report", f, file_name=pdf_filename)

if st.sidebar.button("Set Current as BOM B"):
    st.session_state['bom_b_data'] = {
        "config": {
            "Module": module_choice,
            "Inverter": inverter_choice,
            "Encapsulant": encapsulant,
            "System Size (kW)": f"{system_kw:.2f}"
        },
        "monthly_df": monthly_df,
        "deg_rate": deg_rate,
        "risk_score": risk_score,
        "risk_label": risk_label
    }
    st.success("BOM B saved for comparison in next PDF export.")
