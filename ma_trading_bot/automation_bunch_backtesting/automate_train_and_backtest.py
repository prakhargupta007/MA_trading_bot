
"""
Automation runner to train ML models and backtest strategies in batch.

Run via: python3 -m ma_trading_bot.automation_bunch_backtesting.automate_train_and_backtest
Behaviour preserved; this module mutates config.py on disk to drive child processes.
"""

import os
import sys
import json
import time
import shutil
import traceback
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

from ma_trading_bot.backtest.create_and_save_backtest_summary_table_csv_file import (
    apply_summary_excel_formatting,
)

from .config_utils import patch_config_values
from ma_trading_bot.ml_feature_store import set_runtime_feature_columns

ML_STRATEGIES = {
    "logistic_regression": {
        "model_name": "lr",
        "train_cmd": "python3 -m ML.train_models.train_logistic_regression",
    },
    "random_forest": {
        "model_name": "rf",
        "train_cmd": "python3 -m ML.train_models.train_random_forest",
    },
    "xgboost": {
        "model_name": "xgb",
        "train_cmd": "python3 -m ML.train_models.train_xgboost",
    },
    "mlp": {
        "model_name": "mlp",
        "train_cmd": "python3 -m ML.train_models.train_mlp",
    },
}

RULE_STRATEGIES = {
    "sma",
    "ema",
    "sma_rsi",
    "ema_rsi",
    "sma_rsi_macd",
    "sentiment_strategy",
    "buy_and_hold",
}

BUY_AND_HOLD_STRATEGY_NAME = "buy_and_hold"

MODEL_PATH_KEYS = {
    "logistic_regression": "LOG_REG_MODEL_PATH_FOR_STRATEGY",
    "random_forest": "RANDOM_FOREST_MODEL_PATH_FOR_STRATEGY",
    "xgboost": "XGBOOST_MODEL_PATH_FOR_STRATEGY",
    "mlp": "MLP_MODEL_PATH_FOR_STRATEGY",
}

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parents[2]

# Detect the project root (directory that contains config.py)
project_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(project_root, ".."))

# ----------------------------
# Helpers
# ----------------------------
def load_json(p):
    with open(p, "r") as f:
        return json.load(f)

