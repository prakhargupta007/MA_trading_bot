import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import textwrap

from config import FOLDER_PATH_FOR_PDF_SUMMARIZED_BACKTESTING_FILE
FOLDER_PATH = FOLDER_PATH_FOR_PDF_SUMMARIZED_BACKTESTING_FILE

def convert_csv_summarized_backtest_table_to_pdf(csv_path, title, image_path="temp_table.png"):
    # Ensure output folder exists
    os.makedirs(FOLDER_PATH, exist_ok=True)

    # Load and clean CSV
    df = pd.read_csv(csv_path)
    df.columns = [col.strip() for col in df.columns]

    # Wrap long column names to prevent overlap
    max_width = 25  # Maximum characters per line for column names
    wrapped_columns = [textwrap.fill(col, max_width) for col in df.columns]

    # Calculate approximate column widths based on content length
    col_widths = []
    for col in df.columns:
        # Get max length of column name or cell content (as strings)
        max_col_length = max(
            len(str(col)),  # Length of column name
            max(len(str(val)) for val in df[col])  # Max length of column values
        )
        # Scale width: approximate 0.1 per character, with a minimum and maximum
        col_widths.append(max(0.5, min(2.5, max_col_length * 0.1)))

    # Normalize widths to fit within figure
    total_width = sum(col_widths)
    col_widths = [w / total_width for w in col_widths]  # Normalize to sum to 1

    # Create figure with dynamic size
    fig, ax = plt.subplots(figsize=(12, len(df) * 0.6 + 1.5))  # Adjusted height for wrapped headers
    ax.axis('off')

    # Draw the table with custom column widths
    table = ax.table(
        cellText=df.values,
        colLabels=wrapped_columns,  # Use wrapped column names
        loc='center',
        cellLoc='center',
        colWidths=col_widths  # Set custom column widths
    )

    # Adjust table properties
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    # Make header cells bold
    for (i, j), cell in table.get_celld().items():
        if i == 0:  # Header row
            cell.set_text_props(weight='bold')
            cell.set_height(0.2)  # Existing height adjustment
        cell.set_text_props(wrap=True)

    # Save high-res image
    plt.savefig(image_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
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