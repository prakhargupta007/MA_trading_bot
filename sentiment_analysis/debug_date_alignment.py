import pandas as pd

def debug_date_alignment(data, sentiment_df):
    price_dates = pd.Index(pd.to_datetime(data.index))
    sentiment_dates = pd.Index(pd.to_datetime(sentiment_df['day']))  # Assuming 'day' column in sentiment_df

    print(f"Price data starts at {price_dates.min()} and ends at {price_dates.max()}")
    print(f"Sentiment data starts at {sentiment_dates.min()} and ends at {sentiment_dates.max()}")
    print(f"Length of price data: {len(price_dates)} | Length of sentiment data: {len(sentiment_dates)}")

    missing_in_sentiment = price_dates.difference(sentiment_dates)
    missing_in_price = sentiment_dates.difference(price_dates)

    print(f"❌ Missing in sentiment ({len(missing_in_sentiment)}): {list(missing_in_sentiment[:10])}")
    print(f"❌ Missing in price ({len(missing_in_price)}): {list(missing_in_price[:10])}")
