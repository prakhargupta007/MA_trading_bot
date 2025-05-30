from config import ALPHA_VANTAGE_API_KEY

from alpha_vantage.timeseries import TimeSeries
import pandas as pd

def fetch_data_from_alpha_vantage(ticker, backtesting_period):  
    ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')

    # Fetching data from Alpha Vantage (full data)
    # data, meta_data = ts.get_daily_adjusted(symbol=ticker, outputsize='full')  # --> Premium ALpha Vantage account required for adjusted close price 
    data, meta_data = ts.get_daily(symbol=ticker, outputsize='full') # --> works with free plan 
    data = data.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. adjusted close': 'Adj Close',
        '6. volume': 'Volume',
    })
    
    # Sorting the data so that the oldest data comes first (like yfinance) because the default order of ALpha VAntage data is descendinf (from latest to oldest)
    data = data.sort_index()

    # Convert 'Close' to numeric and handle NaN values
    data["Close"] = pd.to_numeric(data["Close"], errors='coerce')  # Convert to numeric (forlater calulation with dates) , NaN for errors
    data = data.dropna(subset=["Close"])  # Remove rows with NaN in 'Close'

    # Unlike the yfinance API the Alpha VAntage API doesn't take the paramter of period, which is why we need to fetch the whole data first and then slice it according to the backtesting_period
    if backtesting_period:
        # Slice the DataFrame based on backtesting_period (e.g., for 1 year data)
        end_date = data.index.max()
        start_date = end_date - pd.DateOffset(years=int(backtesting_period))  # Limit by years
        data = data[start_date:end_date]

    return data
