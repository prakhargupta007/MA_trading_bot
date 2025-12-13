import pandas as pd
from pathlib import Path

TICKERS = [
    "MSFT",
    "AAPL",
    "GOOG",
    "META",
    "ORCL",
    "ADBE",
    "TSLA",
    "AMD",
    "NVDA"
]

# Folder with sentiment CSVs
SENTIMENT_FOLDER = Path(__file__).parent / "GDELT" / "trading_days_daily_output"

# Folder with stored price data (backtest period)
PRICE_FOLDER = Path(__file__).parent.parent / "data" / "stored_data2"


def load_sentiment(ticker):
    filename = f"{ticker}_2_sentiment_trading_days.csv"
    path = SENTIMENT_FOLDER / filename
    if not path.exists():
        print(f"[WARNING] Missing sentiment file for {ticker}: {filename}")
        return None

    df = pd.read_csv(path)
    df["day"] = pd.to_datetime(df["day"])
    return df.set_index("day")


def load_backtest_price_index(ticker):
    files = list(PRICE_FOLDER.glob(f"data_{ticker}_backtest_*.csv"))
    if len(files) == 0:
        print(f"[WARNING] No backtest file found for {ticker}")
        return None

    path = files[0]
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date").index


def analyze_ticker(ticker):
    sentiment = load_sentiment(ticker)
    price_index = load_backtest_price_index(ticker)

    if sentiment is None or price_index is None:
        return None

    # Align sentiment to price trading days
    aligned = sentiment.reindex(price_index)

    # Missing sentiment inside trading-day index
    missing_mask = aligned.isna().any(axis=1)
    missing_days = list(price_index[missing_mask])

    # EXTRA sentiment days outside the price index
    sentiment_index = sentiment.index
    extra_days = list(sentiment_index.difference(price_index))

    total_days = len(price_index)
    missing_count = len(missing_days)
    extra_count = len(extra_days)
    pct_missing = (missing_count / total_days) * 100

    return {
        "ticker": ticker,
        "total_days": total_days,
        "sentiment_rows": len(sentiment),
        "missing_days": missing_count,
        "extra_days": extra_count,
        "pct_missing": round(pct_missing, 2),
        "missing_dates": missing_days,
        "extra_date_list": extra_days
    }


def main():
    print("\n=== SENTIMENT COVERAGE VS PRICE DATA ===\n")
    print(f"{'Ticker':<8} {'Trading Days':<15} {'Sentiment Rows':<18} "
          f"{'Missing':<10} {'Extra':<10} {'% Missing':<10}")
    print("-" * 90)

    for ticker in TICKERS:
        result = analyze_ticker(ticker)
        if result is None:
            continue

        print(f"{ticker:<8} "
              f"{result['total_days']:<15} "
              f"{result['sentiment_rows']:<18} "
              f"{result['missing_days']:<10} "
              f"{result['extra_days']:<10} "
              f"{result['pct_missing']:<10}")

    print("\n=== Missing Sentiment Dates Per Ticker ===\n")
    for ticker in TICKERS:
        result = analyze_ticker(ticker)
        if result and result["missing_days"] > 0:
            print(f"{ticker}: {result['missing_days']} missing days")
            for d in result["missing_dates"]:
                print(f"  - {d.date()}")
            print()

    print("\n=== EXTRA Sentiment Dates (Rows not in price-data trading index) ===\n")
    for ticker in TICKERS:
        result = analyze_ticker(ticker)
        if result and result["extra_days"] > 0:
            print(f"{ticker}: {result['extra_days']} extra sentiment rows")
            for d in result["extra_date_list"]:
                print(f"  - {d.date()}")
            print()


if __name__ == "__main__":
    main()
