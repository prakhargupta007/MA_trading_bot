"""
Load trained ML artifacts and compute evaluation metrics on the held-out set.

Used by automation to embed condensed metrics into summary outputs. Behaviour
matches existing training data preparation paths.
"""

import importlib
from typing import Optional, Sequence

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from .config_utils import temporary_training_mode
from ma_trading_bot.ml_feature_store import resolve_feature_columns

WITH_SCALING_STRATEGIES = {"logistic_regression", "mlp"}
WITHOUT_SCALING_STRATEGIES = {"random_forest", "xgboost"}

def _load_model_bundle(strategy_name, artifact_path: Optional[str] = None):
    # Map strategy -> model_name & model path var in config
    cfg = importlib.import_module("config")
    if artifact_path is None:
        if strategy_name == "logistic_regression":
            artifact_path = cfg.LOG_REG_MODEL_PATH_FOR_STRATEGY
        elif strategy_name == "random_forest":
            artifact_path = cfg.RANDOM_FOREST_MODEL_PATH_FOR_STRATEGY
        elif strategy_name == "xgboost":
            artifact_path = cfg.XGBOOST_MODEL_PATH_FOR_STRATEGY
        elif strategy_name == "mlp":
            artifact_path = cfg.MLP_MODEL_PATH_FOR_STRATEGY
        else:
            raise ValueError(f"Unknown ML strategy: {strategy_name}")

    if artifact_path is None:
        raise ValueError(f"Unknown ML strategy: {strategy_name}")

    bundle = joblib.load(artifact_path)
    # Allow either {'model':..., 'scaler':...} or a bare model
    model = bundle["model"] if isinstance(bundle, dict) and "model" in bundle else bundle
    scaler = bundle.get("scaler") if isinstance(bundle, dict) else None
    return model, scaler

def _load_train_test_data(
    strategy_name,
    training_csv: Optional[str] = None,
    feature_columns: Optional[Sequence[str]] = None,
):
    # Use the same preparation path that the corresponding training script used.
    cfg = importlib.import_module("config")
    data_path = training_csv or cfg.DATA_FOR_ML_MODEL_TRAINING
    data = pd.read_csv(data_path, index_col="Date", parse_dates=True)

    resolved_columns = resolve_feature_columns(feature_columns)

    if strategy_name in WITH_SCALING_STRATEGIES:
        prep_mod = importlib.import_module("data.prepare_data_with_scaling")
        X_train, X_test, y_train, y_test, *_ = prep_mod.prepare_data_with_scaling(
            data, resolved_columns
        )
    elif strategy_name in WITHOUT_SCALING_STRATEGIES:
        prep_mod = importlib.import_module("data.prepare_data_without_scaling")
        X_train, X_test, y_train, y_test, *_ = prep_mod.prepare_data_without_scaling(
            data, resolved_columns
        )
    else:
        raise ValueError(f"Unsupported strategy for metrics: {strategy_name}")

    return X_test, y_test

def compute_ml_metrics_condensed(
    strategy_name: str,
    ticker: str,
    *,
    training_csv: Optional[str] = None,
    feature_columns: Optional[Sequence[str]] = None,
    model_artifact_path: Optional[str] = None,
):
    """
    Returns:
      dict with Accuracy, Precision, Recall, F1, Confusion_Matrix (string like '[[.. .. ..] ...]')
    """
    with temporary_training_mode(True):
        model, _ = _load_model_bundle(strategy_name, artifact_path=model_artifact_path)
        X_test, y_test = _load_train_test_data(
            strategy_name, training_csv=training_csv, feature_columns=feature_columns
        )

    # Probability thresholding is supported in your training script; here we use plain predict for comparability
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=[0,1,2])

    cm_str = "[" + "; ".join(" ".join(map(str, row)) for row in cm.tolist()) + "]"
    # The above prints as "[a b c; d e f; g h i]" which is compact for Excel.
    # If you prefer the classic [[a b c],[d e f],[g h i]] look, uncomment next line:
    # cm_str = str(cm.tolist())

    return {
        "Accuracy": f"{acc:.4f}",
        "Precision": f"{prec:.4f}",
        "Recall": f"{rec:.4f}",
        "F1": f"{f1:.4f}",
        "Confusion_Matrix": cm_str
    }
