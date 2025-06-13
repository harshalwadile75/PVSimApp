import pandas as pd

def classify_climate_zone(temp):
    if temp > 30:
        return "hot-humid"
    elif 25 < temp <= 30:
        return "hot-dry"
    elif 15 <= temp <= 25:
        return "temperate"
    else:
        return "cold"

def recommend_bom(weather_df, modules_df, inverters_df):
    avg_temp = weather_df["T2m"].mean()
    climate = classify_climate_zone(avg_temp)
    failure_df = pd.read_csv("data/failure_rates.csv")

    candidates = []
    for _, mod in modules_df.iterrows():
        for _, inv in inverters_df.iterrows():
            mod_kw = mod["Power (W)"] / 1000
            if 0.9 * inv["AC Power (kW)"] <= mod_kw <= inv["AC Power (kW)"]:
                for encap in ["EVA", "POE"]:
                    row = failure_df[
                        (failure_df["Model"] == mod["Model"]) &
                        (failure_df["Encapsulant"] == encap) &
                        (failure_df["ClimateZone"] == climate)
                    ]
                    fail_rate = row["AvgAnnualFailureRate"].values[0] if not row.empty else 0.015
                    score = 1 - fail_rate  # Higher score = lower failure
                    candidates.append({
                        "Module": mod["Model"],
                        "Inverter": inv["Model"],
                        "Encapsulant": encap,
                        "Score": round(score, 3)
                    })

    return sorted(candidates, key=lambda x: x["Score"], reverse=True)[:3]
