from datetime import datetime, timedelta
import os
import pandas as pd
import requests
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import yfinance as yf
import time

# ===================== CONFIGURATION =====================
TICKER_CONFIG = {
    "META": {
        # Broad, reliable keywords that actually appear in headlines
        "keywords": [
            "Meta",            # most common
            "Meta Platforms",
            "Facebook",
            "FB",
            "Instagram",
            "WhatsApp",
            "Zuckerberg",
        ],

        # Aggressive exclusions to block non-company META noise
        "exclusion_keywords": [
            # Unrelated companies
            "metamaterial", "metamaterials", "mmat",
            "meta material", "meta materials",
            "metalenz",

            # Meta Financial (bank)
            "meta bank", "meta financial", "meta financial group",

            # Medical / scientific
            "meta-analysis", "meta analysis",
            "systematic review",
            "review and meta analysis",

            # Albanian president
            "ilir meta", "president meta",

            # Restaurants / food
            "meta asian", "meta kitchen",

            # Gaming meta
            "warzone meta", "league meta", "fortnite meta",
            "gaming meta", "game meta", "cod meta",
            "attacker sided meta",

            # SEO & metadata
            "meta descriptions", "meta description",
            "metadata", "meta registry",
            "meta-holographic", "metasurface",

            # Bikes, random companies
            "commencal meta", "meta power",
            "meta vr camera", "meta aramid",

            # Random political/geographic
            "meta wave", "meta quater",
        ],

        "number": "1",
    }
}


DATE_START = "20210101"
DATE_END = "20251024"
CHUNK_DAYS = 30

FULL_OUTPUT_FOLDER = "/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/full_output_folder"
DAILY_OUTPUT_FOLDER = "/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/daily_output_folder"
TRADING_DAYS_OUTPUT_FOLDER = "/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/trading_days_daily_output"

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
# ==========================================================


# ---------- Helper: Format GDELT datetime ----------
def format_to_day(iso_str):
    return datetime.strptime(iso_str, "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")


