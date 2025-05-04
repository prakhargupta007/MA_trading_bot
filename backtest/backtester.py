import pandas as pd
from indicators.sma import calculate_sma 
from backtest.transaction_fee import calculate_transaction_fee, get_accurate_number_of_stocks

def backtest_strategy(data, signals, sma_long_period, starting_balance):
    list_actions = []
    list_dates = []
    list_number_of_stocks = []
    list_price_per_stock = []
    list_total_cash_flow = []

    n_stocks_bought = 0  # Initially, you have 0 stocks
    sma_series_length = len(calculate_sma(data, sma_long_period)) 
    signal_index = 0  # index for tracking position in signals list

    hold_counter = 0
    stay_counter = 0
    position = False  # False means: No stock held

    for i in range(sma_long_period - 1, sma_series_length):
        if signal_index >= len(signals):
            break  # Prevent out-of-range error

        price_of_stock = data['Close'].iloc[i]
        signal = signals[signal_index]

        if signal == 'HOLD':
            if position:
                hold_counter += 1  # If holding stocks, increase the hold counter
            else:
                stay_counter += 1  # If no stocks, increase the stay counter
            signal_index += 1
            continue  # Skip hold signals completely

        if signal == 'BUY':
            # If we were staying, log how long we stayed without buying
            if stay_counter > 0:
                list_actions.append(f'STAY for {stay_counter} days')
                list_dates.append('')
                list_number_of_stocks.append('')
                list_price_per_stock.append('')
                list_total_cash_flow.append('')
                stay_counter = 0  # Reset stay counter

            n_stocks_bought,transaction_fee, reamaining_balance = get_accurate_number_of_stocks(starting_balance, price_of_stock) 
            starting_balance = reamaining_balance
                
            list_actions.append('BUY')
            list_dates.append(data.index[i])   
            list_price_per_stock.append(round(price_of_stock, 2))
            list_number_of_stocks.append(round(n_stocks_bought, 2))
            list_total_cash_flow.append(round(-n_stocks_bought * price_of_stock, 2))  # Correct cash flow

            position = True  # Now we hold stocks
            signal_index += 1

        elif signal == 'SELL':
            # If we were holding, log how long we held
            if hold_counter > 0:
                list_actions.append(f'HOLD for {hold_counter} days')
                list_dates.append('')
                list_number_of_stocks.append('')
                list_price_per_stock.append('')
                list_total_cash_flow.append('')
                hold_counter = 0  # Reset hold counter

            list_actions.append('SELL')
            list_dates.append(data.index[i])
            n_stocks_sold = n_stocks_bought
            starting_balance += (n_stocks_sold * price_of_stock) - calculate_transaction_fee(n_stocks_sold)

            list_price_per_stock.append(round(price_of_stock, 2))
            list_number_of_stocks.append(round(-n_stocks_sold, 2))  # Selling stocks
            list_total_cash_flow.append(round(n_stocks_sold * price_of_stock, 2))  # Correct cash flow

            position = False  # No longer holding stock
            signal_index += 1

    # Final adjustment: if last action was 'BUY', convert stock to cash
    if position:  # If still holding stock, sell it at last price
        if hold_counter > 0:
            list_actions.append(f'HOLD for {hold_counter} days')
            list_dates.append(data.index[-hold_counter])
            list_number_of_stocks.append('')
            list_price_per_stock.append('')
            list_total_cash_flow.append('')

        list_actions.append('SELL (forced at end)')
        list_dates.append(data.index[-1])
        price_of_stock = data['Close'].iloc[-1]
        n_stocks_sold = n_stocks_bought
        starting_balance += n_stocks_sold * price_of_stock
    
    return list_actions, list_dates, list_number_of_stocks, list_price_per_stock, list_total_cash_flow
