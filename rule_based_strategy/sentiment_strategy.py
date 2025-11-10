from pathlib import Path
from typing import Optional

import pandas as pd

from sentiment_analysis.GDELT.load_sentiment_data import load_sentiment_data

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
