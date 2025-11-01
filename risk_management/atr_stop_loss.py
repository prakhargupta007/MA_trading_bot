import talib as ta
import numpy as np

def atr_stop_loss(data, signals, column_name='Close', atr_period=14, atr_mult=2.0, **kwargs):
    """
    Implements a static ATR-based stop-loss.
    Stop-loss = Entry price - ATR * multiplier
    """
    prices = data[column_name].values
    signals = signals.copy()
    atr = ta.ATR(data['High'], data['Low'], data['Close'], timeperiod=atr_period)
    atr = np.nan_to_num(atr)  # replace NaNs with 0

    holding = False
    buy_price = None
    stop_price = None

    n = min(len(signals), len(prices), len(atr))  # <-- key fix

    for i in range(n):
        price = prices[i]

        if signals[i] == 'BUY' and not holding:
            holding = True
            buy_price = price
            stop_price = buy_price - atr_mult * atr[i]

        elif holding:
            # Check for stop-loss trigger
            if price <= stop_price:
                signals[i] = 'SELL'
                holding = False
                buy_price = None
                stop_price = None

            elif signals[i] == 'SELL':
                holding = False
                buy_price = None
                stop_price = None

    return signals
