import pandas as pd

def calculate_ema(data, period):
    ema = data.ewm(span= period, adjust=False).mean()
    return ema 
