import pandas as pd
from indicators.sma import calculate_sma 
from backtest.transaction_fee import calculate_transaction_fee, get_accurate_number_of_stocks

def backtest_strategy(data, signals, starting_balance):
    # Remove sma_long_period parameter if not needed elsewhere
    list_actions = []
    list_dates = []
    list_number_of_stocks = []
    list_price_per_stock = []
    list_total_cash_flow = []

    n_stocks_bought = 0
    hold_counter = 0
    stay_counter = 0
    position = False

    for i in range(len(data)):
        price = data['Close'].iloc[i]
        signal = signals[i]  # Use signals[i] instead of signals[signal_index]

        if signal == 'HOLD':
            if position:
                hold_counter += 1
            else:
                stay_counter += 1
            continue

        if signal == 'BUY':
            if stay_counter > 0:
                list_actions.append(f'STAY for {stay_counter} days')
                list_dates.append(' ')
                list_number_of_stocks.append(' ')
                list_price_per_stock.append(' ')
                list_total_cash_flow.append(' ')
                stay_counter = 0

            n_stocks_bought, fee, starting_balance = get_accurate_number_of_stocks(starting_balance, price)
            list_actions.append('BUY')
            list_dates.append(data.index[i])
            list_number_of_stocks.append(round(n_stocks_bought, 2))
            list_price_per_stock.append(round(price, 2))
            total_cost = n_stocks_bought * price + fee
            list_total_cash_flow.append(round(-total_cost, 2))
            position = True

        elif signal == 'SELL':
            if hold_counter > 0:
                list_actions.append(f'HOLD for {hold_counter} days')
                list_dates.append(' ')
                list_number_of_stocks.append(' ')
                list_price_per_stock.append(' ')
                list_total_cash_flow.append(' ')
                hold_counter = 0

            list_actions.append('SELL')
            list_dates.append(data.index[i])
            n_stocks_sold = n_stocks_bought
            fee = calculate_transaction_fee(n_stocks_sold)
            proceeds = n_stocks_sold * price - fee
            starting_balance += proceeds
            list_number_of_stocks.append(round(-n_stocks_sold, 2))
            list_price_per_stock.append(round(price, 2))
            list_total_cash_flow.append(round(proceeds, 2))
            position = False

    if position:
        if hold_counter > 0:
            list_actions.append(f'HOLD for {hold_counter} days')
            list_dates.append(data.index[-hold_counter])
            list_number_of_stocks.append(' ')
            list_price_per_stock.append(' ')
            list_total_cash_flow.append(' ')
        list_actions.append('SELL (forced at end)')
        list_dates.append(data.index[-1])
        price = data['Close'].iloc[-1]
        n_stocks_sold = n_stocks_bought
        fee = calculate_transaction_fee(n_stocks_sold)
        proceeds = n_stocks_sold * price - fee
        starting_balance += proceeds
        list_number_of_stocks.append(round(-n_stocks_sold, 2))
        list_price_per_stock.append(round(price, 2))
        list_total_cash_flow.append(round(proceeds, 2))

    return list_actions, list_dates, list_number_of_stocks, list_price_per_stock, list_total_cash_flow


def return_endbalance():
    global list_actions
    global list_total_cash_flow

    indices = []

    for i, action in enumerate(list_actions):
        if action in ['SELL', 'SELL (forced at end)']:
            indices.append(i)

    # Error message just in case if there was no SELL action --> but this shouldn't happen
    if not indices:
        print("No SELL actions found.")
        return None

    last_index = indices[-1]

    end_balance = list_total_cash_flow[last_index]

    return end_balance
