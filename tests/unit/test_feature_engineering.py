import numpy as np
import pandas as pd
import pytest

import config
from data.prepare_data_with_scaling import prepare_data_with_scaling
from data.prepare_data_without_scaling import prepare_data_without_scaling
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import (
    calculate_and_add_features_to_data,
)
from data.funcs_for_data_prep_for_ML.label_data_with_future_window import (
    label_data_with_future_window,
)
from data.funcs_for_data_prep_for_ML.split_data_into_features_and_target import (
    split_data_into_features_and_target,
)
from data.funcs_for_data_prep_for_ML.split_data_into_train_and_test_data import (
    split_data_into_train_and_test_data,
)
from data.funcs_for_data_prep_for_ML.generate_sentiment_score_feature_list import (
    generate_sentiment_score_feature_list,
)
from ma_trading_bot import ml_feature_store


def _make_price_frame(length: int) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=length, freq="D")
    close = np.linspace(100, 150, length) + np.sin(np.linspace(0, 3, length))
    volume = np.linspace(1_000, 2_000, length)
    return pd.DataFrame(
        {
            "Date": dates,
            "Close": close,
            "High": close + 1,
            "Low": close - 1,
            "Volume": volume,
        }
    )


@pytest.fixture(autouse=True)
def reset_feature_store(monkeypatch):
    monkeypatch.delenv(ml_feature_store.ENV_VAR_NAME, raising=False)
    ml_feature_store._cached_columns = None
    yield
    monkeypatch.delenv(ml_feature_store.ENV_VAR_NAME, raising=False)
    ml_feature_store._cached_columns = None


# UT-FE-01
def test_indicator_features_only_use_past_candles():
    feature_cols = ["sma_diff_pct_10d"]
    ml_feature_store.set_runtime_feature_columns(feature_cols)
    data = _make_price_frame(25)

    first_run = calculate_and_add_features_to_data(
        data.iloc[:15].copy(), "unused_gspc.csv", "unused_ndx.csv", "unused_vix.csv", feature_cols
    )
    second_run = calculate_and_add_features_to_data(
        data.iloc[:16].copy(), "unused_gspc.csv", "unused_ndx.csv", "unused_vix.csv", feature_cols
    )

    # Feature at index 14 must remain unchanged when adding later data.
    idx = pd.to_datetime(data["Date"].iloc[14])
    assert first_run.loc[idx, "sma_diff_pct_10d"] == second_run.loc[idx, "sma_diff_pct_10d"]


# UT-FE-02
def test_features_share_index_and_scaling_removes_nan(monkeypatch):
    feature_cols = ["momentum_10", "volume_20d_ma"]
    ml_feature_store.set_runtime_feature_columns(feature_cols)
    data = _make_price_frame(80)

    features_df = calculate_and_add_features_to_data(
        data.copy(), "unused_gspc.csv", "unused_ndx.csv", "unused_vix.csv", feature_cols
    )
    assert features_df.index.equals(pd.to_datetime(data["Date"]))

    prepared = prepare_data_with_scaling(data.copy())
    X_train, X_test, y_train, y_test, _, _ = prepared
    assert len(X_train) == len(y_train) and len(X_test) == len(y_test)
    assert not np.isnan(X_train).any()
    assert not np.isnan(X_test).any()

    # Verify StandardScaler produced zero-mean/unit-variance columns on training data.
    train_mean = X_train.mean(axis=0)
    train_std = X_train.std(axis=0)
    assert np.allclose(train_mean, 0.0, atol=1e-7)
    assert np.allclose(train_std, 1.0, atol=1e-7)

    # Manual clean length should match scaled rows.
    labeled = label_data_with_future_window(features_df.copy(), lookahead_days=5)
    X_full, y_full = split_data_into_features_and_target(labeled, feature_cols)
    mask = ~(X_full.isnull().any(axis=1) | y_full.isnull())
    expected_rows = mask.sum()
    assert expected_rows == len(X_train) + len(X_test)


