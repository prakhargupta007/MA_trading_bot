# rsi_trend_filter_strategy.py

from indicators.sma import calculate_sma
from indicators.rsi import calculate_rsi

def rsi_trend_filter_strategy(data, sma_long_period, rsi_period, rsi_overbought, rsi_oversold, **kwargs):
    """
    RSI Trend Filter Strategy
    - Trades RSI signals only when aligned with the long-term trend (SMA200).
    - Long-term uptrend: Close > SMA200 -> buy when RSI < rsi_oversold.
    - Long-term downtrend: Close < SMA200 -> sell when RSI > rsi_overbought.

    Signals follow the len(data)+1 next-day execution convention: initial HOLD
    plus potential trailing entry; execution happens on the following trading day.
    """

    sma_long = calculate_sma(data, sma_long_period)
    rsi = calculate_rsi(data, rsi_period)

    signals = ['HOLD']
    bought = False

    # Initialize with HOLD until indicators are ready
    for _ in range(max(sma_long_period, rsi_period) - 1):
        signals.append('HOLD')

    for i in range(max(sma_long_period, rsi_period) - 1, len(data)):
        signal = 'HOLD'

        # Define market regime
        uptrend = data['Close'].iloc[i] > sma_long.iloc[i]

        if not bought:
            if uptrend and rsi.iloc[i] < rsi_oversold:
                signal = 'BUY'
                bought = True

        elif bought:
            # Sell when overbought and trend reverses
            if (not uptrend) or (rsi.iloc[i] > rsi_overbought):
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
