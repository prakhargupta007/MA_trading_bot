import pandas as pd 
from config import APPL_STOCK_TEST_MODE

if APPL_STOCK_TEST_MODE:
    START_OF_BACKTESTING = '2015-06-01'
    END_OF_BACKTESTING = '2025-05-30'
    BACKTESTING_PERIOD = '10'
    option_1_chosen = False 

else:
    try: 
        from config import BACKTESTING_PERIOD
        print(f'\nOption 1 was chosen --> Backtesting period is set from today to exactly {BACKTESTING_PERIOD} years ago')
        option_1_chosen = True
        START_OF_BACKTESTING = None
        END_OF_BACKTESTING = None
    except:
        from config import START_OF_BACKTESTING, END_OF_BACKTESTING
        print(f'\nOption 2 was chosen --> Backtesting period is set from {START_OF_BACKTESTING} to {END_OF_BACKTESTING}')
        BACKTESTING_PERIOD = ((pd.to_datetime(END_OF_BACKTESTING) - pd.to_datetime(START_OF_BACKTESTING)).days)/365.25
        option_1_chosen = False
    

from config import TICKERS, DATA_API_IS_YFINANCE, STARTING_BALANCE
from config import SMA_LONG_PERIOD, SMA_SHORT_PERIOD, EMA_LONG_PERIOD, EMA_SHORT_PERIOD, RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD
from config import CHOSEN_STRATEGY
from data.fetch_data_from_yfinance import fetch_data_from_yfinance
from data.fetch_data_from_alpha_vantage import fetch_data_from_alpha_vantage 

from strategy.strategy_map import strategy_map

from backtest.backtest_strategy import backtest_strategy
from backtest.backtest_strategy import return_endbalance
from backtest.create_and_save_backtest_table_csv_file import create_and_save_backtest_table_csv_file
from backtest.convert_csv_file_to_excel_file_and_open_it import convert_csv_file_to_excel_file_and_open_it
from backtest.create_and_save_backtest_summary_table_csv_file import create_and_save_backtest_summary_table_csv_file
from backtest.convert_summary_csv_file_to_excel_file_and_open_it import convert_summary_csv_file_to_excel_file_and_open_it 

from matplotlib_plot_backtesting.matplotlib_plot_universal_backtest_signals import matplotlib_plot_universal_strategy_signals
from matplotlib_plot_backtesting.matplotlib_plot_sma_rsi_macd_strategy import matplotlib_plot_sma_rsi_macd_strategy

from plotly_plot_backtesting.plotly_plot_universal_strategy_signals_and_save import plotly_plot_universal_strategy_signals_and_save

from metrics.cagr import calculate_cagr
from metrics.profit import calculate_profit
from metrics.buy_hold_profit import calculate_profit_if_bought_and_held

import traceback 

