from data.funcs_for_data_prep_for_ML.split_data_into_features_and_target import split_data_into_features_and_target
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data  
from data.funcs_for_data_prep_for_ML.label_data_with_threshold import label_data_with_threshold   
from data.funcs_for_data_prep_for_ML.split_data_into_train_and_test_data import split_data_into_train_and_test_data
from data.funcs_for_data_prep_for_ML.scale_features import scale_features

def prepare_data(data):
    data_with_features = calculate_and_add_features_to_data(data)
    print('features added to data\n',data_with_features.head(),'\n\n\n')

    data_with_labels = label_data_with_threshold(data_with_features)
    print('labels added to data\n',data_with_labels.head(),'\n\n\n')

    X, y = split_data_into_features_and_target(data_with_labels)
    print('features and labels split\n\nfeatures:\n',X.head(),'\n\n\nlabels:\n', y.head(),'\n\n\n')

    X_train, X_test, y_train, y_test = split_data_into_train_and_test_data(X, y)
    print('data split into train and test\nX_train:\n',X_train.head(),'\n\n\nX_test:\n', X_test.head(),'\n\n\ny_train:\n', y_train.head(),'\n\n\ny_test\n', y_test.head(),'\n\n\n')

    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
    print('features scaled\nX_train_scaled\n',X_train_scaled[:5],'\n\n\nX_test_scaled\n', X_test_scaled[:5],'\n\n\n')

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler
