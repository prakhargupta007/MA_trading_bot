
# THIS IS HOW TO RUN THIS FILE:
'python3 -m ma_trading_bot.automation_bunch_backtesting.automate_train_and_backtest'



import os
import sys
import json
import time
import shutil
import traceback
import subprocess
from datetime import datetime
from pathlib import Path

from ma_trading_bot.backtest.create_and_save_backtest_summary_table_csv_file import (
    format_confusion_matrix_string,
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
}

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

        row_dict = row.iloc[0].to_dict()

        if strategy in ML_STRATEGIES:
            assigned_feature_set = feature_set_id
            assigned_model_number = model_number
        else:
            assigned_feature_set = ""
            assigned_model_number = ""

        row_dict.update({
            "Ticker": ticker,
            "Strategy": strategy,
            "Model_Number": assigned_model_number,
            "Model_Name": ML_STRATEGIES.get(strategy, {}).get("model_name", ""),
            "Feature_Set_ID": assigned_feature_set,
        })

        signal_plot_raw = row_dict.get("Signal Execution Plot Link") or infer_plot_path(
            final_plots_dir, ticker, strategy
        )
        portfolio_plot_raw = row_dict.get("Portfolio Value Plot Link", "")

        row_dict["_SignalPlotAbsPath"] = signal_plot_raw
        row_dict["_PortfolioPlotAbsPath"] = portfolio_plot_raw
        row_dict["Signal Execution Plot Link"] = "Open Signal Plot" if signal_plot_raw else ""
        row_dict["Portfolio Value Plot Link"] = "Open Portfolio Plot" if portfolio_plot_raw else ""

        if strategy in ML_STRATEGIES:
            try:
                from .ml_metrics_eval import compute_ml_metrics_condensed
                ml_metrics = compute_ml_metrics_condensed(
                    strategy,
                    ticker,
                    training_csv=training_csv,
                    feature_columns=feature_columns,
                    model_artifact_path=model_artifact_path,
                )
                row_dict.update(ml_metrics)
                row_dict["ML_Metrics_Status"] = "ok"
            except Exception as ml_err:
                log(f"[WARN] ML metrics failed for {ticker} {strategy}: {ml_err}", log_path)
                row_dict.update({
                    "Accuracy": "",
                    "Precision": "",
                    "Recall": "",
                    "F1": "",
                    "Confusion_Matrix": ""
                })
                row_dict["ML_Metrics_Status"] = f"error: {ml_err}"
        else:
            row_dict.update({
                "Accuracy": "",
                "Precision": "",
                "Recall": "",
                "F1": "",
                "Confusion_Matrix": ""
            })
            row_dict["ML_Metrics_Status"] = "n/a (rule strategy)"

        return row_dict

    except Exception as err:
        log(f"[WARN] Could not collect summary for {ticker} {strategy}: {err}", log_path)
        return None

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
    combined_rows = []













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
                        continue

                    row_dict = collect_summary_row(
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
                        combined_rows.append(row_dict)
                    else:
                        failure_log.append({
                            "phase": "summary",
                            "ticker": ticker,
                            "strategy": strategy,
                            "feature_set": fs_id,
                            "model_number": model_number,
                            "reason": "summary row missing"
                        })

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
                        continue

                    row_dict = collect_summary_row(
                        ticker=ticker,
                        strategy=strategy,
                        feature_set_id="",
                        model_number="",
                        summary_dir=summary_dir,
                        final_plots_dir=final_plots_dir,
                        log_path=log_path,
                    )
                    if row_dict:
                        combined_rows.append(row_dict)
                    else:
                        failure_log.append({
                            "phase": "summary",
                            "ticker": ticker,
                            "strategy": strategy,
                            "feature_set": "",
                            "model_number": "",
                            "reason": "summary row missing"
                        })

            except Exception as e:
                log(f"[WARN] Rule-based loop failure for ticker {ticker}: {e}", log_path)
                traceback.print_exc()
                continue








    # 3) Build ONE combined Excel file
    try:
        import pandas as pd
        if not combined_rows:
            log("[ERROR] No results collected — nothing to write to Excel.", log_path)
            return

        # Reorder columns nicely
        preferred_cols = [
            "Ticker", "Strategy", "Model_Name", "Model_Number", "Feature_Set_ID",
            "CAGR(%)", "B&H CAGR(%)", "CAGR Efficiency",
            "Sharpe", "B&H Sharpe", "Sharpe Efficiency",
            # Extra trading metrics
            "WinRate(%)", "Avg_Win", "Avg_Loss", "Profit_Factor",
            "Max_Drawdown(%)", "B&H Max_Drawdown(%)", "Sortino", "Calmar",
            "Number_of_Trades",
            # ML metrics (condensed)
            "Accuracy", "Precision", "Recall", "F1", "Confusion_Matrix",
            # Plot link
            "Signal Execution Plot Link", "Portfolio Value Plot Link"
        ]
        df_all = pd.DataFrame(combined_rows)

        signal_abs = df_all["_SignalPlotAbsPath"] if "_SignalPlotAbsPath" in df_all.columns else None
        portfolio_abs = df_all["_PortfolioPlotAbsPath"] if "_PortfolioPlotAbsPath" in df_all.columns else None
        if signal_abs is not None:
            df_all.drop(columns=["_SignalPlotAbsPath"], inplace=True)
        if portfolio_abs is not None:
            df_all.drop(columns=["_PortfolioPlotAbsPath"], inplace=True)

        if "Number_of_Trades" not in df_all.columns:
            df_all["Number_of_Trades"] = [
                row.get("Number_of_Trades", "") for row in combined_rows
            ]
            log("[INFO] Added Number_of_Trades column to combined Excel summary.", log_path)

        # Ensure columns exist
        for c in preferred_cols:
            if c not in df_all.columns:
                df_all[c] = ""

        df_all = df_all[preferred_cols]
        if "Confusion_Matrix" in df_all.columns:
            df_all["Confusion_Matrix"] = df_all["Confusion_Matrix"].apply(format_confusion_matrix_string)
        print(f"[DEBUG] Combined summary columns: {list(df_all.columns)}")

        # Write Excel with formatting
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = Path(final_excel_dir) / f"Backtest_Summary_All_{ts}.xlsx"
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df_all.to_excel(writer, index=False, sheet_name="Summary")
            ws = writer.sheets["Summary"]

            def _apply_hyperlinks(col_name, paths, label):
                if paths is None or col_name not in df_all.columns:
                    return
                col_idx = df_all.columns.get_loc(col_name) + 1
                for row_idx, path in enumerate(paths.tolist(), start=2):
                    if not path:
                        continue
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.value = label
                    cell.hyperlink = str(Path(path).resolve())
                    cell.style = "Hyperlink"

            _apply_hyperlinks("Signal Execution Plot Link", signal_abs, "Open Signal Plot")
            _apply_hyperlinks("Portfolio Value Plot Link", portfolio_abs, "Open Portfolio Plot")

            apply_summary_excel_formatting(ws)

        log(f"✅ Combined Excel written: {excel_path}", log_path)
    except Exception as e:
        log(f"[ERROR] Writing Excel failed: {e}", log_path)

    if failure_log:
        log("\n--- SUMMARY OF FAILED RUNS ---", log_path)
        for entry in failure_log:
            log(
                f"{entry['phase'].upper()}: ticker={entry['ticker']}, "
                f"strategy={entry['strategy']}, feature_set={entry['feature_set']}, "
                f"model_number={entry['model_number']}, reason={entry['reason']}",
                log_path,
            )
    else:
        log("All training/backtest tasks completed successfully.", log_path)

    log(f"=== Automation finished: {datetime.now().isoformat()} ===", log_path)


if __name__ == "__main__":
    main()
