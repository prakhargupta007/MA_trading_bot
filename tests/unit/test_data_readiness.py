import json
import os
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import data.fetch_data.fetch_data_from_yfinance as fetch_module
from data.fetch_data.fetch_data_from_yfinance import fetch_data_from_yfinance
from indicators.check_indicator_length import check_indicator_length
from ma_trading_bot import ml_feature_store
from ma_trading_bot.automation_bunch_backtesting.automate_train_and_backtest import (
    build_backtest_data_path,
    build_training_data_path,
)
from ma_trading_bot.automation_bunch_backtesting import config_utils


@pytest.fixture(autouse=True)
def reset_feature_store(monkeypatch):
    # Ensure feature store cache/environment are reset between tests.
    monkeypatch.delenv(ml_feature_store.ENV_VAR_NAME, raising=False)
    ml_feature_store._cached_columns = None
    yield
    monkeypatch.delenv(ml_feature_store.ENV_VAR_NAME, raising=False)
    ml_feature_store._cached_columns = None


# UT-DA-01
@pytest.mark.parametrize("missing_index", [False, True])
def test_fetch_data_handles_trading_day_counts(monkeypatch, missing_index):
    start_date = "2010-01-04"
    end_date = "2020-01-03"
    business_days = pd.date_range(start=start_date, end=end_date, freq="B")

    def fake_download(ticker, start, end, threads=True):
        idx = business_days
        if missing_index:
            idx = idx.delete(5)
        data = pd.DataFrame(
            {
                "Open": np.linspace(1, 2, len(idx)),
                "High": np.linspace(1, 2, len(idx)),
                "Low": np.linspace(1, 2, len(idx)),
                "Close": np.linspace(1, 2, len(idx)),
                "Volume": np.arange(len(idx)) + 100,
            },
            index=idx,
        )
        data.index.name = "Date"
        return data

    monkeypatch.setattr(fetch_module.yf, "download", fake_download)

    df = fetch_data_from_yfinance(
        "TEST",
        False,
        None,
        end_date,
        start_date,
    )

    if missing_index:
        assert len(df) < len(business_days)
        assert len(df) > 0
    else:
        assert len(df) == len(business_days)
        assert df.index.min() == business_days.min()
        assert df.index.max() == business_days.max()


# UT-DA-02
@pytest.mark.parametrize("nan_positions", [[], [0, 1, 2]])
def test_fetch_data_drops_or_flags_missing_close_values(monkeypatch, nan_positions):
    start_date = "2020-01-01"
    end_date = "2020-01-15"
    business_days = pd.date_range(start=start_date, end=end_date, freq="B")

    def fake_download(ticker, start, end, threads=True):
        values = np.arange(len(business_days)) + 10.0
        for pos in nan_positions:
            values[pos] = np.nan
        return pd.DataFrame(
            {
                "Open": values,
                "High": values,
                "Low": values,
                "Close": values,
                "Volume": 1,
            },
            index=business_days,
        )

    monkeypatch.setattr(fetch_module.yf, "download", fake_download)

    df = fetch_data_from_yfinance("TEST", False, None, end_date, start_date)
    expected = len(business_days) - len(nan_positions)
    assert len(df) == expected, "UT-DA-02: NaN rows must be removed"


# UT-DA-02
def test_check_indicator_length_flags_excessive_windows():
    data = pd.DataFrame(
        {"Close": range(5)}, index=pd.date_range("2020-01-01", periods=5, freq="D")
    )
    indicator_parameters = {
        "sma_long_period": 10,
        "sma_short_period": 3,
        "ticker": "TEST",
        "start_date": data.index[0],
        "end_date": data.index[-1],
        "data": data,
    }
    message, good_to_go = check_indicator_length(data, indicator_parameters)
    assert good_to_go is False, "UT-DA-02: oversized indicators must block execution"
    assert "sma_long_period" in message


# UT-DA-03
def test_build_training_data_path_returns_first_match(monkeypatch, tmp_path):
    stored_dir = tmp_path / "data" / "stored_data2"
    stored_dir.mkdir(parents=True)
    first = stored_dir / "data_TEST_train_test_2010.csv"
    second = stored_dir / "data_TEST_train_test_2011.csv"
    first.write_text("train")
    second.write_text("train")

    monkeypatch.chdir(tmp_path)
    path = build_training_data_path("TEST")
    assert Path(path).resolve() == first.resolve()


def test_build_training_data_path_missing_file_raises(monkeypatch, tmp_path):
    (tmp_path / "data" / "stored_data2").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        build_training_data_path("TEST")


def test_build_backtest_data_path_requires_existing_file(monkeypatch, tmp_path):
    stored_dir = tmp_path / "data" / "stored_data2"
    stored_dir.mkdir(parents=True)
    backtest = stored_dir / "data_TEST_backtest_2021.csv"
    backtest.write_text("backtest")

    monkeypatch.chdir(tmp_path)
    assert Path(build_backtest_data_path("TEST")).resolve() == backtest.resolve()


# UT-DA-04
def test_set_runtime_feature_columns_persists_env_and_cache():
    columns = ["feat_a", "feat_b"]
    result = ml_feature_store.set_runtime_feature_columns(columns)
    assert result == columns
    resolved = ml_feature_store.get_active_feature_columns()
    assert resolved == columns
    env_value = os.environ.get(ml_feature_store.ENV_VAR_NAME)
    assert json.loads(env_value) == columns


def test_set_runtime_feature_columns_rejects_empty_lists():
    with pytest.raises(ValueError):
        ml_feature_store.set_runtime_feature_columns([])


def test_get_active_feature_columns_returns_cached_when_env_missing(monkeypatch):
    columns = ["cached"]
    ml_feature_store.set_runtime_feature_columns(columns)
    monkeypatch.delenv(ml_feature_store.ENV_VAR_NAME, raising=False)
    assert ml_feature_store.get_active_feature_columns() == columns


# UT-DA-05
def test_patch_config_values_updates_temp_config(monkeypatch, tmp_path):
    config_file = tmp_path / "config.py"
    config_file.write_text("TRAINING_MODE = False\nVALUE = 1\n")
    monkeypatch.setattr(config_utils, "CONFIG_PATH", config_file)
    config_utils.patch_config_values({"TRAINING_MODE": "True", "VALUE": "42"})
    text = config_file.read_text()
    assert "TRAINING_MODE = True" in text
    assert "VALUE = 42" in text


def test_temporary_training_mode_restores_previous_value(monkeypatch):
    stub_config = SimpleNamespace(TRAINING_MODE=False)
    applied_states = []

    def fake_patch(updates):
        applied_states.append(updates)
        if "TRAINING_MODE" in updates:
            stub_config.TRAINING_MODE = updates["TRAINING_MODE"] == "True"

    monkeypatch.setattr(config_utils, "config_module", stub_config)
    monkeypatch.setattr(config_utils, "patch_config_values", fake_patch)
    monkeypatch.setattr(config_utils, "reload_config", lambda: stub_config)

    with pytest.raises(RuntimeError):
        with config_utils.temporary_training_mode(True):
            assert stub_config.TRAINING_MODE is True
            raise RuntimeError("boom")

    assert stub_config.TRAINING_MODE is False
    assert applied_states[0]["TRAINING_MODE"] == "True"
    assert applied_states[-1]["TRAINING_MODE"] == "False"
