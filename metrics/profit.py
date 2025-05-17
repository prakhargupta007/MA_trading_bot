def calculate_profit(starting_balance, end_balance):
    absolute_profit = end_balance - starting_balance
    profit_in_percent = f'{(absolute_profit/starting_balance)*100:.2f}%'
    return profit_in_percent, absolute_profit 