# vol_adjusted_momentum_strategy.py

from indicators.volatility import calculate_volatility
from indicators.sma import calculate_sma

def vol_adjusted_momentum_strategy(data, sma_short_period, sma_long_period, vol_window=14,
                                   vol_lower=0.01, vol_upper=0.04, **kwargs):
    """
    Volatility-Adjusted Momentum Strategy
    - Buys when short SMA > long SMA (momentum up) and volatility is normal.
    - Sells when short SMA < long SMA (momentum down) and volatility is normal.
    - 'Normal' volatility means vol_lower <= volatility <= vol_upper.
    """

    sma_short = calculate_sma(data, sma_short_period)
    sma_long = calculate_sma(data, sma_long_period)
    volatility = calculate_volatility(data, vol_window)

    signals = ['HOLD']
    bought = False

    for _ in range(max(sma_long_period, vol_window) - 1):
        signals.append('HOLD')

    for i in range(max(sma_long_period, vol_window) - 1, len(data)):
        signal = 'HOLD'

        vol = volatility.iloc[i]
        normal_vol = (vol >= vol_lower) and (vol <= vol_upper)

        if not bought:
            if sma_short.iloc[i] > sma_long.iloc[i] and normal_vol:
                signal = 'BUY'
                bought = True
        elif bought:
            if sma_short.iloc[i] < sma_long.iloc[i] and normal_vol:
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
