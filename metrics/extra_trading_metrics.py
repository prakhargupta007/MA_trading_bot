import numpy as np
import pandas as pd

def max_drawdown(equity_curve: pd.Series) -> float:
    """
    equity_curve: series of portfolio values indexed by date.
    return: max drawdown in percent (negative value)
    """
    if len(equity_curve) < 2:
        return 0.0
    rolling_max = equity_curve.cummax()
    drawdowns = equity_curve / rolling_max - 1.0
    return float(100.0 * drawdowns.min())

def sortino_ratio(equity_curve: pd.Series, risk_free_rate_annual: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Uses downside deviation only.
    """
    returns = equity_curve.pct_change().dropna()
    rf = risk_free_rate_annual / periods_per_year
    excess = returns - rf
    downside = excess[excess < 0]
    if downside.empty:
        return 0.0
    dd = downside.std(ddof=1)
    if dd == 0:
        return 0.0
    mean_excess = excess.mean()
    return float(mean_excess / dd * np.sqrt(periods_per_year))

def calmar_ratio(cagr_percent: float, max_dd_percent: float) -> float:
    """
    CAGR (%) divided by |MaxDD| (%). If MaxDD is 0, returns 0 to avoid inf.
    """
    if max_dd_percent == 0:
        return 0.0
    return float(cagr_percent / abs(max_dd_percent))

def winrate_avgwins_avgloss_profitfactor(trades_df: pd.DataFrame) -> tuple:
    """
    trades_df must contain per-trade P&L as a column named 'Profit' (in currency or %).
    Returns: (win_rate_percent, avg_win, avg_loss, profit_factor)
    """
    if trades_df is None or trades_df.empty or "Profit" not in trades_df.columns:
        return (0.0, 0.0, 0.0, 0.0)

    wins = trades_df[trades_df["Profit"] > 0]["Profit"]
    losses = trades_df[trades_df["Profit"] < 0]["Profit"]

    win_rate = 100.0 * (len(wins) / max(1, len(trades_df)))
    avg_win = float(wins.mean()) if len(wins) else 0.0
    avg_loss = float(losses.mean()) if len(losses) else 0.0

    gross_profit = wins.sum()
    gross_loss = abs(losses.sum())
    profit_factor = float(gross_profit / gross_loss) if gross_loss > 0 else 0.0

    return (win_rate, avg_win, avg_loss, profit_factor)
