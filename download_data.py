# This function is used for downloading data from yfinance to store locally. function need to get run as seperate file on terminal 

import yfinance as yf
import pandas as pd

start = '2010-01-01'
end = '2025-06-01'
ticker = 'AAPL'
file_path = '/Users/prakhar/MA_trading_bot/data/data_AAPL_2010-2025.csv'

def download_data():
    data = yf.download(ticker, start, end, threads=True)
    if data is None or data.empty:
            raise ValueError(f"❌ No data was fetched for ticker {ticker}. Please check the ticker symbol or your internet connection.")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)  # Get the first level of the MultiIndex columns
    # Ensure 'Close' is numeric and handles any NaN values
    data["Close"] = pd.to_numeric(data["Close"], errors='coerce')  # Convert to numeric, turning errors into NaNs
    data = data.dropna(subset=["Close"])

    data.to_csv(file_path) 
    print('download complete')

download_data()