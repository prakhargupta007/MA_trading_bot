import pandas as pd

def generate_sentiment_score_feature_list(target_index, sentiment_data_path_for_ml_model_training_feature):

    TRADING_DAYS_FILE = sentiment_data_path_for_ml_model_training_feature

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

# instead of just using the scores positive negative and neutral I created a list with continuous nagative and positive values which also tells me the strenth of the sentiment category. 
# Through the categorial method  positive sentiment of score of 0.51 and 0.99 would get the same treatment but in this method the 0.99 would have a higher weightage than 0.51
# This conversion into continous values is done for ML models
# this conversion into continous values makes sense because the ML model ccan also learn the pattern or impact of the strength of the sentiment and potentially lead to better signal prediction.
# This conversion could also be helpful in the rule based sentiment strategy as it could determine the position sizing based on sentiment strength, however  haven't implemented that yet and the categorial method is being used there. 