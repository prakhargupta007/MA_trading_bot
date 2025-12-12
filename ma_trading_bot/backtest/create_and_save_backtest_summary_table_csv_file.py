"""
Build and persist per-ticker backtest summary tables (CSV/Excel).

Includes extended metrics (Sortino, Calmar, MDD, win rate, info ratio) and
supports optional ML metrics embedding. Designed to keep behaviour identical
to previous summary outputs.
"""

import os
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter
from tabulate import tabulate

from config import (
    FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE,
    RISK_FREE_RATE,
    STARTING_BALANCE,
    TICKERS,
)
from metrics.information_ratio import calculate_information_ratio
from metrics.volatility import calculate_volatility

FINAL_EXCEL_DIR = "/Users/prakhar/Desktop/MA_trading_bot/automated_backtesting_results/full_backtesting_tables_excel"

TABLE_COLUMNS = [
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


# ---------------- Helper Metric Functions ---------------- #

def _max_drawdown(equity_curve: pd.Series) -> float:
    if equity_curve is None or len(equity_curve) < 2:
        return 0.0
    eq = pd.Series(equity_curve).astype(float).reset_index(drop=True)
    roll_max = eq.cummax()
    dd = eq / roll_max - 1.0
    return float(100.0 * dd.min())


def _sortino_ratio(equity_curve: pd.Series, rf_annual: float = 0.0, periods_per_year: int = 252) -> float:
    if equity_curve is None or len(equity_curve) < 3:
        return 0.0
    eq = pd.Series(equity_curve).astype(float).reset_index(drop=True)
    rets = eq.pct_change().dropna()
    if len(rets) < 2:
        return 0.0
    rf = rf_annual / periods_per_year
    excess = rets - rf
    downside = excess[excess < 0]
    denom = downside.std(ddof=1)
    if np.isnan(denom) or np.isclose(denom, 0.0):
        return 0.0
    return float((excess.mean() / denom) * np.sqrt(periods_per_year))


def _calmar_ratio(cagr_percent: float, max_dd_percent: float) -> float:
    if max_dd_percent == 0:
        return 0.0
    return float(cagr_percent / abs(max_dd_percent))


def _trade_stats(trades_df: pd.DataFrame) -> Tuple[float, int]:
    if trades_df is None or trades_df.empty or "Profit" not in trades_df.columns:
        return 0.0, 0
    wins = trades_df[trades_df["Profit"] > 0]
    win_rate = 100.0 * len(wins) / len(trades_df)
    return float(win_rate), int(len(trades_df))


def _equity_from_prices(close: pd.Series) -> pd.Series:
    if close is None or len(close) == 0:
        return pd.Series([STARTING_BALANCE])
    base = float(close.iloc[0])
    eq = (close.astype(float) / base) * STARTING_BALANCE
    return eq


def _returns_from_equity(equity_curve: pd.Series) -> pd.Series:
    if equity_curve is None:
        return pd.Series([], dtype=float)
    return pd.Series(equity_curve).astype(float).pct_change().dropna()


def _make_benchmark_returns(price_series: Optional[pd.Series]) -> pd.Series:
    if price_series is None:
        return pd.Series([], dtype=float)
    return pd.Series(price_series).astype(float).pct_change().dropna()


def apply_summary_excel_formatting(ws):
    """Apply simple formatting to the summary worksheet."""
    bold_font = Font(bold=True)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    for cell in ws[1]:
        wrap = cell.value == "Confusion Matrix"
        cell.font = bold_font
        cell.alignment = Alignment(horizontal="center", wrap_text=wrap)
        cell.border = thin_border

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = thin_border
            if cell.hyperlink is not None:
                cell.style = "Hyperlink"
            if ws.cell(row=1, column=cell.column).value == "Confusion Matrix":
                cell.alignment = Alignment(horizontal="left", wrap_text=True)

    for col_idx in range(1, ws.max_column + 1):
        max_len = 0
        for row_idx in range(1, ws.max_row + 1):
            value = ws.cell(row=row_idx, column=col_idx).value
            max_len = max(max_len, len(str(value)) if value is not None else 0)
        width = min(max_len + 4, 60)
        header = ws.cell(row=1, column=col_idx).value
        if header == "Confusion Matrix":
            width = max(width, 25)
        ws.column_dimensions[get_column_letter(col_idx)].width = width


# ---------------- Main Summary Writer ---------------- #

def create_and_save_backtest_summary_table_csv_file(
    summary_tickers: Sequence[str],
    summary_CAGRs: Sequence[float],
    summary_buy_hold_CAGRs: Sequence[float],
    summary_cagr_strategy_efficiencies: Sequence[float],
    summary_sharpe_ratios: Sequence[float],
    strategy_names: Optional[Sequence[str]] = None,
    model_numbers: Optional[Sequence[str]] = None,
    feature_set_ids: Optional[Sequence[str]] = None,
    signal_plot_links: Optional[Sequence[str]] = None,
    portfolio_plot_links: Optional[Sequence[str]] = None,
    portfolio_values_dict: Optional[Dict[str, pd.Series]] = None,
    trade_tables_dict: Optional[Dict[str, pd.DataFrame]] = None,
    price_series_dict: Optional[Dict[str, pd.Series]] = None,
    ml_metrics_dict: Optional[Dict[Tuple[str, str], Dict[str, str]]] = None,
    model_names: Optional[Sequence[str]] = None,
):
    """
    Builds per-ticker strategy rows following the Strategy Backtesting Performance schema.
    Returns (table_preview_str, excel_path) for backward compatibility.
    """
    os.makedirs(FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE, exist_ok=True)
    os.makedirs(FINAL_EXCEL_DIR, exist_ok=True)

    rows: List[Dict[str, object]] = []
    benchmark_returns_cache: Dict[str, pd.Series] = {}

    n = len(summary_tickers)
    for i in range(n):
        ticker = summary_tickers[i]
        strategy = (strategy_names[i] if strategy_names else "").lower()
        model_no = model_numbers[i] if model_numbers else ""
        feat_id = feature_set_ids[i] if feature_set_ids else ""
        model_label = model_names[i] if model_names else ""
        signal_plot = signal_plot_links[i] if signal_plot_links else ""
        portfolio_plot = portfolio_plot_links[i] if portfolio_plot_links else ""

        cagr = float(summary_CAGRs[i]) if summary_CAGRs[i] is not None else 0.0
        sharpe = float(summary_sharpe_ratios[i]) if summary_sharpe_ratios[i] is not None else 0.0

        pv_series = portfolio_values_dict.get(ticker) if portfolio_values_dict else None
        trades_df = trade_tables_dict.get(ticker) if trade_tables_dict else None
        close_series = price_series_dict.get(ticker) if price_series_dict else None

        strat_returns = _returns_from_equity(pv_series)
        if ticker not in benchmark_returns_cache:
            benchmark_returns_cache[ticker] = _make_benchmark_returns(close_series)
        benchmark_returns = benchmark_returns_cache[ticker]
        min_len = min(len(strat_returns), len(benchmark_returns))
        if min_len > 0:
            strat_aligned = pd.Series(strat_returns.iloc[-min_len:].to_numpy(), dtype=float)
            bench_aligned = pd.Series(benchmark_returns.iloc[-min_len:].to_numpy(), dtype=float)
        else:
            strat_aligned = pd.Series([], dtype=float)
            bench_aligned = pd.Series([], dtype=float)

        sortino = _sortino_ratio(pv_series, rf_annual=RISK_FREE_RATE)
        mdd = _max_drawdown(pv_series)
        calmar = _calmar_ratio(cagr, mdd)
        volatility = calculate_volatility(strat_returns)
        win_rate, num_trades = _trade_stats(trades_df)
        info_ratio = calculate_information_ratio(
            strat_aligned,
            bench_aligned,
            risk_free_rate=RISK_FREE_RATE / 252,
        ) if not strat_aligned.empty and not bench_aligned.empty else np.nan
        if strategy == "buy_and_hold":
            # Benchmark equals strategy; IR undefined -> set to NaN
            info_ratio = np.nan

        is_ml = strategy in {"logistic_regression", "random_forest", "xgboost", "mlp"}
        rows.append({
            "Strategy Name": strategy,
            "Ticker": ticker,
            "Model Name": model_label if is_ml else "",
            "Model Number": model_no if is_ml else "",
            "Feature Set ID": feat_id if is_ml else "",
            "CAGR (%)": round(cagr, 2),
            "Sharpe Ratio": round(sharpe, 2),
            "Sortino Ratio": round(sortino, 2),
            "Calmar Ratio": round(calmar, 2),
            "Max Drawdown (%)": round(mdd, 2),
            "Volatility": round(volatility, 4),
            "Win Rate (%)": round(win_rate, 2),
            "Number of Trades": num_trades,
            "Information Ratio": np.nan if np.isnan(info_ratio) else round(info_ratio, 4),
            "Strategy Plot Link": signal_plot,
            "Portfolio Value Plot Link": portfolio_plot,
        })

    df = pd.DataFrame(rows, columns=TABLE_COLUMNS)
    csv_path = os.path.join(
        FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE,
        f"summary_backtest_table_{TICKERS}.csv",
    )
    df.to_csv(csv_path, index=False)
    print(f"✅ Summary CSV with metrics saved at: {csv_path}")

    preview = tabulate(df, headers="keys", tablefmt="grid", floatfmt=".2f")
    print(f"\n✅ Summary rows written to CSV:\n{csv_path}\n")
    return preview, csv_path
