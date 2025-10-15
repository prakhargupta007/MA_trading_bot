import pandas as pd

def sentiment_strategy(data, data_path_for_sentiment_strategy, sentiment_col='sentiment', **kwargs):
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
    og_data = pd.read_csv(data_path_for_sentiment_strategy)

    # --- Ensure datetime index ---
    if 'Date' in og_data.columns:
        og_data['Date'] = pd.to_datetime(og_data['Date'])
        og_data.set_index('Date', inplace=True)
    elif 'day' in og_data.columns:
        og_data['day'] = pd.to_datetime(og_data['day'])
        og_data.set_index('day', inplace=True)
    else:
        og_data.index = pd.to_datetime(og_data.index)

    og_data = og_data.sort_index()

    # --- Align to price data index (trading days only) ---
    sentiment_aligned = og_data.reindex(data.index, method='ffill')

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
