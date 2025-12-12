import pandas as pd
from indicators.sma import calculate_sma
from sentiment_analysis.GDELT.load_sentiment_data import load_sentiment_data


def sentiment_regime_filter_strategy(
    data,
    data_path_for_sentiment_strategy,
    ticker,
    sma_short_period,
    sma_long_period,
    regime_window=3,
    bullish_threshold=0.55,
    start_date=None,
    end_date=None,
    **kwargs,
):
    """
    Sentiment Regime Filter Strategy (Long-Only)
    --------------------------------------------------
    - Defines market regime based on rolling avg of sentiment probabilities.
    - Trades SMA crossover logic only during bullish regimes.
    - Stays in cash (HOLD) otherwise.

    Args:
        data (pd.DataFrame): Price data with a DateTime index (from Yahoo Finance).
        data_path_for_sentiment_strategy (str): Directory path where sentiment CSVs are stored.
        ticker (str): Ticker symbol for sentiment lookup.
        sma_short_period (int): Period for short-term SMA.
        sma_long_period (int): Period for long-term SMA.
        regime_window (int): Rolling window to smooth sentiment probabilities.
        bullish_threshold (float): Minimum positive sentiment mean to trigger bullish regime.
        start_date (str): Optional start date for sentiment alignment.
        end_date (str): Optional end date for sentiment alignment.

    Signals follow the len(data)+1 next-day execution convention: initial HOLD
    plus potential trailing entry; execution happens on the following trading day.
    """

    # --- Load sentiment data ---
    sentiment_df = load_sentiment_data(
        ticker=ticker,
        base_dir=data_path_for_sentiment_strategy,
        start_date=start_date or data.index[0],
        end_date=end_date or data.index[-1],
    )

    if sentiment_df is None or sentiment_df.empty:
        print(f"⚠️ Missing sentiment data for {ticker}. Falling back to HOLD signals.")
        return ['HOLD'] * len(data)

    # --- Align sentiment with trading days ---
    sentiment_aligned = sentiment_df.reindex(data.index, method='ffill')

    # --- Calculate rolling regime ---
    if all(col in sentiment_aligned.columns for col in ['prob_positive', 'prob_negative']):
        pos_prob = sentiment_aligned['prob_positive'].rolling(window=regime_window).mean()
        neg_prob = sentiment_aligned['prob_negative'].rolling(window=regime_window).mean()
    else:
        print(f"⚠️ Sentiment file for {ticker} missing probability columns. Returning HOLDs.")
        return ['HOLD'] * len(data)

    bullish_regime = pos_prob > bullish_threshold
    bearish_regime = neg_prob > bullish_threshold

    # --- Calculate SMAs ---
    sma_short = calculate_sma(data, sma_short_period)
    sma_long = calculate_sma(data, sma_long_period)

    signals = ['HOLD']
    bought = False

    for _ in range(max(sma_long_period, regime_window) - 1):
        signals.append('HOLD')

    # --- Trading logic ---
    for i in range(max(sma_long_period, regime_window) - 1, len(data)):
        signal = 'HOLD'
        in_bullish_regime = bullish_regime.iloc[i] and not bearish_regime.iloc[i]

        if not bought:
            if in_bullish_regime and sma_short.iloc[i] > sma_long.iloc[i]:
                signal = 'BUY'
                bought = True
        elif bought:
            if sma_short.iloc[i] < sma_long.iloc[i]:
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
