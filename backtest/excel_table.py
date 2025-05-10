import pandas as pd
import os
from config import OUTPUT_FOLDER_PATH_FOR_EXCEL_FILE
from config import FOLDER_PATH_FOR_CSV_FILE

def convert_csv_file_to_excel_file(ticker):
    csv_file_name = f"{ticker}_backtesting_table.csv"
    excel_sheet_name = f"{ticker}_backtesting_excel"
    csv_path = os.path.join(FOLDER_PATH_FOR_CSV_FILE, csv_file_name)
    excel_path = os.path.join(OUTPUT_FOLDER_PATH_FOR_EXCEL_FILE, f"{excel_sheet_name}.xlsx")

    # Check if the CSV file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ CSV file not found at: {csv_path}")

    # Read CSV and save as Excel
    df = pd.read_csv(csv_path)
    df.to_excel(excel_path, index=False)

    # Open the Excel file (works only on Mac)
    os.system(f'open "{excel_path}"')

    return f" Excel file of backtesting data of {ticker} converted to Excel and saved"
