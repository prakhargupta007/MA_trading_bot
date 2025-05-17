
from config import TICKER, DATA_API_IS_YFINANCE, SMA_LONG_PERIOD, SMA_SHORT_PERIOD, RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, BACKTESTING_PERIOD, STARTING_BALANCE
from data.fetch_data_from_yfinance import fetch_data_from_yfinance
from data.fetch_data_from_alpha_vantage import fetch_data_from_alpha_vantage 
from strategy.strategy_1 import generate_signals
from strategy.strategy_SMA import strategy_SMA

from backtest.backtest_strategy import backtest_strategy
from backtest.backtest_strategy import return_endbalance
from backtest.backtest_table import create_and_save_backtest_table_csv_file
from backtest.plot_backtest_data import plot_and_show_signals_of_strategy
from backtest.plot_strategy_1 import plot_and_show_indicators_and_signals_of_strategy_1
from backtest.excel_table import convert_csv_file_to_excel_file

from metrics.cagr import calculate_cagr
from metrics.profit import calculate_profit
from metrics.buy_hold_profit import calculate_profit_if_bought_and_held

import traceback 

def main():
    try:
        print(f'\n\nFetching historical data of {TICKER}')
        if DATA_API_IS_YFINANCE:
            data = fetch_data_from_yfinance(TICKER, BACKTESTING_PERIOD)
        else: 
            data = fetch_data_from_alpha_vantage(TICKER, BACKTESTING_PERIOD)
        print('✅ Data of {TICKER} fetched successfully!\n\n')

        print('Generating transaction signals based on strategy...')
        bought = False
        signals = generate_signals(bought, data, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)
        print('✅ Transaction signals generated successfully\n\n')

        print('Backtesting based on strategy...')
        results_of_backtesting = backtest_strategy(data, signals, SMA_LONG_PERIOD, STARTING_BALANCE)
        print('✅ Results of backtesting generated successfully\n\n')

        print('Table getting saved...')
        backtest_table = create_and_save_backtest_table_csv_file(results_of_backtesting, TICKER)
        print(f"✅ Backtest table saved successfully\n\n")

        print('Showing results in table...')
        print(backtest_table)
        print(f"✅ backtest table printed successfully\n\n")

        print('Visualising the used strategy...')
        #Use follllowing line for just buy and sell universal plotting:
        plot_and_show_signals_of_strategy(data,signals,TICKER) 
        #Use following line for just strategy_1 plotting:
        plot_and_show_indicators_and_signals_of_strategy_1(data, signals, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, TICKER)
        print('✅ Plot shown successfully\n\n')

        print('Calculating metrics...')
        end_balance = return_endbalance()
        print(f'End balance: {end_balance}')
        profit_in_percent, profit = calculate_profit(STARTING_BALANCE, end_balance)
        print(f'Profit made: {profit}')
        print(f'Profit made: {profit_in_percent}')
        print(f'CAGR: {calculate_cagr(STARTING_BALANCE, float(BACKTESTING_PERIOD), end_balance)}')
        print('✅ metrics calculated successfully\n\n')
        profit_of_buy_and_hold, cash_at_end_of_buy_and_hold = calculate_profit_if_bought_and_held(data, STARTING_BALANCE)
        print(f'If bought and hold: {profit_of_buy_and_hold}')
        print(f'CAGR of buy and hold: {calculate_cagr(STARTING_BALANCE, float(BACKTESTING_PERIOD), cash_at_end_of_buy_and_hold)}')

        print('Converting csv file to excel file...')
        print(convert_csv_file_to_excel_file(TICKER))
        print('✅ csv file converted to excel sheet successfully\n\n')

        

    except Exception as e:
        print("\n❌ An error occurred:")
        traceback.print_exc()  # Shows full error with file name + line number
        exit(1)

if __name__ == "__main__":
    main()
