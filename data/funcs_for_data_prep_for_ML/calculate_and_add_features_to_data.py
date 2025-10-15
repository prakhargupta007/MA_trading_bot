'''
FUNC BEFORE DATA_ANALYSIS PROBLEM 

import pandas as pd
import numpy as np
import ta

from config import TECH_SECTOR_STOCK
from data.funcs_for_data_prep_for_ML.generate_sentiment_score_feature_list import generate_sentiment_score_feature_list

def calculate_and_add_features_to_data(data,gspc_data_file_path,ndx_data_file_path,vix_data_file_path): 
    data = data.copy()  # avoid changing original data
    # --- Price-based features ---
    rsi = ta.momentum.RSIIndicator(close=data['Close'], window=14)
    data['rsi_14'] = rsi.rsi()

    macd = ta.trend.MACD(close=data['Close'])
    data['macd'] = macd.macd()
    data['macd_signal'] = macd.macd_signal()

    sma_50 = ta.trend.SMAIndicator(close=data['Close'], window=50)
    sma_200 = ta.trend.SMAIndicator(close=data['Close'], window=200)
    data['sma_50'] = sma_50.sma_indicator()
    data['sma_200'] = sma_200.sma_indicator()

    bb = ta.volatility.BollingerBands(close=data['Close'], window=20, window_dev=2)
    data['bb_upper'] = bb.bollinger_hband()
    data['bb_lower'] = bb.bollinger_lband()
    data['bb_percent'] = bb.bollinger_pband()

    data['daily_return'] = data['Close'].pct_change()
    data['volatility_14'] = data['daily_return'].rolling(window=14).std()
    data['momentum_10'] = data['Close'] - data['Close'].shift(10)
    data['volume_20d_ma'] = data['Volume'].rolling(window=20).mean()

    obv = ta.volume.OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume'])
    data['obv'] = obv.on_balance_volume()

    # --- Market indices ---
    gspc_data = pd.read_csv(gspc_data_file_path, parse_dates=['Date'], index_col='Date')

    gspc_returns = gspc_data['Close'].pct_change()
    gspc_volatility = gspc_returns.rolling(window=20).std()
    data['gspc_daily_return'] = gspc_returns.reindex(data.index)
    data['gspc_20d_volatility'] = gspc_volatility.reindex(data.index)

    data['sentiment_score'] = generate_sentiment_score_feature_list(data.index)

    if TECH_SECTOR_STOCK:
        ndx_data = pd.read_csv(ndx_data_file_path, parse_dates=['Date'], index_col='Date')

        ndx_returns = ndx_data['Close'].pct_change()
        ndx_volatility = ndx_returns.rolling(window=20).std()
        ndx_sma = ndx_data['Close'].rolling(window=20).mean()
        data['ndx_daily_return'] = ndx_returns.reindex(data.index)
        data['ndx_20d_volatility'] = ndx_volatility.reindex(data.index)
        data['ndx_20d_sma'] = ndx_sma.reindex(data.index)

    # --- Momentum differences ---
    momentum_windows = [5, 10, 20, 50, 100, 200]
    for w in momentum_windows:
        rolling_mean = data['Close'].rolling(window=w).mean()
        data[f'mom_diff_pct_{w}d'] = ((data['Close'] - rolling_mean) / rolling_mean) * 100

    # --- EMAs ---
    from ta.trend import EMAIndicator
    ema_windows = [10, 50, 200]
    for w in ema_windows:
        ema = EMAIndicator(close=data['Close'], window=w).ema_indicator()
        data[f'ema_diff_pct_{w}d'] = ((data['Close'] - ema) / ema) * 100

    # --- vix features ---
    vix_data = pd.read_csv(vix_data_file_path, parse_dates=['Date'], index_col='Date')

    vix_close = vix_data['Close'].rename('vix').reindex(data.index)

    data['vix_roc1'] = vix_close.pct_change(periods=1)
    data['vix_mean20'] = vix_close.rolling(window=20).mean()
    data['vix_std20'] = vix_close.rolling(window=20).std()

    return data
'''




#FUNC TO FIX DATA_ANALYSIS PROBLEM 
import pandas as pd
import numpy as np
import ta

from config import TECH_SECTOR_STOCK
from data.funcs_for_data_prep_for_ML.generate_sentiment_score_feature_list import generate_sentiment_score_feature_list

