import csv 
from tabulate import tabulate 
import pandas as pd
import os

from config import FOLDER_PATH

def create_and_save_backtest_table(backtesting_results, ticker):
    actions, dates, numbers, prices, cash_flows = backtesting_results

    os.makedirs(FOLDER_PATH, exist_ok=True)

    file_name = f'Backtesting table of {ticker}.csv'
    full_path = os.path.join(FOLDER_PATH, file_name)

    with open(full_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Action', 'Date', 'Number of Stocks', 'Price per Stock', 'Cash Flow'])
        
        # Combine the lists and write each row
        for action, date, number, price, cash_flow in zip(actions, dates, numbers, prices, cash_flows):
            writer.writerow([action, date, number, price, cash_flow])

    print(f'Backtesting procedure of \033[1m{ticker}\033[0m:')
    df = pd.read_csv(file_name)  # Change: read from the unique file
    backtest_table = tabulate(df, headers='keys', tablefmt='grid')

    return backtest_table

