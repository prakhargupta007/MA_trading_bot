def buy_and_hold_strategy(data, **kwargs):
    """
    Buy on the first day, hold throughout the entire backtesting period,
    and sell on the very last day.
    """

    signals = []# There in no default HOLD at start as we may buy on first day cuz we dont need any indiactor to tell us that.
    bought = False

    for i in range(len(data)):
        signal = 'HOLD'  # default action

        # Buy on the first day
        if i == 0 and not bought:
            signal = 'BUY'
            bought = True

        # Sell on the LAST day
        elif i == len(data) - 1 and bought:
            signal = 'SELL'
            bought = False

        signals.append(signal)

    return signals
