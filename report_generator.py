from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import pandas as pd

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "PVSimApp - Simulation Report", ln=True, align="C")
        self.ln(5)

    def add_section(self, title):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(2)

    def add_text(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, text)
        self.ln(2)

    def add_image(self, path, w=180):
        self.image(path, w=w)
        self.ln(5)

def generate_pdf_report(filename, config, monthly_df, deg_rate, risk_score, risk_label, failures, test_plan, financials, bom_b=None):
    pdf = PDFReport()
    pdf.add_page()

    pdf.add_section("System Configuration")
    for key, val in config.items():
        pdf.add_text(f"{key}: {val}")

    pdf.add_section("Monthly Energy Output (kWh)")
    for idx, row in monthly_df.iterrows():
        pdf.add_text(f"{row['Month']}: {row['Energy (kWh)']:.2f}")

    # Save and embed energy chart
    fig1 = plt.figure()
    monthly_df.plot(x='Month', y='Energy (kWh)', kind='bar', legend=False, ax=plt.gca())
    plt.title('Monthly Energy Output')
    fig1.savefig("energy_chart.png")
    pdf.add_image("energy_chart.png")
    plt.close(fig1)

    pdf.add_section("Degradation Analysis")
    pdf.add_text(f"Estimated Annual Degradation: {deg_rate:.2f}%")

    pdf.add_section("Failure Modes Predicted")
    for f in failures:
        pdf.add_text(f)

    pdf.add_section("Test Plan Recommendation")
    for k, v in test_plan.items():
        pdf.add_text(f"{k}: {v}")

    pdf.add_section("Risk Score Summary")
    pdf.add_text(f"Risk Score: {risk_score} ({risk_label})")

    pdf.add_section("Financial Summary")
    for k, v in financials.items():
        pdf.add_text(f"{k}: ${v:,.2f}" if "($)" in k else f"{k}: {v:.2f}")

    # BOM B Comparison (Optional)
    if bom_b:
        pdf.add_page()
        pdf.add_section("🔀 BOM A vs BOM B Comparison")
        for key in ["Module", "Inverter", "Encapsulant", "System Size (kW)"]:
            val_a = config.get(key, "-")
            val_b = bom_b["config"].get(key, "-")
            pdf.add_text(f"{key} → A: {val_a} | B: {val_b}")

        pdf.add_text(f"Energy → A: {monthly_df['Energy (kWh)'].sum():.2f} kWh | B: {bom_b['monthly_df']['Energy (kWh)'].sum():.2f} kWh")
        pdf.add_text(f"Degradation → A: {deg_rate:.2f}% | B: {bom_b['deg_rate']:.2f}%")
        pdf.add_text(f"Risk → A: {risk_score} ({risk_label}) | B: {bom_b['risk_score']} ({bom_b['risk_label']})")

        # Chart comparing BOM A vs B energy
        comp_df = pd.DataFrame({
            'Month': monthly_df['Month'],
            'BOM A': monthly_df['Energy (kWh)'],
            'BOM B': bom_b['monthly_df']['Energy (kWh)']
        })
        fig2 = plt.figure()
        comp_df.set_index("Month").plot(kind="bar", ax=plt.gca())
        plt.title("BOM A vs BOM B - Energy Output")
        fig2.savefig("compare_chart.png")
        pdf.add_image("compare_chart.png")
        plt.close(fig2)

    pdf.output(filename)
    if os.path.exists("energy_chart.png"):
        os.remove("energy_chart.png")
    if os.path.exists("compare_chart.png"):
        os.remove("compare_chart.png")