# UT-FE-03
def test_label_data_alignment_and_insufficient_future_detection():
    dates = pd.date_range("2021-01-01", periods=12, freq="D")
    prices = pd.DataFrame({"Close": np.linspace(100, 120, len(dates))}, index=dates)
    labeled = label_data_with_future_window(prices.copy(), lookahead_days=3)
    assert labeled.index.equals(prices.index)
    assert labeled["Label"].iloc[:3].notna().all()
    assert labeled["Label"].iloc[-3:].isna().all()

    short_prices = pd.DataFrame({"Close": [1.0, 1.1]}, index=pd.date_range("2022-01-01", periods=2))
    short_labeled = label_data_with_future_window(short_prices.copy(), lookahead_days=5)
    assert short_labeled["Label"].isna().all()


# UT-FE-04
def test_split_functions_align_indices_and_require_features():
    df = pd.DataFrame(
        {
            "feat1": [1, 2, 3, 4],
            "feat2": [4, 3, 2, 1],
            "Label": [0, 1, 0, 1],
        }
    )
    X, y = split_data_into_features_and_target(df, ["feat1", "feat2"])
    assert list(X.index) == list(y.index)
    X_train, X_test, y_train, y_test = split_data_into_train_and_test_data(X, y)
    assert len(X_train) + len(X_test) == len(X)
    assert len(y_train) + len(y_test) == len(y)

    with pytest.raises(KeyError):
        split_data_into_features_and_target(df, ["missing_feature"])


# UT-FE-05
def test_preparation_paths_handle_zero_variance_and_empty_sets():
    feature_cols = ["sma_50"]
    ml_feature_store.set_runtime_feature_columns(feature_cols)
    constant_data = _make_price_frame(90)
    constant_data["Close"] = 100.0

    with pytest.raises(ValueError):
        prepare_data_with_scaling(constant_data.copy())

    ml_feature_store.set_runtime_feature_columns(["momentum_10"])
    short_data = _make_price_frame(8)
    with pytest.raises(ValueError):
        prepare_data_without_scaling(short_data.copy())


# UT-FE-06
def test_sentiment_feature_alignment_and_fill(monkeypatch, tmp_path):
    target_index = pd.date_range("2023-01-01", periods=5, freq="D")
    sentiment_path = tmp_path / "sentiment.csv"
    sentiment_path.write_text(
        "day,prob_positive,prob_negative\n"
        "2023-01-01,0.7,0.1\n"
        "2023-01-03,0.5,0.3\n"
    )

    series = generate_sentiment_score_feature_list(target_index, sentiment_path)
    assert series.index.equals(target_index)
    assert series.iloc[0] == pytest.approx(0.6)
    assert np.isnan(series.iloc[1])

    bad_path = tmp_path / "invalid.csv"
    bad_path.write_text("day,prob_positive\n2023-01-01,0.5\n")
    with pytest.raises(KeyError):
        generate_sentiment_score_feature_list(target_index, bad_path)

    ml_feature_store.set_runtime_feature_columns(["sentiment_score"])
    monkeypatch.setattr(config, "SENTIMENT_DATA_PATH_FOR_ML_MODEL_TRAINING_FEATURE", str(sentiment_path))
    monkeypatch.setattr(config, "TECH_SECTOR_STOCK", False)

    data = _make_price_frame(5)
    enriched = calculate_and_add_features_to_data(
        data.copy(), "unused_gspc.csv", "unused_ndx.csv", "unused_vix.csv", ["sentiment_score"]
    )
    assert "sentiment_score" in enriched.columns
    # Sentiment should be forward-filled and remaining NaNs replaced with 0.
    assert enriched["sentiment_score"].iloc[1] == pytest.approx(0.6)
    assert enriched["sentiment_score"].iloc[-1] == pytest.approx((0.5 - 0.3))
