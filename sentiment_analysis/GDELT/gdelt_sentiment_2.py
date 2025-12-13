# This is the ticker configuration for all tickers except for QQQ
'''
TICKER_CONFIG = {
    "AAPL": {
        "keywords": [
            "Apple",
            "AAPL",
            "iPhone",
            "iPad",
            "MacBook",
            "Apple Watch",
            "Tim Cook",
        ],
        "exclusion_keywords": [
            "apple juice",
            "apple orchard",
            "apple pie",
            "apple trees",
            "apple sauce",
        ],
        "number": "2",
    "MSFT": {
        "keywords": [
            "Microsoft",
            "MSFT",
            "Windows",
            "Office 365",
            "Azure",
            "Xbox",
            "Satya Nadella",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
    "GOOG": {
        "keywords": [
            "Google",
            "Alphabet",
            "GOOG",
            "GOOGL",
            "YouTube",
            "Google Cloud",
            "Sundar Pichai",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
    "META": {
        "keywords": [
            "Meta",
            "Meta Platforms",
            "Facebook",
            "FB",
            "Instagram",
            "WhatsApp",
            "Zuckerberg",
        ],
        "exclusion_keywords": [
            "metamaterial", "metamaterials", "mmat",
            "meta material", "meta materials",
            "metalenz",
            "meta bank", "meta financial", "meta financial group",
            "meta-analysis", "meta analysis",
            "systematic review",
            "review and meta analysis",
            "ilir meta", "president meta",
            "meta asian", "meta kitchen",
            "warzone meta", "league meta", "fortnite meta",
            "gaming meta", "game meta", "cod meta",
            "attacker sided meta",
            "meta descriptions", "meta description",
            "metadata", "meta registry",
            "meta-holographic", "metasurface",
            "commencal meta", "meta power",
            "meta vr camera", "meta aramid",
            "meta wave", "meta quater",
        ],
        "number": "2",
    },
    "ORCL": {
        "keywords": [
            "Oracle",
            "ORCL",
            "Larry Ellison",
            "Oracle Cloud",
        ],
        "exclusion_keywords": [
            "oracle of delphi",
            "tarot",
            "horoscope",
            "fortune teller",
        ],
        "number": "2",
    },
    "ADBE": {
        "keywords": [
            "Adobe",
            "ADBE",
            "Photoshop",
            "Illustrator",
            "Premiere Pro",
            "Creative Cloud",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
    "TSLA": {
        "keywords": [
            "Tesla",
            "TSLA",
            "Elon Musk",
            "Model 3",
            "Model Y",
            "Gigafactory",
        ],
        "exclusion_keywords": [
            "tesla coil",
            "nikola tesla",
        ],
        "number": "2",
    },
    "AMD": {
        "keywords": [
            "AMD",
            "Advanced Micro Devices",
            "Ryzen",
            "EPYC",
            "Radeon",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
    "NVDA": {
        "keywords": [
            "Nvidia",
            "NVDA",
            "GeForce",
            "RTX",
            "CUDA",
            "Jensen Huang",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
}
'''














from datetime import datetime, timedelta
import os
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import time

# =====================================================================================
# IMPORTANT NOTE
# This script is designed to generate sentiment aligned to your *existing* backtest
# price CSVs in data/stored_data2 (data_{TICKER}_backtest_*.csv).
#
# It assumes your backtest window is roughly 2021-01-01 to 2025-10-24 and uses the
# trading days from those CSVs as the ONLY truth for which dates are trading days.
#
# Weekend and holiday sentiment is aggregated forward into the NEXT available
# trading day. Trading days with no sentiment at all are filled with a NEUTRAL
# sentiment vector: prob_negative=0.0, prob_neutral=1.0, prob_positive=0.0.
# =====================================================================================

# ===================== CONFIGURATION =====================

# All 9 main tickers (QQQ excluded on purpose)
TICKERS = [ "MSFT", "AAPL", "GOOG", "META", "ORCL", "ADBE", "TSLA", "AMD", "NVDA", ]

