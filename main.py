
from config import TICKER,  SMA_LONG_PERIOD, SMA_SHORT_PERIOD, RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, BACKTESTING_PERIOD, STARTING_BALANCE
from data.fetch_data import fetch_data
from strategy.combined_strategy import generate_signals
from backtest.backtester import backtest_strategy
from backtest.backtest_table import create_backtest_table
from indicators.sma import calculate_sma

def main():

    print('Fetching historical data...')
    data = fetch_data(TICKER, BACKTESTING_PERIOD)
    print('Data fetched successfully!')

    print('Generating transaction signals based on strategy...')
    bought = False
    signals = generate_signals(bought, data, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)
    print('Transaction signals generated successfully')

    print('Backtesting based on strategy...')
    results_of_backtesting = backtest_strategy(data, signals, SMA_LONG_PERIOD, STARTING_BALANCE)
    print('results of backtesting generated successfully')

    print('Showing results...')
    backtest_table = create_backtest_table(results_of_backtesting, TICKER)
    print(f"backtest table printed successfully")

    print('Showing results...')
    print(backtest_table)
    print(f"backtest table printed successfully")

if __name__ == "__main__":
    main()
