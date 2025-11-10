import importlib
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from automation_bunch_backtesting.config_utils import temporary_training_mode

WITH_SCALING_STRATEGIES = {"logistic_regression", "mlp"}
WITHOUT_SCALING_STRATEGIES = {"random_forest", "xgboost"}

def _load_model_bundle(strategy_name):
    # Map strategy -> model_name & model path var in config
    cfg = importlib.import_module("config")
    if strategy_name == "logistic_regression":
        artifact_path = cfg.LOG_REG_MODEL_PATH_FOR_STRATEGY
    elif strategy_name == "random_forest":
        artifact_path = cfg.RANDOM_FOREST_MODEL_PATH_FOR_STRATEGY
    elif strategy_name == "xgboost":
        artifact_path = cfg.XGBOOST_MODEL_PATH_FOR_STRATEGY
    elif strategy_name == "xgboost":
        artifact_path = cfg.XGBOOST_MODEL_PATH_FOR_STRATEGY
    elif strategy_name == "mlp":
        artifact_path = cfg.MLP_MODEL_PATH_FOR_STRATEGY
    else:
        raise ValueError(f"Unknown ML strategy: {strategy_name}")
    bundle = joblib.load(artifact_path)
    # Allow either {'model':..., 'scaler':...} or a bare model
    model = bundle["model"] if isinstance(bundle, dict) and "model" in bundle else bundle
    scaler = bundle.get("scaler") if isinstance(bundle, dict) else None
    return model, scaler

def _load_train_test_data(strategy_name):
    # Use the same preparation path that the corresponding training script used.
    cfg = importlib.import_module("config")
    data = pd.read_csv(cfg.DATA_FOR_ML_MODEL_TRAINING, index_col="Date", parse_dates=True)

    if strategy_name in WITH_SCALING_STRATEGIES:
        prep_mod = importlib.import_module("data.prepare_data_with_scaling")
        X_train, X_test, y_train, y_test, *_ = prep_mod.prepare_data_with_scaling(data)
    elif strategy_name in WITHOUT_SCALING_STRATEGIES:
        prep_mod = importlib.import_module("data.prepare_data_without_scaling")
        X_train, X_test, y_train, y_test, *_ = prep_mod.prepare_data_without_scaling(data)
    else:
        raise ValueError(f"Unsupported strategy for metrics: {strategy_name}")

    return X_test, y_test

def compute_ml_metrics_condensed(strategy_name: str, ticker: str):
    """
    Returns:
      dict with Accuracy, Precision, Recall, F1, Confusion_Matrix (string like '[[.. .. ..] ...]')
    """
    with temporary_training_mode(True):
        model, _ = _load_model_bundle(strategy_name)
        X_test, y_test = _load_train_test_data(strategy_name)

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
