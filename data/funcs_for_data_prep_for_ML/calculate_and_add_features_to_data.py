'''
#FUNC TO FIX DATA_ANALYSIS PROBLEM 
import os
import pandas as pd
import numpy as np
import ta

from config import TECH_SECTOR_STOCK
from config import SENTIMENT_DATA_PATH_FOR_ML_MODEL_TRAINING_FEATURE
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
    print(f"[DEBUG] Loaded {os.path.basename(gspc_data_file_path)} (len={len(gspc_data)})")
    gspc_data.index = pd.to_datetime(gspc_data.index, errors='coerce')
    gspc_returns = gspc_data['Close'].pct_change()
    gspc_volatility = gspc_returns.rolling(window=20).std()
    data['gspc_daily_return'] = gspc_returns.reindex(data.index)
    data['gspc_20d_volatility'] = gspc_volatility.reindex(data.index)

    # --- Sentiment ---
    data['sentiment_score'] = generate_sentiment_score_feature_list(data.index,SENTIMENT_DATA_PATH_FOR_ML_MODEL_TRAINING_FEATURE )
    # Fill any NaNs in sentiment_score with last available value or 0 if none
    data['sentiment_score'] = data['sentiment_score'].ffill().fillna(0)


    # --- Optional Nasdaq features ---
    if TECH_SECTOR_STOCK:
        ndx_data = pd.read_csv(ndx_data_file_path, parse_dates=['Date'], index_col='Date')
        print(f"[DEBUG] Loaded {os.path.basename(ndx_data_file_path)} (len={len(ndx_data)})")
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
    vix = pd.read_csv(vix_data_file_path)
    vix['Date'] = pd.to_datetime(vix['Date'], errors='coerce')
    vix = vix.sort_values('Date')
    vix = vix[['Date', 'Close']].rename(columns={'Close': 'VIX_Close'})

    vix_idx = vix.set_index('Date')
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)
    if vix_idx.index.tz is not None:
        vix_idx.index = vix_idx.index.tz_localize(None)
    vix_idx = vix_idx.reindex(data.index)
    vix_close = vix_idx['VIX_Close']

    data['vix_roc1'] = vix_close.pct_change(periods=1)
    data['vix_mean20'] = vix_close.rolling(window=20, min_periods=1).mean()
    data['vix_std20'] = vix_close.rolling(window=20, min_periods=1).std()

    valid_ratio = vix_close.notna().mean()
    print(f"✅ VIX merge check: overlap {vix_close.notna().sum()} valid out of {len(vix_close)} rows ({valid_ratio:.2%} valid).")

    nan_ratio = data.isna().mean()
    dead_features = nan_ratio[nan_ratio == 1.0].index.tolist()
    if dead_features:
        print(f"[WARN] Dropping dead feature columns (all NaN): {dead_features}")
        data = data.drop(columns=dead_features)

    if data.isna().all().any():
        print("[ERROR] One or more feature columns are entirely NaN. Check your alignment or data sources.")
        print(data.isna().mean())
        raise ValueError("Feature columns invalid (all NaN).")

    return data
'''















import os
import pandas as pd
import numpy as np
import ta

from config import TECH_SECTOR_STOCK, FEATURE_COLUMNS, SENTIMENT_DATA_PATH_FOR_ML_MODEL_TRAINING_FEATURE
from data.funcs_for_data_prep_for_ML.generate_sentiment_score_feature_list import generate_sentiment_score_feature_list

