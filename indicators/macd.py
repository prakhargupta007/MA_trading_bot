import pandas as pd
from ema import * 

def calculate_macd(data,short_period, long_period, signal_period):
    long_ema = calculate_ema(data,long_period)
    short_ema = calculate_ema(data,short_period)
    macd = short_ema - long_ema
    macd_signal = calculate_ema(macd,signal_period)
    return macd, macd_signal