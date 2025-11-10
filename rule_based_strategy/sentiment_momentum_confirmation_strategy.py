import pandas as pd
from indicators.rsi import calculate_rsi
from sentiment_analysis.GDELT.load_sentiment_data import load_sentiment_data


def sentiment_momentum_confirmation_strategy(
    data,
    data_path_for_sentiment_strategy,
    ticker,
    rsi_period,
    rsi_overbought,
    rsi_oversold,
    start_date=None,
    end_date=None,
    **kwargs,
):
    """
    Sentiment-Momentum Confirmation Strategy (Long-Only)
    ----------------------------------------------------
    - Buys when RSI < rsi_oversold AND positive sentiment > negative sentiment.
    - Sells when RSI > rsi_overbought AND negative sentiment > positive sentiment.
    - Otherwise holds.

    Args:
        data (pd.DataFrame): Price data with DateTime index.
        data_path_for_sentiment_strategy (str): Directory path for sentiment CSVs.
        ticker (str): Stock ticker symbol.
        rsi_period (int): RSI period (e.g., 14).
        rsi_overbought (float): RSI level above which to consider sell.
        rsi_oversold (float): RSI level below which to consider buy.
        start_date, end_date (str): Optional clipping range for sentiment data.
    """

    # --- Load sentiment data ---
    sentiment_df = load_sentiment_data(
        ticker=ticker,
        base_dir=data_path_for_sentiment_strategy,
        start_date=start_date or data.index[0],
        end_date=end_date or data.index[-1],
    )

    if sentiment_df is None or sentiment_df.empty:
        print(f"⚠️ Missing sentiment data for {ticker}. Returning HOLD signals.")
        return ['HOLD'] * len(data)

    # --- Align sentiment with trading days ---
    sentiment_aligned = sentiment_df.reindex(data.index, method='ffill')

    if not all(col in sentiment_aligned.columns for col in ['prob_positive', 'prob_negative']):
        print(f"⚠️ Sentiment data missing probability columns for {ticker}. Returning HOLDs.")
        return ['HOLD'] * len(data)

    # --- Compute RSI ---
    rsi = calculate_rsi(data, rsi_period)

    signals = ['HOLD']
    bought = False

    # Fill initial period with HOLD
    for _ in range(rsi_period - 1):
        signals.append('HOLD')

    # --- Core logic ---
    for i in range(rsi_period - 1, len(data)):
        signal = 'HOLD'
        pos_prob = sentiment_aligned['prob_positive'].iloc[i]
        neg_prob = sentiment_aligned['prob_negative'].iloc[i]

        # --- BUY ---
        if not bought:
            if (rsi.iloc[i] < rsi_oversold) and (pos_prob > neg_prob):
                signal = 'BUY'
                bought = True

        # --- SELL ---
        elif bought:
            if (rsi.iloc[i] > rsi_overbought) and (neg_prob > pos_prob):
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
