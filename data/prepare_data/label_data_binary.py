
from config import MINIMUM_PERCENTAGE_THRESHOLD
def add_labels_with_threshold(data):
    """
    This func adds a 'Label' column to the input DataFrame based on next-day % change.
    0 = SELL, 1 = HOLD, 2 = BUY
    It returns the same data as before just with a new 'label' column added
    """
    # Calculate next day's close price
    data['Next_Close'] = data['Close'].shift(-1)
    
    # Calculate % change between today and tomorrow
    pct_change = (data['Next_Close'] - data['Close']) / data['Close']
    
    # Define a normal function to assign label
    def assign_label(x):
        if x > MINIMUM_PERCENTAGE_THRESHOLD:
            return 2  # BUY
        elif x < -MINIMUM_PERCENTAGE_THRESHOLD:
            return 0  # SELL
        else:
            return 1  # HOLD

    # Apply the function to the percentage change
    data['Label'] = pct_change.apply(assign_label)
    
    # Optional: Drop the helper column
    data.drop(columns=['Next_Close'], inplace=True)
    
    return data
