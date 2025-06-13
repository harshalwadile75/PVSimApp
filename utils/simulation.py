import pandas as pd
import numpy as np

def simulate_energy_output(weather_df, lat, lon, tilt, azimuth, system_kw):
    irradiance = weather_df["G(i)"].values
    temp_air = weather_df["T2m"].values
    wind_speed = weather_df["WS10m"].values

    poa_irradiance = irradiance  # already POA from PVGIS
    module_temp = temp_air + (irradiance * (0.035 / (8.91 + 2.0 * wind_speed)))
    temp_coeff = -0.004  # %/°C

    reference_eff = 0.18
    nominal_power = system_kw * 1000
    power_output = nominal_power * (poa_irradiance / 1000.0)
    temp_loss = 1 + temp_coeff * (module_temp - 25)
    power_output *= temp_loss

    monthly = pd.DataFrame({
        "Month": pd.to_datetime(weather_df["time"], utc=True).month,
        "Energy (kWh)": power_output / 1000.0
    }).groupby("Month").sum().reset_index()

    hourly_details = pd.DataFrame({
        "Time": pd.to_datetime(weather_df["time"], utc=True),
        "POA Irradiance (W/m²)": poa_irradiance,
        "Module Temp (°C)": module_temp,
        "Efficiency (%)": (power_output / (poa_irradiance * system_kw + 1e-9)) * 100
    })

    return monthly, hourly_details
