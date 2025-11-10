# indicators/bollinger_bands.py

import pandas as pd

def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    Calculates Bollinger Bands.
    Returns upper_band, lower_band, mid_band
    """
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()

    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, lower_band, rolling_mean