# ---------- NEW: Check if a headline is truly financial ----------
def is_financial_headline(ticker, headline):
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
def load_sentiment_model(model_name):
    print("🔹 Loading sentiment model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, use_safetensors=True)
    model.eval()

    id2label = {i: lbl.lower() for i, lbl in getattr(model.config, "id2label", {}).items()}
    if not id2label:
        num_labels = model.config.num_labels
        id2label = {0: "negative", 1: ("positive" if num_labels == 2 else "neutral")}
        if num_labels == 3:
            id2label[2] = "positive"
    return tokenizer, model, id2label


# ---------- Fetch GDELT news ----------
def fetch_articles_robust(keywords, start_date, end_date, output_file, CHUNK_DAYS, max_retries=1):
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
        current_end = min(current_start + timedelta(days=CHUNK_DAYS - 1), end_dt)
        for attempt in range(1, max_retries + 1):
            try:
                print(f"   • Fetching chunk: {current_start.strftime('%Y%m%d')} → {current_end.strftime('%Y%m%d')} (Attempt {attempt})")
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
                    df_chunk.to_csv(output_file, mode="a", index=False, header=not os.path.exists(output_file))
                    print(f"      ✅ Saved {len(df_chunk)} articles")
                break
            except Exception as e:
                print(f"      ⚠️ Error: {e}")
                time.sleep(5)
        current_start = current_end + timedelta(days=1)
    print(f"✅ Finished fetching. Full file at {output_file}")
    return pd.read_csv(output_file) if os.path.exists(output_file) else pd.DataFrame()


# ---------- Deduplicate ----------
def deduplicate(df):
    print("🔹 Deduplicating headlines...")
    return df.drop_duplicates(subset=["title"], keep="first")


# ---------- Filter headlines (UPDATED) ----------
def filter_headlines_by_keywords(df, keywords, ticker=None):  # 🔹 MODIFIED SIGNATURE
    print("🔹 Filtering headlines by keywords...")
    keywords_lower = [k.lower() for k in keywords]
    pattern = "|".join(keywords_lower)
    df_filtered = df[df["title"].str.lower().str.contains(pattern, na=False)].copy()

    # 🔹 NEW: Exclusion filtering
    if ticker:
        df_filtered = df_filtered[df_filtered["title"].apply(lambda t: is_financial_headline(ticker, t))]

    return df_filtered


# ---------- Run sentiment ----------
def run_sentiment(df, tokenizer, model, id2label):
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

    df["sentiment"] = labels
    for idx, lbl in enumerate(label_names):
        df[f"prob_{lbl}"] = [p[idx] for p in probs_list]
    return df


# ---------- Add formatted day ----------
def add_formatted_day(df):
    df["day"] = df["seendate"].apply(format_to_day)
    return df


# ---------- Save full file ----------
def save_full_file(df, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cols = ["day", "title", "url", "sentiment", "prob_negative", "prob_neutral", "prob_positive"]
    df_full = df[cols]
    df_full.to_csv(output_path, index=False)
    print(f"✅ Full sentiment file saved: {output_path}")
    return df_full


# ---------- Aggregate daily ----------
def aggregate_daily(df_full):
    print("🔹 Aggregating daily sentiment...")
    daily = df_full.groupby("day")[["prob_negative", "prob_neutral", "prob_positive"]].mean().reset_index()
    daily["sentiment"] = daily[["prob_negative", "prob_neutral", "prob_positive"]].idxmax(axis=1).str.replace("prob_", "")
    daily["mean"] = daily.apply(lambda r: r[f"prob_{r['sentiment']}"], axis=1)
    return daily[["day", "sentiment", "prob_negative", "prob_neutral", "prob_positive", "mean"]]


# ---------- Save daily ----------
def save_daily_file(daily_df, output_path):
    if daily_df.empty:
        print(f"⚠️ No daily data for {output_path}. Skipping.")
        return
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    daily_df.to_csv(output_path, index=False)
    print(f"✅ Daily aggregated file saved: {output_path}")


# ---------- Weekend & holiday aggregation ----------
def aggregate_weekend_holiday(daily_df, ticker):
    print("🔹 Folding weekends and holidays...")
    df = daily_df.copy()
    df["day"] = pd.to_datetime(df["day"])
    df = df.sort_values("day").reset_index(drop=True)
    vec_cols = ["prob_negative", "prob_neutral", "prob_positive"]
    id2name = {0: "negative", 1: "neutral", 2: "positive"}

    consumed, out = set(), {}
    for day in sorted(df["day"].unique()):
        if day in consumed:
            continue
        wd = day.weekday()
        vec = df.loc[df["day"] == day, vec_cols].mean().values
        if wd == 4:
            for offset in (1, 2):
                d2 = day + timedelta(days=offset)
                if d2 in df["day"].values:
                    vec += df.loc[df["day"] == d2, vec_cols].mean().values
                    consumed.add(d2)
        out[day] = vec

    df_folded = pd.DataFrame(
        [{"day": d, "prob_negative": v[0], "prob_neutral": v[1], "prob_positive": v[2]} for d, v in out.items()]
    ).sort_values("day")

    idxmax = df_folded[vec_cols].values.argmax(axis=1)
    df_folded["sentiment"] = [id2name[i] for i in idxmax]
    df_folded["mean"] = df_folded[vec_cols].to_numpy()[range(len(df_folded)), idxmax]

    start, end = df_folded["day"].min(), df_folded["day"].max() + timedelta(days=1)
    yf_data = yf.download(ticker, start=start, end=end, progress=False)
    trading_days = set(pd.to_datetime(yf_data.index.date))
    df_folded.set_index("day", inplace=True)

    for d in list(df_folded.index):
        if d.weekday() < 5 and d.date() not in trading_days:
            prev = d - timedelta(days=1)
            while prev >= start:
                if (prev in df_folded.index) and (prev.weekday() < 5) and (prev.date() in trading_days):
                    df_folded.loc[prev, vec_cols] += df_folded.loc[d, vec_cols]
                    df_folded.drop(index=d, inplace=True)
                    break
                prev -= timedelta(days=1)

    df_folded.reset_index(inplace=True)
    return df_folded.sort_values("day")


# ---------- Save trading days ----------
def save_trading_days_file(df, output_path):
    if df.empty:
        print(f"⚠️ No trading-day data to save for {output_path}. Skipping.")
        return
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Trading-day file saved: {output_path}")


# ---------- MAIN ----------
def main():
    tokenizer, model, id2label = load_sentiment_model(MODEL_NAME)

    for ticker, cfg in TICKER_CONFIG.items():
        print("\n" + "="*80)
        print(f"🚀 Processing ticker: {ticker}")
        print("="*80)

        keywords = cfg["keywords"]
        num = cfg["number"]

        full_output = f"{FULL_OUTPUT_FOLDER}/{ticker}_{num}_sentiment_full.csv"
        daily_output = f"{DAILY_OUTPUT_FOLDER}/{ticker}_{num}_sentiment_daily.csv"
        trading_output = f"{TRADING_DAYS_OUTPUT_FOLDER}/{ticker}_{num}_sentiment_trading_days.csv"

        articles = fetch_articles_robust(keywords, DATE_START, DATE_END, full_output, CHUNK_DAYS)
        if articles.empty:
            print(f"⚠️ No articles found for {ticker}. Skipping.")
            continue

        articles = deduplicate(articles)
        articles = filter_headlines_by_keywords(articles, keywords, ticker=ticker)  # 🔹 UPDATED
        if articles.empty:
            print(f"⚠️ No filtered articles for {ticker}. Skipping.")
            continue

        articles = run_sentiment(articles, tokenizer, model, id2label)
        articles = add_formatted_day(articles)
        full_df = save_full_file(articles, full_output)

        daily_df = aggregate_daily(full_df)
        save_daily_file(daily_df, daily_output)

        trading_df = aggregate_weekend_holiday(daily_df, ticker)
        save_trading_days_file(trading_df, trading_output)

        print(f"✅ Done with {ticker}\n")

    print("🎯 All tickers processed successfully.")


if __name__ == "__main__":
    main()
