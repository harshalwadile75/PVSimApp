def validate_bom(module, inverter, num_modules, location, weather_df):
    results = []
    issues = 0

    # DC/AC ratio check
    system_kw = module["Power (W)"] * num_modules / 1000
    ac_kw = inverter["AC Power (kW)"]
    dcac_ratio = system_kw / ac_kw
    if dcac_ratio > 1.35:
        results.append(f"⚠️ DC/AC ratio is high ({dcac_ratio:.2f}). Risk of clipping.")
        issues += 1
    elif dcac_ratio < 0.8:
        results.append(f"⚠️ DC/AC ratio is low ({dcac_ratio:.2f}). Under-utilized inverter.")
        issues += 1
    else:
        results.append(f"✅ DC/AC ratio ({dcac_ratio:.2f}) is within recommended range.")

    # Voltage range sanity (simplified)
    if module["Voc (V)"] * num_modules > inverter["Max Input Voltage (V)"]:
        results.append("❌ String voltage exceeds inverter max input. Reduce # modules or reconfigure.")
        issues += 1
    else:
        results.append("✅ String voltage within inverter input limits.")

    # Irradiance check
    high_irr_days = (weather_df["G(i)"] > 1000).sum()
    if high_irr_days > 20:
        results.append("🔆 Location has many high irradiance days. Ensure thermal management is good.")
    else:
        results.append("☁️ Location irradiance levels are moderate.")

    return results, issues
