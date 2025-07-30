from config import FEATURE_COLUMNS
def split_data_into_features_and_target(data):
    # Split the data into features (X) and target (Y)
    X = data[FEATURE_COLUMNS]
    y = data['Label']
    return X, y

