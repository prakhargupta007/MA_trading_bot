from pathlib import Path
from typing import Optional

import pandas as pd

SENTIMENT_FILE_MAP = {
    "AAPL": "AAPL_2_sentiment_trading_days.csv",
    "MSFT": "MSFT_2_sentiment_trading_days.csv",
    "NVDA": "NVDA_2_sentiment_trading_days.csv",
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
    date_col = None
    if "day" in sentiment_df.columns:
        date_col = "day"
    elif "Date" in sentiment_df.columns:
        date_col = "Date"

    if date_col is None:
        sentiment_df.index = pd.to_datetime(sentiment_df.index)
    else:
        sentiment_df[date_col] = pd.to_datetime(sentiment_df[date_col])
        sentiment_df.set_index(date_col, inplace=True)

    sentiment_df = sentiment_df.sort_index()

    if start_date is not None:
        start_ts = pd.to_datetime(start_date)
        sentiment_df = sentiment_df[sentiment_df.index >= start_ts]
    if end_date is not None:
        end_ts = pd.to_datetime(end_date)
        sentiment_df = sentiment_df[sentiment_df.index <= end_ts]

    print(
        f"[DEBUG] Loaded sentiment data for {ticker_key}: "
        f"{len(sentiment_df)} rows from {sentiment_df.index.min().date()} to {sentiment_df.index.max().date()}"
    )
    return sentiment_df

def sentiment_strategy(
    data,
    data_path_for_sentiment_strategy,
    sentiment_col='sentiment',
    ticker=None,
    start_date=None,
    end_date=None,
    **kwargs,
):
    """
    Rule-based sentiment strategy aligned to trading (price) days.

    Args:
        data (pd.DataFrame): The price data (from Yahoo Finance) with a DateTime index.
        data_path_for_sentiment_strategy (str): Path to the sentiment CSV file.
        sentiment_col (str): Column name for sentiment values (e.g. 'positive', 'neutral', 'negative').

    Returns:
        list[str]: List of trading signals ('BUY', 'SELL', 'HOLD') for each trading day.
    """

    # --- Load sentiment data ---
    sentiment_df = load_sentiment_data(
        ticker=ticker,
        base_dir=data_path_for_sentiment_strategy,
        start_date=start_date or data.index[0],
        end_date=end_date or data.index[-1],
    )

    if sentiment_df is None or sentiment_df.empty:
        print("⚠️ Falling back to HOLD signals due to missing sentiment data.")
        return ['HOLD'] * len(data)

    # --- Align to price data index (trading days only) ---
    sentiment_aligned = sentiment_df.reindex(data.index, method='ffill')

    # --- Sanity check ---
    print(f"✅ Sentiment data aligned to price data ({len(sentiment_aligned)} rows)")
    print(f"Price start: {data.index[0]}, end: {data.index[-1]}")
    print(f"Sentiment start: {sentiment_aligned.index[0]}, end: {sentiment_aligned.index[-1]}\n")

    # --- Generate signals ---
    signals = []
    in_position = False

    for i in range(len(sentiment_aligned)):
        signal = 'HOLD'
        current_sentiment = sentiment_aligned[sentiment_col].iloc[i]

        if not in_position:
            if current_sentiment == 'positive':
                signal = 'BUY'
                in_position = True
        else:
            if current_sentiment == 'negative':
                signal = 'SELL'
                in_position = False
            # else: HOLD

        signals.append(signal)

    return signals
