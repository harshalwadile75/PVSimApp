import matplotlib.pyplot as plt
import pandas as pd

def plot_hourly_time_series(hourly_df):
    fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

    axs[0].plot(hourly_df["Time"], hourly_df["POA Irradiance (W/m²)"])
    axs[0].set_title("POA Irradiance Over Time")
    axs[0].set_ylabel("Irradiance (W/m²)")

    axs[1].plot(hourly_df["Time"], hourly_df["Module Temp (°C)"], color="orange")
    axs[1].set_title("Module Temperature Over Time")
    axs[1].set_ylabel("Temp (°C)")

    axs[2].plot(hourly_df["Time"], hourly_df["Efficiency (%)"], color="green")
    axs[2].set_title("Module Efficiency Over Time")
    axs[2].set_ylabel("Efficiency (%)")
    axs[2].set_xlabel("Time")

    plt.tight_layout()
    return fig

def plot_loss_waterfall(system_kwh, loss_factors):
    labels = []
    values = [system_kwh]
    for name, pct in loss_factors.items():
        labels.append(f"- {name.capitalize()} Loss")
        values.append(-system_kwh * (pct / 100.0))
    labels.append("Final Output")
    values.append(system_kwh + sum(values[1:]))

    fig, ax = plt.subplots()
    ax.bar(range(len(values)), values, tick_label=labels)
    ax.set_title("Energy Loss Breakdown (Waterfall)")
    ax.set_ylabel("Energy (kWh)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    return fig
