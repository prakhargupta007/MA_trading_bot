from indicators.ema import calculate_ema

def calculate_macd(data,fast_period, slow_period, signal_period):
    slow_ema = calculate_ema(data['Close'],slow_period)
    fast_ema = calculate_ema(data['Close'],fast_period)
    macd = fast_ema - slow_ema
    macd_signal = calculate_ema(macd,signal_period)
    return macd, macd_signal
