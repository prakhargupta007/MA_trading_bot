import numpy as np
from config import RISK_FREE_RATE


def safe_sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    returns = np.asarray(returns, dtype=float)
    if returns.size == 0:
        return 0.0

    excess_returns = returns - risk_free_rate / periods_per_year
    mean_return = np.nanmean(excess_returns)
    std_return = np.nanstd(excess_returns)

    if np.isnan(std_return) or np.isclose(std_return, 0.0):
        return 0.0
    return (mean_return / std_return) * np.sqrt(periods_per_year)


def calculate_sharpe_ratio(portfolio_values, periods_per_year=252):
    """
    Calculate an annualized Sharpe ratio safely.
    """
    if hasattr(portfolio_values, "pct_change"):
        returns = portfolio_values.pct_change().dropna().to_numpy()
    else:
        pv = np.asarray(portfolio_values, dtype=float)
        returns = np.diff(pv) / pv[:-1]
    sharpe = safe_sharpe_ratio(
        returns,
        risk_free_rate=RISK_FREE_RATE,
        periods_per_year=periods_per_year,
    )
    return round(sharpe, 3)
