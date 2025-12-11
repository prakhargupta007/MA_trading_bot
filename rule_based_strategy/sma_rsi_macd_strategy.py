from indicators.sma import calculate_sma
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd

def sma_rsi_macd_strategy(data, sma_long_period, sma_short_period, rsi_period, rsi_overbought, rsi_oversold, **kwargs):
    """
    SMA crossover filtered by RSI with MACD confirmation (next-day execution).

    Signals follow the len(data)+1 convention: initial HOLD plus potential
    trailing entry; execution happens on the following trading day.
    """
    sma_short = calculate_sma(data, sma_short_period)
    sma_long = calculate_sma(data, sma_long_period)
    rsi = calculate_rsi(data, rsi_period)
    macd, macd_signal_line = calculate_macd(data, fast_period=12, slow_period=26, signal_period=9)

    signals = ['HOLD']
    bought = False

    for _ in range(max(sma_long_period, rsi_period) - 1):
        signals.append('HOLD')

    for i in range(max(sma_long_period, rsi_period) - 1, len(data)):
        # Default signal is 'HOLD'
        signal = 'HOLD'
        
        if not bought:
            if (sma_short.iloc[i] > sma_long.iloc[i] 
                and rsi.iloc[i] < rsi_oversold 
                and macd.iloc[i] > macd_signal_line.iloc[i]):
                signal = 'BUY'
                bought = True  # Set bought to True after buying
        
        elif bought:  # Explicitly written, just for better readability 
            if (sma_short.iloc[i] < sma_long.iloc[i] 
                and rsi.iloc[i] > rsi_overbought 
                or macd.iloc[i] < macd_signal_line.iloc[i]):
                signal = 'SELL'
                bought = False  # Reset bought to False after selling
        
        signals.append(signal)  # Append the signal for this day

    return signals

