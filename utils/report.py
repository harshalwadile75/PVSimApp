import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_to_csv(df, filename):
    df.to_csv(filename, index=False)

def export_to_pdf(filename, config, monthly_energy, degradation, risk, test_summary, roi_info, rationale):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 40
    line_height = 18

    def write_line(text, size=10):
        nonlocal y
        c.setFont("Helvetica", size)
        c.drawString(40, y, str(text))
        y -= line_height

    write_line("🔆 PVSimApp – Simulation Report", size=14)
    write_line("")

    write_line("📍 Configuration")
    for k, v in config.items():
        write_line(f"{k}: {v}")
    write_line("")

    write_line("📈 Monthly Energy (kWh)")
    for month, energy in monthly_energy:
        write_line(f"{month}: {energy:.2f}")
    write_line("")

    write_line(f"📉 Annual Degradation: {degradation:.2f}%")
    write_line(f"Risk Classification: {risk}")
    write_line("")

    write_line("🧪 Recommended Tests")
    for k, v in test_summary.items():
        write_line(f"{k}: {v}")
    write_line("")

    write_line("📌 Rationale")
    for r in rationale:
        write_line(f"- {r}")
    write_line("")

    write_line("💰 Financial Summary")
    for k, v in roi_info.items():
        if isinstance(v, float):
            write_line(f"{k}: {v:,.2f}")
        else:
            write_line(f"{k}: {v}")

    c.save()

def export_comparison_pdf(filename, bom_a, bom_b):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 40
    line_height = 20

    def write(text, size=10):
        nonlocal y
        c.setFont("Helvetica", size)
        c.drawString(40, y, str(text))
        y -= line_height

    write("🔆 PVSimApp – BOM Comparison Summary", size=14)
    write("")

    metrics = ["Annual Energy (kWh)", "Degradation (%)", "ROI (%)"]
    a_vals = [bom_a["Energy"], bom_a["Degradation"], bom_a["ROI"]]
    b_vals = [bom_b["Energy"], bom_b["Degradation"], bom_b["ROI"]]

    for i in range(3):
        write(f"{metrics[i]}")
        write(f"  - BOM A: {a_vals[i]:.2f}")
        write(f"  - BOM B: {b_vals[i]:.2f}")
        write("")

    c.save()
