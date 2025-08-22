# Run the following command to run this file on terminal:
# python3 -m ML.train_models.train_xgboost

from data.prepare_data_without_scaling import prepare_data_without_scaling
from ML.evaluate_model import evaluate_model
from ML.feature_importance.universal_permutation_importance_score import universal_permutation_importance_score
from ML.feature_importance.xgboost_gain_importance import xgboost_gain_importance

from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier
from config import (
    DATA_FOR_ML_MODEL_TRAINING,
    MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED,
    XGB_N_ESTIMATORS,
    XGB_MAX_DEPTH,
    XGB_LEARNING_RATE,
    XGB_SUBSAMPLE,
    XGB_COLSAMPLE_BYTREE,
    XGB_RANDOM_STATE,
    XGB_N_JOBS,
    VERBOSITY,
    EVAL_METRIC,
    BASE_SCORE,
    OBJECTIVE
)

from config import USE_PROBABILITY_THRESHOLD, PROBABILITY_THRESHOLD
import pandas as pd
import joblib
import os


print('Data file as determined in the config file is being used to train model...\n\n')

# Load data
data = pd.read_csv(DATA_FOR_ML_MODEL_TRAINING, index_col="Date", parse_dates=True)

# Prepare features and labels
X_train, X_test, y_train, y_test, feature_names = prepare_data_without_scaling(data)
num_class = len(y_train.unique())

print('Data has been prepared successfully')

# Train XGBoost model
model = XGBClassifier(
    n_estimators=XGB_N_ESTIMATORS,
    max_depth=XGB_MAX_DEPTH,
    learning_rate=XGB_LEARNING_RATE,
    subsample=XGB_SUBSAMPLE,
    colsample_bytree=XGB_COLSAMPLE_BYTREE,
    random_state=XGB_RANDOM_STATE,
    n_jobs=XGB_N_JOBS,
    verbosity=VERBOSITY,
    eval_metric=EVAL_METRIC,

    base_score= BASE_SCORE,   
    objective=OBJECTIVE,  # multiclass objective

    num_class=num_class,

)

# Compute sample weights
sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)

# Train XGBoost with sample weights
model.fit(X_train,y_train,sample_weight=sample_weights)


# Predict
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
            y_pred.append(1)    
else:
    y_pred = model.predict(X_test)

# Feature Importances
print("\nGain-based feature importance:")
gain_importances = xgboost_gain_importance(model, feature_names)
for feat, imp in gain_importances:
    print(f"{feat}: {imp:.4f}")

print("\nPermutation-based feature importance:")
print(universal_permutation_importance_score(model, X_test, y_test, feature_names))

# Evaluate model
evaluate_model(y_test, y_pred)

# Save model
os.makedirs('ML/saved_models', exist_ok=True)
joblib.dump({'model': model}, MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED)

print(f'XGBoost model saved successfully as:\n{MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED}\n')
print('End of training \n')