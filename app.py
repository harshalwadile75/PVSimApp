import streamlit as st
from utils.weather import fetch_pvgis_tmy
from utils.simulation import simulate_energy_output
from utils.financials import calculate_financials
from utils.report import export_to_csv, export_to_pdf, export_comparison_pdf
from utils.optimizer import optimize_tilt_azimuth
from utils.curves import plot_iv_pv_curves
from utils.panond_parser import parse_pan_file, parse_ond_file
from utils.project_config import save_config, load_config
from utils.visuals import plot_hourly_time_series, plot_loss_waterfall
from utils.degradation import estimate_annual_degradation, simulate_lifetime_energy
from utils.bom_validator import validate_bom
from utils.risk_classifier import classify_degradation_risk, explain_risk_factors
from utils.failure_predictor import predict_failure_modes
from utils.test_recommender import recommend_tests
from utils.ai_recommender import recommend_bom  # ✅ NEW

import pandas as pd
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import folium
from datetime import datetime

st.set_page_config(page_title="PVSimApp - Phase 5", layout="wide")
st.title("🔆 PVSimApp – Smart Solar with AI BOM Optimization (Phase 5)")

modules_df = pd.read_csv("modules.csv")
inverters_df = pd.read_csv("inverters.csv")

# Location
st.sidebar.header("🌍 Select Location")
default_coords = [37.77, -122.42]
m = folium.Map(location=default_coords, zoom_start=4)
marker = folium.Marker(location=default_coords, draggable=True)
marker.add_to(m)
map_data = st_folium(m, height=300, returned_objects=["last_clicked"])
latitude = map_data["last_clicked"]["lat"] if map_data["last_clicked"] else default_coords[0]
longitude = map_data["last_clicked"]["lng"] if map_data["last_clicked"] else default_coords[1]
st.sidebar.markdown(f"**Latitude**: `{latitude:.4f}`, **Longitude**: `{longitude:.4f}`")

# Orientation
st.sidebar.subheader("📐 Orientation")
optimize = st.sidebar.checkbox("Auto Optimize Tilt/Azimuth", value=True)
tilt = azimuth = None
if not optimize:
    tilt = st.sidebar.slider("Tilt (°)", 0, 60, 30)
    azimuth = st.sidebar.slider("Azimuth (°)", 90, 270, 180)

# BOM Comparison Toggle
st.sidebar.subheader("⚙️ BOM Mode")
compare_mode = st.sidebar.checkbox("🔁 Enable BOM Comparison", value=False)

# BOM A
st.sidebar.subheader("📦 BOM A – Main")
module_A = st.sidebar.selectbox("Module A", modules_df["Model"], key="mod_a")
inverter_A = st.sidebar.selectbox("Inverter A", inverters_df["Model"], key="inv_a")
num_modules_A = st.sidebar.number_input("Modules A", 1, 100, 12, key="num_a")
encapsulant_A = st.sidebar.selectbox("Encapsulant A", ["EVA", "POE"], key="encap_a")

# BOM B (optional)
if compare_mode:
    st.sidebar.subheader("📦 BOM B – Comparison")
    module_B = st.sidebar.selectbox("Module B", modules_df["Model"], key="mod_b")
    inverter_B = st.sidebar.selectbox("Inverter B", inverters_df["Model"], key="inv_b")
    num_modules_B = st.sidebar.number_input("Modules B", 1, 100, 12, key="num_b")
    encapsulant_B = st.sidebar.selectbox("Encapsulant B", ["EVA", "POE"], key="encap_b")

# Losses
st.sidebar.subheader("🔧 Losses")
losses = {
    "Soiling": st.sidebar.slider("Soiling (%)", 0, 10, 2),
    "Shading": st.sidebar.slider("Shading (%)", 0, 20, 3),
    "Wiring": st.sidebar.slider("Wiring (%)", 0, 5, 2),
    "Inverter": st.sidebar.slider("Inverter (%)", 0, 5, 2)
}

