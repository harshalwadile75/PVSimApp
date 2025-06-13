import random

def recommend_bom(weather_df, modules_df, inverters_df):
    # Use average ambient temp to decide encapsulant
    avg_temp = weather_df["T2m"].mean()
    suggested_encap = "POE" if avg_temp > 28 else "EVA"

    # Heuristic: Match module & inverter by power size with safety margin
    candidates = []
    for _, mod in modules_df.iterrows():
        for _, inv in inverters_df.iterrows():
            mod_kw = mod["Power (W)"] / 1000
            if 0.9 * inv["AC Power (kW)"] <= mod_kw <= inv["AC Power (kW)"]:
                score = random.uniform(0.7, 1.0)  # Simulated score
                candidates.append({
                    "Module": mod["Model"],
                    "Inverter": inv["Model"],
                    "Score": round(score, 3),
                    "Encapsulant": suggested_encap
                })

    # Return top 3
    ranked = sorted(candidates, key=lambda x: x["Score"], reverse=True)
    return ranked[:3]
