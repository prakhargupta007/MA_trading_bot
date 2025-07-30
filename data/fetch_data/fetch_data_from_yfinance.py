import yfinance as yf
import pandas as pd

def fetch_data_from_yfinance(ticker, option_1_chosen, backtesting_period, end_of_backtesting, start_of_backtesting):   
    try:
        if option_1_chosen:
            # Calculate start and end dates
            backtesting_period = float(backtesting_period)
            end_date = pd.to_datetime("today")
            full_years = int(backtesting_period)
            extra_days = int((backtesting_period - full_years) * 365.25)
            offset = pd.DateOffset(years=full_years, days=extra_days)
            start_date = end_date - offset
            
            # Download exact range
            data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), threads=True)
        
        else:
            data = yf.download(ticker, start=start_of_backtesting, end=end_of_backtesting, threads=True)

        if data is None or data.empty:
            raise ValueError(f"❌ No data was fetched for ticker {ticker}. Please check the ticker symbol or your internet connection.")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)  # Get the first level of the MultiIndex columns
        # Ensure 'Close' is numeric and handles any NaN values
        data["Close"] = pd.to_numeric(data["Close"], errors='coerce')  # Convert to numeric, turning errors into NaNs
        data = data.dropna(subset=["Close"])

        # Following line was just used for downloading test data instead of new fresh data, which would lead to limit error.
        #data.to_csv('/Users/prakhar/MA_trading_bot/data/test_data_AAPL.csv') 

        return data
    except Exception as e:
        raise ValueError(f"❌ Error fetching data for ticker {ticker}: {str(e)}")