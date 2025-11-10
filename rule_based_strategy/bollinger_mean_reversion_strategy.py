# bollinger_mean_reversion_strategy.py

from indicators.bollinger_bands import calculate_bollinger_bands

def bollinger_mean_reversion_strategy(data, bb_window, bb_std_dev, **kwargs):
    """
    Bollinger Mean Reversion Strategy
    - Buy when price < lower Bollinger Band.
    - Sell when price > upper Bollinger Band.
    - Hold otherwise.
    """

    bb_upper, bb_lower, bb_mid = calculate_bollinger_bands(data, bb_window, bb_std_dev)

    signals = ['HOLD']
    bought = False

    for _ in range(bb_window - 1):
        signals.append('HOLD')

    for i in range(bb_window - 1, len(data)):
        signal = 'HOLD'

        close = data['Close'].iloc[i]

        if not bought:
            if close < bb_lower.iloc[i]:
                signal = 'BUY'
                bought = True
        elif bought:
            if close > bb_upper.iloc[i]:
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
