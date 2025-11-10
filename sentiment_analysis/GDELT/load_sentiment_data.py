# data/sentiment_loader.py

from pathlib import Path
from typing import Optional
import pandas as pd

SENTIMENT_FILE_MAP = {
    "AAPL": "AAPL_1_sentiment_trading_days.csv",
    "MSFT": "MSFT_1_sentiment_trading_days.csv",
    "NVDA": "NVDA_1_sentiment_trading_days.csv",
    "GOOG": "GOOG_1_sentiment_trading_days.csv",
    "PLTR": "PLTR_1_sentiment_trading_days.csv",
    "CRWD": "CRWD_1_sentiment_trading_days.csv",
    "NET":  "NET_1_sentiment_trading_days.csv",
    "TSLA": "TSLA_1_sentiment_trading_days.csv",
    "AMD":  "AMD_1_sentiment_trading_days.csv",
}

def load_sentiment_data(
    ticker: str,
    base_dir: str,
    start_date=None,
    end_date=None,
) -> Optional[pd.DataFrame]:
    """
    Load sentiment data for the given ticker and clip it to the requested period.
    """
    if not ticker:
        print("⚠️ No ticker supplied to load_sentiment_data.")
        return None

    ticker_key = ticker.upper()
    file_name = SENTIMENT_FILE_MAP.get(ticker_key)
    if not file_name:
        print(f"⚠️ No sentiment mapping found for {ticker_key}. Skipping sentiment strategy.")
        return None

    base_path = Path(base_dir)
    sentiment_path = base_path / file_name
    if not sentiment_path.exists():
        print(f"⚠️ Sentiment data file not found: {sentiment_path}")
        return None

    sentiment_df = pd.read_csv(sentiment_path)
    date_col = "day" if "day" in sentiment_df.columns else "Date" if "Date" in sentiment_df.columns else None

    if date_col:
        sentiment_df[date_col] = pd.to_datetime(sentiment_df[date_col])
        sentiment_df.set_index(date_col, inplace=True)
    else:
        sentiment_df.index = pd.to_datetime(sentiment_df.index)

    sentiment_df = sentiment_df.sort_index()

    if start_date:
        sentiment_df = sentiment_df[sentiment_df.index >= pd.to_datetime(start_date)]
    if end_date:
        sentiment_df = sentiment_df[sentiment_df.index <= pd.to_datetime(end_date)]

    print(
        f"[DEBUG] Loaded sentiment data for {ticker_key}: "
        f"{len(sentiment_df)} rows from {sentiment_df.index.min().date()} to {sentiment_df.index.max().date()}"
    )

    return sentiment_df
