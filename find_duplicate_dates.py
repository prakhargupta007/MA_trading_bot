import pandas as pd

def find_duplicate_dates(csv_path):
    """
    Checks a CSV file for duplicate dates in the 'day' column.
    
    Args:
        csv_path (str): Path to the CSV file.
    
    Returns:
        pd.DataFrame: Rows with duplicate dates.
        pd.Series: Count of duplicates per date.
    """
    # Load CSV
    df = pd.read_csv(csv_path, parse_dates=['day'])
    
    # Find duplicate rows based on 'day'
    duplicates_df = df[df.duplicated(subset='day', keep=False)]
    
    # Count how many times each duplicate date appears
    duplicate_counts = duplicates_df['day'].value_counts()
    
    return duplicates_df, duplicate_counts


path = '/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/trading_days_daily_output/NVDA_1_sentiment_trading_days.csv'
print(find_duplicate_dates(path))