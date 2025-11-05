import pandas as pd
import numpy as np
import tensorflow as tf
import joblib

from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data
from ML.ML_strategy.processing_steps_for_signal_generation.translate_raw_signals import translate_raw_signals
from ML.ML_strategy.processing_steps_for_signal_generation.apply_positioning_rule_to_translated_signals import apply_positioning_rule_to_translated_signals
from config import FEATURE_COLUMNS, GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH
from config import MLP_MODEL_PATH_FOR_STRATEGY, MLP_SCALAR_PATH_FOR_STRATEGY


# Paths to model/scaler


def mlp_strategy(data, **kwargs):
    # Load model + scaler
    print("Loading trained MLP model and scaler...")
    model = tf.keras.models.load_model(MLP_MODEL_PATH_FOR_STRATEGY)
    scaler = joblib.load(MLP_SCALAR_PATH_FOR_STRATEGY)
    print("Model and scaler loaded successfully.\n")

    # Add features
    data_with_features = calculate_and_add_features_to_data(
        data, GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH
    )
    data_with_features = data_with_features[FEATURE_COLUMNS]
    print(f"len(data_with_features): {len(data_with_features)}")

    # Drop rows with NaNs
    valid_rows_mask = data_with_features.notnull().all(axis=1)
    valid_data = data_with_features[valid_rows_mask]
    print(f"Number of valid rows: {valid_rows_mask.sum()}")

    # Scale features
    X_new_scaled = scaler.transform(valid_data)

    # Predict class probabilities
    probs = model.predict(X_new_scaled, verbose=0)
    predicted_classes = np.argmax(probs, axis=1)

    # Map predictions back into full signal array
    full_signals = ['HOLD'] * len(data_with_features)
    valid_indices = data_with_features[valid_rows_mask].index
    for idx, signal in zip(valid_indices, predicted_classes):
        if signal == 0:
            label = 'SELL'
        elif signal == 1:
            label = 'HOLD'
        else:
            label = 'BUY'
        full_signals[data_with_features.index.get_loc(idx)] = label

    print(f"len(full_signals): {len(full_signals)}")

    # Translate & position
    raw_signals = full_signals
    translated_signals = translate_raw_signals(raw_signals)
    final_signals = apply_positioning_rule_to_translated_signals(translated_signals)
    final_signals.insert(0, 'HOLD')

    print("✅ Final MLP signals generated successfully!\n")
    return final_signals
