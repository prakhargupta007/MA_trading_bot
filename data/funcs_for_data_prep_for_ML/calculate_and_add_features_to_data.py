import pandas as pd
import numpy as np 
import ta 

from config import GSPC_DATA_FILE_PATH 
from config import NDX_DATA_FILE_PATH 
from config import TECH_SECTOR_STOCK 


def calculate_and_add_features_to_data(data):
    '''
    arguments: data
    returns: data with calculated features which in this case are different indicators
    '''
    data = data.copy()  # In order to avoid changing the original data by accident

    # RSI (Relative Strength Index) with a 14-day window
    rsi = ta.momentum.RSIIndicator(close=data['Close'], window=14)
    data['rsi_14'] = rsi.rsi()

    # MACD and its signal line
    macd = ta.trend.MACD(close=data['Close'])
    data['macd'] = macd.macd()
    data['macd_signal'] = macd.macd_signal()

    # Simple Moving Averages (50-day and 200-day)
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

    # Volume Moving Average (20-day rolling mean of volume)
    data['volume_20d_ma'] = data['Volume'].rolling(window=20).mean()

    # On-Balance Volume (OBV)
    obv = ta.volume.OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume'])
    data['obv'] = obv.on_balance_volume()

    # Load and prepare GSPC data
    gspc_data = pd.read_csv(GSPC_DATA_FILE_PATH, parse_dates=['Date'], index_col='Date')
    gspc_returns = gspc_data['Close'].pct_change()
    gspc_volatility = gspc_returns.rolling(window=20).std()

    # Align to main data's index
    data['gspc_daily_return'] = gspc_returns.reindex(data.index)
    data['gspc_20d_volatility'] = gspc_volatility.reindex(data.index)



    if TECH_SECTOR_STOCK:
        # Load and prepare NDX data
        ndx_data = pd.read_csv(NDX_DATA_FILE_PATH, parse_dates=['Date'], index_col='Date')
        ndx_returns = ndx_data['Close'].pct_change()
        ndx_volatility = ndx_returns.rolling(window=20).std()
        ndx_sma = ndx_data['Close'].rolling(window=20).mean()

        # Align to main data's index
        data['ndx_daily_return'] = ndx_returns.reindex(data.index)
        data['ndx_20d_volatility'] = ndx_volatility.reindex(data.index)
        data['ndx_20d_sma'] = ndx_sma.reindex(data.index)


    # Momentum difference % from rolling mean
    momentum_windows = [5, 10, 20, 50, 100]
    for w in momentum_windows:
        rolling_mean = data['Close'].rolling(window=w).mean()
        data[f'mom_diff_pct_{w}d'] = ((data['Close'] - rolling_mean) / rolling_mean) * 100

    return data
