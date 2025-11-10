# indicators/volatility.py

import pandas as pd
import numpy as np

def calculate_volatility(data, window=14):
    """
    Calculates rolling volatility (standard deviation of daily returns).
    Returns daily volatility as a decimal (e.g., 0.02 = 2%).
    """
    returns = data['Close'].pct_change()
    rolling_std = returns.rolling(window=window).std()
    return rolling_std
