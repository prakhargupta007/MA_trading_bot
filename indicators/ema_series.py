def calculate_ema_series(series, period):
    ema_series = series.ewm(span=period, adjust=False).mean()
    return ema_series
