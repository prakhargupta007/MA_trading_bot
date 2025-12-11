"""
Backtesting engine for next-day execution with fractional shares.

Global lists track actions/prices/cash for downstream plotting. Signals are assumed
to follow the len(data)+1 pattern (day i signal executes on day i+1, first entry is
HOLD, and the final signal is intentionally unexecuted).
"""

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


def backtest_strategy(data, signals, starting_balance):
    """
    Fractional-share backtesting engine for next-day execution signals.

    Assumptions:
    - Strategies prepend a HOLD to cover the 1-day execution lag.
    - signal[i] executes at Open[i]; a trailing unexecuted signal may be present.
    - Global state (list_* variables) is reused across runs; each call resets them.
    """

    global list_portfolio_values, list_actions, list_dates
    global list_number_of_stocks, list_price_per_stock
    global list_total_cash_flow, _end_cash

    # reset logs
    list_actions = []
    list_dates = []
    list_number_of_stocks = []
    list_price_per_stock = []
    list_total_cash_flow = []
    list_portfolio_values = []

    # Data validation
    if "Open" not in data.columns:
        raise ValueError("Backtest requires an 'Open' column for execution pricing.")
    if len(signals) != len(data):
        raise ValueError("Signals list must be the same length as the data index.")

    cash = float(starting_balance)
    position = False
    n_stocks_held = 0.0
    last_buy_cost = None

    trade_rows = []

    # Day 0 portfolio valuation (assumes initial HOLD)
    list_portfolio_values.append(round(cash, 2))

    # MAIN BACKTEST LOOP — EACH ROW IS A FULL DAY
    for i in range(len(data)):
        date_i = data.index[i]
        open_i = float(data["Open"].iloc[i])     # execution price
        close_i = float(data["Close"].iloc[i])   # mark-to-market price
        sig = signals[i]                         # DIRECT — because strategy handles lag

        # HOLD -----------------------------------------------------------
        if sig == "HOLD":
            portfolio_value = cash + (n_stocks_held * close_i if position else 0.0)
            list_portfolio_values.append(round(portfolio_value, 2))
            continue

        # BUY ------------------------------------------------------------
        if sig == "BUY":
            px = (1.0 + SLIPPAGE_RATE) * open_i

            # fractional shares supported
            qty, fee, new_cash = get_accurate_number_of_stocks(cash, px)
            total_cost = qty * px + fee
            cash = new_cash

            list_actions.append("BUY")
            list_dates.append(date_i)
            list_number_of_stocks.append(round(qty, 6))
            list_price_per_stock.append(round(px, 6))
            list_total_cash_flow.append(round(-total_cost, 2))

            position = True
            n_stocks_held = qty
            last_buy_cost = total_cost

            trade_rows.append({
                "Action": "BUY",
                "Date": pd.to_datetime(date_i),
                "Number of Stocks": round(qty, 6),
                "Price per Stock": round(px, 6),
                "Cash Flow": round(-total_cost, 2),
                "Profit": float("nan")
            })

        # SELL ------------------------------------------------------------
        elif sig == "SELL":
            if not position:
                # invalid sell, ignore
                portfolio_value = cash
                list_portfolio_values.append(round(portfolio_value, 2))
                continue

            px = (1.0 - SLIPPAGE_RATE) * open_i
            fee = calculate_transaction_fee(n_stocks_held)
            proceeds = n_stocks_held * px - fee
            cash += proceeds

            list_actions.append("SELL")
            list_dates.append(date_i)
            list_number_of_stocks.append(round(-n_stocks_held, 6))
            list_price_per_stock.append(round(px, 6))
            list_total_cash_flow.append(round(proceeds, 2))

            realized_profit = float("nan")
            if last_buy_cost is not None:
                realized_profit = round(proceeds - last_buy_cost, 2)

            trade_rows.append({
                "Action": "SELL",
                "Date": pd.to_datetime(date_i),
                "Number of Stocks": round(-n_stocks_held, 6),
                "Price per Stock": round(px, 6),
                "Cash Flow": round(proceeds, 2),
                "Profit": realized_profit
            })

            position = False
            n_stocks_held = 0.0
            last_buy_cost = None

        # PORTFOLIO VALUE AT END OF DAY (using close price)
        portfolio_value = cash + (n_stocks_held * close_i if position else 0.0)
        list_portfolio_values.append(round(portfolio_value, 2))

    # FORCED CLOSE AT END --------------------------------------------
    if position and n_stocks_held > 0:
        final_date = data.index[-1]
        close_px = float(data["Close"].iloc[-1])
        fee = calculate_transaction_fee(n_stocks_held)
        proceeds = n_stocks_held * close_px - fee
        cash += proceeds

        list_actions.append("SELL (forced at end)")
        list_dates.append(final_date)
        list_number_of_stocks.append(round(-n_stocks_held, 6))
        list_price_per_stock.append(round(close_px, 6))
        list_total_cash_flow.append(round(proceeds, 2))

        realized_profit = float("nan")
        if last_buy_cost is not None:
            realized_profit = round(proceeds - last_buy_cost, 2)

        trade_rows.append({
            "Action": "SELL (forced at end)",
            "Date": pd.to_datetime(final_date),
            "Number of Stocks": round(-n_stocks_held, 6),
            "Price per Stock": round(close_px, 6),
            "Cash Flow": round(proceeds, 2),
            "Profit": realized_profit
        })

        position = False
        n_stocks_held = 0.0
        list_portfolio_values[-1] = round(cash, 2)

    # SAVE END CASH ----------------------------------------------------
    _end_cash = round(cash, 2)

    # TRADES DATAFRAME -------------------------------------------------
    trades_df = pd.DataFrame(trade_rows, columns=[
        "Action", "Date", "Number of Stocks",
        "Price per Stock", "Cash Flow", "Profit"
    ])

    if not trades_df.empty:
        trades_df = trades_df.sort_values("Date").reset_index(drop=True)
        for col in ["Number of Stocks", "Price per Stock", "Cash Flow", "Profit"]:
            trades_df[col] = pd.to_numeric(trades_df[col], errors="coerce")

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
    Final cash after the last day.
    If nothing happened, returns starting cash.
    """
    global _end_cash, list_portfolio_values
    if _end_cash is not None:
        return _end_cash
    if list_portfolio_values:
        return list_portfolio_values[-1]
    return None