TICKER_CONFIG = {
    "MSFT": {
        "keywords": [
            "Microsoft",
            "MSFT",
            "Windows",
            "Office 365",
            "Azure",
            "Xbox",
            "Satya Nadella",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
    "AAPL": {
        "keywords": [
            "Apple",
            "AAPL",
            "iPhone",
            "iPad",
            "MacBook",
            "Apple Watch",
            "Tim Cook",
        ],
        "exclusion_keywords": [
            "apple juice",
            "apple orchard",
            "apple pie",
            "apple trees",
            "apple sauce",
        ],
        "number": "2",
    },
    "GOOG": {
        "keywords": [
            "Google",
            "Alphabet",
            "GOOG",
            "GOOGL",
            "YouTube",
            "Google Cloud",
            "Sundar Pichai",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
    "META": {
        "keywords": [
            "Meta",
            "Meta Platforms",
            "Facebook",
            "FB",
            "Instagram",
            "WhatsApp",
            "Zuckerberg",
        ],
        "exclusion_keywords": [
            "metamaterial", "metamaterials", "mmat",
            "meta material", "meta materials",
            "metalenz",
            "meta bank", "meta financial", "meta financial group",
            "meta-analysis", "meta analysis",
            "systematic review",
            "review and meta analysis",
            "ilir meta", "president meta",
            "meta asian", "meta kitchen",
            "warzone meta", "league meta", "fortnite meta",
            "gaming meta", "game meta", "cod meta",
            "attacker sided meta",
            "meta descriptions", "meta description",
            "metadata", "meta registry",
            "meta-holographic", "metasurface",
            "commencal meta", "meta power",
            "meta vr camera", "meta aramid",
            "meta wave", "meta quater",
        ],
        "number": "2",
    },
    "ORCL": {
        "keywords": [
            "Oracle",
            "ORCL",
            "Larry Ellison",
            "Oracle Cloud",
        ],
        "exclusion_keywords": [
            "oracle of delphi",
            "tarot",
            "horoscope",
            "fortune teller",
        ],
        "number": "2",
    },
    "ADBE": {
        "keywords": [
            "Adobe",
            "ADBE",
            "Photoshop",
            "Illustrator",
            "Premiere Pro",
            "Creative Cloud",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
    "TSLA": {
        "keywords": [
            "Tesla",
            "TSLA",
            "Elon Musk",
            "Model 3",
            "Model Y",
            "Gigafactory",
        ],
        "exclusion_keywords": [
            "tesla coil",
            "nikola tesla",
        ],
        "number": "2",
    },
    "AMD": {
        "keywords": [
            "AMD",
            "Advanced Micro Devices",
            "Ryzen",
            "EPYC",
            "Radeon",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
    "NVDA": {
        "keywords": [
            "Nvidia",
            "NVDA",
            "GeForce",
            "RTX",
            "CUDA",
            "Jensen Huang",
        ],
        "exclusion_keywords": [],
        "number": "2",
    },
}


# GDELT fetch window (roughly matches your backtest)
DATE_START = "20210101"
#DATE_END = "20211231"
DATE_END = "20251024"
CHUNK_DAYS = 30

# Paths (keep as in your original script)
FULL_OUTPUT_FOLDER = "/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/full_output_folder"
DAILY_OUTPUT_FOLDER = "/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/daily_output_folder"
TRADING_DAYS_OUTPUT_FOLDER = "/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/trading_days_daily_output"

# Price data folder for trading calendar
PRICE_FOLDER = Path(__file__).resolve().parents[2] / "data" / "stored_data2"

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# (Optional) Hardcoded NYSE holidays 2021–2025 for reference / debugging.
# The core algorithm uses the price CSV trading calendar, so these are not
# strictly necessary, but we keep them here for clarity.
NYSE_HOLIDAYS_2021_2025 = {
    # 2021
    "2021-01-01", "2021-01-18", "2021-02-15", "2021-04-02",
    "2021-05-31", "2021-07-05", "2021-09-06", "2021-11-25", "2021-12-24",
    # 2022
    "2022-01-17", "2022-02-21", "2022-04-15", "2022-05-30",
    "2022-06-20", "2022-07-04", "2022-09-05", "2022-11-24", "2022-12-26",
    # 2023
    "2023-01-02", "2023-01-16", "2023-02-20", "2023-04-07",
    "2023-05-29", "2023-06-19", "2023-07-04", "2023-09-04",
    "2023-11-23", "2023-12-25",
    # 2024
    "2024-01-01", "2024-01-15", "2024-02-19", "2024-03-29",
    "2024-05-27", "2024-06-19", "2024-07-04", "2024-09-02",
    "2024-11-28", "2024-12-25",
    # 2025
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18",
    "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01",
    "2025-11-27", "2025-12-25",
}
# ==========================================================


# ---------- Helper: Format GDELT datetime ----------
def format_to_day(iso_str: str) -> str:
    return datetime.strptime(iso_str, "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")


# ---------- NEW: Check if a headline is truly financial ----------
def is_financial_headline(ticker: str, headline: str) -> bool:
    """Return False if a headline contains exclusion keywords (non-financial context)."""
    if not headline or ticker not in TICKER_CONFIG:
        return True
    headline_lower = headline.lower()
    for bad_word in TICKER_CONFIG[ticker].get("exclusion_keywords", []):
        if bad_word in headline_lower:
            return False
    return True
# ---------------------------------------------------------------


# ---------- Load sentiment model ----------
def load_sentiment_model(model_name: str):
    print("🔹 Loading sentiment model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        use_safetensors=True,
    )
    model.eval()

    id2label = {i: lbl.lower() for i, lbl in getattr(model.config, "id2label", {}).items()}
    if not id2label:
        num_labels = model.config.num_labels
        id2label = {0: "negative", 1: ("positive" if num_labels == 2 else "neutral")}
        if num_labels == 3:
            id2label[2] = "positive"
    return tokenizer, model, id2label


# ---------- Fetch GDELT news ----------
def fetch_articles_robust(keywords, start_date, end_date, output_file, chunk_days, max_retries=1):
    print(f"🔹 Fetching news from GDELT for keywords: {keywords}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")

    if os.path.exists(output_file):
        print(f"⚠️ Output file {output_file} already exists. It will be appended to.")
        df_full = pd.read_csv(output_file)
        if "seendate" in df_full.columns:
            last_day = df_full["seendate"].max()
            start_dt = datetime.strptime(str(last_day), "%Y%m%d") + timedelta(days=1)
    else:
        df_full = pd.DataFrame()

    current_start = start_dt
    while current_start <= end_dt:
        current_end = min(current_start + timedelta(days=chunk_days - 1), end_dt)
        for attempt in range(1, max_retries + 1):
            try:
                print(
                    f"   • Fetching chunk: {current_start.strftime('%Y%m%d')} → "
                    f"{current_end.strftime('%Y%m%d')} (Attempt {attempt})"
                )
                query = f"({' OR '.join(keywords)})"
                url = (
                    f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}"
                    f"&mode=ArtList&maxrecords=250&format=json"
                    f"&startdatetime={current_start.strftime('%Y%m%d')}000000"
                    f"&enddatetime={current_end.strftime('%Y%m%d')}235959"
                )
                resp = requests.get(url, timeout=30)
                if resp.status_code != 200:
                    raise ValueError(f"Status code {resp.status_code}")
                if not resp.text.strip():
                    break
                data = resp.json()
                if "articles" not in data or not data["articles"]:
                    break
                df_chunk = pd.DataFrame(data["articles"])
                if not df_chunk.empty:
                    df_chunk.to_csv(
                        output_file,
                        mode="a",
                        index=False,
                        header=not os.path.exists(output_file),
                    )
                    print(f"      ✅ Saved {len(df_chunk)} articles")
                break
            except Exception as e:
                print(f"      ⚠️ Error: {e}")
                time.sleep(5)
        current_start = current_end + timedelta(days=1)

    print(f"✅ Finished fetching. Full file at {output_file}")
    return pd.read_csv(output_file) if os.path.exists(output_file) else pd.DataFrame()


# ---------- Deduplicate ----------
def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    print("🔹 Deduplicating headlines...")
    if "title" not in df.columns:
        return df
    return df.drop_duplicates(subset=["title"], keep="first")


# ---------- Filter headlines (UPDATED) ----------
def filter_headlines_by_keywords(df: pd.DataFrame, keywords, ticker=None) -> pd.DataFrame:
    print("🔹 Filtering headlines by keywords...")
    if "title" not in df.columns:
        return pd.DataFrame(columns=df.columns)

    keywords_lower = [k.lower() for k in keywords]
    pattern = "|".join(keywords_lower)
    df_filtered = df[df["title"].str.lower().str.contains(pattern, na=False)].copy()

    # Exclusion filtering
    if ticker:
        df_filtered = df_filtered[df_filtered["title"].apply(lambda t: is_financial_headline(ticker, t))]

    return df_filtered


# ---------- Run sentiment ----------
def run_sentiment(df: pd.DataFrame, tokenizer, model, id2label) -> pd.DataFrame:
    print("🔹 Running sentiment analysis...")
    texts = df["title"].fillna("").tolist()
    labels, probs_list = [], []
    label_names = [lbl for _, lbl in sorted(id2label.items())]

    for i, txt in enumerate(texts, 1):
        inputs = tokenizer(txt, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0].tolist()
        pred_idx = int(torch.argmax(logits))
        labels.append(id2label[pred_idx])
        probs_list.append(probs)
        if i % 10 == 0 or i == len(texts):
            print(f"   ✅ Processed {i}/{len(texts)} headlines")

    df = df.copy()
    df["sentiment"] = labels
    for idx, lbl in enumerate(label_names):
        df[f"prob_{lbl}"] = [p[idx] for p in probs_list]
    return df


# ---------- Add formatted day ----------
def add_formatted_day(df: pd.DataFrame) -> pd.DataFrame:
    if "seendate" not in df.columns:
        raise ValueError("Expected 'seendate' column from GDELT response.")
    df = df.copy()
    df["day"] = df["seendate"].apply(format_to_day)
    return df


# ---------- Save full file ----------
def save_full_file(df: pd.DataFrame, output_path: str) -> pd.DataFrame:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cols = ["day", "title", "url", "sentiment", "prob_negative", "prob_neutral", "prob_positive"]
    df_full = df[cols]
    df_full.to_csv(output_path, index=False)
    print(f"✅ Full sentiment file saved: {output_path}")
    return df_full


# ---------- Aggregate daily ----------
def aggregate_daily(df_full: pd.DataFrame) -> pd.DataFrame:
    print("🔹 Aggregating daily sentiment...")
    daily = (
        df_full.groupby("day")[["prob_negative", "prob_neutral", "prob_positive"]]
        .mean()
        .reset_index()
    )
    daily["sentiment"] = (
        daily[["prob_negative", "prob_neutral", "prob_positive"]]
        .idxmax(axis=1)
        .str.replace("prob_", "")
    )
    daily["mean"] = daily.apply(lambda r: r[f"prob_{r['sentiment']}"], axis=1)
    return daily[["day", "prob_negative", "prob_neutral", "prob_positive", "sentiment", "mean"]]



# ---------- Load trading calendar from stored_data2 ----------
def load_trading_calendar(ticker: str) -> pd.DatetimeIndex:
    """
    Loads the backtest price CSV for a ticker and returns its Date index
    as the authoritative trading calendar.
    """
    files = list(PRICE_FOLDER.glob(f"data_{ticker}_backtest_*.csv"))
    if not files:
        raise FileNotFoundError(f"No backtest price file found for {ticker} in {PRICE_FOLDER}")
    # Take the first match (your naming convention should ensure it's the correct one)
    path = files[0]
    df = pd.read_csv(path)
    if "Date" not in df.columns:
        raise ValueError(f"Expected a 'Date' column in {path}")
    df["Date"] = pd.to_datetime(df["Date"])
    trading_index = df["Date"].sort_values().drop_duplicates()
    trading_index = pd.DatetimeIndex(trading_index)
    return trading_index


# ---------- Align / fold sentiment into trading days ----------
def fold_sentiment_to_trading_days(daily_df: pd.DataFrame, trading_index: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Your logic:
    - Sentiment from a calendar day affects the NEXT trading day's decision.
    - Because sentiment is only known after market close, we fold backward:
      calendar day → previous trading day.
    - Weekend and holidays get folded into the last open session.
    """

    print("🔹 Folding sentiment BACKWARD into trading days (your logic)...")

    vec_cols = ["prob_negative", "prob_neutral", "prob_positive"]

    # If no sentiment at all → fill with neutral
    if daily_df.empty:
        out = pd.DataFrame(index=trading_index, columns=vec_cols, dtype=float)
        out["prob_negative"] = 0.0
        out["prob_neutral"] = 1.0
        out["prob_positive"] = 0.0
        out["sentiment"] = "neutral"
        out["mean"] = 1.0

        out.index.name = "day"      # FIX
        out = out.reset_index()
        return out[["day", "prob_negative", "prob_neutral", "prob_positive", "sentiment", "mean"]]


    df = daily_df.copy()
    df["day"] = pd.to_datetime(df["day"])
    df = df.sort_values("day").reset_index(drop=True)

    trading_index = pd.DatetimeIndex(trading_index.sort_values())
    first_trading = trading_index.min()
    last_trading = trading_index.max()

    # Sum and count containers
    agg_sum = pd.DataFrame(0.0, index=trading_index, columns=vec_cols)
    agg_count = pd.Series(0, index=trading_index, dtype=int)

    # BACKWARD mapping
    for _, row in df.iterrows():
        day = row["day"]

        if day > last_trading:
            continue

        pos = trading_index.get_indexer([day], method="ffill")[0]
        if pos == -1:
            continue

        t_day = trading_index[pos]

        agg_sum.loc[t_day, vec_cols] += row[vec_cols].values
        agg_count.loc[t_day] += 1

    out = agg_sum.copy()
    has_sent = agg_count > 0

    out.loc[has_sent, vec_cols] = agg_sum.loc[has_sent, vec_cols].div(
        agg_count[has_sent], axis=0
    )

    out.loc[~has_sent, "prob_negative"] = 0.0
    out.loc[~has_sent, "prob_neutral"] = 1.0
    out.loc[~has_sent, "prob_positive"] = 0.0

    labels = np.array(["negative", "neutral", "positive"])
    probs = out[vec_cols].to_numpy()
    idx = probs.argmax(axis=1)
    out["sentiment"] = labels[idx]
    out["mean"] = probs[np.arange(len(probs)), idx]

    out.index.name = "day"          # <<< THE FIX
    out = out.reset_index()

    return out[["day", "sentiment", "prob_negative", "prob_neutral", "prob_positive", "mean"]]




# ---------- Save daily ----------
def save_daily_file(daily_df: pd.DataFrame, output_path: str):
    if daily_df.empty:
        print(f"⚠️ No daily data for {output_path}. Skipping.")
        return
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    daily_df.to_csv(output_path, index=False)
    print(f"✅ Daily aggregated file saved: {output_path}")


# ---------- Save trading days ----------
def save_trading_days_file(df: pd.DataFrame, output_path: str):
    if df.empty:
        print(f"⚠️ No trading-day data to save for {output_path}. Skipping.")
        return
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Trading-day file saved: {output_path}")


# ---------- MAIN ----------
def main():
    tokenizer, model, id2label = load_sentiment_model(MODEL_NAME)

    for ticker in TICKERS:
        print("\n" + "=" * 80)
        print(f"🚀 Processing ticker: {ticker}")
        print("=" * 80)

        cfg = TICKER_CONFIG.get(ticker)
        if cfg is None:
            print(f"⚠️ No TICKER_CONFIG entry for {ticker}, skipping.")
            continue

        keywords = cfg["keywords"]
        num = cfg["number"]

        full_output = f"{FULL_OUTPUT_FOLDER}/{ticker}_{num}_sentiment_full.csv"
        daily_output = f"{DAILY_OUTPUT_FOLDER}/{ticker}_{num}_sentiment_daily.csv"
        trading_output = f"{TRADING_DAYS_OUTPUT_FOLDER}/{ticker}_{num}_sentiment_trading_days.csv"

        # 1. Fetch articles
        articles = fetch_articles_robust(
            keywords,
            DATE_START,
            DATE_END,
            full_output,
            CHUNK_DAYS,
        )
        if articles.empty:
            print(f"⚠️ No articles found for {ticker}. Skipping.")
            continue

        # 2. Deduplicate
        articles = deduplicate(articles)

        # 3. Filter by keywords + exclusions
        articles = filter_headlines_by_keywords(articles, keywords, ticker=ticker)
        if articles.empty:
            print(f"⚠️ No filtered articles for {ticker}. Skipping.")
            continue

        # 4. Run sentiment
        articles = run_sentiment(articles, tokenizer, model, id2label)

        # 5. Add 'day'
        articles = add_formatted_day(articles)

        # 6. Save full file
        full_df = save_full_file(articles, full_output)

        # 7. Aggregate by calendar day
        daily_df = aggregate_daily(full_df)
        save_daily_file(daily_df, daily_output)

        # 8. Load trading calendar from price CSV
        trading_index = load_trading_calendar(ticker)

        # 9. Fold + align to trading days using price calendar
        trading_df = fold_sentiment_to_trading_days(daily_df, trading_index)

        # 10. Save trading-day file
        save_trading_days_file(trading_df, trading_output)

        print(f"✅ Done with {ticker}\n")

    print("🎯 All tickers processed successfully.")


if __name__ == "__main__":
    main()



