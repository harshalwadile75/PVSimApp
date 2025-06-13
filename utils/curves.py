import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_iv_curve(vmp, imp, voc, isc, n_points=100):
    voltages = np.linspace(0, voc, n_points)
    currents = []

    for v in voltages:
        if v < vmp:
            i = isc - (isc - imp) / vmp * v
        else:
            i = imp * max(0, (voc - v) / (voc - vmp))
        currents.append(i)

    return voltages, np.array(currents)

def plot_iv_pv_curves(vmp, imp, voc, isc):
    v, i = generate_iv_curve(vmp, imp, voc, isc)
    p = v * i

    fig1, ax1 = plt.subplots()
    ax1.plot(v, i)
    ax1.set_title("I-V Curve")
    ax1.set_xlabel("Voltage (V)")
    ax1.set_ylabel("Current (A)")
    ax1.grid(True)

    fig2, ax2 = plt.subplots()
    ax2.plot(v, p)
    ax2.set_title("P-V Curve")
    ax2.set_xlabel("Voltage (V)")
    ax2.set_ylabel("Power (W)")
    ax2.grid(True)

    return fig1, fig2
