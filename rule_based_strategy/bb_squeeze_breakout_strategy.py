# bb_squeeze_breakout_strategy.py

from indicators.bollinger_bands import calculate_bollinger_bands

def bb_squeeze_breakout_strategy(
    data,
    bb_window=20,
    bb_std_dev=2,
    squeeze_threshold=0.05,
    breakout_lookback=5,
    **kwargs
):
    """
    Corrected Bollinger Band Squeeze Breakout Strategy

    Logic:
    1. A "squeeze" occurs when the Bollinger Band width is extremely tight.
       - bandwidth = (upper - lower) / mid
       - squeeze = bandwidth < squeeze_threshold

    2. A breakout is valid ONLY AFTER a squeeze ends.

       BUY conditions:
       - Squeeze was active in the past `breakout_lookback` bars
       - Current close > upper band

       SELL conditions:
       - Squeeze was active in the past `breakout_lookback` bars
       - Current close < lower band

    3. Ensures signal length EXACTLY matches data length.
    """

    bb_upper, bb_lower, bb_mid = calculate_bollinger_bands(data, bb_window, bb_std_dev)

    # Compute volatility compression (squeeze)
    band_width = bb_upper - bb_lower
    bandwidth_ratio = band_width / bb_mid

    squeeze = bandwidth_ratio < squeeze_threshold

    signals = ['HOLD'] * len(data)
    bought = False

    # Debug counters
    squeeze_count = 0
    squeeze_exit_count = 0
    buy_signals = 0
    sell_signals = 0

    for i in range(bb_window, len(data)):

        close = data['Close'].iloc[i]
        upper = bb_upper.iloc[i]
        lower = bb_lower.iloc[i]

        # Check if a squeeze happened recently
        recent_squeeze = squeeze.iloc[max(0, i - breakout_lookback):i].any()

        if squeeze.iloc[i]:
            squeeze_count += 1

        # No squeeze recently → no breakout trading
        if not recent_squeeze:
            continue

        # BUY breakout
        if not bought and close > upper:
            signals[i] = 'BUY'
            bought = True
            buy_signals += 1
            continue

        # SELL breakdown
        if bought and close < lower:
            signals[i] = 'SELL'
            bought = False
            sell_signals += 1

    print(f"[BB SQUEEZE DEBUG] Squeeze candles: {squeeze_count}")
    print(f"[BB SQUEEZE DEBUG] Buy signals: {buy_signals}")
    print(f"[BB SQUEEZE DEBUG] Sell signals: {sell_signals}")

    return signals
