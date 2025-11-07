import os
import sys
import json
import time
import shutil
import traceback
import subprocess
from datetime import datetime
from pathlib import Path

from backtest.create_and_save_backtest_summary_table_csv_file import (
    format_confusion_matrix_string,
    apply_summary_excel_formatting,
)

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
    # Convert to clickable file:// URL for Excel
    p = Path(path_str).resolve()
    return f"file://{p}"

def patch_config_values(updates: dict):
    """Safely patch values in config.py while preserving indentation."""
    config_path = os.path.join(project_root, "config.py")
    with open(config_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        stripped = line.strip()
        replaced = False
        for key, value in updates.items():
            if stripped.startswith(f"{key} =") or stripped.startswith(f"{key}="):
                indent = len(line) - len(line.lstrip(" "))  # count spaces
                new_lines.append(" " * indent + f"{key} = {value}\n")
                replaced = True
                break
        if not replaced:
            new_lines.append(line)

    with open(config_path, "w") as f:
        f.writelines(new_lines)


def set_feature_columns(columns):
    """
    Overwrite FEATURE_COLUMNS in config.py with provided list.
    """
    cfg_path = Path("config.py")
    text = cfg_path.read_text()

    import re, json as pyjson
    pattern = r"(^|\n)\s*FEATURE_COLUMNS\s*=\s*\[.*?\]"
    replacement = f"\nFEATURE_COLUMNS = {pyjson.dumps(columns, ensure_ascii=False)}"
    text = re.sub(pattern, replacement, text, flags=re.S)

    cfg_path.write_text(text)

def build_training_data_path(ticker):
    # Uses your existing pattern for training CSVs
    # Example from your config: data/stored_data2/data_{TICKER}_train_test_2010-01-01--2020-12-31.csv
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
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {adjusted_cmd}")

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

# ----------------------------
# Main
# ----------------------------
def main():
    cfg = load_json("automation_bunch_backtesting/automation_config.json")
    model_number = cfg["model_number"]
    tickers = cfg["tickers"]
    strategies = cfg["strategies"]
    feature_sets = cfg["feature_sets"]
    paths = cfg["paths"]

    project_root = Path(paths["project_root"])
    final_root = Path(paths["final_root"])
    final_excel_dir = Path(paths["final_excel_dir"])
    final_plots_dir = Path(paths["final_plots_dir"])
    sentiment_data_dir = paths.get("sentiment_data_dir")
    if sentiment_data_dir:
        sentiment_data_dir = Path(sentiment_data_dir)
        if not sentiment_data_dir.is_absolute():
            sentiment_data_dir = project_root / sentiment_data_dir
        sentiment_data_dir = sentiment_data_dir.resolve()

    ensure_dirs(final_root, final_excel_dir, final_plots_dir)

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













    # 1) Loop over feature sets (you currently have one; this scales later)
    for fs in feature_sets:
        fs_id = fs["feature_set_id"]
        fs_cols = fs["feature_columns"]

        # Set FEATURE_COLUMNS in config.py
        try:
            set_feature_columns(fs_cols)
            log(f"Set FEATURE_COLUMNS → {fs_id}", log_path)
        except Exception as e:
            log(f"[ERROR] Failed to set FEATURE_COLUMNS for {fs_id}: {e}", log_path)
            continue

        # 2) For each ticker (model_number stays constant for this feature set)
        for ticker in tickers:
            try:
                # Build data paths
                training_csv = build_training_data_path(ticker)
                backtest_csv = build_backtest_data_path(ticker)

                # 2a) Train ML models only for ML strategies listed in config
                selected_ml_strategies = [s for s in strategies if s in ML_STRATEGIES]
                if not selected_ml_strategies:
                    log(f"[INFO] No ML strategies selected for {ticker}; skipping training phase.", log_path)
                else:
                    for ml_strategy in selected_ml_strategies:
                        ml_config = ML_STRATEGIES[ml_strategy]
                        patch_config_values({
                            "TICKER": f"'{ticker}'",
                            "DATA_FOR_ML_MODEL_TRAINING": f"'{training_csv}'",
                            "model_name": f"'{ml_config['model_name']}'",
                            "model_number": f"'{model_number}'",
                            **(
                                {"DATA_PATH_FOR_SENTIMENT_STRATEGY": f"'{sentiment_data_dir}'"}
                                if sentiment_data_dir
                                else {}
                            ),
                        })
                        try:
                            log(f"[INFO] Training ML model for strategy: {ml_strategy}", log_path)
                            run_cmd(ml_config["train_cmd"], log_path)
                        except Exception as e:
                            log(f"[WARN] Training failed for {ticker} {ml_strategy}_{model_number}: {e}", log_path)
                            continue

                # 2b) Backtest all requested strategies for this ticker
                for strategy in strategies:
                    patch_config_values({
                        "USE_STORED_DATA": "True",
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
                    try:
                        log(f"[INFO] Backtesting strategy: {strategy}", log_path)
                        run_cmd("python3 main.py", log_path)
                    except Exception as e:
                        log(f"[WARN] Backtest failed for {ticker} {strategy}: {e}", log_path)
                        continue

                    # 2c) Read the summary CSV for this run
                    try:
                        summary_csv_path = latest_summary_csv(summary_dir, ticker)
                        import pandas as pd
                        df = pd.read_csv(summary_csv_path)
                        row = df[df["Ticker"] == ticker].tail(1)
                        if row.empty:
                            row = df.tail(1)

                        row_dict = row.iloc[0].to_dict()

                        # 2d) Add identifiers
                        if strategy in ML_STRATEGIES:
                            feature_set_id = fs_id
                        else:
                            feature_set_id = ""
                            log(f"[INFO] Skipping feature set ID for rule-based strategy: {strategy}", log_path)

                        row_dict.update({
                            "Ticker": ticker,
                            "Strategy": strategy,
                            "Model_Number": model_number if strategy in ML_STRATEGIES else "",
                            "Model_Name": ML_STRATEGIES.get(strategy, {}).get("model_name", ""),
                            "Feature_Set_ID": feature_set_id
                        })

                        # 2e) Add clickable Plotly link
                        plot_path = infer_plot_path(final_plots_dir, ticker, strategy)
                        row_dict["Plot Link"] = file_url(plot_path)

                        # 2f) ML metrics (only for ML-based strategies)
                        if strategy in ML_STRATEGIES:
                            try:
                                from automation_bunch_backtesting.ml_metrics_eval import compute_ml_metrics_condensed
                                ml_metrics = compute_ml_metrics_condensed(strategy, ticker)
                                row_dict.update(ml_metrics)
                            except Exception as e:
                                log(f"[WARN] ML metrics failed for {ticker} {strategy}: {e}", log_path)
                                row_dict.update({
                                    "Accuracy": "",
                                    "Precision": "",
                                    "Recall": "",
                                    "F1": "",
                                    "Confusion_Matrix": ""
                                })
                        else:
                            row_dict.update({
                                "Accuracy": "",
                                "Precision": "",
                                "Recall": "",
                                "F1": "",
                                "Confusion_Matrix": ""
                            })

                        combined_rows.append(row_dict)

                    except Exception as e:
                        log(f"[WARN] Could not collect summary for {ticker} {strategy}: {e}", log_path)
                        continue

            except Exception as e:
                log(f"[WARN] Outer loop failure for ticker {ticker}: {e}", log_path)
                traceback.print_exc()
                continue

        # ✅ Increment model_number after all tickers in this feature set are done
        model_number = str(int(model_number) + 1)
        log(f"Incremented model_number → {model_number}", log_path)








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
            "Plot Link"
        ]
        df_all = pd.DataFrame(combined_rows)
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
            apply_summary_excel_formatting(ws)

        log(f"✅ Combined Excel written: {excel_path}", log_path)
    except Exception as e:
        log(f"[ERROR] Writing Excel failed: {e}", log_path)

    log(f"=== Automation finished: {datetime.now().isoformat()} ===", log_path)


if __name__ == "__main__":
    main()
