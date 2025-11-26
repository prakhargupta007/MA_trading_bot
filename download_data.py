# This function is used for downloading data from yfinance to store locally. function need to get run as seperate file on terminal 

import yfinance as yf
import pandas as pd

'This function downloads data of the period why is exactly in between start and end dates, excluding the start and end dates themselves.'


#start = '2012-05-18'
#end = '2020-12-31'

start = '2020-12-31'
end = '2025-10-25'

#tickers = ['AAPL','NVDA','MSFT','QQQ','^VIX']
#tickers = ['^GSPC','^NDX']
#tickers = ['^VIX']
tickers = [
    "MSFT",
    "AAPL",
    "GOOG",
    "META",
    "ORCL",
    "ADBE",
    "TSLA",
    "AMD",
    "NVDA",
    "QQQ",
    "^GSPC",
    "^NDX",
    "^VIX"
]

word = 'backtest' 
#word = 'train_test'

def download_data():
    for ticker in tickers:
        file_path = f'/Users/prakhar/Desktop/MA_trading_bot/data/stored_data2/data_{ticker}_{word}_{start}--{end}.csv'
        data = yf.download(ticker, start, end, threads=True)
        if data is None or data.empty:
                raise ValueError(f"❌ No data was fetched for ticker {ticker}. Please check the ticker symbol or your internet connection.")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)  # Get the first level of the MultiIndex columns
        # Ensure 'Close' is numeric and handles any NaN values
        data["Close"] = pd.to_numeric(data["Close"], errors='coerce')  # Convert to numeric, turning errors into NaNs
        data = data.dropna(subset=["Close"])

        data.to_csv(file_path) 
        print(f'download of {tickers} complete')

download_data()