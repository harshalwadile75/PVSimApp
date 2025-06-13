from utils.simulation import simulate_energy_output
from utils.financials import calculate_financials

def run_comparison(weather_df, lat, lon, config1, config2):
    # Simulate system 1
    energy1, _ = simulate_energy_output(
        weather_df, lat, lon,
        config1['tilt'], config1['azimuth'], config1['system_size_kw']
    )
    energy1["Energy (kWh)"] *= (1 - config1['total_loss'])

    # Simulate system 2
    energy2, _ = simulate_energy_output(
        weather_df, lat, lon,
        config2['tilt'], config2['azimuth'], config2['system_size_kw']
    )
    energy2["Energy (kWh)"] *= (1 - config2['total_loss'])

    # Financials
    finance1 = calculate_financials(
        config1['system_size_kw'], config1['cost_per_kw'],
        config1['energy_price'], energy1
    )
    finance2 = calculate_financials(
        config2['system_size_kw'], config2['cost_per_kw'],
        config2['energy_price'], energy2
    )

    return energy1, energy2, finance1, finance2
