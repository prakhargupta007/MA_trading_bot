def calculate_sma(data, period):
    sma = data['Close'].rolling(window=period).mean()
    return sma

