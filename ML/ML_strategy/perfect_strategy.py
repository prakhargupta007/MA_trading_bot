from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data  
from data.funcs_for_data_prep_for_ML.single_day_label_data_with_threshold import label_data_with_threshold
from data.funcs_for_data_prep_for_ML.label_data_with_future_window import label_data_with_future_window
from ML.ML_strategy.processing_steps_for_signal_generation.translate_raw_signals import translate_raw_signals
from ML.ML_strategy.processing_steps_for_signal_generation.apply_positioning_rule_to_translated_signals import apply_positioning_rule_to_translated_signals
import pandas as pd
from config import GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH
# Because for this strategy we also need the NaN signal values that the labeling function generates, the NaN values don't get dropped in that function.
def perfect_strategy(data, **kwargs):
    print(f"Original input data: {len(data)}")

    data_with_features = calculate_and_add_features_to_data(data,GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH)
    print(f"After feature calculation: {len(data_with_features)}")

    #data_with_labels = label_data_with_threshold(data_with_features)
    data_with_labels = label_data_with_future_window(data_with_features)
    print(f"After labeling: {len(data_with_labels)}")

    raw_signals = data_with_labels['Label'].tolist()
    print(f"Length of raw signals: {len(raw_signals)}")
    # Replace NaN values with 'HOLD' to ensure all signals are valid
    raw_signals = [signal if pd.notnull(signal) else 'HOLD' for signal in raw_signals]

    translated_signals = translate_raw_signals(raw_signals)
    final_signals = apply_positioning_rule_to_translated_signals(translated_signals)
    final_signals.insert(0, 'HOLD')  # for alignment

    print(f"Length of final signals: {len(final_signals)}")
    print('Final ideal perfect signals of ML model have been generated!\n\n')

    return final_signals
