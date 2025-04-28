from indicators.sma import calculate_sma
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd

def generate_signals(bought,data, sma_long_period, sma_short_period, rsi_period, macd_fast, macd_short, macd_signal):
    # Calculate indicators
    sma_short = calculate_sma(data, sma_short_period)
    sma_long = calculate_sma(data, sma_long_period)
    rsi = calculate_rsi(data, rsi_period)
    macd, macd_signal_line = calculate_macd(data, macd_fast, macd_short, macd_signal)

    signals = []
    for i in range(sma_long_period -1 ,len(data)):
        decision = 'tbd'
        if not bought:
            if sma_short.iloc[i] > sma_long.iloc[i] and rsi > 30 and macd > macd_signal_line:
                signal = 'BUY'
           #else: 
               #signal = 'HOLD'
        
        else: #if already bought
            if sma_short.iloc[i] > sma_long.iloc[i] or rsi > 30 or macd > macd_signal_line:
                signal = 'SELL'
                bought = False 
           #else: 
               #signal = 'HOLD'

        signals.append(signal)

    return signals
            


