import joblib
import pandas as pd
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data
from ML.ML_strategy.processing_steps_for_signal_generation.translate_raw_signals import translate_raw_signals
from ML.ML_strategy.processing_steps_for_signal_generation.apply_positioning_rule_to_translated_signals import apply_positioning_rule_to_translated_signals
from ML.ML_strategy.processing_steps_for_signal_generation.load_model_and_scaler import load_model_and_scaler
from config import FEATURE_COLUMNS

def logistic_regression_strategy(data, **kwargs):
    # load model and scaler
    model, scaler = load_model_and_scaler('ML/saved_models/lr_model_with_scaler_AAPL.joblib')


    # Load the data and preprocess it
    #data = pd.read_csv("/Users/prakhar/MA_trading_bot/data/data_AAPL_2020-2025.csv", index_col="Date", parse_dates=True)
    #print('\nSample data of AAPL from 2020 to 2025, which is stored locally is being used')

    data_with_features = calculate_and_add_features_to_data(data)
    data_with_features = data_with_features[FEATURE_COLUMNS]

    # Keep only rows where all feature values are present (no NaNs)

    # valid_rows_mask is a list (actually a pandas Series) that marks which rows are safe for your model, where all required indicators are calculated. Basically: rows without NaNs
    valid_rows_mask = data_with_features.notnull().all(axis=1)
    
    valid_data = data_with_features[valid_rows_mask]


    X_new_scaled = scaler.transform(valid_data)
    predicted_signals = model.predict(X_new_scaled)

    # Fill 'HOLD' for invalid rows, and insert predictions where available
    full_signals = ['HOLD'] * len(data_with_features)
    valid_indices = data_with_features[valid_rows_mask].index
    for idx, signal in zip(valid_indices, predicted_signals):
        full_signals[data_with_features.index.get_loc(idx)] = signal

    raw_signals = full_signals
    translated_signals = translate_raw_signals(raw_signals)
    final_signals = apply_positioning_rule_to_translated_signals(translated_signals)

    final_signals.insert(0, 'HOLD')  
    print('Final signals of ML model have been generated!\n\n')

    return final_signals
