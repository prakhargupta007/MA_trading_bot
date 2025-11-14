from ma_trading_bot.backtest.transaction_fee import (
    calculate_transaction_fee,
    get_accurate_number_of_stocks,
)

def calculate_profit_if_bought_and_held(data, starting_balance):
    initial_investment = starting_balance
    first_price = data['Close'].iloc[0]
    last_price = data['Close'].iloc[-1]
    n_stocks_bought, fee, starting_balance = get_accurate_number_of_stocks(starting_balance, first_price)

    n_stocks_sold = n_stocks_bought
    fee = calculate_transaction_fee(n_stocks_sold)
    proceeds = n_stocks_sold * last_price - fee
    starting_balance += proceeds
    cash_at_end = starting_balance
    profit = cash_at_end - initial_investment


    return profit, cash_at_end
