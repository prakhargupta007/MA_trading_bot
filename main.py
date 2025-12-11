"""
Main orchestration script for the MA trading bot.

Reads configuration, fetches data, builds indicators, generates signals
(including the intentional len(data)+1 convention for next-day execution),
runs the backtest, computes metrics, and writes plots/summary outputs.
"""

import traceback
import pandas as pd
from datetime import datetime
import math
from collections import Counter

# ======================= CONFIG IMPORTS =======================
from config import (
    USE_STORED_DATA,
    STORED_DATA_TO_BE_READ,
    TICKERS,
    DATA_API_IS_YFINANCE,
    STARTING_BALANCE,
    VISUALISE_PLOTTED_SIGNAL_EXECUTIONS,
    SMA_LONG_PERIOD,
    SMA_SHORT_PERIOD,
    EMA_LONG_PERIOD,
    EMA_SHORT_PERIOD,
    RSI_PERIOD,
    MACD_FAST_PERIOD,
    MACD_SLOW_PERIOD,
    MACD_SIGNAL_PERIOD,
    RSI_OVERBOUGHT_WARNING,
    RSI_OVERSOLD_WARNING,
    DATA_PATH_FOR_SENTIMENT_STRATEGY,
    CHOSEN_STRATEGY,
    USE_STOP_LOSS,
    CHOSEN_STOP_LOSS,
    COLUMN_NAME,
    STOP_LOSS_THRESHOLD,
    ATR_PERIOD,
    ATR_MULTIPLIER,
    model_number,  # your global ML model number
    BB_WINDOW,
    BB_STD_DEV,
    OBV_SMA_PERIOD,
    MA_DISTANCE_PERIOD,
    MA_DISTANCE_THRESHOLD,
    MOMENTUM_WINDOW,
    VOL_WINDOW,
    VOL_SMOOTH_PERIOD,
    TREND_SMA_PERIOD,
    RSI_TREND_THRESHOLD,
    MACD_HIST_THRESHOLD,
    SENTIMENT_COL,
    SENTIMENT_THRESHOLD,
    SENTIMENT_WINDOW,
    SENTIMENT_MA_PERIOD,
)

# ======================= FUNCTION IMPORTS =======================
from data.fetch_data.fetch_data_from_yfinance import fetch_data_from_yfinance
# from data.fetch_data.fetch_data_from_alpha_vantage import fetch_data_from_alpha_vantage

from indicators.check_indicator_length import check_indicator_length

from strategy_map import strategy_map
from stop_loss_map import stop_loss_map

from ma_trading_bot.backtest.backtest_strategy import (
    backtest_strategy,
    return_endbalance,
    return_portfolio_values,
)
from ma_trading_bot.backtest.create_and_save_backtest_table_csv_file import (
    create_and_save_backtest_table_csv_file,
)
from ma_trading_bot.backtest.enforce_signal_consistency import enforce_signal_consistency

from plotly_plot_backtesting.plotly_plot_universal_strategy_signals_and_save import (
    plotly_plot_universal_strategy_signals_and_save,
)
from plotly_plot_backtesting.plotly_plot_portfolio_values_chart import (
    plotly_plot_portfolio_values,
)

from metrics.cagr import calculate_cagr
from metrics.profit import calculate_profit
from metrics.buy_hold_profit import calculate_profit_if_bought_and_held
from metrics.cagr_strategy_efficiency import cagr_strategy_efficiency
from metrics.average_cagr_of_list import calculate_average_cagr_of_list
from metrics.sharpe import calculate_sharpe_ratio

# upgraded summary writer (Excel + links)
from ma_trading_bot.backtest.create_and_save_backtest_summary_table_csv_file import (
    create_and_save_backtest_summary_table_csv_file,
)
from ma_trading_bot.automation_bunch_backtesting.ml_metrics_eval import compute_ml_metrics_condensed
from ma_trading_bot.ml_feature_store import get_active_feature_columns

ML_STRATEGIES_SET = {"logistic_regression", "random_forest", "xgboost", "mlp"}

ML_STRATEGY_MODEL_LABELS = {
    "logistic_regression": "lr",
    "random_forest": "rf",
    "xgboost": "xgb",
    "mlp": "mlp",
}


