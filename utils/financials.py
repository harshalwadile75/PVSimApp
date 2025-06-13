def calculate_financials(system_size_kw, cost_per_kw, energy_price, monthly_energy_df):
    """
    Calculate system cost, annual savings, payback period, and ROI.
    """
    system_cost = system_size_kw * cost_per_kw
    annual_energy = monthly_energy_df["Energy (kWh)"].sum()
    annual_savings = annual_energy * energy_price
    payback_period = system_cost / annual_savings if annual_savings else float('inf')
    roi = (annual_savings / system_cost) * 100 if system_cost else 0

    return {
        "System Cost ($)": system_cost,
        "Annual Energy (kWh)": annual_energy,
        "Annual Savings ($)": annual_savings,
        "Payback Period (Years)": payback_period,
        "ROI (%)": roi
    }

