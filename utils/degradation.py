import numpy as np
import pandas as pd

def arrhenius_acceleration(temp_c, ea=0.7):
    k = 8.617e-5  # Boltzmann constant in eV/K
    t_ref = 25 + 273.15  # reference temperature (25°C)
    t_actual = temp_c + 273.15  # convert °C to Kelvin
    return np.exp((ea / k) * ((1 / t_ref) - (1 / t_actual)))

def estimate_annual_degradation(temp_series, base_deg=0.5):
    """
    Use Arrhenius model to adjust base degradation (e.g. 0.5%/year) based on temp stress.
    Returns estimated annual degradation rate in %.
    """
    acc_factors = arrhenius_acceleration(temp_series)
    avg_accel = np.mean(acc_factors)
    return base_deg * avg_accel

def simulate_lifetime_energy(monthly_df, annual_deg_rate, years=25):
    """
    Simulates total energy degraded over years.
    Returns DataFrame with yearly degraded energy.
    """
    baseline_yearly = monthly_df["Energy (kWh)"].sum()
    records = []

    for year in range(1, years + 1):
        energy = baseline_yearly * ((1 - annual_deg_rate / 100) ** (year - 1))
        records.append({"Year": year, "Degraded Energy (kWh)": energy})

    return pd.DataFrame(records)
