def classify_degradation_risk(annual_deg_rate):
    if annual_deg_rate <= 0.5:
        return "🟢 Low Risk"
    elif 0.5 < annual_deg_rate <= 0.75:
        return "🟡 Moderate Risk"
    else:
        return "🔴 High Risk"

def explain_risk_factors(temp_c_series):
    avg_temp = temp_c_series.mean()
    max_temp = temp_c_series.max()

    if avg_temp > 35 or max_temp > 55:
        return "⚠️ High operating temperature increases chemical aging risk. Consider POE encapsulant."
    elif avg_temp > 28:
        return "ℹ️ Medium temp profile — use materials with moderate DH resistance."
    else:
        return "✅ Temperature profile is favorable for long-term reliability."
