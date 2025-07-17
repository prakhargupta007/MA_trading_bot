from backtest.transaction_fee import calculate_transaction_fee, get_accurate_number_of_stocks

def backtest_strategy(data, signals, starting_balance):
    # Declare global variables so that they can be accessed in the return_endbalance() function
    global list_portfolio_values
    global list_actions
    global list_total_cash_flow

    # Initialize all tracking lists
    list_actions = []
    list_dates = []
    list_number_of_stocks = []
    list_price_per_stock = []
    list_total_cash_flow = []
    list_portfolio_values = []  # Stores portfolio value for each day

    n_stocks_bought = 0
    hold_counter = 0
    stay_counter = 0
    position = False  # Whether a stock is currently held

    cash = starting_balance  # Cash available in portfolio
    n_stocks_held = 0  # Number of stocks held currently

    # Iterate over each day in the dataset
    for i in range(len(data)):
        price = data['Close'].iloc[i]  # Current day's closing price
        signal = signals[i] if i < len(signals) else 'HOLD'

        # Calculate and store portfolio value: cash + value of held stocks (if any) --> reason for this logic is to keep the flexibility to be able to invest just a specific part of the cash available. 
        
        portfolio_value = cash + (n_stocks_held * price if position else 0)
        list_portfolio_values.append(round(portfolio_value, 2))

        # If HOLD or STAY
        if signal == 'HOLD':
            if position:
                hold_counter += 1
            else:
                stay_counter += 1
            continue  # Skip to next day

        # BUY signal
        if signal == 'BUY':
            # Store stay period
            if stay_counter > 0:
                list_actions.append(f'STAY for {stay_counter} days')
                list_dates.append(' ')
                list_number_of_stocks.append(' ')
                list_price_per_stock.append(' ')
                list_total_cash_flow.append(' ')
                stay_counter = 0

            # Execute buy logic
            n_stocks_bought, fee, cash = get_accurate_number_of_stocks(cash, price)
            list_actions.append('BUY')
            list_dates.append(data.index[i])
            list_number_of_stocks.append(round(n_stocks_bought, 2))
            list_price_per_stock.append(round(price, 2))
            total_cost = n_stocks_bought * price + fee
            list_total_cash_flow.append(round(-total_cost, 2))  # Negative cash flow
            position = True
            n_stocks_held = n_stocks_bought

        # SELL signal
        elif signal == 'SELL':
            # store hold period
            if hold_counter > 0:
                list_actions.append(f'HOLD for {hold_counter} days')
                list_dates.append(' ')
                list_number_of_stocks.append(' ')
                list_price_per_stock.append(' ')
                list_total_cash_flow.append(' ')
                hold_counter = 0

            # Execute sell logic
            list_actions.append('SELL')
            list_dates.append(data.index[i])
            fee = calculate_transaction_fee(n_stocks_held)
            proceeds = n_stocks_held * price - fee
            cash += proceeds  # Add sale proceeds to cash
            list_number_of_stocks.append(round(-n_stocks_held, 2))  # Negative value because of 'sell'
            list_price_per_stock.append(round(price, 2))
            list_total_cash_flow.append(round(proceeds, 2))  # Positive cash flow
            position = False
            n_stocks_held = 0

    # If still holding a position at the end, force a sell
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
        fee = calculate_transaction_fee(n_stocks_held)
        proceeds = n_stocks_held * price - fee
        cash += proceeds
        list_number_of_stocks.append(round(-n_stocks_held, 2))
        list_price_per_stock.append(round(price, 2))
        list_total_cash_flow.append(round(proceeds, 2))

    # Return all result lists, including new list of portfolio values
    return list_actions, list_dates, list_number_of_stocks, list_price_per_stock, list_total_cash_flow

def return_portfolio_values():
    # This returns the portfolio values only on trading days, which are only weekdays and non-holiday days 
    global list_portfolio_values
    return list_portfolio_values

def return_endbalance():
    global list_actions
    global list_total_cash_flow

    # Find last sell action to determine end balance
    indices = [i for i, action in enumerate(list_actions) if action in ['SELL', 'SELL (forced at end)']]

    if not indices:
        print("No SELL actions found.")
        return None

    last_index = indices[-1]
    end_balance = list_total_cash_flow[last_index]

    return end_balance
