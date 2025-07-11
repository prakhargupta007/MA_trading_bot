import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

from config import FOLDER_PATH_FOR_PDF_SUMMARIZED_BACKTESTING_FILE
FOLDER_PATH = FOLDER_PATH_FOR_PDF_SUMMARIZED_BACKTESTING_FILE

def convert_csv_summarized_backtest_table_to_pdf(csv_path, title, image_path="temp_table.png"):
    # Ensure output folder exists
    os.makedirs(FOLDER_PATH, exist_ok=True)

    # Load and clean CSV
    df = pd.read_csv(csv_path)
    df.columns = [col.strip() for col in df.columns]

    # Create figure for table
    fig, ax = plt.subplots(figsize=(12, len(df) * 0.6 + 1))  # Dynamic height
    ax.axis('off')

    # Draw the table
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    # Save high-res image
    plt.savefig(image_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Prepare PDF
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated on: {timestamp}", ln=True, align='C')

    # Insert table image
    pdf.image(image_path, x=10, y=40, w=190)

    # Save PDF with fixed name (no timestamp)
    pdf_filename = os.path.join(FOLDER_PATH, f"{title.replace(' ', '_')}.pdf")
    pdf.output(pdf_filename)
    print(f"✅ PDF created: {pdf_filename}")

    # Clean up image
    if os.path.exists(image_path):
        os.remove(image_path)
