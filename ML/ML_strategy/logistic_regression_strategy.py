import joblib
import pandas as pd
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data
from ML.ML_strategy.processing_steps_for_signal_generation.translate_raw_signals import translate_raw_signals
from ML.ML_strategy.processing_steps_for_signal_generation.apply_positioning_rule_to_translated_signals import apply_positioning_rule_to_translated_signals
from config import FEATURE_COLUMNS

def logistic_regression_strategy(data, **kwargs):
    # load model and scaler
    model_bundle = joblib.load('ML/saved_models/lr_model_with_scaler_AAPL.joblib')
    model = model_bundle['model']
    scaler = model_bundle['scaler']

    # Load the data and preprocess it
    #data = pd.read_csv("/Users/prakhar/MA_trading_bot/data/data_AAPL_2020-2025.csv", index_col="Date", parse_dates=True)
    #print('\nSample data of AAPL from 2020 to 2025, which is stored locally is being used')

    data_with_features = calculate_and_add_features_to_data(data)
    data_with_features = data_with_features[FEATURE_COLUMNS]
    X_new_scaled = scaler.transform(data_with_features)
    predicted_signals = model.predict(X_new_scaled)
    raw_signals = predicted_signals.tolist()

    translated_signals = translate_raw_signals(raw_signals)
    final_signals = apply_positioning_rule_to_translated_signals(translated_signals)

    # Currently signal on dax x is actuaally action signal for day x+1, so to fix that...
    # --> Insert 'HOLD' at the beginning to avoid lookahead bias and make signals logical.
    final_signals.insert(0, 'HOLD')  
    print('Final signals of ML model have been generated!\n\n')

    return final_signals