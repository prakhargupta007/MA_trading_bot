def calculate_cagr(starting_balance, backtesting_period, end_balance):
    cagr = ((end_balance / starting_balance) ** (1 / backtesting_period)) - 1  
    cagr = round((cagr * 100),2)
    return cagr
