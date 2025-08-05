from config import MINIMUM_PERCENTAGE_THRESHOLD
import pandas as pd 
def label_data_with_threshold(data):
    """
    Adds a 'Label' column to the input DataFrame based on next-day % change.
    0 = SELL, 1 = HOLD, 2 = BUY

    This version preserves the original length of the data and avoids lookahead bias.
    NaNs will exist where labeling can't be done (e.g., at the end).
    """
    # Calculate next day's close price
    data['Next_Close'] = data['Close'].shift(-1)

    # Calculate % change between today and tomorrow
    pct_change = (data['Next_Close'] - data['Close']) / data['Close']

    # Define labeling function
    def assign_label(x):
        if pd.isna(x):
            return None  # This keeps the row for plotting, but no label is assigned
        elif x > MINIMUM_PERCENTAGE_THRESHOLD:
            return 2  # BUY
        elif x < -MINIMUM_PERCENTAGE_THRESHOLD:
            return 0  # SELL
        else:
            return 1  # HOLD

    # Apply labeling logic
    data['Label'] = pct_change.apply(assign_label)

    # If I want to drop the helper column, because not needed anymore, following line can be used...
    #data.drop(columns=['Next_Close'], inplace=True)
    # KEEP Nan Values in Label Column, because this same function is used to simulate the labels and see their performance in the perfect_strategy.py file

    return data
