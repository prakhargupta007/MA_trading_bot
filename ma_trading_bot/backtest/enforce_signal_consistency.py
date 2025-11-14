def enforce_signal_consistency(signals):
    position_open = False
    for i, s in enumerate(signals):
        if s == 'BUY':
            if position_open:
                # Prevent double BUYs
                signals[i] = 'HOLD'
            else:
                position_open = True
        elif s == 'SELL':
            if not position_open:
                # Prevent random SELL without BUY
                signals[i] = 'HOLD'
            else:
                position_open = False

    # If at the end you're still holding, enforce a final SELL
    if position_open:
        signals[-1] = 'SELL'

    return signals
