from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def export_to_pdf(
    filename,
    config: dict,
    monthly_energy: list,
    degradation: float,
    risk: str,
    test_summary: dict,
    roi_info: dict,
    rationale: list
):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    line_height = 20
    y = height - 40

    def write(text, font="Helvetica", size=10, color=(0, 0, 0)):
        nonlocal y
        c.setFont(font, size)
        c.setFillColorRGB(*color)
        c.drawString(40, y, str(text))
        y -= line_height

    c.setTitle("PV Simulation Report")

    write("📄 PV Simulation Report", size=14)
    write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    write("")

    write("⚙️ Configuration Summary", size=12)
    for k, v in config.items():
        write(f"{k}: {v}")
    write("")

    write("📊 Monthly Energy (kWh)", size=12)
    for month, kwh in monthly_energy:
        write(f"{month}: {kwh:.2f}")
    write("")

    write("📉 Degradation & Risk", size=12)
    write(f"Estimated Annual Degradation: {degradation:.2f}%")
    write(f"Risk Classification: {risk}")
    write("")

    write("🧪 Recommended Tests", size=12)
    for k, v in test_summary.items():
        write(f"{k}: {v}")
    for line in rationale:
        write(f"- {line}")
    write("")

    write("💰 Financial Summary", size=12)
    for k, v in roi_info.items():
        write(f"{k}: ${v:,.2f}" if "($)" in k else f"{k}: {v:.2f}")

    c.save()
