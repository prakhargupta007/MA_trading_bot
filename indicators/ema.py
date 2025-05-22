def calculate_ema(data, period):
    ema = data['Close'].ewm(span=period, adjust=False).mean()
    return ema

