# Run the following command to run this file on terminal: 
# python3 -m ML.train_models.train_logistic_regression

from data.prepare_data import prepare_data
from ML.evaluate_model import evaluate_model
from sklearn.linear_model import LogisticRegression
import pandas as pd
import joblib
import os

print('data of AAPL stock is being used to train model\n\n\n')
data = pd.read_csv("/Users/prakhar/MA_trading_bot/data/data_AAPL_2010-2020.csv", index_col="Date", parse_dates=True)
X_train_scaled, X_test_scaled, y_train, y_test, scaler = prepare_data(data)


# Drop any rows with NaNs in either X or y before training becuase model shouldnt be trained on incomplete data which contains emtpy columns due to NaN values
import pandas as pd
train_mask = ~(pd.DataFrame(X_train_scaled).isnull().any(axis=1) | pd.Series(y_train).isnull())
X_train = X_train_scaled[train_mask]
y_train = y_train[train_mask]

test_mask = ~(pd.DataFrame(X_test_scaled).isnull().any(axis=1) | pd.Series(y_test).isnull())
X_test = X_test_scaled[test_mask]
y_test = y_test[test_mask]


print('data has been successfully prepared')

# Train a Logistic Regression model on the training data of AAPL stock
model = LogisticRegression()
model.fit(X_train_scaled, y_train)  

# Test model on test data
print('Testing model on test data...')
y_pred = model.predict(X_test_scaled)

# Evaluate
evaluate_model(y_test, y_pred)

# save the model
os.makedirs('ML/saved_models', exist_ok=True)
joblib.dump({'model': model, 'scaler': scaler}, 'ML/saved_models/lr_model_with_scaler_AAPL.joblib')
print('Model has been successfuly saved')