def ensure_dirs(*dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def log(msg, log_path):
    print(msg, flush=True)
    with open(log_path, "a") as f:
        f.write(msg + "\n")

def file_url(path_str):
    """Return a project-relative path for display in Excel/CSV."""
    if not path_str:
        return ""
    p = Path(path_str).resolve()
    try:
        rel = p.relative_to(PROJECT_ROOT)
    except ValueError:
        rel = p
    return str(rel)

def set_feature_columns(columns):
    """
    Activate feature columns for downstream ML processes.
    """
    set_runtime_feature_columns(columns)


def build_model_path(model_prefix: str, ticker: str, model_number: str, base_dir: Path) -> str:
    filename = f"{model_prefix}_model_{ticker}_{model_number}.joblib"
    return str((base_dir / filename).resolve())

def build_training_data_path(ticker):
    # Uses your existing pattern for training CSVs
    # Example from your config: data/stored_data2/data_{TICKER}_train_test_2012-05-18--2020-12-31.csv
    # We’ll look up the first matching file in stored_data2 for that ticker.
    folder = Path("data/stored_data2")
    candidates = sorted(folder.glob(f"data_{ticker}_train_test_*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No training data CSV found for {ticker} in {folder}")
    return str(candidates[0])

def build_backtest_data_path(ticker):
    # Uses your USE_STORED_DATA path convention
    folder = Path("data/stored_data2")
    candidates = sorted(folder.glob(f"data_{ticker}_backtest_*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No backtest data CSV found for {ticker} in {folder}")
    return str(candidates[0])

def run_cmd(cmd, log_path):
    import sys
    adjusted_cmd = cmd
    stripped = cmd.lstrip()
    if stripped.startswith("python3 "):
        adjusted_cmd = f"{sys.executable} {stripped[len('python3 '):]}"
    elif stripped == "python3":
        adjusted_cmd = sys.executable
    log(f"$ {adjusted_cmd}", log_path)
    result = subprocess.run(adjusted_cmd, shell=True)
    if result.returncode != 0:
        log(f"[WARN] Command failed with exit code {result.returncode}: {adjusted_cmd}", log_path)
        return False
    return True

def latest_summary_csv(summary_dir, ticker):
    # Your summary function writes: summary_backtest_table_{TICKERS}.csv
    # During automation we set TICKERS to a single ticker string.
    p = Path(summary_dir) / f"summary_backtest_table_{ticker}.csv"
    if not p.exists():
        # If user had a different path, try to locate newest matching
        candidates = sorted(Path(summary_dir).glob(f"summary_backtest_table_{ticker}*.csv"), key=os.path.getmtime)
        if not candidates:
            raise FileNotFoundError(f"Cannot find backtest summary CSV for {ticker} in {summary_dir}")
        return str(candidates[-1])
    return str(p)

def infer_plot_path(final_plots_dir, ticker, strategy):
    # Matches your plotly naming: f"{ticker}_{chosen_strategy}_strategy_plot.html"
    # chosen_strategy is upper() in title, but filename you wrote was literal chosen_strategy.
    # We will use the lower-case strategy string you pass in.
    return str(Path(final_plots_dir) / f"{ticker}_{strategy}_strategy_plot.html")


def collect_summary_row(
    ticker,
    strategy,
    feature_set_id,
    model_number,
    summary_dir,
    final_plots_dir,
    log_path,
    *,
    feature_columns=None,
    training_csv=None,
    model_artifact_path=None,
):
    try:
        import pandas as pd

        summary_csv_path = latest_summary_csv(summary_dir, ticker)
        df = pd.read_csv(summary_csv_path)
        row = df[df["Ticker"] == ticker].tail(1)
        if row.empty:
            row = df.tail(1)

        raw = row.iloc[0].to_dict()
        strategy_name = (raw.get("Strategy Name") or strategy).lower()
        model_label = raw.get("Model Name") or ""
        assigned_feature_set = feature_set_id if strategy in ML_STRATEGIES else ""
        assigned_model_number = model_number if strategy in ML_STRATEGIES else ""

        signal_plot_path = raw.get("Strategy Plot Link") or infer_plot_path(final_plots_dir, ticker, strategy)
        portfolio_plot_path = raw.get("Portfolio Value Plot Link", "")
        visible_strategy_link = "Open Strategy Plot" if signal_plot_path else ""
        visible_portfolio_link = "Open Portfolio Plot" if portfolio_plot_path else ""

        backtest_row = {
            "Strategy Name": strategy_name,
            "Ticker": ticker,
            "Model Name": model_label,
            "Model Number": assigned_model_number,
            "Feature Set ID": assigned_feature_set,
            "CAGR (%)": raw.get("CAGR (%)", ""),
            "Sharpe Ratio": raw.get("Sharpe Ratio", ""),
            "Sortino Ratio": raw.get("Sortino Ratio", ""),
            "Calmar Ratio": raw.get("Calmar Ratio", ""),
            "Max Drawdown (%)": raw.get("Max Drawdown (%)", ""),
            "Volatility": raw.get("Volatility", ""),
            "Win Rate (%)": raw.get("Win Rate (%)", ""),
            "Number of Trades": raw.get("Number of Trades", ""),
            "Information Ratio": raw.get("Information Ratio", ""),
            "Strategy Plot Link": visible_strategy_link,
            "Portfolio Value Plot Link": visible_portfolio_link,
            "_StrategyPlotAbsPath": signal_plot_path,
            "_PortfolioPlotAbsPath": portfolio_plot_path,
            "_StrategyKey": strategy,
        }

        ml_training_row = None
        if strategy in ML_STRATEGIES:
            from .ml_metrics_eval import compute_ml_metrics_condensed

            try:
                ml_metrics = compute_ml_metrics_condensed(
                    strategy,
                    ticker,
                    training_csv=training_csv,
                    feature_columns=feature_columns,
                    model_artifact_path=model_artifact_path,
                )
                ml_training_row = {
                    "Strategy Name": strategy_name,
                    "Ticker": ticker,
                    "Model Name": ML_STRATEGIES[strategy]["model_name"],
                    "Model Number": assigned_model_number,
                    "Feature Set ID": assigned_feature_set,
                    "Accuracy": _as_float_or_nan(ml_metrics.get("Accuracy", "")),
                    "Precision": _as_float_or_nan(ml_metrics.get("Precision", "")),
                    "Recall": _as_float_or_nan(ml_metrics.get("Recall", "")),
                    "F1 Score": _as_float_or_nan(ml_metrics.get("F1", "")),
                    "Confusion Matrix": _format_confusion_matrix(ml_metrics.get("Confusion_Matrix", "")),
                }
            except Exception as ml_err:
                log(f"[WARN] ML metrics failed for {ticker} {strategy}: {ml_err}", log_path)
                ml_training_row = {
                    "Strategy Name": strategy_name,
                    "Ticker": ticker,
                    "Model Name": ML_STRATEGIES[strategy]["model_name"],
                    "Model Number": assigned_model_number,
                    "Feature Set ID": assigned_feature_set,
                    "Accuracy": np.nan,
                    "Precision": np.nan,
                    "Recall": np.nan,
                    "F1 Score": np.nan,
                    "Confusion Matrix": "",
                }

        return backtest_row, ml_training_row

    except Exception as err:
        log(f"[WARN] Could not collect summary for {ticker} {strategy}: {err}", log_path)
        return None, None


def _as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_confusion_matrix(matrix_value: Optional[str]) -> str:
    """
    Convert a serialized confusion matrix like "[12 3 4; 5 9 2; 1 4 7]"
    into a multiline string suitable for a single Excel cell.
    """
    if not matrix_value:
        return ""
    import re
    numbers = re.findall(r"-?\d+", matrix_value)
    if not numbers:
        return ""
    chunk = int(len(numbers) ** 0.5) or 1
    rows = [
        numbers[i : i + chunk]
        for i in range(0, len(numbers), chunk)
    ]
    formatted_rows = ["    ".join(row) for row in rows]
    return "\n".join(formatted_rows)


def _as_float_or_nan(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan

# ----------------------------
# Main
# ----------------------------
def main():
    cfg = load_json(PACKAGE_ROOT / "automation_config.json")
    model_number = cfg["model_number"]
    tickers = cfg["tickers"]
    strategies = cfg["strategies"]
    selected_ml_strategies = [s for s in strategies if s in ML_STRATEGIES]
    selected_rule_strategies = [s for s in strategies if s not in ML_STRATEGIES]
    if BUY_AND_HOLD_STRATEGY_NAME not in selected_rule_strategies:
        selected_rule_strategies.append(BUY_AND_HOLD_STRATEGY_NAME)
    feature_sets = cfg["feature_sets"]
    paths = cfg["paths"]

    project_root = Path(paths["project_root"])
    final_root = Path(paths["final_root"])
    final_excel_dir = Path(paths["final_excel_dir"])
    final_plots_dir = Path(paths["final_plots_dir"])
    ml_saved_models_dir = Path(paths.get("ml_saved_models_dir", "ML/saved_models"))
    if not ml_saved_models_dir.is_absolute():
        ml_saved_models_dir = project_root / ml_saved_models_dir
    ml_saved_models_dir = ml_saved_models_dir.resolve()
    sentiment_data_dir = paths.get("sentiment_data_dir")
    if sentiment_data_dir:
        sentiment_data_dir = Path(sentiment_data_dir)
        if not sentiment_data_dir.is_absolute():
            sentiment_data_dir = project_root / sentiment_data_dir
        sentiment_data_dir = sentiment_data_dir.resolve()

    ensure_dirs(final_root, final_excel_dir, final_plots_dir, ml_saved_models_dir)

    # Log file
    log_path = str(final_root / "automation_log.txt")
    log(f"=== Automation started: {datetime.now().isoformat()} ===", log_path)

    # Where your existing summary CSVs are written (from config)
    # We will read the current setting to avoid hardcoding.
    # Import config at runtime to grab FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE
    import importlib
    config_mod = importlib.import_module("config")
    summary_dir = getattr(config_mod, "FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE", "saved_files/csv_summary_files_backtesting")
    summary_dir = str(Path(summary_dir))

    # Combined dataframe rows (we’ll assemble manually, then send to Excel)
    combined_backtest_rows = []
    combined_ml_training_rows = []
    benchmark_rows = []
    successful_runs = []
    failed_runs = []
    skipped_runs = []

    failure_log = []

    # 1) Loop over feature sets (ML strategies only)
    for fs in feature_sets:
        fs_id = fs["feature_set_id"]
        fs_cols = fs["feature_columns"]

        # Activate feature set for this run
        try:
            set_feature_columns(fs_cols)
            log(f"Activated feature set → {fs_id}", log_path)
        except Exception as e:
            log(f"[ERROR] Failed to activate feature set {fs_id}: {e}", log_path)
            continue

        # 2) For each ticker (model_number stays constant for this feature set)
        for ticker in tickers:
            try:
                # Build data paths
                training_csv = build_training_data_path(ticker)
                backtest_csv = build_backtest_data_path(ticker)

                # 2a) Train ML models only for ML strategies listed in config
                if not selected_ml_strategies:
                    log(f"[INFO] No ML strategies selected for {ticker}; skipping training phase.", log_path)
                else:
                    for ml_strategy in selected_ml_strategies:
                        ml_config = ML_STRATEGIES[ml_strategy]
                        model_path = build_model_path(
                            ml_config["model_name"], ticker, model_number, ml_saved_models_dir
                        )
                        strategy_path_key = MODEL_PATH_KEYS.get(ml_strategy)
                        patch_config_values({
                            "TICKER": f"'{ticker}'",
                            "DATA_FOR_ML_MODEL_TRAINING": f"'{training_csv}'",
                            "model_name": f"'{ml_config['model_name']}'",
                            "model_number": f"'{model_number}'",
                            "MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED": f"'{model_path}'",
                            "TRAINING_MODE": "True",
                            **(
                                {strategy_path_key: f"'{model_path}'"}
                                if strategy_path_key
                                else {}
                            ),
                            **(
                                {"DATA_PATH_FOR_SENTIMENT_STRATEGY": f"'{sentiment_data_dir}'"}
                                if sentiment_data_dir
                                else {}
                            ),
                        })
                        log(f"[INFO] Training ML model for strategy: {ml_strategy}", log_path)
                        if not run_cmd(ml_config["train_cmd"], log_path):
                            msg = f"[WARN] Training failed for {ticker} {ml_strategy}_{model_number}. Skipping this model."
                            log(msg, log_path)
                            failure_log.append({
                                "phase": "training",
                                "ticker": ticker,
                                "strategy": ml_strategy,
                                "feature_set": fs_id,
                                "model_number": model_number,
                                "reason": "training command failed"
                            })
                            failed_runs.append((ticker, ml_strategy))
                            continue

                # 2b) Backtest only ML strategies for this ticker/feature set
                for strategy in selected_ml_strategies:
                    model_path_patch = {}
                    strategy_model_path = None
                    if strategy in ML_STRATEGIES:
                        strategy_config = ML_STRATEGIES[strategy]
                        strategy_model_path = build_model_path(
                            strategy_config["model_name"], ticker, model_number, ml_saved_models_dir
                        )
                        if not Path(strategy_model_path).exists():
                            log(
                                f"[WARN] Model file missing for {ticker} {strategy}: {strategy_model_path}. "
                                "Skipping backtest for this combination.",
                                log_path,
                            )
                            skipped_runs.append((ticker, strategy))
                            continue
                        strategy_key = MODEL_PATH_KEYS.get(strategy)
                        if strategy_key:
                            model_path_patch[strategy_key] = f"'{strategy_model_path}'"

                    patch_config_values({
                        "USE_STORED_DATA": "True",
                        "TRAINING_MODE": "False",
                        "TICKERS": f"'{ticker}'",
                        "STORED_DATA_TO_BE_READ": f"'{backtest_csv}'",
                        "CHOSEN_STRATEGY": f"'{strategy}'",
                        "VISUALISE_PLOTTED_SIGNAL_EXECUTIONS": "True",
                        **model_path_patch,
                        **(
                            {"DATA_PATH_FOR_SENTIMENT_STRATEGY": f"'{sentiment_data_dir}'"}
                            if sentiment_data_dir
                            else {}
                        ),
                    })
                    log(f"[INFO] Backtesting strategy: {strategy}", log_path)
                    if not run_cmd("python3 main.py", log_path):
                        msg = f"[WARN] Backtest failed for {ticker} {strategy}. Continuing."
                        log(msg, log_path)
                        failure_log.append({
                            "phase": "backtest",
                            "ticker": ticker,
                            "strategy": strategy,
                            "feature_set": fs_id,
                            "model_number": model_number,
                            "reason": "backtest command failed"
                        })
                        failed_runs.append((ticker, strategy))
                        continue

                    row_dict, ml_training_row = collect_summary_row(
                        ticker=ticker,
                        strategy=strategy,
                        feature_set_id=fs_id,
                        model_number=model_number,
                        summary_dir=summary_dir,
                        final_plots_dir=final_plots_dir,
                        log_path=log_path,
                        feature_columns=fs_cols if strategy in ML_STRATEGIES else None,
                        training_csv=training_csv if strategy in ML_STRATEGIES else None,
                        model_artifact_path=strategy_model_path if strategy in ML_STRATEGIES else None,
                    )
                    if row_dict:
                        combined_backtest_rows.append(row_dict)
                        successful_runs.append((ticker, strategy))
                        if ml_training_row:
                            combined_ml_training_rows.append(ml_training_row)
                    else:
                        failure_log.append({
                            "phase": "summary",
                            "ticker": ticker,
                            "strategy": strategy,
                            "feature_set": fs_id,
                            "model_number": model_number,
                            "reason": "summary row missing"
                        })
                        failed_runs.append((ticker, strategy))

            except Exception as e:
                log(f"[WARN] Outer loop failure for ticker {ticker}: {e}", log_path)
                traceback.print_exc()
                continue

        # ✅ Increment model_number after all tickers in this feature set are done
        model_number = str(int(model_number) + 1)
        log(f"Incremented model_number → {model_number}", log_path)

    # Separate pass for rule-based strategies (feature-set agnostic)
    if selected_rule_strategies:
        log("=== Running rule-based strategies (feature-set agnostic phase) ===", log_path)
        for ticker in tickers:
            try:
                backtest_csv = build_backtest_data_path(ticker)
                for strategy in selected_rule_strategies:
                    patch_config_values({
                        "USE_STORED_DATA": "True",
                        "TRAINING_MODE": "False",
                        "TICKERS": f"'{ticker}'",
                        "STORED_DATA_TO_BE_READ": f"'{backtest_csv}'",
                        "CHOSEN_STRATEGY": f"'{strategy}'",
                        "VISUALISE_PLOTTED_SIGNAL_EXECUTIONS": "True",
                        **(
                            {"DATA_PATH_FOR_SENTIMENT_STRATEGY": f"'{sentiment_data_dir}'"}
                            if sentiment_data_dir
                            else {}
                        ),
                    })
                    log(f"[INFO] Backtesting rule-based strategy: {strategy}", log_path)
                    if not run_cmd("python3 main.py", log_path):
                        msg = f"[WARN] Backtest failed for {ticker} {strategy}. Continuing."
                        log(msg, log_path)
                        failure_log.append({
                            "phase": "backtest",
                            "ticker": ticker,
                            "strategy": strategy,
                            "feature_set": "",
                            "model_number": "",
                            "reason": "backtest command failed"
                        })
                        failed_runs.append((ticker, strategy))
                        continue

                    row_dict, ml_training_row = collect_summary_row(
                        ticker=ticker,
                        strategy=strategy,
                        feature_set_id="",
                        model_number="",
                        summary_dir=summary_dir,
                        final_plots_dir=final_plots_dir,
                        log_path=log_path,
                    )
                    if row_dict:
                        combined_backtest_rows.append(row_dict)
                        if strategy == BUY_AND_HOLD_STRATEGY_NAME:
                            benchmark_rows.append({
                                "Strategy Name": BUY_AND_HOLD_STRATEGY_NAME,
                                "Ticker": ticker,
                                "CAGR (%)": _as_float(row_dict.get("CAGR (%)", 0)),
                                "Sharpe Ratio": _as_float(row_dict.get("Sharpe Ratio", 0)),
                                "Sortino Ratio": _as_float(row_dict.get("Sortino Ratio", 0)),
                                "Calmar Ratio": _as_float(row_dict.get("Calmar Ratio", 0)),
                                "Max Drawdown (%)": _as_float(row_dict.get("Max Drawdown (%)", 0)),
                                "Volatility": _as_float(row_dict.get("Volatility", 0)),
                                "Strategy Plot Link": row_dict.get("_StrategyPlotAbsPath", ""),
                                "Portfolio Value Plot Link": row_dict.get("_PortfolioPlotAbsPath", "")
                            })
                        successful_runs.append((ticker, strategy))
                        if ml_training_row:
                            combined_ml_training_rows.append(ml_training_row)
                    else:
                        failure_log.append({
                            "phase": "summary",
                            "ticker": ticker,
                            "strategy": strategy,
                            "feature_set": "",
                            "model_number": "",
                            "reason": "summary row missing"
                        })
                        failed_runs.append((ticker, strategy))

            except Exception as e:
                log(f"[WARN] Rule-based loop failure for ticker {ticker}: {e}", log_path)
                traceback.print_exc()
                continue








    # 3) Build strategy, ML, and benchmark tables
    try:
        import pandas as pd

        if not combined_backtest_rows:
            log("[ERROR] No results collected — nothing to write to Excel.", log_path)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        def _display_strategy_name(key: str) -> str:
            return (key or "").lower()

        def _model_label(row):
            key = row.get("_StrategyKey")
            if key in ML_STRATEGIES:
                return row.get("Model Name") or ML_STRATEGIES[key]["model_name"]
            return ""

        table2_cols = [
            "Strategy Name",
            "Ticker",
            "Model Name",
            "Model Number",
            "Feature Set ID",
            "CAGR (%)",
            "Sharpe Ratio",
            "Sortino Ratio",
            "Calmar Ratio",
            "Max Drawdown (%)",
            "Volatility",
            "Win Rate (%)",
            "Number of Trades",
            "Information Ratio",
            "Strategy Plot Link",
            "Portfolio Value Plot Link",
        ]

        all_df = pd.DataFrame(combined_backtest_rows)
        for col in table2_cols:
            if col not in all_df.columns:
                all_df[col] = ""
        ml_keys_set = set(ML_STRATEGIES.keys())
        all_df["Model Name"] = all_df.apply(_model_label, axis=1)
        all_df["Strategy Name"] = all_df["_StrategyKey"].apply(_display_strategy_name)
        non_ml_mask = ~all_df["_StrategyKey"].isin(ml_keys_set)
        all_df.loc[non_ml_mask, ["Model Name", "Model Number", "Feature Set ID"]] = ""
        all_df["Information Ratio"] = pd.to_numeric(all_df["Information Ratio"], errors="coerce")

        def _write_excel(df: pd.DataFrame, path: Path):
            helper_df = df.reset_index(drop=True).copy()
            visible_df = helper_df[[col for col in helper_df.columns if not col.startswith("_")]]
            visible_df = visible_df.apply(pd.to_numeric, errors="ignore")
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                visible_df.to_excel(writer, index=False, sheet_name="Summary")
                ws = writer.sheets["Summary"]
                for col_name, label in {
                    "Strategy Plot Link": "Open Strategy Plot",
                    "Portfolio Value Plot Link": "Open Portfolio Plot",
                }.items():
                    if col_name not in visible_df.columns:
                        continue
                    abs_col = "_StrategyPlotAbsPath" if "Strategy" in col_name else "_PortfolioPlotAbsPath"
                    col_idx = visible_df.columns.get_loc(col_name) + 1
                    for row_idx in range(2, ws.max_row + 1):
                        if abs_col in helper_df.columns:
                            path_value = helper_df.iloc[row_idx - 2][abs_col]
                        else:
                            path_value = helper_df.iloc[row_idx - 2][col_name]
                        if not path_value:
                            continue
                        cell = ws.cell(row=row_idx, column=col_idx)
                        cell.value = label
                        cell.hyperlink = str(Path(path_value).resolve())
                apply_summary_excel_formatting(ws)

        non_bh_df = all_df[all_df["_StrategyKey"] != BUY_AND_HOLD_STRATEGY_NAME].copy()
        if not non_bh_df.empty:
            all_output_df = non_bh_df[table2_cols + ["_StrategyPlotAbsPath", "_PortfolioPlotAbsPath", "_StrategyKey"]].copy()
            all_output_df.drop(columns=["_StrategyKey"], inplace=True)
            all_path = Path(final_excel_dir) / f"Strategy_Backtesting_Performance_All_{timestamp}.xlsx"
            _write_excel(all_output_df, all_path)
            log(f"✅ Strategy performance (all) → {all_path}", log_path)

        for ticker in tickers:
            ticker_df = all_df[all_df["Ticker"] == ticker].copy()
            if ticker_df.empty:
                continue
            ticker_df["_BH_ORDER"] = (ticker_df["_StrategyKey"] != BUY_AND_HOLD_STRATEGY_NAME).astype(int)
            ticker_df.sort_values(by=["_BH_ORDER", "Strategy Name"], inplace=True)
            ticker_df.drop(columns=["_BH_ORDER"], inplace=True)
            ticker_df.drop(columns=["_StrategyKey"], inplace=True)
            df_to_write = ticker_df[table2_cols + ["_StrategyPlotAbsPath", "_PortfolioPlotAbsPath"]].copy()
            path = Path(final_excel_dir) / f"{ticker}_Final_Backtesting_Summary_{timestamp}.xlsx"
            _write_excel(df_to_write, path)
            log(f"✅ Strategy performance ({ticker}) → {path}", log_path)

        ml_cols = [
            "Strategy Name",
            "Ticker",
            "Model Name",
            "Model Number",
            "Feature Set ID",
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score",
            "Confusion Matrix",
        ]
        ml_df = pd.DataFrame(combined_ml_training_rows, columns=ml_cols) if combined_ml_training_rows else pd.DataFrame(columns=ml_cols)
        if not ml_df.empty:
            ml_df["Strategy Name"] = ml_df["Strategy Name"].apply(_display_strategy_name)
        ml_df = ml_df.apply(pd.to_numeric, errors="ignore")
        ml_path = Path(final_excel_dir) / f"ML_Training_Performance_{timestamp}.xlsx"
        with pd.ExcelWriter(ml_path, engine="openpyxl") as writer:
            ml_df.to_excel(writer, index=False, sheet_name="Training Performance")
            ws = writer.sheets["Training Performance"]
            apply_summary_excel_formatting(ws)
        log(f"✅ ML training performance → {ml_path}", log_path)

        benchmark_cols = [
            "Strategy Name",
            "Ticker",
            "CAGR (%)",
            "Sharpe Ratio",
            "Sortino Ratio",
            "Calmar Ratio",
            "Max Drawdown (%)",
            "Volatility",
            "Strategy Plot Link",
            "Portfolio Value Plot Link",
        ]
        benchmark_df = pd.DataFrame(benchmark_rows, columns=benchmark_cols) if benchmark_rows else pd.DataFrame(columns=benchmark_cols)
        if not benchmark_df.empty:
            numeric_cols = [
                "CAGR (%)",
                "Sharpe Ratio",
                "Sortino Ratio",
                "Calmar Ratio",
                "Max Drawdown (%)",
                "Volatility",
            ]
            for col in numeric_cols:
                if col in benchmark_df.columns:
                    benchmark_df[col] = pd.to_numeric(benchmark_df[col], errors="coerce")
            benchmark_df["Strategy Name"] = benchmark_df["Strategy Name"].str.lower()
        benchmark_df = benchmark_df.apply(pd.to_numeric, errors="ignore")
        benchmark_path = Path(final_excel_dir) / f"Benchmark_Performance_{timestamp}.xlsx"
        with pd.ExcelWriter(benchmark_path, engine="openpyxl") as writer:
            benchmark_df.to_excel(writer, index=False, sheet_name="Benchmark")
            ws = writer.sheets["Benchmark"]
            link_labels = {
                "Strategy Plot Link": "Open Strategy Plot",
                "Portfolio Value Plot Link": "Open Portfolio Plot",
            }
            for col_name, label in link_labels.items():
                if col_name not in benchmark_df.columns:
                    continue
                col_idx = benchmark_df.columns.get_loc(col_name) + 1
                for row_idx in range(2, ws.max_row + 1):
                    path_value = benchmark_df.iloc[row_idx - 2][col_name]
                    if not path_value:
                        continue
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.value = label
                    cell.hyperlink = str(Path(path_value).resolve())
            apply_summary_excel_formatting(ws)
        log(f"✅ Benchmark performance → {benchmark_path}", log_path)

    except Exception as e:
        log(f"[ERROR] Writing Excel tables failed: {e}", log_path)

    if failure_log:
        log("\n--- SUMMARY OF FAILED RUNS ---", log_path)
        for entry in failure_log:
            log(
                f"{entry['phase'].upper()}: ticker={entry['ticker']}, "
                f"strategy={entry['strategy']}, feature_set={entry['feature_set']}, "
                f"model_number={entry['model_number']}, reason={entry['reason']}",
                log_path,
            )

    if failed_runs:
        log("\n--- FAILED STRATEGY RUNS ---", log_path)
        for ticker, strategy in failed_runs:
            log(f"FAILED → ticker={ticker}, strategy={strategy}", log_path)

    if skipped_runs:
        log("\n--- SKIPPED STRATEGY RUNS ---", log_path)
        for ticker, strategy in skipped_runs:
            log(f"SKIPPED → ticker={ticker}, strategy={strategy}", log_path)

    log(
        f"Run summary: successful={len(successful_runs)}, "
        f"failed={len(failed_runs)}, skipped={len(skipped_runs)}",
        log_path,
    )

    if not failed_runs and not skipped_runs:
        log("All training/backtest tasks completed successfully.", log_path)

    log(f"=== Automation finished: {datetime.now().isoformat()} ===", log_path)


if __name__ == "__main__":
    main()
