# ma_distance_reversion_strategy.py
import pandas as pd

from indicators.sma import calculate_sma

def ma_distance_reversion_strategy(data, ma_period, upper_threshold=0.03, lower_threshold=-0.03, **kwargs):
    """
    MA Distance Reversion Strategy
    - Buys when price deviates too far below MA.
    - Sells when price deviates too far above MA.
    - Thresholds are in % (e.g., 0.03 = 3%).
    """

    ma = calculate_sma(data, ma_period)
    signals = ['HOLD']
    bought = False

    for _ in range(ma_period - 1):
        signals.append('HOLD')

    for i in range(ma_period - 1, len(data)):
        signal = 'HOLD'
        close = data['Close'].iloc[i]
        ma_value = ma.iloc[i]

        if pd.isna(ma_value) or ma_value == 0:
            signals.append('HOLD')
            continue

        deviation = (close - ma_value) / ma_value  # percentage deviation

        if not bought:
            if deviation < lower_threshold:  # price too low below MA
                signal = 'BUY'
                bought = True
        elif bought:
            if deviation > upper_threshold:  # price too high above MA
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