def calculate_and_add_features_to_data(data, gspc_data_file_path, ndx_data_file_path, vix_data_file_path): 
    data = data.copy()  # avoid changing original data

    # --- Ensure 'Date' column exists correctly ---
    if 'Date' not in data.columns:
        if 'date' in data.columns:
            data.rename(columns={'date': 'Date'}, inplace=True)
        elif data.index.name in ['Date', 'date']:
            data.reset_index(inplace=True)

    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data = data.set_index('Date')

    # --- Price-based features ---
    if any(f in FEATURE_COLUMNS for f in ['rsi_14']):
        rsi = ta.momentum.RSIIndicator(close=data['Close'], window=14)
        data['rsi_14'] = rsi.rsi()

    if any(f in FEATURE_COLUMNS for f in ['macd', 'macd_signal']):
        macd = ta.trend.MACD(close=data['Close'])
        if 'macd' in FEATURE_COLUMNS:
            data['macd'] = macd.macd()
        if 'macd_signal' in FEATURE_COLUMNS:
            data['macd_signal'] = macd.macd_signal()

    if 'sma_50' in FEATURE_COLUMNS:
        data['sma_50'] = ta.trend.SMAIndicator(close=data['Close'], window=50).sma_indicator()
    if 'sma_200' in FEATURE_COLUMNS:
        data['sma_200'] = ta.trend.SMAIndicator(close=data['Close'], window=200).sma_indicator()

    # --- SMA differences (percentage) ---
    if 'sma_diff_pct_50d' in FEATURE_COLUMNS:
        data['sma_50'] = ta.trend.SMAIndicator(close=data['Close'], window=50).sma_indicator()
        data["sma_diff_pct_50d"] = ((data["Close"] - data["sma_50"]) / data["sma_50"]) * 100
    if 'sma_diff_pct_200d' in FEATURE_COLUMNS:
        data['sma_200'] = ta.trend.SMAIndicator(close=data['Close'], window=200).sma_indicator()
        data["sma_diff_pct_200d"] = ((data["Close"] - data["sma_200"]) / data["sma_200"]) * 100
    if 'sma_diff_pct_10d' in FEATURE_COLUMNS:
        data['sma_10'] = ta.trend.SMAIndicator(close=data['Close'], window=10).sma_indicator()
        data["sma_diff_pct_10d"] = ((data["Close"] - data["sma_10"]) / data["sma_10"]) * 100



    if any(f in FEATURE_COLUMNS for f in ['bb_upper', 'bb_lower', 'bb_percent']):
        bb = ta.volatility.BollingerBands(close=data['Close'], window=20, window_dev=2)
        if 'bb_upper' in FEATURE_COLUMNS:
            data['bb_upper'] = bb.bollinger_hband()
        if 'bb_lower' in FEATURE_COLUMNS:
            data['bb_lower'] = bb.bollinger_lband()
        if 'bb_percent' in FEATURE_COLUMNS:
            data['bb_percent'] = bb.bollinger_pband()

    if 'daily_return' in FEATURE_COLUMNS:
        data['daily_return'] = data['Close'].pct_change()
    if 'volatility_14' in FEATURE_COLUMNS:
        data['volatility_14'] = data['Close'].pct_change().rolling(window=14).std()
    if 'momentum_10' in FEATURE_COLUMNS:
        data['momentum_10'] = data['Close'] - data['Close'].shift(10)
    if 'volume_20d_ma' in FEATURE_COLUMNS:
        data['volume_20d_ma'] = data['Volume'].rolling(window=20).mean()
    if 'obv' in FEATURE_COLUMNS:
        data['obv'] = ta.volume.OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume']).on_balance_volume()

    # --- Market indices ---
    if any(f.startswith('gspc') for f in FEATURE_COLUMNS):
        gspc_data = pd.read_csv(gspc_data_file_path, parse_dates=['Date'], index_col='Date')
        print(f"[DEBUG] Loaded {os.path.basename(gspc_data_file_path)} (len={len(gspc_data)})")
        gspc_data.index = pd.to_datetime(gspc_data.index, errors='coerce')
        gspc_returns = gspc_data['Close'].pct_change()
        gspc_volatility = gspc_returns.rolling(window=20).std()
        if 'gspc_daily_return' in FEATURE_COLUMNS:
            data['gspc_daily_return'] = gspc_returns.reindex(data.index)
        if 'gspc_20d_volatility' in FEATURE_COLUMNS:
            data['gspc_20d_volatility'] = gspc_volatility.reindex(data.index)

    # --- Sentiment ---
    if 'sentiment_score' in FEATURE_COLUMNS:
        data['sentiment_score'] = generate_sentiment_score_feature_list(
            data.index, SENTIMENT_DATA_PATH_FOR_ML_MODEL_TRAINING_FEATURE
        ).ffill().fillna(0)

    # --- Optional Nasdaq features ---
    if TECH_SECTOR_STOCK and any(f.startswith('ndx') for f in FEATURE_COLUMNS):
        ndx_data = pd.read_csv(ndx_data_file_path, parse_dates=['Date'], index_col='Date')
        print(f"[DEBUG] Loaded {os.path.basename(ndx_data_file_path)} (len={len(ndx_data)})")
        ndx_data.index = pd.to_datetime(ndx_data.index, errors='coerce')
        ndx_returns = ndx_data['Close'].pct_change()
        ndx_volatility = ndx_returns.rolling(window=20).std()
        ndx_sma = ndx_data['Close'].rolling(window=20).mean()
        if 'ndx_daily_return' in FEATURE_COLUMNS:
            data['ndx_daily_return'] = ndx_returns.reindex(data.index)
        if 'ndx_20d_volatility' in FEATURE_COLUMNS:
            data['ndx_20d_volatility'] = ndx_volatility.reindex(data.index)
        if 'ndx_20d_sma' in FEATURE_COLUMNS:
            data['ndx_20d_sma'] = ndx_sma.reindex(data.index)

    # --- Momentum differences ---
    momentum_windows = [5, 10, 20, 50, 100, 200]
    for w in momentum_windows:
        col_name = f'mom_diff_pct_{w}d'
        if col_name in FEATURE_COLUMNS:
            rolling_mean = data['Close'].rolling(window=w).mean()
            data[col_name] = ((data['Close'] - rolling_mean) / rolling_mean) * 100

    # --- EMAs ---
    ema_windows = [10, 50, 200]
    for w in ema_windows:
        col_name = f'ema_diff_pct_{w}d'
        if col_name in FEATURE_COLUMNS:
            ema = ta.trend.EMAIndicator(close=data['Close'], window=w).ema_indicator()
            data[col_name] = ((data['Close'] - ema) / ema) * 100

    # --- VIX features ---
    if any(f.startswith('vix') for f in FEATURE_COLUMNS):
        vix = pd.read_csv(vix_data_file_path)
        vix['Date'] = pd.to_datetime(vix['Date'], errors='coerce')
        vix = vix.sort_values('Date')
        vix = vix[['Date', 'Close']].rename(columns={'Close': 'VIX_Close'})

        vix_idx = vix.set_index('Date')
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        if vix_idx.index.tz is not None:
            vix_idx.index = vix_idx.index.tz_localize(None)
        vix_idx = vix_idx.reindex(data.index)
        vix_close = vix_idx['VIX_Close']

        if 'vix_roc1' in FEATURE_COLUMNS:
            data['vix_roc1'] = vix_close.pct_change(periods=1)
        if 'vix_mean20' in FEATURE_COLUMNS:
            data['vix_mean20'] = vix_close.rolling(window=20, min_periods=1).mean()
        if 'vix_std20' in FEATURE_COLUMNS:
            data['vix_std20'] = vix_close.rolling(window=20, min_periods=1).std()

        valid_ratio = vix_close.notna().mean()
        print(f"✅ VIX merge check: overlap {vix_close.notna().sum()} valid out of {len(vix_close)} rows ({valid_ratio:.2%} valid).")

    nan_ratio = data.isna().mean()
    dead_features = nan_ratio[nan_ratio == 1.0].index.tolist()
    if dead_features:
        print(f"[WARN] Dropping dead feature columns (all NaN): {dead_features}")
        data = data.drop(columns=dead_features)

    if data.isna().all().any():
        print("[ERROR] One or more feature columns are entirely NaN. Check your alignment or data sources.")
        print(data.isna().mean())
        raise ValueError("Feature columns invalid (all NaN).")

    return data
