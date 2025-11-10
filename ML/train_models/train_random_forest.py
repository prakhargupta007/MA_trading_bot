# Run the following command to run this file on terminal: 
# python3 -m ML.train_models.train_random_forest

from data.prepare_data_without_scaling import prepare_data_without_scaling
from ML.evaluate_model import evaluate_model
from ML.feature_importance.universal_permutation_importance_score import universal_permutation_importance_score
from ML.feature_importance.random_forest_feature_importance import random_forest_feature_importance

from sklearn.ensemble import RandomForestClassifier
from config import DATA_FOR_ML_MODEL_TRAINING, MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED
from config import RF_N_ESTIMATORS, RF_MAX_DEPTH, RF_RANDOM_STATE, RF_N_JOBS, RF_MIN_SAMPLES_LEAF, RF_MIN_SAMPLES_SPLIT, RF_CLASS_WEIGHT, RF_OOB_SCORE, RF_MAX_FEATURES
from config import USE_PROBABILITY_THRESHOLD, PROBABILITY_THRESHOLD
import pandas as pd
import joblib
import os

print('Data file as determined in the config file is being used to train model...\n\n')

data = pd.read_csv(DATA_FOR_ML_MODEL_TRAINING, index_col="Date", parse_dates=True)
print(data.head())
print("Before split:", data.shape)

# Prepare data (scaling is optional for RandomForest)
prepared = prepare_data_without_scaling(data)
if prepared is None:
    print("[WARN] Training data empty after cleaning; exiting.")
    raise SystemExit(0)
X_train, X_test, y_train, y_test, feature_names = prepared
print("After cleaning:", X_train.shape, X_test.shape, y_train.shape, y_test.shape)

print('Data has been prepared successfully')

# Train Random Forest model
model = RandomForestClassifier(
    n_estimators=RF_N_ESTIMATORS,
    max_depth=RF_MAX_DEPTH,
    min_samples_leaf=RF_MIN_SAMPLES_LEAF,
    min_samples_split=RF_MIN_SAMPLES_SPLIT,
    max_features=RF_MAX_FEATURES,
    class_weight=RF_CLASS_WEIGHT,
    oob_score=RF_OOB_SCORE,
    random_state=RF_RANDOM_STATE,
    n_jobs=RF_N_JOBS
)

model.fit(X_train, y_train)

# Test
if USE_PROBABILITY_THRESHOLD:
    print(f"Using probability threshold: {PROBABILITY_THRESHOLD}")
    probs = model.predict_proba(X_test)
    y_pred = []

    for p in probs:
        if p[2] >= PROBABILITY_THRESHOLD:      # Buy probability check
            y_pred.append(2)
        elif p[0] >= PROBABILITY_THRESHOLD:    # Sell probability check
            y_pred.append(0)
        else:
            y_pred.append(1)                   # Otherwise Hold
else:
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

print(f'Random Forest model saved successfully as:\n{MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED}\n')
print('End of training \n')
