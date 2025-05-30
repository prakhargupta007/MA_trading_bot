from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi


def ema_rsi_strategy(data, ema_long_period, ema_short_period, rsi_period, **kwargs):
    # Calculate indicators
    ema_short = calculate_ema(data, ema_short_period)
    ema_long = calculate_ema(data, ema_long_period)
    rsi = calculate_rsi(data, rsi_period) 

    signals = []
    bought = False
    # Add initial HOLDs so signal list matches the data length
    for _ in range(ema_long_period - 1):  # replace with correct variable name
        signals.append('HOLD')
        
    for i in range(ema_long_period - 1, len(data)):
        # Default signal is 'HOLD'
        signal = 'HOLD'
        
        if not bought:
            if (ema_short.iloc[i] > ema_long.iloc[i] 
                and rsi.iloc[i] < 30 
                #and macd.iloc[i] > macd_signal_line.iloc[i]
                ):
                signal = 'BUY'
                bought = True  # Set bought to True after buying
        
        elif bought:  # Explicitly written , just for better readibility 
            if (ema_short.iloc[i] < ema_long.iloc[i] 
                and rsi.iloc[i] > 70 
                #or macd.iloc[i] < macd_signal_line.iloc[i]
                ):
                signal = 'SELL'
                bought = False  # Reset bought to False after selling
        
        signals.append(signal)  # Append the signal for this day

    return signals    