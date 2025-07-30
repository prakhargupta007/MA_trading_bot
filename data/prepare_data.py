from funcs_for_data_prep_for_ML import split_data_into_features_and_target
from data.funcs_for_data_prep_for_ML import calculate_and_add_features_to_data  
from data.funcs_for_data_prep_for_ML import label_data_with_threshold   
from data.funcs_for_data_prep_for_ML import split_data_into_train_and_test_data
from data.funcs_for_data_prep_for_ML import scale_features

def prepare_data(data):
    data_with_features = calculate_and_add_features_to_data(data)
    data_with_labels = label_data_with_threshold(data_with_features)
    X, y = split_data_into_features_and_target(data_with_labels)
    X_train, X_test, y_train, y_test = split_data_into_train_and_test_data(X, y)
    X_train_scaled, X_test_scaled = scale_features(X_train, X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test
