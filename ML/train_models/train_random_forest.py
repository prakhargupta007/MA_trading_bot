# Run the following command to run this file on terminal: 
# python3 -m ML.train_models.train_random_forest

from data.prepare_data_without_scaling import prepare_data_without_scaling
from ML.evaluate_model import evaluate_model
from ML.feature_importance.universal_permutation_importance_score import universal_permutation_importance_score
from ML.feature_importance.random_forest_feature_importance import random_forest_feature_importance

from sklearn.ensemble import RandomForestClassifier
from config import DATA_FOR_ML_MODEL_TRAINING, MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED
from config import RF_N_ESTIMATORS, RF_MAX_DEPTH, RF_RANDOM_STATE, RF_N_JOBS
import pandas as pd
import joblib
import os

print('Data file as determined in the config file is being used to train model...\n\n')

data = pd.read_csv(DATA_FOR_ML_MODEL_TRAINING, index_col="Date", parse_dates=True)

# Prepare data (scaling is optional for RandomForest)
X_train, X_test, y_train, y_test, feature_names = prepare_data_without_scaling(data)

print('Data has been prepared successfully')

# Train Random Forest model
model = RandomForestClassifier(
    n_estimators=RF_N_ESTIMATORS,
    max_depth=RF_MAX_DEPTH,
    random_state=RF_RANDOM_STATE,
    n_jobs=RF_N_JOBS
)

model.fit(X_train, y_train)

# Test
y_pred = model.predict(X_test)

# Feature importance
print("\nGini-based feature importance:")
print(random_forest_feature_importance(model, feature_names))
print('\n\n')
print("\nPermutation-based feature importance:")
print(universal_permutation_importance_score(model, X_test, y_test, feature_names))

evaluate_model(y_test, y_pred)

# Save model + scaler
os.makedirs('ML/saved_models', exist_ok=True)
joblib.dump({'model': model}, MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED)

print('Random Forest model saved successfully')
print('End of training \n\n')