from indicators.sma import calculate_sma
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd
import pandas as pd

def sma_rsi_macd_strategy(bought,data, sma_long_period, sma_short_period, rsi_period, macd_fast, macd_short, macd_signal):
    # Calculate indicators
    sma_short = calculate_sma(data, sma_short_period)
    sma_long = calculate_sma(data, sma_long_period)
    rsi = calculate_rsi(data, rsi_period) 
    macd, macd_signal_line = calculate_macd(data, macd_fast, macd_short, macd_signal)

    signals = []

    # Add initial HOLDs so signal list matches the data length
    for _ in range(sma_long_period - 1):  # replace with correct variable name
        signals.append('HOLD')

    for i in range(sma_long_period - 1, len(data)):
        # Default signal is 'HOLD'
        signal = 'HOLD'
        
        if not bought:
            if sma_short.iloc[i] > sma_long.iloc[i] and rsi.iloc[i] < 30 and macd.iloc[i] > macd_signal_line.iloc[i]:
                signal = 'BUY'
                bought = True  # Set bought to True after buying
        
        elif bought:  # Explicitly written , just for better readibility 
            if sma_short.iloc[i] < sma_long.iloc[i] or rsi.iloc[i] > 70 or macd.iloc[i] < macd_signal_line.iloc[i]:
                signal = 'SELL'
                bought = False  # Reset bought to False after selling
        
        signals.append(signal)  # Append the signal for this day

    return signals    


