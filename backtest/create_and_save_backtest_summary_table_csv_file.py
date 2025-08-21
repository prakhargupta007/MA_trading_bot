'''
import csv 
from tabulate import tabulate 
import pandas as pd
import os

from config import TICKERS
from config import FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE
FOLDER_PATH = FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE

def create_and_save_backtest_summary_table_csv_file(summary_tickers, summary_CAGRs, summary_buy_hold_CAGRs, summary_cagr_strategy_efficiencies, summary_sharpe_ratios, summary_realized_CAGRs=None):
    os.makedirs(FOLDER_PATH, exist_ok=True)

    file_name = f'summary_backtest_table_{TICKERS}.csv'
    full_path = os.path.join(FOLDER_PATH, file_name)

    # Write to CSV file
    with open(full_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Ticker', 'Strategy CAGR (%)', 'Realized CAGR (%)', 'Buy & Hold CAGR (%)', 'CAGR Strategy Efficiency (%)', 'Sharpe ratio', ''])

        for ticker, strategy_cagr, buy_hold_cagr, cagr_strategy_efficiency, sharpe_ratio, realized_cagr in zip(
            summary_tickers, 
            summary_CAGRs, 
            summary_buy_hold_CAGRs, 
            summary_cagr_strategy_efficiencies, 
            summary_sharpe_ratios, 
            summary_realized_CAGRs or [None] * len(summary_tickers)
        ):
            writer.writerow([
                ticker, 
                f"{strategy_cagr:.2f}", 
                f"{realized_cagr:.2f}" if realized_cagr is not None else "N/A", 
                f"{buy_hold_cagr:.2f}", 
                f"{cagr_strategy_efficiency:.2f}", 
                f"{sharpe_ratio:.2f}" if sharpe_ratio is not None else "N/A"
            ])

    print(f'\n\033[1mSummary of all tickers:\033[0m')
    df = pd.read_csv(full_path)
    summary_table = tabulate(df, headers='keys', tablefmt='grid')

    return summary_table, full_path
'''
'''
import csv 
from tabulate import tabulate 
import pandas as pd
import os

from config import TICKERS
from config import FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE
FOLDER_PATH = FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE

def create_and_save_backtest_summary_table_csv_file(
    summary_tickers, 
    summary_CAGRs, 
    summary_buy_hold_CAGRs, 
    summary_cagr_strategy_efficiencies, 
    summary_sharpe_ratios, 
    summary_realized_CAGRs=None,
    summary_realized_sharpe_ratios=None,
    summary_realized_cagr_strategy_efficiencies=None
):
    os.makedirs(FOLDER_PATH, exist_ok=True)

    file_name = f'summary_backtest_table_{TICKERS}.csv'
    full_path = os.path.join(FOLDER_PATH, file_name)

    # Write to CSV file
    with open(full_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Ticker', 
            'Strategy CAGR (%)', 
            'Realized CAGR (%)', 
            'Buy & Hold CAGR (%)', 
            'CAGR Strategy Efficiency (%)',
            'Realized CAGR Strategy Efficiency (%)',
            'Sharpe Ratio', 
            'Realized Sharpe Ratio'
        ])

        for ticker, strategy_cagr, realized_cagr, buy_hold_cagr, cagr_strategy_efficiency, realized_cagr_efficiency, sharpe_ratio, realized_sharpe_ratio in zip(
            summary_tickers, 
            summary_CAGRs, 
            summary_realized_CAGRs or [None] * len(summary_tickers),
            summary_buy_hold_CAGRs, 
            summary_cagr_strategy_efficiencies, 
            summary_realized_cagr_strategy_efficiencies or [None] * len(summary_tickers),
            summary_sharpe_ratios, 
            summary_realized_sharpe_ratios or [None] * len(summary_tickers)
        ):
            writer.writerow([
                ticker, 
                f"{strategy_cagr:.2f}" if strategy_cagr is not None else "N/A", 
                f"{realized_cagr:.2f}" if realized_cagr is not None else "N/A", 
                f"{buy_hold_cagr:.2f}" if buy_hold_cagr is not None else "N/A", 
                f"{cagr_strategy_efficiency:.2f}" if cagr_strategy_efficiency is not None else "N/A", 
                f"{realized_cagr_efficiency:.2f}" if realized_cagr_efficiency is not None else "N/A", 
                f"{sharpe_ratio:.2f}" if sharpe_ratio is not None else "N/A", 
                f"{realized_sharpe_ratio:.2f}" if realized_sharpe_ratio is not None else "N/A"
            ])

    print(f'\n\033[1mSummary of all tickers:\033[0m')
    df = pd.read_csv(full_path)
    summary_table = tabulate(df, headers='keys', tablefmt='grid')

    return summary_table, full_path

'''










import csv 
from tabulate import tabulate 
import pandas as pd
import os

from config import TICKERS
from config import FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE
FOLDER_PATH = FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE

def create_and_save_backtest_summary_table_csv_file(
    summary_tickers, 
    summary_CAGRs, 
    summary_buy_hold_CAGRs, 
    summary_cagr_strategy_efficiencies, 
    summary_sharpe_ratios, 
    summary_realized_CAGRs=None,
    summary_realized_sharpe_ratios=None,
    summary_realized_cagr_strategy_efficiencies=None
):
    os.makedirs(FOLDER_PATH, exist_ok=True)

    file_name = f'summary_backtest_table_{TICKERS}.csv'
    full_path = os.path.join(FOLDER_PATH, file_name)

    # Write to CSV file
    with open(full_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Ticker', 
            'CAGR', 
            'Realized CAGR', 
            'B&H CAGR', 
            'CAGR Eff.',
            'Realized CAGR Eff.',
            'Sharpe', 
            'Realized Sharpe'
        ])

        for ticker, strategy_cagr, realized_cagr, buy_hold_cagr, cagr_strategy_efficiency, realized_cagr_efficiency, sharpe_ratio, realized_sharpe_ratio in zip(
            summary_tickers, 
            summary_CAGRs, 
            summary_realized_CAGRs or [None] * len(summary_tickers),
            summary_buy_hold_CAGRs, 
            summary_cagr_strategy_efficiencies, 
            summary_realized_cagr_strategy_efficiencies or [None] * len(summary_tickers),
            summary_sharpe_ratios, 
            summary_realized_sharpe_ratios or [None] * len(summary_tickers)
        ):
            writer.writerow([
                ticker, 
                f"{strategy_cagr:.2f}" if strategy_cagr is not None else "N/A", 
                f"{realized_cagr:.2f}" if realized_cagr is not None else "N/A", 
                f"{buy_hold_cagr:.2f}" if buy_hold_cagr is not None else "N/A", 
                f"{cagr_strategy_efficiency:.2f}" if cagr_strategy_efficiency is not None else "N/A", 
                f"{realized_cagr_efficiency:.2f}" if realized_cagr_efficiency is not None else "N/A", 
                f"{sharpe_ratio:.2f}" if sharpe_ratio is not None else "N/A", 
                f"{realized_sharpe_ratio:.2f}" if realized_sharpe_ratio is not None else "N/A"
            ])

    print(f'\n\033[1mSummary of all tickers:\033[0m')
    df = pd.read_csv(full_path)
    summary_table = tabulate(df, headers='keys', tablefmt='grid', floatfmt=".2f")

    return summary_table, full_path
