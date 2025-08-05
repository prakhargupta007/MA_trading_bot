# Run the following command to run this file on terminal: 
# python3 -m ML.train_models.train_logistic_regression

from data.prepare_data import prepare_data
from ML.evaluate_model import evaluate_model
from sklearn.linear_model import LogisticRegression
import pandas as pd
import joblib
import os

print('data of AAPL stock from 2010 till 2020 (including data split) is being used to train model\n\n\n')

data = pd.read_csv("/Users/prakhar/MA_trading_bot/data/stored_data/data_AAPL_2010-2020.csv", index_col="Date", parse_dates=True)

# Prepare data (this now includes cleaning + scaling)
X_train_scaled, X_test_scaled, y_train, y_test, scaler = prepare_data(data)

print('data has been successfully prepared')

# Train a Logistic Regression model on the training data of AAPL stock
model = LogisticRegression()
model.fit(X_train_scaled, y_train) 

# Test model on test data
print('Testing model on test data...')
y_pred = model.predict(X_test_scaled)

evaluate_model(y_test, y_pred)

# Save the model and scaler together
os.makedirs('ML/saved_models', exist_ok=True)
joblib.dump({'model': model, 'scaler': scaler}, 'ML/saved_models/lr_model_with_scaler_AAPL_2.joblib')

print('Model has been successfully saved')
