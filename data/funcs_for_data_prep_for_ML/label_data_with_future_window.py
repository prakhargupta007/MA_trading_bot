from config import MINIMUM_PERCENTAGE_THRESHOLD
from config import LOOKAHEAD_DAYS
import pandas as pd
import numpy as np

def label_data_with_future_window(data, lookahead_days=5):
    """
    Adds a 'Label' column to the input DataFrame based on whether the stock moves up or down 
    by at least MINIMUM_PERCENTAGE_THRESHOLD within the next 'lookahead_days' days.
    
    0 = SELL, 1 = HOLD, 2 = BUY

    This version preserves the original length of the data and avoids lookahead bias.
    NaNs will exist where labeling can't be done (e.g., near the end).
    """

    close_prices = data['Close'].values

    labels = []

    # Loop over each row in the dataset
    for i in range(len(close_prices)):
        # Get the future price window (from t+1 to t+lookahead_days)
        future_prices = close_prices[i+1:i+1+lookahead_days]

        # If not enough future data, append None (so row stays for plotting)
        if len(future_prices) < 1:
            labels.append(None)
            continue

        current_price = close_prices[i]
        future_returns = (future_prices - current_price) / current_price

        max_gain = np.max(future_returns)
        max_loss = np.min(future_returns)

        # Assign label based on threshold logic
        if max_gain >= MINIMUM_PERCENTAGE_THRESHOLD:
            labels.append(2)  # BUY
        elif max_loss <= -MINIMUM_PERCENTAGE_THRESHOLD:
            labels.append(0)  # SELL
        else:
            labels.append(1)  # HOLD

    # Add label column to the DataFrame
    data['Label'] = labels

    # KEEP Nan values in 'Label' column --> needed for plotting or perfect strategy use
    return data
