import numpy as np
from config import RISK_FREE_RATE

def calculate_sharpe_ratio(portfolio_values, periods_per_year=252):
    '''
    # This function calculates the annualized Sharpe ratio of a portfolio
    Arguments:
        portfolio_values (pd.Series): Series of portfolio values for every day of backtesting data (exmpl: end-of-day balances)
        risk_free_rate (float): Annual risk-free rate as decimal (usuall ROI of US treasury bonds)
        periods_per_year (int): Number of periods per year (252 for daily)
    '''
    returns = portfolio_values.pct_change().dropna()
    excess_returns = returns - (RISK_FREE_RATE / periods_per_year)
    mean_excess_return = excess_returns.mean()
    std_excess_return = excess_returns.std()
    if std_excess_return == 0:
        return np.nan
    sharpe_ratio = (mean_excess_return / std_excess_return) * np.sqrt(periods_per_year)
    return round(sharpe_ratio, 3) 