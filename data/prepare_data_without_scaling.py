from data.funcs_for_data_prep_for_ML.split_data_into_features_and_target import split_data_into_features_and_target
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data    
from data.funcs_for_data_prep_for_ML.label_data_with_future_window import label_data_with_future_window
from data.funcs_for_data_prep_for_ML.split_data_into_train_and_test_data import split_data_into_train_and_test_data
from config import LOOKAHEAD_DAYS
from config import GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH
def prepare_data_without_scaling(data):
    # Add features to the raw data
    data_with_features = calculate_and_add_features_to_data(data,GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH)

    # Label the data based on future price movement
    data_with_labels = label_data_with_future_window(data_with_features,LOOKAHEAD_DAYS)

    # Drop any rows that have NaNs anywhere, so training data is clean
    data_clean = data_with_labels.dropna()

    # Split clean data into features (X) and target labels (y)
    X, y = split_data_into_features_and_target(data_clean)
    feature_names = list(X.columns)

    # Split features and labels into training and testing sets
    X_train, X_test, y_train, y_test = split_data_into_train_and_test_data(X, y)

    # Warn if training or testing sets are too small
    if len(X_train) < 200:
        print("[WARNING]!!! Training set size is suspiciously small:", len(X_train))
    if len(X_test) < 50:
        print(f"[WARNING]!! Test set size is suspiciously small: {len(X_test)}")

    return X_train, X_test, y_train, y_test, feature_names
