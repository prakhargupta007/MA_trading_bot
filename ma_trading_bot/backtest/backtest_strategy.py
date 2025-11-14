'''
from .transaction_fee import calculate_transaction_fee, get_accurate_number_of_stocks
from config import SLIPPAGE_RATE

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
            price = (1+SLIPPAGE_RATE) * price 
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
            price = (1-SLIPPAGE_RATE) * price 
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
'''


import pandas as pd
from .transaction_fee import calculate_transaction_fee, get_accurate_number_of_stocks
from config import SLIPPAGE_RATE

# --- global state for plotting / summaries ---
list_portfolio_values = []
list_actions = []
list_dates = []
list_number_of_stocks = []
list_price_per_stock = []
list_total_cash_flow = []
_end_cash = None  # final cash at end of backtest

def _align_signals_to_data_index(data, signals_list):
    """
    Align a list of signals to the DataFrame index:
    last len(signals_list) rows get the signals; earlier rows are HOLD.
    Returns a list of length len(data).
    """
    n = len(data)
    m = len(signals_list)
    aligned = ['HOLD'] * max(0, n - m) + list(signals_list[-min(m, n):])
    return aligned[:n]

def backtest_strategy(data, signals, starting_balance):
    """
    Runs backtest and fills global lists for table output.
    Also constructs and returns a trades_df (only BUY/SELL rows) with Profit per closed round-trip.
    """
    global list_portfolio_values, list_actions, list_dates, list_number_of_stocks, list_price_per_stock, list_total_cash_flow, _end_cash

    # reset globals
    list_actions = []
    list_dates = []
    list_number_of_stocks = []
    list_price_per_stock = []
    list_total_cash_flow = []
    list_portfolio_values = []

    # align signals to data index to avoid index mismatches
    signals_aligned = _align_signals_to_data_index(data, signals)

    cash = float(starting_balance)
    position = False
    n_stocks_held = 0.0
    last_buy_cost = None  # total cash out on the last BUY (including fee)
    last_buy_qty = 0.0

    trade_rows = []  # rows for trades_df with Profit computed on SELLs

    for i in range(len(data)):
        date_i = data.index[i]
        close_i = float(data['Close'].iloc[i])
        sig = signals_aligned[i] if i < len(signals_aligned) else 'HOLD'

        if sig == 'HOLD':
            # No change in holdings
            portfolio_value = cash + (n_stocks_held * close_i if position else 0.0)
            list_portfolio_values.append(round(portfolio_value, 2))
            continue

        if sig == 'BUY':
            # Price with slippage
            px = (1.0 + SLIPPAGE_RATE) * close_i
            qty, fee, cash = get_accurate_number_of_stocks(cash, px)
            total_cost = qty * px + fee  # positive number; cash already reduced in helper

            # record table row
            list_actions.append('BUY')
            list_dates.append(date_i)
            list_number_of_stocks.append(round(qty, 6))
            list_price_per_stock.append(round(px, 6))
            list_total_cash_flow.append(round(-total_cost, 2))  # negative cash flow

            # set position state
            position = True
            n_stocks_held = qty
            last_buy_qty = qty
            last_buy_cost = total_cost  # store positive cost

            # trades_df row (profit N/A at buy)
            trade_rows.append({
                "Action": "BUY",
                "Date": pd.to_datetime(date_i),
                "Number of Stocks": round(qty, 6),
                "Price per Stock": round(px, 6),
                "Cash Flow": round(-total_cost, 2),
                "Profit": float("nan")
            })

        elif sig == 'SELL':
            px = (1.0 - SLIPPAGE_RATE) * close_i
            fee = calculate_transaction_fee(n_stocks_held)
            proceeds = n_stocks_held * px - fee
            cash += proceeds

            # record table row
            list_actions.append('SELL')
            list_dates.append(date_i)
            list_number_of_stocks.append(round(-n_stocks_held, 6))
            list_price_per_stock.append(round(px, 6))
            list_total_cash_flow.append(round(proceeds, 2))

            # compute realized profit for this round-trip if we had a prior BUY
            realized_profit = float("nan")
            if last_buy_cost is not None:
                # buy cash flow was -last_buy_cost; sell cash flow is +proceeds
                realized_profit = round(proceeds - last_buy_cost, 2)

            trade_rows.append({
                "Action": "SELL",
                "Date": pd.to_datetime(date_i),
                "Number of Stocks": round(-n_stocks_held, 6),
                "Price per Stock": round(px, 6),
                "Cash Flow": round(proceeds, 2),
                "Profit": realized_profit
            })

            # reset position
            position = False
            n_stocks_held = 0.0
            last_buy_qty = 0.0
            last_buy_cost = None

        # end-of-day portfolio (AFTER the action)
        portfolio_value = cash + (n_stocks_held * close_i if position else 0.0)
        list_portfolio_values.append(round(portfolio_value, 2))

    # force close at end if still in position (so we always realize a SELL)
    if position and n_stocks_held > 0:
        date_i = data.index[-1]
        close_i = float(data['Close'].iloc[-1])
        px = close_i  # no slippage on forced close, or apply if you prefer
        fee = calculate_transaction_fee(n_stocks_held)
        proceeds = n_stocks_held * px - fee
        cash += proceeds

        list_actions.append('SELL (forced at end)')
        list_dates.append(date_i)
        list_number_of_stocks.append(round(-n_stocks_held, 6))
        list_price_per_stock.append(round(px, 6))
        list_total_cash_flow.append(round(proceeds, 2))

        realized_profit = float("nan")
        if last_buy_cost is not None:
            realized_profit = round(proceeds - last_buy_cost, 2)

        trade_rows.append({
            "Action": "SELL (forced at end)",
            "Date": pd.to_datetime(date_i),
            "Number of Stocks": round(-n_stocks_held, 6),
            "Price per Stock": round(px, 6),
            "Cash Flow": round(proceeds, 2),
            "Profit": realized_profit
        })

        position = False
        n_stocks_held = 0.0
        last_buy_qty = 0.0
        last_buy_cost = None

        # final portfolio after forced close
        portfolio_value = cash
        list_portfolio_values[-1] = round(portfolio_value, 2)

    # store final cash for return_endbalance()
    _end_cash = round(cash, 2)

    # Build trades_df (only BUY/SELL rows), ensure correct dtypes
    trades_df = pd.DataFrame(trade_rows, columns=[
        "Action", "Date", "Number of Stocks", "Price per Stock", "Cash Flow", "Profit"
    ])
    if not trades_df.empty:
        trades_df = trades_df.sort_values("Date").reset_index(drop=True)
        numeric_cols = ["Number of Stocks", "Price per Stock", "Cash Flow", "Profit"]
        for col in numeric_cols:
            trades_df[col] = pd.to_numeric(trades_df[col], errors="coerce")

    # return old tuple PLUS trades_df for downstream summary code
    return (
        list_actions,
        list_dates,
        list_number_of_stocks,
        list_price_per_stock,
        list_total_cash_flow,
        trades_df
    )

def return_portfolio_values():
    global list_portfolio_values
    return list_portfolio_values

def return_endbalance():
    """
    Return the true end balance (cash after final day).
    Never returns None; if the engine never traded, returns starting cash reflected in list_portfolio_values.
    """
    global _end_cash, list_portfolio_values
    if _end_cash is not None:
        return _end_cash
    # fallback if something odd happens
    if list_portfolio_values:
        return list_portfolio_values[-1]
    return None