if st.sidebar.button("Run Comparison" if compare_mode else "Run Simulation"):
    st.info("Fetching weather data...")
    weather = fetch_pvgis_tmy(latitude, longitude)
    if isinstance(weather, pd.DataFrame):
        if optimize:
            tilt, azimuth, _ = optimize_tilt_azimuth(weather, latitude, longitude, 1)
        st.success(f"Tilt: {tilt}°, Azimuth: {azimuth}°")

        col1, col2 = st.columns(2) if compare_mode else [st]

        def run_bom_analysis(mod, inv, n_mod, encapsulant, col, label):
            kw = (mod["Power (W)"] * n_mod) / 1000
            col.subheader(f"📦 {label} – {mod['Model']} + {inv['Model']}")
            col.markdown(f"🔋 System Size: `{kw:.2f} kW`")

            monthly, hourly = simulate_energy_output(weather, latitude, longitude, tilt, azimuth, kw)
            monthly["Energy (kWh)"] *= (1 - sum(losses.values()) / 100)
            col.markdown("📊 **Monthly Energy**")
            col.dataframe(monthly)

            deg_rate = estimate_annual_degradation(hourly["Module Temp (°C)"])
            label_risk = classify_degradation_risk(deg_rate)
            col.markdown(f"📉 Annual Degradation: `{deg_rate:.2f}%` ({label_risk})")

            failures = predict_failure_modes(mod, weather, encapsulant)
            for f in failures:
                col.write(f)

            test, rationale = recommend_tests(weather, encapsulant)
            for k, v in test.items():
                col.markdown(f"🧪 {k}: `{v}`")
            for r in rationale:
                col.info(r)

            roi = calculate_financials(kw, 1200, 0.12, monthly)
            col.markdown(f"💰 ROI: `{roi['ROI (%)']:.2f}%`")

            config = {
                "Location": f"{latitude:.4f}, {longitude:.4f}",
                "Tilt": tilt,
                "Azimuth": azimuth,
                "Module": mod["Model"],
                "Inverter": inv["Model"],
                "Encapsulant": encapsulant,
                "System Size (kW)": kw,
                "Date": datetime.now().strftime("%Y-%m-%d"),
            }

            pdf_name = f"{label}_report.pdf"
            export_to_pdf(
                filename=pdf_name,
                config=config,
                monthly_energy=list(zip(monthly["Month"], monthly["Energy (kWh)"])),
                degradation=deg_rate,
                risk=label_risk,
                test_summary=test,
                roi_info=roi,
                rationale=rationale,
            )
            with open(pdf_name, "rb") as f:
                col.download_button("📄 Download PDF Report", f, file_name=pdf_name)

            return {
                "Label": label,
                "Energy": monthly["Energy (kWh)"].sum(),
                "Degradation": deg_rate,
                "ROI": roi["ROI (%)"]
            }

        bom_a_result = run_bom_analysis(
            modules_df[modules_df["Model"] == module_A].iloc[0],
            inverters_df[inverters_df["Model"] == inverter_A].iloc[0],
            num_modules_A, encapsulant_A, col1, "BOM A"
        )

        if compare_mode:
            bom_b_result = run_bom_analysis(
                modules_df[modules_df["Model"] == module_B].iloc[0],
                inverters_df[inverters_df["Model"] == inverter_B].iloc[0],
                num_modules_B, encapsulant_B, col2, "BOM B"
            )

            # Summary Chart
            st.subheader("📊 BOM Comparison Summary")
            labels = ["Annual Energy (kWh)", "Degradation (%)", "ROI (%)"]
            a_vals = [bom_a_result["Energy"], bom_a_result["Degradation"], bom_a_result["ROI"]]
            b_vals = [bom_b_result["Energy"], bom_b_result["Degradation"], bom_b_result["ROI"]]

            x = range(len(labels))
            fig, ax = plt.subplots()
            ax.bar([i - 0.2 for i in x], a_vals, width=0.4, label="BOM A")
            ax.bar([i + 0.2 for i in x], b_vals, width=0.4, label="BOM B")
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.set_ylabel("Value")
            ax.set_title("BOM A vs BOM B Summary")
            ax.legend()
            st.pyplot(fig)

            # Export Summary Table
            summary_df = pd.DataFrame({
                "Metric": labels,
                "BOM A": a_vals,
                "BOM B": b_vals
            })
            summary_df.to_csv("comparison_summary.csv", index=False)
            with open("comparison_summary.csv", "rb") as f:
                st.download_button("⬇️ Download CSV Summary", f, file_name="comparison_summary.csv")

            export_comparison_pdf("comparison_summary.pdf", bom_a_result, bom_b_result)
            with open("comparison_summary.pdf", "rb") as f:
                st.download_button("⬇️ Download PDF Summary", f, file_name="comparison_summary.pdf")

    else:
        st.error("❌ Weather fetch failed.")

# ✅ AI BOM Recommendation
st.markdown("---")
st.subheader("🤖 AI-Based BOM Recommendations")

try:
    weather = fetch_pvgis_tmy(latitude, longitude)
    if isinstance(weather, pd.DataFrame):
        top_boms = recommend_bom(weather, modules_df, inverters_df)
        for idx, bom in enumerate(top_boms):
            st.markdown(f"**🔧 Recommendation #{idx+1}**")
            st.write(f"Module: `{bom['Module']}`")
            st.write(f"Inverter: `{bom['Inverter']}`")
            st.write(f"Suggested Encapsulant: `{bom['Encapsulant']}`")
            st.write(f"Smart Score: `{bom['Score']}`")
            st.markdown("---")
except Exception as e:
    st.error(f"AI recommendation failed: {e}")
