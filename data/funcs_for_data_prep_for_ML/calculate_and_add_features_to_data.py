import pandas as pd
import numpy as np 
import ta 

def calculate_and_add_features_to_data(data):
    '''
    arguments: data
    returns: data with calculated features which in this case are different indicators
    '''
    data = data.copy() # In order to avoid changing the original data by accident

    # RSI (Relative Strength Index) with a 14-day window
    rsi = ta.momentum.RSIIndicator(close=data['Close'], window=14)
    data['rsi_14'] = rsi.rsi()

    # MACD and its signal line
    macd = ta.trend.MACD(close=data['Close'])
    data['macd'] = macd.macd()
    data['macd_signal'] = macd.macd_signal()

    # Simple Moving Averages (10-day and 50-day)
    sma_50 = ta.trend.SMAIndicator(close=data['Close'], window=50)
    sma_200 = ta.trend.SMAIndicator(close=data['Close'], window=200)
    data['sma_50'] = sma_50.sma_indicator()
    data['sma_200'] = sma_200.sma_indicator()

    # Bollinger Bands (20-day window, 2 standard deviations)
    bb = ta.volatility.BollingerBands(close=data['Close'], window=20, window_dev=2)
    data['bb_upper'] = bb.bollinger_hband()
    data['bb_lower'] = bb.bollinger_lband()
    data['bb_percent'] = bb.bollinger_pband()  # how wide the bands are, as a %

    # Daily returns and rolling volatility (standard deviation of daily returns)
    data['daily_return'] = data['Close'].pct_change()
    data['volatility_14'] = data['daily_return'].rolling(window=14).std()

    # Momentum: how much price has changed over 10 days
    data['momentum_10'] = data['Close'] - data['Close'].shift(10)

    # Drop any rows with NaN values caused by indicator windows
    data_with_features = data.dropna().reset_index(drop=True)

    return data_with_features



