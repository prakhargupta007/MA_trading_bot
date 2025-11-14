import joblib
import pandas as pd
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data
from ML.ML_strategy.processing_steps_for_signal_generation.translate_raw_signals import translate_raw_signals
from ML.ML_strategy.processing_steps_for_signal_generation.apply_positioning_rule_to_translated_signals import apply_positioning_rule_to_translated_signals
from ML.ML_strategy.processing_steps_for_signal_generation.load_model_and_scaler_if_existant import load_model_and_scaler_if_existant
from config import RANDOM_FOREST_MODEL_PATH_FOR_STRATEGY
from config import GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH
from ma_trading_bot.ml_feature_store import resolve_feature_columns
def random_forest_strategy(data, **kwargs):
    model, scaler = load_model_and_scaler_if_existant(RANDOM_FOREST_MODEL_PATH_FOR_STRATEGY)
    feature_columns = resolve_feature_columns(kwargs.get("feature_columns"))

    data_with_features = calculate_and_add_features_to_data(
        data, GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH, feature_columns
    )
    data_with_features = data_with_features[feature_columns]
    print(f"len(data_with_features): {len(data_with_features)}")

    valid_rows_mask = data_with_features.notnull().all(axis=1)
    valid_data = data_with_features[valid_rows_mask]
    print(f"Number of valid rows: {valid_rows_mask.sum()}")  # Number of non-NaN rows

    X_new_scaled = valid_data
    predicted_signals = model.predict(X_new_scaled)
    print(f"len(predicted_signals): {len(predicted_signals)}")  # Matches valid rows

    full_signals = ['HOLD'] * len(data_with_features)
    valid_indices = data_with_features[valid_rows_mask].index
    for idx, signal in zip(valid_indices, predicted_signals):
        full_signals[data_with_features.index.get_loc(idx)] = signal
    print(f"len(full_signals): {len(full_signals)}") 

    raw_signals = full_signals
    translated_signals = translate_raw_signals(raw_signals)
    print(f"len(translated_signals): {len(translated_signals)}")  # Check for change

    final_signals = apply_positioning_rule_to_translated_signals(translated_signals)
    print(f"len(final_signals) before insert: {len(final_signals)}")  

    final_signals.insert(0, 'HOLD')
    print(f"len(final_signals) after insert: {len(final_signals)}") 
    print('Final signals of ML model have been generated!\n\n')
    return final_signals
