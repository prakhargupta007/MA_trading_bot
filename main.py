import traceback 
import pandas as pd 
from datetime import datetime

from config import USE_STORED_DATA, STORED_DATA_TO_BE_READ

if USE_STORED_DATA:

    #START_OF_BACKTESTING = '2023-01-03'
    #END_OF_BACKTESTING = '2025-08-15'
    
    START_OF_BACKTESTING = '2017-01-02'
    END_OF_BACKTESTING = '2025-08-15'

    BACKTESTING_PERIOD = str(round((datetime.strptime(END_OF_BACKTESTING, '%Y-%m-%d') - datetime.strptime(START_OF_BACKTESTING, '%Y-%m-%d')).days / 365.25, 3))
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
    

from config import TICKERS, DATA_API_IS_YFINANCE, STARTING_BALANCE, VISUALISE_PLOTTED_SIGNAL_EXECUTIONS
from config import SMA_LONG_PERIOD, SMA_SHORT_PERIOD, EMA_LONG_PERIOD, EMA_SHORT_PERIOD, RSI_PERIOD, MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD, RSI_OVERBOUGHT_WARNING, RSI_OVERSOLD_WARNING
from config import DATA_PATH_FOR_SENTIMENT_STRATEGY
from config import CHOSEN_STRATEGY
from config import USE_STOP_LOSS, CHOSEN_STOP_LOSS
from config import COLUMN_NAME, STOP_LOSS_THRESHOLD, ATR_PERIOD, ATR_MULTIPLIER
from data.fetch_data.fetch_data_from_yfinance import fetch_data_from_yfinance
from data.fetch_data.fetch_data_from_alpha_vantage import fetch_data_from_alpha_vantage 

from indicators.check_indicator_length import check_indicator_length

from strategy_map import strategy_map
from stop_loss_map import stop_loss_map

from backtest.backtest_strategy import backtest_strategy
from backtest.backtest_strategy import return_endbalance
from backtest.backtest_strategy import return_portfolio_values 
from backtest.create_and_save_backtest_table_csv_file import create_and_save_backtest_table_csv_file
from backtest.convert_csv_file_to_excel_file_and_open_it import convert_csv_file_to_excel_file_and_open_it
from backtest.create_and_save_backtest_summary_table_csv_file import create_and_save_backtest_summary_table_csv_file
from backtest.convert_summary_csv_file_to_excel_file_and_open_it import convert_summary_csv_file_to_excel_file_and_open_it 
from backtest.convert_csv_file_to_pdf import convert_csv_summarized_backtest_table_to_pdf
from backtest.enforce_signal_consistency import enforce_signal_consistency

from matplotlib_plot_backtesting.matplotlib_plot_universal_backtest_signals import matplotlib_plot_universal_strategy_signals
from matplotlib_plot_backtesting.matplotlib_plot_sma_rsi_macd_strategy import matplotlib_plot_sma_rsi_macd_strategy

from plotly_plot_backtesting.plotly_plot_universal_strategy_signals_and_save import plotly_plot_universal_strategy_signals_and_save
from plotly_plot_backtesting.plotly_plot_strategy_with_indicators_and_save import plotly_plot_strategy_with_indicators_and_save
from plotly_plot_backtesting.plotly_plot_portfolio_values_chart import plotly_plot_portfolio_values

from metrics.cagr import calculate_cagr
from metrics.profit import calculate_profit
from metrics.buy_hold_profit import calculate_profit_if_bought_and_held
from metrics.cagr_strategy_efficiency import cagr_strategy_efficiency
from metrics.average_cagr_of_list import calculate_average_cagr_of_list
from metrics.sharpe import calculate_sharpe_ratio

from sentiment_analysis.debug_date_alignment import debug_date_alignment




