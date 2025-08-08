from data.funcs_for_data_prep_for_ML.split_data_into_features_and_target import split_data_into_features_and_target
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data  
from data.funcs_for_data_prep_for_ML.single_day_label_data_with_threshold import label_data_with_threshold   
from data.funcs_for_data_prep_for_ML.label_data_with_future_window import label_data_with_future_window
from data.funcs_for_data_prep_for_ML.split_data_into_train_and_test_data import split_data_into_train_and_test_data

# The only differnce to prepare_data_with_scaling is that this function does not scale the data, 
# because it is not required for random forest and would otherwise lead to inefficient training and computational wastage 

def prepare_data_without_scaling(data):
    data_with_features = calculate_and_add_features_to_data(data)
    print('features added to data\n', data_with_features.head(), '\n\n\n')

    data_with_labels = label_data_with_future_window(data_with_features)
    print('labels added to data\n', data_with_labels.head(), '\n\n\n')

    X, y = split_data_into_features_and_target(data_with_labels)
    print('features and labels split\n\nfeatures:\n', X.head(), '\n\n\nlabels:\n', y.head(), '\n\n\n')

    feature_names = list(X.columns)

    X_train, X_test, y_train, y_test = split_data_into_train_and_test_data(X, y)
    print('data split into train and test\nX_train:\n', X_train.head(), '\n\n\nX_test:\n', X_test.head(), '\n\n\ny_train:\n', y_train.head(), '\n\n\ny_test\n', y_test.head(), '\n\n\n')

    # Remove potentially missing values (=NaNs) from data as ML models get confused by them
    train_mask = ~(X_train.isnull().any(axis=1) | y_train.isnull())
    test_mask = ~(X_test.isnull().any(axis=1) | y_test.isnull())

    X_train = X_train[train_mask]
    y_train = y_train[train_mask]
    X_test = X_test[test_mask]
    y_test = y_test[test_mask]

    # Return unscaled data
    return X_train, X_test, y_train, y_test, feature_names
