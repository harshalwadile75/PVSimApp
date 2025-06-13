def recommend_tests(weather_df, encapsulant="EVA"):
    avg_temp = weather_df["T2m"].mean()
    max_temp = weather_df["T2m"].max()
    high_uv_days = (weather_df["G(i)"] > 900).sum()
    high_humidity_days = (weather_df["RH"] > 75).sum()

    dh_hours = 1000  # base
    uv_hrs = 300     # base
    tc_cycles = 200  # base

    if avg_temp > 35 or max_temp > 55:
        dh_hours += 500
        tc_cycles += 100

    if high_uv_days > 50:
        uv_hrs += 200

    if high_humidity_days > 60:
        dh_hours += 500

    if encapsulant == "POE":
        dh_hours = int(dh_hours * 0.8)  # POE is more resistant
        uv_hrs = int(uv_hrs * 0.9)

    summary = {
        "Recommended Damp Heat (hrs)": dh_hours,
        "Recommended UV Exposure (hrs)": uv_hrs,
        "Recommended Thermal Cycles": tc_cycles
    }

    rationale = []
    if dh_hours > 1000:
        rationale.append("🔴 High humidity/temp region — extended DH test suggested.")
    if uv_hrs > 300:
        rationale.append("🔆 High UV region — increased UV stress test advised.")
    if tc_cycles > 200:
        rationale.append("🌡️ High temperature fluctuation — extra TC cycles beneficial.")
    if encapsulant == "POE":
        rationale.append("✅ POE reduces DH/UV test need slightly.")

    return summary, rationale
