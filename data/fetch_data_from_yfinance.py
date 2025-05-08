import yfinance as yf
import pandas as pd

def fetch_data_from_yfinance(ticker, backtesting_period):   
    data = yf.download(ticker, period=f'{backtesting_period}y', threads=True)
    data.columns.name = None

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)  # Get the first level of the MultiIndex columns
    # Ensure 'Close' is numeric and handles any NaN values
    data["Close"] = pd.to_numeric(data["Close"], errors='coerce')  # Convert to numeric, turning errors into NaNs
    data = data.dropna(subset=["Close"])

    return data