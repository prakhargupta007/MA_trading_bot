# macd_trend_follow_strategy.py

from indicators.macd import calculate_macd

def macd_trend_follow_strategy(data, macd_fast, macd_slow, macd_signal, **kwargs):
    """
    MACD Trend Follow Strategy
    - Buys when MACD crosses above signal line and MACD > 0 (bullish momentum).
    - Sells when MACD crosses below signal line and MACD < 0 (bearish momentum).
    """

    macd_line, signal_line = calculate_macd(
        data,
        fast_period=macd_fast,
        slow_period=macd_slow,
        signal_period=macd_signal
    )

    signals = ['HOLD']
    bought = False

    for _ in range(macd_slow - 1):
        signals.append('HOLD')

    for i in range(macd_slow - 1, len(data)):
        signal = 'HOLD'

        # Cross detection
        cross_up = macd_line.iloc[i - 1] <= signal_line.iloc[i - 1] and macd_line.iloc[i] > signal_line.iloc[i]
        cross_down = macd_line.iloc[i - 1] >= signal_line.iloc[i - 1] and macd_line.iloc[i] < signal_line.iloc[i]

        if not bought:
            if cross_up and macd_line.iloc[i] > 0:
                signal = 'BUY'
                bought = True

        elif bought:
            if cross_down and macd_line.iloc[i] < 0:
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
