from indicators.sma import calculate_sma
from indicators.rsi import calculate_rsi

def sma_rsi_strategy(data, sma_long_period, sma_short_period, rsi_period, rsi_overbought, rsi_oversold, **kwargs):
    sma_short = calculate_sma(data, sma_short_period)
    sma_long = calculate_sma(data, sma_long_period)
    rsi = calculate_rsi(data, rsi_period)

    signals = ['HOLD']
    bought = False

    for _ in range(max(sma_long_period, rsi_period) - 1):
        signals.append('HOLD')

    for i in range(max(sma_long_period, rsi_period) - 1, len(data)):
        # Default signal is 'HOLD'
        signal = 'HOLD'
        
        if not bought:
            if sma_short.iloc[i] > sma_long.iloc[i] and rsi.iloc[i] < rsi_oversold:
                signal = 'BUY'
                bought = True  # Set bought to True after buying
        
        elif bought:  # Explicitly written, just for better readability 
            if sma_short.iloc[i] < sma_long.iloc[i] and rsi.iloc[i] > rsi_overbought:
                signal = 'SELL'
                bought = False  # Reset bought to False after selling
        
        signals.append(signal)  # Append the signal for this day

    return signals    