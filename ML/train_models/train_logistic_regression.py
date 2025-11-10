# Run the following command to run this file on terminal: 
# python3 -m ML.train_models.train_logistic_regression

from data.prepare_data_with_scaling import prepare_data_with_scaling
from ML.evaluate_model import evaluate_model
from ML.feature_importance.logistic_coefficient_importance import logistic_coefficient_importance
from ML.feature_importance.universal_permutation_importance_score import universal_permutation_importance_score

from sklearn.linear_model import LogisticRegression
from config import MAX_ITER,SOLVER,CLASS_WEIGHT, RANDOM_STATE
from config import DATA_FOR_ML_MODEL_TRAINING, MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED
from config import USE_PROBABILITY_THRESHOLD, PROBABILITY_THRESHOLD
import pandas as pd
import joblib
import os

print('data file as determined in the config file (including data split) is being used to train model\n\n\n')

data = pd.read_csv( DATA_FOR_ML_MODEL_TRAINING, index_col="Date", parse_dates=True)

# Prepare data (this now includes cleaning + scaling)
prepared = prepare_data_with_scaling(data)
if prepared is None:
    print("[WARN] Training data empty after cleaning; exiting.")
    raise SystemExit(0)
X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names = prepared

print("Training class distribution:\n", pd.Series(y_train).value_counts())
print("Test class distribution:\n", pd.Series(y_test).value_counts())



print('data has been successfully prepared')

# Train Logistic Regression model
model = LogisticRegression(max_iter=MAX_ITER, solver=SOLVER,class_weight=CLASS_WEIGHT, random_state=RANDOM_STATE)
model.fit(X_train_scaled, y_train) 

# Test model on test data
print('Testing model on test data...')
if USE_PROBABILITY_THRESHOLD:
    print(f"Using probability threshold: {PROBABILITY_THRESHOLD}")
    probs = model.predict_proba(X_test_scaled)
    y_pred = []

    for p in probs:
        if p[2] >= PROBABILITY_THRESHOLD:      # Buy probability check
            y_pred.append(2)
        elif p[0] >= PROBABILITY_THRESHOLD:    # Sell probability check
            y_pred.append(0)
        else:
            y_pred.append(1)                   # Otherwise Hold
else:
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

print(f'Logistic Regression model saved successfully as:\n{MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED}\n')
print('End of training \n')
