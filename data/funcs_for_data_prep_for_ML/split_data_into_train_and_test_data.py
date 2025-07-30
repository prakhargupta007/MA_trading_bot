from config import TRAIN_SIZE
def split_data(X, y):
    split_index = int(len(X) * TRAIN_SIZE)
    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]
    return X_train, X_test, y_train, y_test
