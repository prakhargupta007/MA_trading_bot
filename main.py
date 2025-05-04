
from config import TICKER,  SMA_LONG_PERIOD, SMA_SHORT_PERIOD, RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, BACKTESTING_PERIOD, STARTING_BALANCE
from data.fetch_data import fetch_data
from strategy.strategy_1 import generate_signals

from backtest.backtester import backtest_strategy
from backtest.backtest_table import create_and_save_backtest_table
from backtest.plot_backtest_data import plot_and_show_signals_of_strategy
from backtest.plot_strategy_1 import plot_and_show_indicators_and_signals_of_strategy_1

import traceback 

def main():
    try:
        print(f'\n\nFetching historical data of {TICKER}')
        data = fetch_data(TICKER, BACKTESTING_PERIOD)
        print('Data of {TICKER} fetched successfully!\n\n')

        print('Generating transaction signals based on strategy...')
        bought = False
        signals = generate_signals(bought, data, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)
        print('Transaction signals generated successfully\n\n')

        print('Backtesting based on strategy...')
        results_of_backtesting = backtest_strategy(data, signals, SMA_LONG_PERIOD, STARTING_BALANCE)
        print('results of backtesting generated successfully\n\n')

        print('Showing results...')
        backtest_table = create_and_save_backtest_table(results_of_backtesting, TICKER)
        print(f"backtest table printed successfully\n\n")

        print('Showing results...')
        print(backtest_table)
        print(f"backtest table printed successfully\n\n")

        print('Visualising the used strategy...')
        #plot_and_show_signals_of_strategy(data,signals,TICKER)
        plot_and_show_indicators_and_signals_of_strategy_1(data, signals, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, TICKER)
        print('Plot shown successfully\n\n')

    except Exception as e:
        print("\n❌ An error occurred:")
        traceback.print_exc()  # Shows full error with file name + line number
        exit(1)

if __name__ == "__main__":
    main()
