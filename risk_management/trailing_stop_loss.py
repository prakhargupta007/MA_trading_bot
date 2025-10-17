def trailing_stop_loss(data, signals, column_name='Close', threshold=0.03,**kwargs):
    """
    Implements a trailing percentage stop-loss.
    Stop-loss moves upward as price increases, locking in gains.
    threshold: e.g. 0.03 for 3% trailing distance.
    """
    prices = data[column_name].values
    signals = signals.copy()

    holding = False
    buy_price = None
    stop_price = None
    max_price = None

    for i in range(len(signals)):
        price = prices[i]

        if signals[i] == 'BUY' and not holding:
            holding = True
            buy_price = price
            max_price = price
            stop_price = buy_price * (1 - threshold)

        elif holding:
            max_price = max(max_price, price)
            stop_price = max(stop_price, max_price * (1 - threshold))  # trail up

            # Trigger stop-loss if price drops below trailing level
            if price <= stop_price:
                signals[i] = 'SELL'
                holding = False
                buy_price = None
                stop_price = None
                max_price = None

            elif signals[i] == 'SELL':
                holding = False
                buy_price = None
                stop_price = None
                max_price = None

    return signals
