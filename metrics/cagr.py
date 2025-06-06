def calculate_cagr(starting_balance, backtesting_period, end_balance):
    if backtesting_period <= 0:
        return 0.0
    cagr = ((end_balance / starting_balance) ** (1 / backtesting_period)) - 1  
    cagr = round((cagr * 100),2)
    return cagr
