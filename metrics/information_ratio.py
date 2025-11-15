import numpy as np
import pandas as pd


def calculate_information_ratio(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0.0,
) -> float:
    """
    Information Ratio = mean(strategy - benchmark - rf) / std(strategy - benchmark).
    Returns NaN when insufficient data or zero tracking-error volatility.
    """
    if strategy_returns is None or benchmark_returns is None:
        return np.nan

    strat = pd.Series(strategy_returns).dropna()
    bench = pd.Series(benchmark_returns).dropna()
    if strat.empty or bench.empty:
        return np.nan

    aligned = strat.align(bench, join="inner")[0] - bench
    if aligned.empty:
        return np.nan

    excess = aligned - risk_free_rate
    tracking_error = excess.std(ddof=1)
    if np.isnan(tracking_error) or np.isclose(tracking_error, 0.0):
        return np.nan

    return float(excess.mean() / tracking_error)
