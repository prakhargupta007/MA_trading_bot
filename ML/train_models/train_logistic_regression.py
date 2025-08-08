# Run the following command to run this file on terminal: 
# python3 -m ML.train_models.train_logistic_regression

from data.prepare_data_with_scaling import prepare_data_with_scaling
from ML.evaluate_model import evaluate_model
from ML.feature_importance.logistic_coefficient_importance import logistic_coefficient_importance
from ML.feature_importance.universal_permutation_importance_score import universal_permutation_importance_score

from sklearn.linear_model import LogisticRegression
from config import DATA_FOR_ML_MODEL_TRAINING, MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED
import pandas as pd
import joblib
import os

print('data file as determined in the config file (including data split) is being used to train model\n\n\n')

data = pd.read_csv( DATA_FOR_ML_MODEL_TRAINING, index_col="Date", parse_dates=True)

# Prepare data (this now includes cleaning + scaling)
X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names = prepare_data_with_scaling(data)

print('data has been successfully prepared')

# Train Logistic Regression model
model = LogisticRegression()
model.fit(X_train_scaled, y_train) 

# Test model on test data
print('Testing model on test data...')
y_pred = model.predict(X_test_scaled)

# Feature importance: 
print('Determining feature importance...\n')
print("\nCoefficient-based feature importance:")
print(logistic_coefficient_importance(model, feature_names))
print('\n\n')
print("\nPermutation-based feature importance:")
print(universal_permutation_importance_score(model, X_test_scaled, y_test, feature_names))

evaluate_model(y_test, y_pred)

# Save the model and scaler together
os.makedirs('ML/saved_models', exist_ok=True)
joblib.dump({'model': model, 'scaler': scaler}, MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED)

print('Logistic regression model has been successfully saved')
