# bb_squeeze_breakout_strategy.py

from indicators.bollinger_bands import calculate_bollinger_bands

def bb_squeeze_breakout_strategy(data, bb_window, bb_std_dev, squeeze_threshold=0.02, **kwargs):
    """
    Bollinger Band Squeeze Breakout Strategy
    - Detects low volatility (bandwidth < threshold * mid_band)
    - Buys if price breaks above upper band after a squeeze.
    - Sells if price breaks below lower band after a squeeze.
    """

    bb_upper, bb_lower, bb_mid = calculate_bollinger_bands(data, bb_window, bb_std_dev)
    band_width = bb_upper - bb_lower

    signals = ['HOLD']
    bought = False

    for _ in range(bb_window - 1):
        signals.append('HOLD')

    for i in range(bb_window - 1, len(data)):
        signal = 'HOLD'
        close = data['Close'].iloc[i]
        mid = bb_mid.iloc[i]

        # Detect squeeze: narrow band
        is_squeeze = band_width.iloc[i] / mid < squeeze_threshold

        if not bought:
            if is_squeeze and close > bb_upper.iloc[i]:
                signal = 'BUY'
                bought = True
        elif bought:
            if close < bb_mid.iloc[i]:
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
