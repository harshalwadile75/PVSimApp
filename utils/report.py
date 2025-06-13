import pandas as pd
from fpdf import FPDF
import os

def export_to_csv(df, filename="monthly_energy.csv"):
    df.to_csv(filename)
    return filename

def export_to_pdf(df, filename="monthly_energy.pdf", title="Monthly Energy Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_title(title)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)

    for index, row in df.iterrows():
        line = f"{index}: {row['Energy (kWh)']:.2f} kWh"
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.output(filename)
    return filename

