from data.funcs_for_data_prep_for_ML.split_data_into_features_and_target import split_data_into_features_and_target
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data    
from data.funcs_for_data_prep_for_ML.label_data_with_future_window import label_data_with_future_window
from data.funcs_for_data_prep_for_ML.split_data_into_train_and_test_data import split_data_into_train_and_test_data


def prepare_data_without_scaling(data):
    # Add features to the raw data
    data_with_features = calculate_and_add_features_to_data(data)

    # Label the data based on future price movement
    data_with_labels = label_data_with_future_window(data_with_features)

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


'''
def prepare_data_without_scaling(data):
    print("Step 0 raw:", data.shape)

    # Add features
    data_with_features = calculate_and_add_features_to_data(data)
    print("Step 1 features:", data_with_features.shape)
    print(data_with_features.head())

    # Label data
    data_with_labels = label_data_with_future_window(data_with_features)
    print("Step 2 labels:", data_with_labels.shape)
    print(data_with_labels.head())

    # Drop NaNs
    data_clean = data_with_labels.dropna()
    print("Step 3 after dropna:", data_clean.shape)

    # Split
    X, y = split_data_into_features_and_target(data_clean)
    print("Step 4 features/target:", X.shape, y.shape)
    feature_names = list(X.columns)

    # Split train/test
    X_train, X_test, y_train, y_test = split_data_into_train_and_test_data(X, y)
    print("Step 5 train/test:", X_train.shape, X_test.shape, y_train.shape, y_test.shape)

    print("NaNs in X_train:\n", X_train.isnull().sum().sort_values(ascending=False).head(20))
    print("NaNs in y_train:", y_train.isnull().sum())

    return X_train, X_test, y_train, y_test, feature_names
'''