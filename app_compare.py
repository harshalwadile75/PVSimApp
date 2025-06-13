import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.weather import fetch_pvgis_tmy
from utils.comparison import run_comparison

st.set_page_config(page_title="PVSimApp - Comparison", layout="wide")
st.title("🆚 PV System Comparison Tool")

# Load module and inverter data
modules_df = pd.read_csv("modules.csv")
inverters_df = pd.read_csv("inverters.csv")

col1, col2 = st.columns(2)

# Shared inputs
lat = st.number_input("Latitude", value=40.0)
lon = st.number_input("Longitude", value=-105.0)

# --- System 1 ---
with col1:
    st.subheader("🔵 System 1")
    mod1 = st.selectbox("Module", modules_df["Model"], key="mod1")
    inv1 = st.selectbox("Inverter", inverters_df["Model"], key="inv1")
    num1 = st.number_input("Modules", 1, 100, 12, key="num1")
    tilt1 = st.slider("Tilt", 0, 60, 30, key="tilt1")
    az1 = st.slider("Azimuth", 90, 270, 180, key="az1")
    s1 = st.slider("Soiling", 0, 10, 2, key="s1")
    sh1 = st.slider("Shading", 0, 20, 3, key="sh1")
    wr1 = st.slider("Wiring", 0, 5, 2, key="wr1")
    invl1 = st.slider("Inverter Loss", 0, 5, 2, key="invl1")
    cost1 = st.number_input("Cost ($/kW)", value=1200, key="cost1")
    price1 = st.number_input("Electricity Price ($/kWh)", value=0.12, key="price1")

# --- System 2 ---
with col2:
    st.subheader("🟢 System 2")
    mod2 = st.selectbox("Module", modules_df["Model"], key="mod2")
    inv2 = st.selectbox("Inverter", inverters_df["Model"], key="inv2")
    num2 = st.number_input("Modules", 1, 100, 12, key="num2")
    tilt2 = st.slider("Tilt", 0, 60, 30, key="tilt2")
    az2 = st.slider("Azimuth", 90, 270, 180, key="az2")
    s2 = st.slider("Soiling", 0, 10, 2, key="s2")
    sh2 = st.slider("Shading", 0, 20, 3, key="sh2")
    wr2 = st.slider("Wiring", 0, 5, 2, key="wr2")
    invl2 = st.slider("Inverter Loss", 0, 5, 2, key="invl2")
    cost2 = st.number_input("Cost ($/kW)", value=1200, key="cost2")
    price2 = st.number_input("Electricity Price ($/kWh)", value=0.12, key="price2")

if st.button("🔍 Compare Systems"):
    st.info("Fetching weather & running simulations...")
    weather_df = fetch_pvgis_tmy(lat, lon)

    if weather_df is not None:
        power1 = modules_df[modules_df["Model"] == mod1]["Power (W)"].values[0]
        power2 = modules_df[modules_df["Model"] == mod2]["Power (W)"].values[0]

        config1 = {
            "tilt": tilt1,
            "azimuth": az1,
            "system_size_kw": (num1 * power1) / 1000,
            "total_loss": (s1 + sh1 + wr1 + invl1) / 100,
            "cost_per_kw": cost1,
            "energy_price": price1
        }

        config2 = {
            "tilt": tilt2,
            "azimuth": az2,
            "system_size_kw": (num2 * power2) / 1000,
            "total_loss": (s2 + sh2 + wr2 + invl2) / 100,
            "cost_per_kw": cost2,
            "energy_price": price2
        }

        energy1, energy2, finance1, finance2 = run_comparison(
            weather_df, lat, lon, config1, config2
        )

        col3, col4 = st.columns(2)
        with col3:
            st.write("### 🔵 System 1 Monthly Energy")
            st.dataframe(energy1)
            st.write("### Financials")
            for k, v in finance1.items():
                st.write(f"**{k}**: ${v:,.2f}" if "($)" in k else f"**{k}**: {v:,.2f}")

        with col4:
            st.write("### 🟢 System 2 Monthly Energy")
            st.dataframe(energy2)
            st.write("### Financials")
            for k, v in finance2.items():
                st.write(f"**{k}**: ${v:,.2f}" if "($)" in k else f"**{k}**: {v:,.2f}")

        # Side-by-side bar chart
        st.write("## 📊 Comparison Chart")
        combined = pd.DataFrame({
            "System 1": energy1["Energy (kWh)"].values,
            "System 2": energy2["Energy (kWh)"].values
        }, index=energy1.index)

        fig, ax = plt.subplots()
        combined.plot(kind="bar", ax=ax)
        ax.set_ylabel("Energy (kWh)")
        st.pyplot(fig)
    else:
        st.error("Weather data fetch failed.")
