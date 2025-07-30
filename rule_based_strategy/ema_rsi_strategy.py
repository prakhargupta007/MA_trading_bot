from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi

def ema_rsi_strategy(data, ema_long_period, ema_short_period, rsi_period, rsi_overbought, rsi_oversold, **kwargs):
    ema_short = calculate_ema(data, ema_short_period)
    ema_long = calculate_ema(data, ema_long_period)
    rsi = calculate_rsi(data, rsi_period)

    signals = ['HOLD']
    bought = False

    for _ in range(max(ema_long_period, rsi_period) - 1):
        signals.append('HOLD')

    for i in range(max(ema_long_period, rsi_period) - 1, len(data)):
        # Default signal is 'HOLD'
        signal = 'HOLD'
        
        if not bought:
            if ema_short.iloc[i] > ema_long.iloc[i] and rsi.iloc[i] < rsi_oversold:
                signal = 'BUY'
                bought = True  # Set bought to True after buying
        
        elif bought:  # Explicitly written, just for better readability 
            if ema_short.iloc[i] < ema_long.iloc[i] and rsi.iloc[i] > rsi_overbought:
                signal = 'SELL'
                bought = False  # Reset bought to False after selling
        
        signals.append(signal)  # Append the signal for this day

    return signals    