def calculate_and_add_features_to_data(data, gspc_data_file_path, ndx_data_file_path, vix_data_file_path): 
    data = data.copy()  # avoid changing original data

    # --- Convert Date column to datetime ---

    # --- Ensure 'Date' column exists correctly ---
    if 'Date' not in data.columns:
        if 'date' in data.columns:
            data.rename(columns={'date': 'Date'}, inplace=True)
        elif data.index.name == 'Date':
            data.reset_index(inplace=True)
        elif data.index.name == 'date':
            data.reset_index(inplace=True)


    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data = data.set_index('Date')  # optional, aligns with index of market data

    # --- Price-based features ---
    rsi = ta.momentum.RSIIndicator(close=data['Close'], window=14)
    data['rsi_14'] = rsi.rsi()

    macd = ta.trend.MACD(close=data['Close'])
    data['macd'] = macd.macd()
    data['macd_signal'] = macd.macd_signal()

    sma_50 = ta.trend.SMAIndicator(close=data['Close'], window=50)
    sma_200 = ta.trend.SMAIndicator(close=data['Close'], window=200)
    data['sma_50'] = sma_50.sma_indicator()
    data['sma_200'] = sma_200.sma_indicator()

    bb = ta.volatility.BollingerBands(close=data['Close'], window=20, window_dev=2)
    data['bb_upper'] = bb.bollinger_hband()
    data['bb_lower'] = bb.bollinger_lband()
    data['bb_percent'] = bb.bollinger_pband()

    data['daily_return'] = data['Close'].pct_change()
    data['volatility_14'] = data['daily_return'].rolling(window=14).std()
    data['momentum_10'] = data['Close'] - data['Close'].shift(10)
    data['volume_20d_ma'] = data['Volume'].rolling(window=20).mean()

    obv = ta.volume.OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume'])
    data['obv'] = obv.on_balance_volume()

    # --- Market indices ---
    gspc_data = pd.read_csv(gspc_data_file_path, parse_dates=['Date'], index_col='Date')
    gspc_data.index = pd.to_datetime(gspc_data.index, errors='coerce')
    gspc_returns = gspc_data['Close'].pct_change()
    gspc_volatility = gspc_returns.rolling(window=20).std()
    data['gspc_daily_return'] = gspc_returns.reindex(data.index)
    data['gspc_20d_volatility'] = gspc_volatility.reindex(data.index)

    # --- Sentiment ---
    data['sentiment_score'] = generate_sentiment_score_feature_list(data.index)
    # Fill any NaNs in sentiment_score with last available value or 0 if none
    data['sentiment_score'] = data['sentiment_score'].ffill().fillna(0)


    # --- Optional Nasdaq features ---
    if TECH_SECTOR_STOCK:
        ndx_data = pd.read_csv(ndx_data_file_path, parse_dates=['Date'], index_col='Date')
        ndx_data.index = pd.to_datetime(ndx_data.index, errors='coerce')
        ndx_returns = ndx_data['Close'].pct_change()
        ndx_volatility = ndx_returns.rolling(window=20).std()
        ndx_sma = ndx_data['Close'].rolling(window=20).mean()
        data['ndx_daily_return'] = ndx_returns.reindex(data.index)
        data['ndx_20d_volatility'] = ndx_volatility.reindex(data.index)
        data['ndx_20d_sma'] = ndx_sma.reindex(data.index)

    # --- Momentum differences ---
    momentum_windows = [5, 10, 20, 50, 100, 200]
    for w in momentum_windows:
        rolling_mean = data['Close'].rolling(window=w).mean()
        data[f'mom_diff_pct_{w}d'] = ((data['Close'] - rolling_mean) / rolling_mean) * 100

    # --- EMAs ---
    from ta.trend import EMAIndicator
    ema_windows = [10, 50, 200]
    for w in ema_windows:
        ema = EMAIndicator(close=data['Close'], window=w).ema_indicator()
        data[f'ema_diff_pct_{w}d'] = ((data['Close'] - ema) / ema) * 100

    # --- VIX features ---
    vix_data = pd.read_csv(vix_data_file_path, parse_dates=['Date'], index_col='Date')
    vix_data.index = pd.to_datetime(vix_data.index, errors='coerce')
    vix_close = vix_data['Close'].rename('vix').reindex(data.index)
    data['vix_roc1'] = vix_close.pct_change(periods=1)
    data['vix_mean20'] = vix_close.rolling(window=20).mean()
    data['vix_std20'] = vix_close.rolling(window=20).std()

    return data
