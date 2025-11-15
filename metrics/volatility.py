import numpy as np
import pandas as pd


def calculate_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility given a series of periodic returns.
    Returns:
        float: annualized standard deviation in percent units matching input (e.g., 0.20 == 20%).
    """
    if returns is None:
        return 0.0
    series = pd.Series(returns).dropna()
    if series.empty:
        return 0.0
    std = series.std(ddof=1)
    if np.isnan(std):
        return 0.0
    return float(std * np.sqrt(periods_per_year))
