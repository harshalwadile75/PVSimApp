import numpy as np
from utils.simulation import simulate_energy_output

def optimize_tilt_azimuth(weather_df, lat, lon, system_size_kw):
    best_energy = 0
    best_tilt = 0
    best_azimuth = 180

    for tilt in range(0, 61, 10):
        for azimuth in range(90, 271, 30):
            monthly_energy, _ = simulate_energy_output(
                weather_df, lat, lon, tilt, azimuth, system_size_kw
            )
            total_energy = monthly_energy["Energy (kWh)"].sum()

            if total_energy > best_energy:
                best_energy = total_energy
                best_tilt = tilt
                best_azimuth = azimuth

    return best_tilt, best_azimuth, best_energy