# ======================= MAIN FUNCTION =======================
def main():
    """
    Orchestrate a full backtest run using the configured strategy.

    Signal conventions:
    - Strategies may return len(data)+1 signals: day i signal executes on day i+1,
      day 0 defaults to HOLD, and the final signal is intentionally unexecuted.
    - A trailing unexecutable signal is trimmed here only when the strategy returned
      one extra entry.
    """
    try:
        # --- Determine backtesting period ---
        if USE_STORED_DATA:
            START_DATE = "2021-01-01"
            END_DATE = "2025-10-24"
            BACKTEST_PERIOD_YEARS = str(
                round(
                    (
                        datetime.strptime(END_DATE, "%Y-%m-%d")
                        - datetime.strptime(START_DATE, "%Y-%m-%d")
                    ).days
                    / 365.25,
                    3,
                )
            )
            option_1_chosen = False
        else:
            try:
                from config import BACKTESTING_PERIOD as BACKTEST_PERIOD_YEARS

                print(
                    f"\nOption 1 was chosen --> Backtesting period is set from today to exactly {BACKTEST_PERIOD_YEARS} years ago"
                )
                option_1_chosen = True
                START_DATE, END_DATE = None, None
            except:
                from config import START_OF_BACKTESTING as START_DATE
                from config import END_OF_BACKTESTING as END_DATE

                BACKTEST_PERIOD_YEARS = (
                    (pd.to_datetime(END_DATE) - pd.to_datetime(START_DATE)).days / 365.25
                )
                option_1_chosen = False

        # --- Initialize lists ---
        TICKER_LIST = TICKERS.split(",")

        summary_tickers = []
        summary_CAGRs = []
        summary_buy_hold_CAGRs = []
        summary_cagr_strategy_efficiencies = []
        summary_sharpe_ratios = []
        signal_plot_links = []
        portfolio_plot_links = []
        summary_ml_metrics = {}

        # extra for summary Excel
        portfolio_values_dict = {}
        trade_tables_dict = {}
        price_series_dict = {}
        strategy_names = []
        model_names = []
        model_numbers = []
        feature_set_ids = []

        for TICKER in TICKER_LIST:
            print("\n" + "_" * 200)
            print(f"\nProcessing {TICKER}...\n")

            # =========== FETCH DATA ===========
            if USE_STORED_DATA:
                data = pd.read_csv(STORED_DATA_TO_BE_READ, index_col="Date", parse_dates=True)
                print("✅ Using locally stored sample data.\n")
            else:
                print(f"Fetching historical data of {TICKER}...")
                if DATA_API_IS_YFINANCE:
                    data = fetch_data_from_yfinance(
                        TICKER, option_1_chosen, BACKTEST_PERIOD_YEARS, END_DATE, START_DATE
                    )
                
                if data is None or data.empty:
                    raise ValueError(
                        f"❌ No data was fetched for ticker {TICKER}. Please check the ticker symbol or your internet connection."
                    )
                print(f"✅ Data of {TICKER} fetched successfully.\n")

            # =========== INDICATORS ===========
            indicator_parameters = {
            # --- Core ---
            "data": data,
            "ticker": TICKER,
            "start_date": data.index[0],
            "end_date": data.index[-1],
            "data_path_for_sentiment_strategy": DATA_PATH_FOR_SENTIMENT_STRATEGY,

            # --- SMA / EMA / RSI / MACD core parameters ---
            "sma_long_period": SMA_LONG_PERIOD,       # e.g. 200
            "sma_short_period": SMA_SHORT_PERIOD,     # e.g. 50
            "ema_long_period": EMA_LONG_PERIOD,       # e.g. 200
            "ema_short_period": EMA_SHORT_PERIOD,     # e.g. 50
            "rsi_period": RSI_PERIOD,                 # e.g. 14
            "rsi_overbought": RSI_OVERBOUGHT_WARNING, # e.g. 70
            "rsi_oversold": RSI_OVERSOLD_WARNING,     # e.g. 30
            "macd_fast": MACD_FAST_PERIOD,            # e.g. 12
            "macd_slow": MACD_SLOW_PERIOD,            # e.g. 26
            "macd_signal": MACD_SIGNAL_PERIOD,        # e.g. 9

            # --- Bollinger Bands strategies ---
            "bb_window": BB_WINDOW,
            "bb_std_dev": BB_STD_DEV,

            # --- OBV Trend Confirmation strategy ---
            "sma_period": OBV_SMA_PERIOD,

            # --- MA Distance Reversion strategy ---
            "ma_period": MA_DISTANCE_PERIOD,
            "ma_threshold": MA_DISTANCE_THRESHOLD,

            # --- Volume / Volatility adjusted momentum strategy ---
            "momentum_window": MOMENTUM_WINDOW,
            "vol_window": VOL_WINDOW,
            "vol_smooth_period": VOL_SMOOTH_PERIOD,

            # --- RSI Trend Filter strategy ---
            "trend_sma_period": TREND_SMA_PERIOD,
            "rsi_threshold": RSI_TREND_THRESHOLD,

            # --- MACD Trend Follow strategy ---
            "macd_hist_threshold": MACD_HIST_THRESHOLD,

            # --- Sentiment-based strategies ---
            "sentiment_col": SENTIMENT_COL,
            "sentiment_threshold": SENTIMENT_THRESHOLD,
            "sentiment_window": SENTIMENT_WINDOW,
            "sentiment_ma_period": SENTIMENT_MA_PERIOD,
}

            if CHOSEN_STRATEGY in ML_STRATEGIES_SET:
                indicator_parameters["feature_columns"] = get_active_feature_columns()



            stop_loss_parameters = {
                "column_name": COLUMN_NAME,
                "threshold": STOP_LOSS_THRESHOLD,
                "atr_period": ATR_PERIOD,
                "atr_mult": ATR_MULTIPLIER,
            }

            message, good_to_go = check_indicator_length(data, indicator_parameters)
            if not good_to_go:
                print(f"❌ {message}")
                continue
            print(f"✅ {message}")

            # =========== GENERATE SIGNALS ===========
            print(f"\nBacktesting strategy: {CHOSEN_STRATEGY.upper()} STRATEGY")
            print("Generating transaction signals...")
            signals = strategy_map[CHOSEN_STRATEGY](**indicator_parameters)
            print("Signal distribution:")
            print("Signal distribution:")
            print(Counter(signals))
            print("✅ Transaction signals generated successfully.\n")

            if len(signals) == len(data) + 1:
                # Strategies intentionally include a final unexecuted signal for the next-day model.
                print("[INFO] Trimming final unexecutable signal.")
                signals = signals[:-1]
                print(f"[DEBUG] Signals length after trim: {len(signals)} (data length: {len(data)})")

            # =========== STOP LOSS ===========
            if USE_STOP_LOSS:
                signals = stop_loss_map[CHOSEN_STOP_LOSS](data, signals, **stop_loss_parameters)
                signals = enforce_signal_consistency(signals)
                print("✅ Stop-loss applied successfully.\n")

            # =========== BACKTEST STRATEGY ===========
            print("Running backtest...")
            print("Last 10 signals:", signals[-10:])
            print("Last action:", signals[-1])

            results_of_backtesting = backtest_strategy(data, signals, STARTING_BALANCE)
            actions, dates, numbers, prices, cash_flows, trades_df = results_of_backtesting
            print("✅ Backtest results generated.\n")

            # =========== SAVE INDIVIDUAL BACKTEST TABLE ===========
            print("Saving backtest table...")
            backtest_table = create_and_save_backtest_table_csv_file(
                (actions, dates, numbers, prices, cash_flows, trades_df),
                TICKER,
            )
            print("✅ Backtest table saved.\n")

            print("Results summary of this ticker:")
            print(backtest_table)

            # =========== PLOTS ===========
            plot_path = None
            portfolio_plot_path = None
            if VISUALISE_PLOTTED_SIGNAL_EXECUTIONS:
                print("Generating Plotly chart...")

                plot_path = plotly_plot_universal_strategy_signals_and_save(data, signals, TICKER, CHOSEN_STRATEGY.upper())
                portfolio_value = return_portfolio_values()
                portfolio_plot_path = plotly_plot_portfolio_values(portfolio_value, data, TICKER)
                print("✅ Plots generated.\n")

            # =========== METRICS ===========
            print("Calculating metrics...")
            final_balance = return_endbalance()
            if final_balance is None:
                print("⚠️ No SELL actions found — using last known portfolio value as final balance.")
                final_balance = portfolio_value[-1] if 'portfolio_value' in locals() else STARTING_BALANCE

            profit_in_percent, profit = calculate_profit(STARTING_BALANCE, final_balance)
            cagr = calculate_cagr(STARTING_BALANCE, float(BACKTEST_PERIOD_YEARS), final_balance)

            portfolio_values = return_portfolio_values()
            portfolio_values_series = pd.Series(portfolio_values, dtype=float)

            # =========== BUY & HOLD PLOT GENERATION (FIXED) ===========
            if CHOSEN_STRATEGY.lower() == "buy_and_hold":
                try:
                    # Synthetic signals for Buy & Hold:
                    # BUY at the first day, SELL at the last day, HOLD in between
                    bh_signals = ["HOLD"] * len(data)
                    if len(bh_signals) >= 2:
                        bh_signals[0] = "BUY"
                        bh_signals[-1] = "SELL"

                    # 1) Strategy plot with correct markers + green hold region
                    bh_plot_path = plotly_plot_universal_strategy_signals_and_save(
                        data,
                        bh_signals,
                        TICKER,
                        "buy_and_hold"
                    )

                    # 2) Portfolio value plot
                    bh_portfolio_plot_path = plotly_plot_portfolio_values(
                        portfolio_values_series,
                        data,
                        TICKER
                    )

                    plot_path = bh_plot_path
                    portfolio_plot_path = bh_portfolio_plot_path

                    print(f"✅ Buy & Hold (fixed) strategy plot saved: {bh_plot_path}")
                    print(f"✅ Buy & Hold (fixed) portfolio plot saved: {bh_portfolio_plot_path}")

                except Exception as e:
                    print(f"⚠️ Failed to generate buy & hold plots: {e}")
                    plot_path = ""
                    portfolio_plot_path = ""

            sharpe_ratio = (
                calculate_sharpe_ratio(portfolio_values_series)
                if len(portfolio_values) > 1
                else 0
            )

            if sharpe_ratio is None or math.isnan(sharpe_ratio):
                sharpe_ratio = 0

            # --- Buy & Hold comparison ---
            profit_of_buy_and_hold, bh_end_balance = calculate_profit_if_bought_and_held(
                data, STARTING_BALANCE
            )
            bh_cagr = calculate_cagr(STARTING_BALANCE, float(BACKTEST_PERIOD_YEARS), bh_end_balance)
            cagr_efficiency = cagr_strategy_efficiency(cagr, bh_cagr)

            # =========== SAVE METRICS FOR SUMMARY ===========
            summary_tickers.append(TICKER)
            summary_CAGRs.append(cagr)
            summary_buy_hold_CAGRs.append(bh_cagr)
            summary_cagr_strategy_efficiencies.append(cagr_efficiency)
            summary_sharpe_ratios.append(sharpe_ratio)

            portfolio_values_dict[TICKER] = portfolio_values_series.copy()
            trade_tables_dict[TICKER] = trades_df.copy(deep=True)
            price_series_dict[TICKER] = data["Close"]
            strategy_names.append(CHOSEN_STRATEGY)
            if CHOSEN_STRATEGY in ML_STRATEGIES_SET:
                dynamic_model_name = ML_STRATEGY_MODEL_LABELS.get(
                    CHOSEN_STRATEGY, CHOSEN_STRATEGY
                )
                model_names.append(dynamic_model_name)
            else:
                model_names.append("")
            model_numbers.append(model_number)
            feature_set_ids.append(
                f"fs_{model_number}_default" if CHOSEN_STRATEGY in ML_STRATEGIES_SET else ""
            )
            signal_plot_links.append(plot_path or "")
            portfolio_plot_links.append(portfolio_plot_path or "")

            if CHOSEN_STRATEGY in ML_STRATEGIES_SET:
                key = (TICKER, CHOSEN_STRATEGY)
                if key not in summary_ml_metrics:
                    try:
                        ml_metrics = compute_ml_metrics_condensed(CHOSEN_STRATEGY, TICKER)
                        summary_ml_metrics[key] = {
                            "accuracy": ml_metrics.get("Accuracy", ""),
                            "precision": ml_metrics.get("Precision", ""),
                            "recall": ml_metrics.get("Recall", ""),
                            "f1": ml_metrics.get("F1", ""),
                            "confusion_matrix": ml_metrics.get("Confusion_Matrix", ""),
                        }
                    except Exception as ml_err:
                        print(f"[WARN] ML metrics computation failed for {TICKER} {CHOSEN_STRATEGY}: {ml_err}")
                        summary_ml_metrics[key] = {
                            "accuracy": "",
                            "precision": "",
                            "recall": "",
                            "f1": "",
                            "confusion_matrix": "",
                        }

            
        # =========== FINAL SUMMARY ===========

    
        print("\nCreating final Excel summary...\n")
        summary_table, excel_path = create_and_save_backtest_summary_table_csv_file(
            summary_tickers,
            summary_CAGRs,
            summary_buy_hold_CAGRs,
            summary_cagr_strategy_efficiencies,
            summary_sharpe_ratios,
            strategy_names=strategy_names,
            model_numbers=model_numbers,
            feature_set_ids=feature_set_ids,
            signal_plot_links=signal_plot_links,
            portfolio_plot_links=portfolio_plot_links,
            portfolio_values_dict=portfolio_values_dict,
            trade_tables_dict=trade_tables_dict,
            price_series_dict=price_series_dict,
            ml_metrics_dict=summary_ml_metrics if summary_ml_metrics else None,
            model_names=model_names,
        )

        print(
            f"\nRESULTS OF {CHOSEN_STRATEGY.upper()} STRATEGY from {START_DATE} to {END_DATE} "
            f"({round(float(BACKTEST_PERIOD_YEARS), 2)} years)"
        )
        print(summary_table)
        print(f"Average CAGR: {calculate_average_cagr_of_list(summary_CAGRs):.2f}%")

        print(f"\n✅ Summary CSV saved at: {excel_path}")
        print("\nEnd of backtesting!\nADIOS! 😎\n")

    except Exception as e:
        print("\n❌ An error occurred:")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