def main():
    try:
        TICKER_LIST = TICKERS.split(',')

        summary_tickers = []
        summary_CAGRs = []
        summary_realized_CAGRs = []
        summary_buy_hold_CAGRs = []
        summary_cagr_strategy_efficiencies = []
        summary_sharpe_ratios = []
        # NEW lists
        summary_realized_sharpe_ratios = []
        summary_realized_cagr_strategy_efficiencies = []

        for TICKER in TICKER_LIST: 
            bold_underscore = '\033[1m_\033[0m'
            print('\n', bold_underscore * 200)

            if USE_STORED_DATA: 
                data = pd.read_csv(STORED_DATA_TO_BE_READ, index_col="Date", parse_dates=True)
                print('\nSample data of AAPL, which is stored locally is being used')
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
                'macd_signal': MACD_SIGNAL_PERIOD,
                'rsi_overbought': RSI_OVERBOUGHT_WARNING,
                'rsi_oversold': RSI_OVERSOLD_WARNING,
                'data_path_for_sentiment_strategy' : DATA_PATH_FOR_SENTIMENT_STRATEGY
            }

            stop_loss_parameters = {
                'column_name': COLUMN_NAME,
                'threshold': STOP_LOSS_THRESHOLD,
                'atr_period': ATR_PERIOD,
                'atr_mult': ATR_MULTIPLIER,
            }


            message, good_to_go = check_indicator_length(data, indicator_parameters)
            if not good_to_go:
                print(f'❌ {message}')
                exit()
            else:
                print(f'✅ {message}')

            print(f'Backtesting strategy:  \033[1m{CHOSEN_STRATEGY.upper()}\033[0m STRATEGY\n')
            print(f'Generating transaction signals based on the strategy ...')
            signals = strategy_map[CHOSEN_STRATEGY](**indicator_parameters) 
            print('✅ Transaction signals generated successfully\n\n')
            

            #debug_date_alignment(data, signals)
            if USE_STOP_LOSS:
                signals = stop_loss_map[CHOSEN_STOP_LOSS](data, signals, **stop_loss_parameters)
                signals = enforce_signal_consistency(signals) # Fix so that so that no Nan Vaues occur in summar backtest table
                #signals = static_stop_loss(data, signals, STOP_LOSS_THRESHOLD)
                print('✅ Stop-loss applied successfully\n\n')

            print('Backtesting based on strategy...')

            # diagnostic step for quick check 
            print("Last 10 signals:", signals[-10:])
            print("Last action in signals:", signals[-1])
            results_of_backtesting = backtest_strategy(data, signals, STARTING_BALANCE)
            print('✅ Results of backtesting generated successfully\n\n')

            print('Table getting saved...')
            backtest_table = create_and_save_backtest_table_csv_file(results_of_backtesting, TICKER)
            print(f"✅ Backtest table saved successfully\n\n")

            print('Showing results in table...')
            print(f'RESULTS OF \033[1m{CHOSEN_STRATEGY.upper()}\033[0m STRATEGY:')
            print('The number of days inbetween buy and sell transactions are just the number of tradings days (=days which exclude weekends and holidays)')
            print(backtest_table)
            print(f"✅ backtest table printed successfully\n\n")

            if VISUALISE_PLOTTED_SIGNAL_EXECUTIONS:
                print('Visualising the used strategy...')
                plotly_plot_universal_strategy_signals_and_save(data, signals, TICKER, CHOSEN_STRATEGY.upper())
                plotly_plot_strategy_with_indicators_and_save(data, signals, TICKER, CHOSEN_STRATEGY.upper(), indicator_parameters)

            portfolio_values = return_portfolio_values()
            portfolio_values_series = pd.Series(portfolio_values)

            if VISUALISE_PLOTTED_SIGNAL_EXECUTIONS:      
                plotly_plot_portfolio_values(portfolio_values_series, data, TICKER)
                print('✅ plots shown successfully\n\n')

            # --- Metrics ---
            print('Calculating metrics...')
            final_balance = return_endbalance()
            profit_in_percent, profit = calculate_profit(STARTING_BALANCE, final_balance)
            cagr = calculate_cagr(STARTING_BALANCE, float(BACKTESTING_PERIOD), final_balance)

            # --- Sharpe Ratios ---
            sharpe_ratio = calculate_sharpe_ratio(portfolio_values_series) if len(portfolio_values) > 1 else None

            # --- Realized Sharpe & CAGR ---
            action_indices = [i for i, action in enumerate(results_of_backtesting[0]) if action in ['SELL', 'SELL (forced at end)']]


            last_sell_data_index = None
            holding = False
            for i in range(len(signals)):
                if signals[i] == 'BUY' and not holding:
                    holding = True
                elif signals[i] in ['SELL', 'SELL (forced at end)'] and holding:
                    last_sell_data_index = i
                    holding = False

            realized_sharpe_ratio = None
            if last_sell_data_index is not None:
                last_action_index = action_indices[-1]
                last_sell_balance = results_of_backtesting[4][last_action_index]
                realized_portfolio_values = portfolio_values_series.copy()
                realized_portfolio_values.iloc[last_sell_data_index + 1:] = last_sell_balance
                if len(realized_portfolio_values) > 1:
                    realized_sharpe_ratio = calculate_sharpe_ratio(realized_portfolio_values)
            else:
                last_sell_balance = STARTING_BALANCE
                realized_portfolio_values = pd.Series([STARTING_BALANCE] * len(portfolio_values_series), index=portfolio_values_series.index)
                if len(realized_portfolio_values) > 1:
                    realized_sharpe_ratio = calculate_sharpe_ratio(realized_portfolio_values)

            realized_cagr = calculate_cagr(STARTING_BALANCE, float(BACKTESTING_PERIOD), last_sell_balance)

            # Handle cases where sharpe might be NaN (e.g., zero volatility)
            import math
            if sharpe_ratio is None or math.isnan(sharpe_ratio):
                sharpe_ratio = 0
            if realized_sharpe_ratio is None or math.isnan(realized_sharpe_ratio):
                realized_sharpe_ratio = 0

            # --- Buy & Hold comparison ---
            profit_of_buy_and_hold, cash_at_end_of_buy_and_hold = calculate_profit_if_bought_and_held(data, STARTING_BALANCE)
            cagr_buy_hold = calculate_cagr(STARTING_BALANCE, float(BACKTESTING_PERIOD), cash_at_end_of_buy_and_hold)
            cagr_strategy_efficiency_in_percent = cagr_strategy_efficiency(cagr, cagr_buy_hold)
            realized_cagr_strategy_efficiency_in_percent = cagr_strategy_efficiency(realized_cagr, cagr_buy_hold)

            # --- Append all values (always filled now) ---
            summary_tickers.append(TICKER)
            summary_CAGRs.append(cagr)
            summary_realized_CAGRs.append(realized_cagr)
            summary_buy_hold_CAGRs.append(cagr_buy_hold)
            summary_cagr_strategy_efficiencies.append(cagr_strategy_efficiency_in_percent)
            summary_sharpe_ratios.append(sharpe_ratio)
            summary_realized_sharpe_ratios.append(realized_sharpe_ratio)
            summary_realized_cagr_strategy_efficiencies.append(realized_cagr_strategy_efficiency_in_percent)

        # Summary table creation
        summary_table, csv_path_of_summary_table = create_and_save_backtest_summary_table_csv_file(
            summary_tickers, 
            summary_CAGRs, 
            summary_buy_hold_CAGRs, 
            summary_cagr_strategy_efficiencies, 
            summary_sharpe_ratios,
            summary_realized_CAGRs=summary_realized_CAGRs,
            summary_realized_sharpe_ratios=summary_realized_sharpe_ratios,
            summary_realized_cagr_strategy_efficiencies=summary_realized_cagr_strategy_efficiencies
        )
        # Headline + printing
        if option_1_chosen == False or USE_STORED_DATA:
            print(f'RESULTS OF \033[1m{CHOSEN_STRATEGY.upper()}\033[0m STRATEGY FROM \033[1m{START_OF_BACKTESTING}\033[0m TO \033[1m{END_OF_BACKTESTING}\033[0m --> (\033[1m{round(float(BACKTESTING_PERIOD), 2)}\033[0m years)')
        else:
            print(f'RESULTS OF \033[1m{CHOSEN_STRATEGY.upper()}\033[0m STRATEGY OVER PAST \033[1m{round(float(BACKTESTING_PERIOD), 2)}\033[0m years')
        print(summary_table)
        print(f'Average CAGR: {calculate_average_cagr_of_list(summary_CAGRs):.2f}%')
        print(f'Average Realized CAGR: {calculate_average_cagr_of_list(summary_realized_CAGRs):.2f}%')

        # File conversions
        convert_summary_csv_file_to_excel_file_and_open_it()
        convert_csv_summarized_backtest_table_to_pdf(
            csv_path_of_summary_table,
            title=f'{CHOSEN_STRATEGY.upper()} STRATEGY RESULTS with Backtesting period from {START_OF_BACKTESTING} to {END_OF_BACKTESTING}'
        )

        print('\n\nEnd of backtesting!\nADIOS! :D\n\n\n')

    except Exception as e:
        print("\n❌ An error occurred:")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()