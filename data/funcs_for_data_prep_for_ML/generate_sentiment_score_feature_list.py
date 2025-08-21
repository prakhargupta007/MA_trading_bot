import pandas as pd

def generate_sentiment_score_feature_list(target_index):
    # ================= CONFIGURATION =================
    TICKER = "AAPL"
     #TRADING_DAYS_FILE = f"/Users/prakhar/MA_trading_bot/sentiment_analysis/trading_days_daily_output/{TICKER}_sentiment_trading_days.csv"
    TRADING_DAYS_FILE = '/Users/prakhar/MA_trading_bot/sentiment_analysis/GDELT/trading_days_daily_output/AAPL_2017_till_2025-08-15_sentiment.csv'
    # =================================================

    # Load the sentiment trading days CSV
    df = pd.read_csv(TRADING_DAYS_FILE, parse_dates=['day'])

    # Calculate sentiment score: magnitude adjusted by probabilities
    df["sentiment_score"] = df["prob_positive"] - df["prob_negative"]

    # Make Series with 'day' as index
    sentiment_series = pd.Series(df["sentiment_score"].values, index=df["day"])
    sentiment_series.name = "sentiment_score"

    # Align only to target_index
    sentiment_series = sentiment_series.reindex(target_index)

    return sentiment_series
