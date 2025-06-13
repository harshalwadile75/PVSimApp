def compute_risk_score(deg_rate, test_plan, failures):
    # Normalize degradation rate
    deg_score = max(0, 1 - deg_rate / 5)

    # Evaluate test plan intensity
    dh = test_plan.get("Damp Heat (hours)", 1000)
    uv = test_plan.get("UV Exposure (kWh/m²)", 15)
    tc = test_plan.get("Thermal Cycles", 200)

    test_score = (
        min(dh / 2000, 1.0) * 0.4 +
        min(uv / 30, 1.0) * 0.3 +
        min(tc / 300, 1.0) * 0.3
    )

    # Penalty for failure modes
    penalty = len(failures) * 0.05
    raw_score = max(0.0, (deg_score + test_score) / 2 - penalty)

    label = "High Risk" if raw_score < 0.4 else "Medium Risk" if raw_score < 0.7 else "Low Risk"
    return round(raw_score, 3), label
