DATA_FOR_DATA_ANALYSIS = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_AAPL_train_test_2017-01-02--2025-08-16.csv'

ALL_FEATURES = [
    # --- Price-based features ---
    'rsi_14',
    'macd',
    'macd_signal',
    'sma_50',
    'sma_200',
    'bb_upper',
    'bb_lower',
    'bb_percent',
    'daily_return',
    'volatility_14',
    'momentum_10',
    'volume_20d_ma',
    'obv',

    # --- Market indices ---
    'gspc_daily_return',
    'gspc_20d_volatility',
    'sentiment_score',

    # --- Tech-sector features (conditional) ---
    # Only present if TECH_SECTOR_STOCK == True
    'ndx_daily_return',
    'ndx_20d_volatility',
    'ndx_20d_sma',

    # --- Momentum differences (Close vs rolling mean) ---
    'mom_diff_pct_5d',
    'mom_diff_pct_10d',
    'mom_diff_pct_20d',
    'mom_diff_pct_50d',
    'mom_diff_pct_100d',
    'mom_diff_pct_200d',

    # --- EMA-based percentage differences ---
    'ema_diff_pct_10d',
    'ema_diff_pct_50d',
    'ema_diff_pct_200d',

    # --- VIX features ---
    'vix_roc1',
    'vix_mean20',
    'vix_std20'
]

DA_GSPC_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^GSPC_(SP500)_2017-01-02--2025-08-16.csv'
DA_NDX_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^NDX_(QQQ)_2017-01-02--2025-08-16.csv'
DA_VIX_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^VIX_2017-01-02--2025-08-16.csv'