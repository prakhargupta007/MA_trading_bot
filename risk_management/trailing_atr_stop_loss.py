'''
import talib as ta
import numpy as np

def trailing_atr_stop_loss(data, signals, column_name='Close', atr_period=14, atr_mult=2.0,**kwargs):
    """
    Implements a trailing ATR-based stop-loss.
    Stop-loss = max_price_since_entry - ATR * multiplier
    """
    prices = data[column_name].values
    signals = signals.copy()
    atr = ta.ATR(data['High'], data['Low'], data['Close'], timeperiod=atr_period)
    atr = np.nan_to_num(atr)

    holding = False
    max_price = None
    stop_price = None

    for i in range(len(signals)):
        price = prices[i]

        if signals[i] == 'BUY' and not holding:
            holding = True
            max_price = price
            stop_price = price - atr_mult * atr[i]

        elif holding:
            max_price = max(max_price, price)
            stop_price = max_price - atr_mult * atr[i]

            # Check for stop-loss trigger
            if price <= stop_price:
                signals[i] = 'SELL'
                holding = False
                max_price = None
                stop_price = None

            elif signals[i] == 'SELL':
                holding = False
                max_price = None
                stop_price = None

    return signals
'''


import talib as ta
import numpy as np

def trailing_atr_stop_loss(data, signals, column_name='Close', atr_period=14, atr_mult=2.0, **kwargs):
    """
    Implements a trailing ATR-based stop-loss.
    Stop-loss = max_price_since_entry - ATR * multiplier
    """
    prices = data[column_name].values
    signals = signals.copy()
    atr = ta.ATR(data['High'], data['Low'], data['Close'], timeperiod=atr_period)
    atr = np.nan_to_num(atr)

    holding = False
    max_price = None
    stop_price = None

    # ensure all arrays have the same usable length
    n = min(len(signals), len(prices), len(atr))

    for i in range(n):
        price = prices[i]

        if signals[i] == 'BUY' and not holding:
            holding = True
            max_price = price
            stop_price = price - atr_mult * atr[i]

        elif holding:
            max_price = max(max_price, price)
            stop_price = max_price - atr_mult * atr[i]

            # Check for stop-loss trigger
            if price <= stop_price:
                signals[i] = 'SELL'
                holding = False
                max_price = None
                stop_price = None

            elif signals[i] == 'SELL':
                holding = False
                max_price = None
                stop_price = None

    return signals
