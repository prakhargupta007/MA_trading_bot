import csv 
from tabulate import tabulate 
import pandas as pd

def create_backtest_table(backtesting_results, ticker):
    actions, dates, numbers, prices, cash_flows = backtesting_results

    file_name = f'Backtesting table of {ticker}.csv'
    with open(file_name, mode='w', newline='') as file:
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