import pandas as pd 

def calculate_sma(data, period):
    return data['Close'].rolling(window=period).mean()

