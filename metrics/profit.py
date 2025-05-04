def calculate_profit(starting_balance, end_balance):
    profit = (end_balance - starting_balance)/starting_balance
    profit_in_percent = f'{profit*100:.2f}%'
    return profit_in_percent