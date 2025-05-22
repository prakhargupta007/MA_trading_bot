from indicators.ema import calculate_ema
from indicators.ema_series import calculate_ema_series
def calculate_macd(data,fast_period, slow_period, signal_period):
    slow_ema = calculate_ema_series(data['Close'],slow_period)
    fast_ema = calculate_ema_series(data['Close'],fast_period)
    macd = fast_ema - slow_ema
    macd_signal = calculate_ema_series(macd, signal_period)

    return macd, macd_signal
