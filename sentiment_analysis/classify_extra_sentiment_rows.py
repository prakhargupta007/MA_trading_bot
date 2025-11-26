import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import pandas as pd

TICKERS = [
    "MSFT",
    "AAPL",
    "GOOG",
    "META",
    "ORCL",
    "ADBE",
    "TSLA",
    "AMD",
    "NVDA",
]

NYSE_HOLIDAYS: Set[pd.Timestamp] = {
    pd.Timestamp(d) for d in {
        "2021-01-01","2021-01-18","2021-02-15","2021-04-02","2021-05-31",
        "2021-07-05","2021-09-06","2021-11-25","2021-12-24",
        "2022-01-17","2022-02-21","2022-04-15","2022-05-30","2022-06-20",
        "2022-07-04","2022-09-05","2022-11-24","2022-12-26",
        "2023-01-02","2023-01-16","2023-02-20","2023-04-07","2023-05-29",
        "2023-06-19","2023-07-04","2023-09-04","2023-11-23","2023-12-25",
        "2024-01-01","2024-01-15","2024-02-19","2024-03-29","2024-05-27",
        "2024-06-19","2024-07-04","2024-09-02","2024-11-28","2024-12-25",
        "2025-01-01","2025-01-20","2025-02-17","2025-04-18","2025-05-26",
        "2025-06-19","2025-07-04","2025-09-01","2025-11-27","2025-12-25",
    }
}

SENTIMENT_DIR = Path("sentiment_analysis/GDELT/trading_days_daily_output")
PRICE_DIR = Path("data/stored_data2")


def load_price_index(ticker: str) -> pd.DatetimeIndex:
    pattern = f"data_{ticker}_backtest_"
    matches = sorted(PRICE_DIR.glob(f"{pattern}*.csv"))
    if not matches:
        raise FileNotFoundError(f"No price backtest file found for {ticker}")
    df = pd.read_csv(matches[0], parse_dates=["Date"])
    return pd.DatetimeIndex(df["Date"].dropna().unique())


def load_sentiment_index(ticker: str) -> pd.DatetimeIndex:
    csv_path = SENTIMENT_DIR / f"{ticker}_1_sentiment_trading_days.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Sentiment file missing for {ticker}")
    df = pd.read_csv(csv_path, parse_dates=["day"])
    return pd.DatetimeIndex(df["day"].dropna())


def classify_dates(extra_dates: Set[pd.Timestamp], price_index: pd.DatetimeIndex, duplicates: Set[pd.Timestamp]) -> Dict[str, List[pd.Timestamp]]:
    results: Dict[str, List[pd.Timestamp]] = {
        "OUTSIDE_PERIOD_BEFORE": [],
        "OUTSIDE_PERIOD_AFTER": [],
        "WEEKEND": [],
        "HOLIDAY": [],
        "DUPLICATE": [],
        "UNKNOWN": [],
    }
    if len(price_index) == 0:
        for date in extra_dates:
            results["UNKNOWN"].append(date)
        return results

    min_price = price_index.min()
    max_price = price_index.max()

    for date in sorted(extra_dates):
        if date < min_price:
            results["OUTSIDE_PERIOD_BEFORE"].append(date)
            continue
        if date > max_price:
            results["OUTSIDE_PERIOD_AFTER"].append(date)
            continue
        if date in duplicates:
            results["DUPLICATE"].append(date)
            continue
        if date.weekday() >= 5:
            results["WEEKEND"].append(date)
            continue
        if date in NYSE_HOLIDAYS:
            results["HOLIDAY"].append(date)
            continue
        results["UNKNOWN"].append(date)

    return results


def detect_duplicate_dates(index: pd.DatetimeIndex) -> Set[pd.Timestamp]:
    counts = Counter(index)
    return {date for date, count in counts.items() if count > 1}


def report_ticker(ticker: str) -> Dict[str, int]:
    sentiment_index = load_sentiment_index(ticker)
    price_index = load_price_index(ticker)
    sentiment_dates = set(sentiment_index)
    price_dates = set(price_index)

    extra_dates = sentiment_dates - price_dates
    duplicates = detect_duplicate_dates(sentiment_index)

    classification = classify_dates(extra_dates, price_index, duplicates)

    print(f"=== EXTRA ROW CLASSIFICATION: {ticker} ===")
    print(f"Total Extra Rows: {len(extra_dates)}")
    for key in [
        "OUTSIDE_PERIOD_BEFORE",
        "OUTSIDE_PERIOD_AFTER",
        "WEEKEND",
        "HOLIDAY",
        "DUPLICATE",
        "UNKNOWN",
    ]:
        print(f"{key.replace('_', ' ').title()}: {len(classification[key])}")

    # Examples
    examples = []
    for category, dates in classification.items():
        if dates:
            for date in dates[:3]:
                examples.append(f"  - {date.date()} {category}")
            break
    if not examples:
        print("Examples: none")
    else:
        print("Examples:")
        for example in examples:
            print(example)
    print()

    summary = {
        "Ticker": ticker,
        "Extra": len(extra_dates),
        "Before": len(classification["OUTSIDE_PERIOD_BEFORE"]),
        "After": len(classification["OUTSIDE_PERIOD_AFTER"]),
        "Weekend": len(classification["WEEKEND"]),
        "Holiday": len(classification["HOLIDAY"]),
        "Duplicate": len([d for d in duplicates if d in extra_dates]),
        "Unknown": len(classification["UNKNOWN"]),
    }
    return summary


def main():
    summaries = []
    for ticker in TICKERS:
        try:
            summary = report_ticker(ticker)
            summaries.append(summary)
        except Exception as exc:
            print(f"[ERROR] {ticker}: {exc}")

    if summaries:
        print("Ticker | Extra | Before | After | Weekend | Holiday | Duplicate | Unknown")
        for s in summaries:
            print(
                f"{s['Ticker']} | {s['Extra']} | {s['Before']} | {s['After']} | "
                f"{s['Weekend']} | {s['Holiday']} | {s['Duplicate']} | {s['Unknown']}"
            )


if __name__ == "__main__":
    main()
