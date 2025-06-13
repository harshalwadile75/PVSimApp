def recommend_tests(weather_df, encapsulant):
    avg_temp = weather_df["T2m"].mean()
    avg_rh = weather_df["RH"].mean() if "RH" in weather_df.columns else 60
    avg_irr = weather_df["G(h)"].mean() if "G(h)" in weather_df.columns else 5.5

    # --- DH Logic ---
    dh_hours = 1000
    if avg_temp > 30 and avg_rh > 70:
        dh_hours = 2000
    elif avg_temp < 20:
        dh_hours = 800

    # --- UV Logic ---
    uv_exposure = 15
    if avg_irr > 6:
        uv_exposure = 30
    elif avg_irr < 4:
        uv_exposure = 10

    # --- TC Logic ---
    tc_cycles = 200
    if avg_temp > 30:
        tc_cycles = 300
    elif avg_temp < 15:
        tc_cycles = 250

    # Encapsulant modifier
    if encapsulant == "POE":
        dh_hours += 200
        uv_exposure += 5

    test_plan = {
        "Damp Heat (hours)": dh_hours,
        "UV Exposure (kWh/m²)": uv_exposure,
        "Thermal Cycles": tc_cycles
    }

    rationale = [
        f"Location Avg Temp = {avg_temp:.1f} °C",
        f"Avg Humidity = {avg_rh:.1f}%",
        f"Avg Irradiance = {avg_irr:.1f} kWh/m²/day",
        f"Encapsulant = {encapsulant}"
    ]

    return test_plan, rationale
