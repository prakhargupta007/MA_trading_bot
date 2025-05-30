import csv 
from tabulate import tabulate 
import pandas as pd
import os

from config import TICKERS
from config import FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE
FOLDER_PATH = FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE

def create_and_save_backtest_summary_table_csv_file(summary_tickers, summary_CAGRs, summary_buy_hold_CAGRs):
    os.makedirs(FOLDER_PATH, exist_ok=True)

    file_name = f'summary_backtest_table_{TICKERS}.csv'
    full_path = os.path.join(FOLDER_PATH, file_name)

    # Write to CSV file
    with open(full_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Ticker', 'Strategy CAGR (%)', 'Buy & Hold CAGR (%)'])

        for ticker, strategy_cagr, buy_hold_cagr in zip(summary_tickers, summary_CAGRs, summary_buy_hold_CAGRs):
            writer.writerow([ticker, strategy_cagr, buy_hold_cagr])

    print(f'\n\033[1mSummary of all tickers:\033[0m')
    df = pd.read_csv(full_path)
    summary_table = tabulate(df, headers='keys', tablefmt='grid')

    return summary_table
