def predict_failure_modes(module, weather_df, encapsulant="EVA"):
    temp = weather_df["T2m"]
    irr = weather_df["G(i)"]
    rh = weather_df["RH"]

    avg_temp = temp.mean()
    max_temp = temp.max()
    high_uv_days = (irr > 900).sum()
    high_humidity_days = (rh > 75).sum()

    failures = []

    if encapsulant == "EVA":
        if avg_temp > 35 or max_temp > 55:
            failures.append("🔴 Risk of PID (high temp + EVA)")
        if high_uv_days > 30:
            failures.append("🟡 Possible yellowing/discoloration (UV + EVA)")
        if high_humidity_days > 40:
            failures.append("🔴 Corrosion/delamination risk (humid + EVA)")
    elif encapsulant == "POE":
        failures.append("✅ POE: better resistance to PID, UV, corrosion")

    if max_temp - temp.min() > 50:
        failures.append("🟡 High thermal cycling range — check solder bond durability")

    if not failures:
        failures.append("✅ No major failure risks detected.")

    return failures
