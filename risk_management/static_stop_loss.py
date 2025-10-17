def static_stop_loss(data, signals, column_name='Close', threshold=0.03, **kwargs):
    """
    Modifies the buy/sell signals based on a stop-loss threshold.
    threshold: e.g. 0.03 for 3% stop-loss.
    """
    prices = data[column_name].values
    signals = signals.copy()

    holding = False
    buy_price = None

    for i in range(len(signals)):
        if signals[i] == 'BUY' and not holding:
            holding = True
            buy_price = prices[i]
        elif holding:
            # Check for stop-loss condition
            if prices[i] <= buy_price * (1 - threshold):
                signals[i] = 'SELL'
                holding = False
                buy_price = None
            elif signals[i] == 'SELL':
                holding = False
                buy_price = None

    return signals
