import gspread
import pandas as pd
import os
from google.oauth2.service_account import Credentials
from config import OUTPUT_FOLDER_PATH_FOR_EXCEL_FILE

def convert_csv_file_to_excel_file(ticker):

    # Load account credentials from JSON file
    creds = Credentials.from_service_account_file("credentials.json", scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)

    # Define your target Excel output folder
    output_folder = OUTPUT_FOLDER_PATH_FOR_EXCEL_FILE

    csv_file_name = f"{ticker}_backtesting_table.csv"   # The name of the csv file that will get converted
    excel_sheet_name = f"{ticker}_backtesting_excel"    # The name of the new excel file that will get created

    # Create Google Sheet
    spreadsheet = client.create(excel_sheet_name)
    worksheet = spreadsheet.get_worksheet(0)

    df = pd.read_csv(csv_file_name)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    # Save to Folder 3
    excel_path = os.path.join(output_folder, f"{excel_sheet_name}.xlsx")
    df.to_excel(excel_path, index=False)
    # index=False means it won’t add the DataFrame’s index (like 0, 1, 2...) as a separate first column in Excel

    # Open file
    os.system(f'open "{excel_path}"')

    return f"✅ {csv_file_name} uploaded to Google Sheets as '{excel_sheet_name}', saved to Folder 'excel_trial_files_backtesting' and opened!"