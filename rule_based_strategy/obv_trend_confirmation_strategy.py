# obv_trend_confirmation_strategy.py

from indicators.obv import calculate_obv
from indicators.sma import calculate_sma

def obv_trend_confirmation_strategy(data, sma_period, **kwargs):
    """
    OBV Trend Confirmation Strategy
    - Buys when price > SMA and OBV is rising (volume confirms uptrend).
    - Sells when price < SMA and OBV is falling (volume confirms downtrend).
    """

    sma = calculate_sma(data, sma_period)
    obv = calculate_obv(data)

    signals = ['HOLD']
    bought = False

    for _ in range(sma_period - 1):
        signals.append('HOLD')

    for i in range(sma_period - 1, len(data)):
        signal = 'HOLD'

        price_up = data['Close'].iloc[i] > sma.iloc[i]
        obv_up = obv.iloc[i] > obv.iloc[i - 1]
        price_down = data['Close'].iloc[i] < sma.iloc[i]
        obv_down = obv.iloc[i] < obv.iloc[i - 1]

        if not bought:
            if price_up and obv_up:
                signal = 'BUY'
                bought = True
        elif bought:
            if price_down and obv_down:
                signal = 'SELL'
                bought = False

        signals.append(signal)

    return signals
