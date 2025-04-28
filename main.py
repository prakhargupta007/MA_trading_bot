
from config import TICKER,  SMA_LONG_PERIOD, SMA_SHORT_PERIOD, RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, BACKTESTING_PERIOD, STARTING_BALANCE
from data.fetch_data import fetch_data
from strategy.combined_strategy import generate_signals
from backtest.backtester import backtest
from indicators.sma import calculate_sma

def main():
    # Fetch historical data
    data = fetch_data(TICKER, BACKTESTING_PERIOD)
    # Generate signals based on the strategy
    bought = False
    signals = generate_signals(bought, data, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)
    # Backtest the strategy
    sma_series_length = len(calculate_sma(data, SMA_SHORT_PERIOD))
    final_balance = backtest(data, signals, SMA_LONG_PERIOD, STARTING_BALANCE)
    
    print(f"Final balance after backtesting: ${final_balance:.2f}")

if __name__ == "__main__":
    main()
