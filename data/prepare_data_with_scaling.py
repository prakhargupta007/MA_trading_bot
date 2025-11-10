from data.funcs_for_data_prep_for_ML.split_data_into_features_and_target import split_data_into_features_and_target
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data  
from data.funcs_for_data_prep_for_ML.label_data_with_future_window import label_data_with_future_window
from data.funcs_for_data_prep_for_ML.split_data_into_train_and_test_data import split_data_into_train_and_test_data
from data.funcs_for_data_prep_for_ML.scale_features import scale_features
from config import LOOKAHEAD_DAYS
from config import GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH

def prepare_data_with_scaling(data):
    data_with_features = calculate_and_add_features_to_data(data,GSPC_DATA_FILE_PATH, NDX_DATA_FILE_PATH, VIX_DATA_FILE_PATH)
    print('features added to data\n', data_with_features.head(), '\n\n\n')

    data_with_labels = label_data_with_future_window(data_with_features,LOOKAHEAD_DAYS)
    print('labels added to data\n', data_with_labels.head(), '\n\n\n')

    X, y = split_data_into_features_and_target(data_with_labels)
    print('features and labels split\nfeatures:\n', X.head(), '\n\n\nlabels:\n', y.head(), '\n\n\n')
    feature_names = list(X.columns)
    print(f'feature_names:\n{feature_names}')

    X_train, X_test, y_train, y_test = split_data_into_train_and_test_data(X, y)
    print('data split into train and test\nX_train:\n', X_train.head(), '\n\n\nX_test:\n', X_test.head(), '\n\n\ny_train:\n', y_train.head(), '\n\n\ny_test\n', y_test.head(), '\n\n\n')


    print("Number of NaN values in training features:", X_train.isna().sum().sum())
    print("Number of NaN values in test features:", X_test.isna().sum().sum())
    print("NaN ratio per feature column (train):")
    print(X_train.isna().mean().sort_values(ascending=False).head(15))
    print("NaN ratio per feature column (test):")
    print(X_test.isna().mean().sort_values(ascending=False).head(15))


    # Remove potentially missing values (=NanNs) from data as ML models get confused by them
    # Clean out NaNs here BEFORE scaling, becuase scalars don't like NaNs
    train_mask = ~(X_train.isnull().any(axis=1) | y_train.isnull())
    test_mask = ~(X_test.isnull().any(axis=1) | y_test.isnull())

    X_train = X_train[train_mask]
    y_train = y_train[train_mask]
    X_test = X_test[test_mask]
    y_test = y_test[test_mask]

    print(f"After cleaning: {len(X_train)} training rows, {len(X_test)} test rows remaining")
    print("Number of NaN values in cleaned training features:", X_train.isna().sum().sum())

    if len(X_train) == 0 or len(X_test) == 0:
        raise ValueError(
            f"[ERROR] After cleaning, dataset is empty (X_train={len(X_train)}, X_test={len(X_test)}). "
            "Check your feature generation logic or external data alignment."
        )

    # Now scale clean data
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
    print('features scaled\nX_train_scaled\n', X_train_scaled[:5], '\n\n\nX_test_scaled\n', X_test_scaled[:5], '\n\n\n')

    return X_train_scaled, X_test_scaled, y_train.astype(int), y_test.astype(int), scaler, feature_names 
