'''
import requests
from datetime import datetime, timedelta
import csv
import os

# -------CONFIG---------#
TICKER = "AAPL"  
START_DATE = "2019-03-01"
END_DATE = "2025-08-15"

STOCK_NEWS_API_KEY = 'wpqforq8df93rtio5njvfmw8lv4mqjujaakrxmdk'
FILE_NAME = f"{TICKER}_stocknewsapi_sentiment.csv"
OUTPUT_FOLDER = "/Users/prakhar/MA_trading_bot/sentiment_analysis/stock_news_api/output_stocknewsapi"

def stock_news_api_sentiment(ticker, start_date, end_date):
    """
    Fetches aggregated daily sentiment scores for a given stock ticker from StockNewsAPI
    and saves them to a CSV file in the specified output folder.
    
    Parameters:
        ticker (str): Stock ticker symbol, e.g. 'AAPL'
        start_date (str): Start date in 'YYYY-MM-DD'
        end_date (str): End date in 'YYYY-MM-DD'
    
    Returns:
        list of dict: Each dict contains 'date' and 'sentiment_score'
    """
    
    # Convert YYYY-MM-DD to MMDDYYYY for API
    def convert_date(date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%m%d%Y")
    
    # Chunk long date ranges into 30-day windows
    def chunk_date_range(start, end, chunk_size=30):
        chunks = []
        current_start = start
        while current_start <= end:
            current_end = min(current_start + timedelta(days=chunk_size-1), end)
            chunks.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)
        return chunks
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    chunks = chunk_date_range(start_dt, end_dt)
    
    all_results = []
    
    for chunk_start, chunk_end in chunks:
        date_param = f"{convert_date(chunk_start.strftime('%Y-%m-%d'))}-{convert_date(chunk_end.strftime('%Y-%m-%d'))}"
        url = "https://stocknewsapi.com/api/v1/stat"
        params = {
            "tickers": ticker,
            "date": date_param,
            "page": 1,
            "token": STOCK_NEWS_API_KEY
        }
        
        print(f"Fetching {chunk_start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}...")
        
        while True:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "data" not in data:
                print("Error or no data found:", data)
                break
            
            for entry in data["data"]:
                all_results.append({
                    "date": entry["date"],
                    "sentiment_score": entry["sentiment_score"]  # aggregated score for the day
                })
            
            # Stop if no more pages
            if not data.get("has_more", False):
                break
            
            params["page"] += 1
        
        print("Done.")
    
    # Ensure output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    full_path = os.path.join(OUTPUT_FOLDER, FILE_NAME)
    
    # Save to CSV
    with open(full_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "sentiment_score"])
        writer.writeheader()
        for row in all_results:
            writer.writerow(row)
    
    print(f"Saved results to {full_path}")
    return all_results


# Call the function
stock_news_api_sentiment(TICKER, START_DATE, END_DATE)
'''


import requests
from datetime import datetime
import csv
import os

# -------CONFIG---------#
TICKER = "AAPL"  
START_DATE = "2019-03-01"  # StockNewsAPI only allows historical data from March 2019
END_DATE = "2025-08-15"

STOCK_NEWS_API_KEY = 'wpqforq8df93rtio5njvfmw8lv4mqjujaakrxmdk'
FILE_NAME = f"{TICKER}_stocknewsapi_sentiment.csv"
OUTPUT_FOLDER = "/Users/prakhar/MA_trading_bot/sentiment_analysis/stock_news_api/output_stocknewsapi"

def stock_news_api_sentiment(ticker, start_date, end_date):
    """
    Fetches aggregated daily sentiment scores for a given stock ticker from StockNewsAPI
    and saves them to a CSV file in the specified output folder.
    
    Parameters:
        ticker (str): Stock ticker symbol, e.g. 'AAPL'
        start_date (str): Start date in 'YYYY-MM-DD'
        end_date (str): End date in 'YYYY-MM-DD'
    
    Returns:
        list of dict: Each dict contains 'date' and 'sentiment_score'
    """
    
    # Convert YYYY-MM-DD to MMDDYYYY for API
    def convert_date(date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%m%d%Y")
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Use one giant chunk to maximize free trial calls
    date_param = f"{convert_date(start_dt.strftime('%Y-%m-%d'))}-{convert_date(end_dt.strftime('%Y-%m-%d'))}"
    
    url = "https://stocknewsapi.com/api/v1/stat"
    params = {
        "tickers": ticker,
        "date": date_param,
        "page": 1,
        "token": STOCK_NEWS_API_KEY
    }
    
    all_results = []
    
    print(f"Fetching {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}...")
    
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "data" not in data:
            print("Error or no data found:", data)
            break
        
        # Iterate over each date in the 'data' dictionary
        for date_str, ticker_data in data["data"].items():
            if ticker in ticker_data and "sentiment_score" in ticker_data[ticker]:
                score = ticker_data[ticker]["sentiment_score"]
                all_results.append({
                    "date": date_str,
                    "sentiment_score": score
                })
            else:
                print(f"No data for {ticker} on {date_str}, skipping...")
        
        # Stop if no more pages
        if not data.get("has_more", False):
            break
        
        params["page"] += 1
    
    print("Done fetching.")
    
    # Ensure output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    full_path = os.path.join(OUTPUT_FOLDER, FILE_NAME)
    
    # Save to CSV
    with open(full_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "sentiment_score"])
        writer.writeheader()
        for row in all_results:
            writer.writerow(row)
    
    print(f"Saved results to {full_path}")
    return all_results

# Call the function
stock_news_api_sentiment(TICKER, START_DATE, END_DATE)
