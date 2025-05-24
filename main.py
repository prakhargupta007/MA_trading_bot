
from config import TICKER, DATA_API_IS_YFINANCE, SMA_LONG_PERIOD, SMA_SHORT_PERIOD, EMA_LONG_PERIOD , EMA_SHORT_PERIOD, RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, BACKTESTING_PERIOD, STARTING_BALANCE
from data.fetch_data_from_yfinance import fetch_data_from_yfinance
from data.fetch_data_from_alpha_vantage import fetch_data_from_alpha_vantage 

from strategy.sma_strategy import sma_strategy 
from strategy.ema_strategy import ema_strategy
from strategy.sma_rsi_strategy import sma_rsi_strategy 
from strategy.sma_rsi_macd_strategy import sma_rsi_macd_strategy

from backtest.backtest_strategy import backtest_strategy
from backtest.backtest_strategy import return_endbalance
from backtest.create_and_save_backtest_table_csv_file import create_and_save_backtest_table_csv_file
from backtest.convert_csv_file_to_excel_file_and_open_it import convert_csv_file_to_excel_file_and_open_it

from matplotlib_plot_backtesting.matplotlib_plot_universal_backtest_signals import matplotlib_plot_universal_strategy_signals
from matplotlib_plot_backtesting.matplotlib_plot_sma_rsi_macd_strategy import matplotlib_plot_sma_rsi_macd_strategy

from plotly_plot_backtesting.plotly_plot_universal_strategy_signals_and_save import plotly_plot_universal_strategy_signals_and_save

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
        print(f'✅ Data of {TICKER} fetched successfully!\n\n')

        print('Generating transaction signals based on strategy...')
        bought = False
        #signals = sma_strategy(bought, data, SMA_LONG_PERIOD, SMA_SHORT_PERIOD)
        #signals = ema_strategy(bought, data, EMA_LONG_PERIOD, EMA_SHORT_PERIOD)
        #signals = sma_rsi_strategy(bought, data, SMA_LONG_PERIOD, SMA_SHORT_PERIOD, RSI_PERIOD)
        signals = sma_rsi_macd_strategy(bought, data, SMA_LONG_PERIOD, SMA_SHORT_PERIOD, RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD)
        print('✅ Transaction signals generated successfully\n\n')

        print('Backtesting based on strategy...')
        results_of_backtesting = backtest_strategy(data, signals, STARTING_BALANCE)
        print('✅ Results of backtesting generated successfully\n\n')

        print('Table getting saved...')
        backtest_table = create_and_save_backtest_table_csv_file(results_of_backtesting, TICKER)
        print(f"✅ Backtest table saved successfully\n\n")

        print('Showing results in table...')
        print(backtest_table)
        print(f"✅ backtest table printed successfully\n\n")

        print('Visualising the used strategy...')
        #Use following line for just buy and sell universal plotting:
        #matplotlib_plot_universal_strategy_signals(data,signals,TICKER)
        plotly_plot_universal_strategy_signals_and_save(data,signals,TICKER)    
        #Use following line for just sma_rsi_macd_strategy plotting:
        #matplotlib_plot_sma_rsi_macd_strategy(data, signals, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, TICKER) #matplotlib_plot_sma_rsi_macd_strategy(data, signals, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, TICKER)
        print('✅ plot shown successfully\n\n')

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
        print('✅ metrics of buy and hold option calculated successfully\n\n')

        print('Converting csv file to excel file and opening it (if desired)...')
        print(convert_csv_file_to_excel_file_and_open_it(TICKER)) #will only open if chose to do so in config file


    except Exception as e:
        print("\n❌ An error occurred:")
        traceback.print_exc()  # Shows full error with file name + line number
        exit(1)

if __name__ == "__main__":
    main()