def main():
    try:

        TICKER_LIST = TICKERS.split(',')

        summary_tickers = []
        summary_CAGRs = []
        summary_buy_hold_CAGRs = []

        for TICKER in TICKER_LIST: 

            bold_underscore = '\033[1m_\033[0m'
            print('\n',bold_underscore * 100)

            if APPL_STOCK_TEST_MODE: 
                data = pd.read_csv("/Users/prakhar/MA_trading_bot/data/test_data_AAPL.csv", index_col="Date", parse_dates=True)
                print('\nSample data of APPL, which is stored locally is being used')

            else:
                print(f'\n\nFetching historical data of {TICKER}')
                if DATA_API_IS_YFINANCE:
                    data = fetch_data_from_yfinance(TICKER, option_1_chosen, BACKTESTING_PERIOD, END_OF_BACKTESTING, START_OF_BACKTESTING)
                else: 
                    data = fetch_data_from_alpha_vantage(TICKER, option_1_chosen, BACKTESTING_PERIOD, END_OF_BACKTESTING, START_OF_BACKTESTING)
                    
                if data is None or data.empty:
                    raise ValueError(f"❌ No data was fetched for ticker {TICKER}. Please check the ticker symbol or your internet connection.")

                print(f'✅ Data of {TICKER} fetched successfully!\n\n')

            indicator_parameters = {
                'data': data,
                'sma_long_period': SMA_LONG_PERIOD,
                'sma_short_period': SMA_SHORT_PERIOD,
                'ema_long_period': EMA_LONG_PERIOD,
                'ema_short_period': EMA_SHORT_PERIOD,
                'rsi_period': RSI_PERIOD,
                'macd_fast': MACD_FAST_PERIOD,
                'macd_slow': MACD_SLOW_PERIOD,
                'macd_signal': MACD_SIGNAL_PERIOD
            }

            print(f'Backtesting strategy:  \033[1m{CHOSEN_STRATEGY.upper()}\033[0m STRATEGY\n')
            print(f'Generating transaction signals based on the strategy ...')
            signals = strategy_map[CHOSEN_STRATEGY](**indicator_parameters)
            print('✅ Transaction signals generated successfully\n\n')

            print('Backtesting based on strategy...')
            results_of_backtesting = backtest_strategy(data, signals, STARTING_BALANCE)
            print('✅ Results of backtesting generated successfully\n\n')

            print('Table getting saved...')
            backtest_table = create_and_save_backtest_table_csv_file(results_of_backtesting, TICKER)
            print(f"✅ Backtest table saved successfully\n\n")

            print('Showing results in table...')
            print(f'RESULTS OF \033[1m{CHOSEN_STRATEGY.upper()}\033[0m STRATEGY:')
            print(backtest_table)
            print(f"✅ backtest table printed successfully\n\n")

            print('Visualising the used strategy...')
            #Use following line for just buy and sell universal plotting:
            #matplotlib_plot_universal_strategy_signals(data,signals,TICKER, CHOSEN_STRATEGY.upper())
            plotly_plot_universal_strategy_signals_and_save(data,signals,TICKER, CHOSEN_STRATEGY.upper())    
            #Use following line for just sma_rsi_macd_strategy plotting:
            #matplotlib_plot_sma_rsi_macd_strategy(data, signals, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, TICKER, CHOSEN_STRATEGY.upper()) #matplotlib_plot_sma_rsi_macd_strategy(data, signals, SMA_LONG_PERIOD, SMA_SHORT_PERIOD,RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, TICKER)
            print('✅ plot shown successfully\n\n')

            print('Calculating metrics...')
            end_balance = return_endbalance()
            print(f'End balance: {end_balance}')
            profit_in_percent, profit = calculate_profit(STARTING_BALANCE, end_balance)
            print(f'Profit made: {profit}')
            print(f'Profit made: {profit_in_percent}')
            cagr = calculate_cagr(STARTING_BALANCE, float(BACKTESTING_PERIOD), end_balance)
            print(f'CAGR: {cagr} %')
            print('✅ metrics calculated successfully\n\n')

            profit_of_buy_and_hold, cash_at_end_of_buy_and_hold = calculate_profit_if_bought_and_held(data, STARTING_BALANCE)
            print(f'If bought and hold: {profit_of_buy_and_hold}')
            cagr_buy_hold = calculate_cagr(STARTING_BALANCE, float(BACKTESTING_PERIOD), cash_at_end_of_buy_and_hold)
            print(f'CAGR of buy and hold: {cagr_buy_hold} %')
            print('✅ metrics of buy and hold option calculated successfully\n\n')

            print('Converting csv file to excel file and opening it (if desired)...')
            print(convert_csv_file_to_excel_file_and_open_it(TICKER)) # will only open if chosen to do so in config file

            summary_tickers.append(TICKER)
            summary_CAGRs.append(f'{cagr} %')
            summary_buy_hold_CAGRs.append(f'{cagr_buy_hold} %')

        summary_table = create_and_save_backtest_summary_table_csv_file(summary_tickers, summary_CAGRs, summary_buy_hold_CAGRs)
        if option_1_chosen == False or APPL_STOCK_TEST_MODE:
            print(f'RESULTS OF \033[1m{CHOSEN_STRATEGY.upper()}\033[0m STRATEGY FROM \033[1m{START_OF_BACKTESTING}\033[0m TO \033[1m{END_OF_BACKTESTING}\033[0m --> (\033[1m{round(float(BACKTESTING_PERIOD), 2)}\033[0m years)')
        else:
            print(f'RESULTS OF \033[1m{CHOSEN_STRATEGY.upper()}\033[0m STRATEGY OVER PAST \033[1m{round(float(BACKTESTING_PERIOD), 2)}\033[0m years')
        print(f'{summary_table}\n\n')

        print('Converting csv summary file to excel summary file and opening it (if desired)...') 
        print(convert_summary_csv_file_to_excel_file_and_open_it())

    except Exception as e:
        print("\n❌ An error occurred:")
        traceback.print_exc()  # Shows full error with file name + line number
        exit(1)

if __name__ == "__main__":
    main()





