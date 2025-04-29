import pandas as pd
from indicators.sma import calculate_sma 

def backtest_strategy(data, signals, sma_long_period, starting_balance):
    list_actions = []
    list_dates = []
    list_number_of_stocks = []
    list_price_per_stock = []
    list_total_cash_flow = []

    n_stocks_bought = 0  # Initially, you have 0 stocks
    sma_series_length = len(calculate_sma(data, sma_long_period)) 

    signal_index = 0  # index for tracking position in signals list

    for i in range(sma_long_period - 1, sma_series_length):
        if signal_index >= len(signals):
            break  # Prevent out-of-range error

        price_of_stock = data['Close'].iloc[i]
        signal = signals[signal_index]

        if signal == 'HOLD':
            signal_index += 1
            continue  # <-- SKIP hold signals completely

        if signal == 'BUY':
            n_stocks_bought = starting_balance / price_of_stock
            total_spent = n_stocks_bought * price_of_stock
            starting_balance -= total_spent

            list_price_per_stock.append(round(price_of_stock, 2))
            list_number_of_stocks.append(round(n_stocks_bought, 2))
            list_total_cash_flow.append(round(-total_spent, 2))  # 💥 correct cash flow

        elif signal == 'SELL':
            n_stocks_sold = n_stocks_bought
            starting_balance += n_stocks_sold * price_of_stock

            list_price_per_stock.append(round(price_of_stock, 2))
            list_number_of_stocks.append(round(n_stocks_sold * -1, 2))
            list_total_cash_flow.append(round(starting_balance, 2))

        list_actions.append(signal)
        list_dates.append(data.index[i])

        signal_index += 1

    # Final adjustment: if last action was 'BUY', convert stock to cash
    if signals[-1] == 'BUY':
        final_price = data["Close"].iloc[-1]
        starting_balance += final_price * n_stocks_bought

        list_actions.append('STAY, but stock value converted into cash')
        list_dates.append(f'last date of data: {data.index[-1]}')
        list_number_of_stocks.append(round(n_stocks_bought, 2))
        list_price_per_stock.append(round(final_price, 2))
        list_total_cash_flow.append(f'+{round(starting_balance, 2)}')

    return list_actions, list_dates, list_number_of_stocks, list_price_per_stock, list_total_cash_flow
