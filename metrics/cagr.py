def calculate_cagr(starting_balance, backtesting_period, end_balance):
    cagr = ((end_balance / starting_balance) ** (1 / backtesting_period)) - 1  
    cagr_in_percent = f'{cagr * 100:.2f}%'
    return cagr_in_percent
