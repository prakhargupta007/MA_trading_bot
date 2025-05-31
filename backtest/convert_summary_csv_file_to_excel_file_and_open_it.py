import pandas as pd
import os
from config import FOLDER_PATH_FOR_SUMMARIZED_EXCEL_FILE
from config import FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE
from config import OPEN_SUMMARY_EXCEL_FILE_AFTER_SAVING
from config import TICKERS

def convert_summary_csv_file_to_excel_file_and_open_it():

    csv_file_name = f'summary_backtest_table_{TICKERS}.csv'
    excel_sheet_name = f"summary_backtesting_excel_{TICKERS}"
    csv_path = os.path.join(FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE, csv_file_name)
    excel_path = os.path.join(FOLDER_PATH_FOR_SUMMARIZED_EXCEL_FILE, f"{excel_sheet_name}.xlsx")

    # Check if the CSV file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ CSV file not found at: {csv_path}")

    # Read CSV and save as Excel
    df = pd.read_csv(csv_path)
    df.to_excel(excel_path, index=False)

    # Open the Excel file (works only on Mac)
    if OPEN_SUMMARY_EXCEL_FILE_AFTER_SAVING:
        os.system(f'open "{excel_path}"')

    return f"✅ csv summary file of backtesting data converted to summary Excel file and saved\n\n"
