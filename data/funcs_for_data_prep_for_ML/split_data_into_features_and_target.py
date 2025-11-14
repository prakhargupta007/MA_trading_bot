from typing import Sequence


def split_data_into_features_and_target(data, feature_columns: Sequence[str]):
    if not feature_columns:
        raise ValueError("feature_columns cannot be empty when splitting data.")

    cols = list(feature_columns)
    missing = [col for col in cols if col not in data.columns]
    if missing:
        raise KeyError(f"Requested feature columns not found in data: {missing}")

    X = data[cols]
    y = data['Label']
    return X, y
