from datetime import datetime, timedelta
import os
import pandas as pd
import requests
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import yfinance as yf  # make sure this is installed
import time


# ===================== CONFIGURATION =====================
TICKER = 'MSFT'

#TICKER_KEYWORDS = ["Apple", "AAPL", "Apple Inc"]
#TICKER_KEYWORDS = ["Nvidia", "NVDA", "Nvidia Corp", "Nvidia Corporation"]
#TICKER_KEYWORDS = ["QQQ", "Invesco QQQ", "Nasdaq-100", "Nasdaq 100", "NDX", "Nasdaq ETF"]
TICKER_KEYWORDS = ["MSFT", "Microsoft", "microsoft"]

NUMBER = "1"      # For file naming

DATE_START = "20100101"
DATE_END = "20250815"

#DATE_START = "20100101"
#DATE_END = "20250810"

CHUNK_DAYS = 30  # Fetch articles in chunks of 30 days

FULL_OUTPUT_FOLDER = "/Users/prakhar/MA_trading_bot/sentiment_analysis/GDELT/full_output_folder"
DAILY_OUTPUT_FOLDER = "/Users/prakhar/MA_trading_bot/sentiment_analysis/GDELT/daily_output_folder"
TRADING_DAYS_OUTPUT_FOLDER = "/Users/prakhar/MA_trading_bot/sentiment_analysis/GDELT/trading_days_daily_output"

FULL_OUTPUT_FILE = f"{FULL_OUTPUT_FOLDER}/{TICKER}_{NUMBER}_sentiment_full.csv"
DAILY_OUTPUT_FILE = f"{DAILY_OUTPUT_FOLDER}/{TICKER}_{NUMBER}_sentiment_daily.csv"
TRADING_DAYS_FILE = f"{TRADING_DAYS_OUTPUT_FOLDER}/{TICKER}_{NUMBER}_sentiment_trading_days.csv"

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
# ==========================================================

# ---------- Helper: Format GDELT datetime ----------
def format_to_day(iso_str):
    return datetime.strptime(iso_str, "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")

# ---------- Step 1: Load sentiment model ----------
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

# ---------- Step 2 (updated): Fetch GDELT news in chunks ----------
def fetch_articles_robust(keywords, start_date, end_date, output_file, CHUNK_DAYS, max_retries=1):
    print("🔹 Fetching news from GDELT in robust chunks...")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")
    
    if os.path.exists(output_file):
        print(f"⚠️ Output file {output_file} already exists. It will be appended to.")
        df_full = pd.read_csv(output_file)
        last_day = df_full['seendate'].max()
        start_dt = datetime.strptime(last_day, "%Y%m%d") + timedelta(days=1)
    else:
        df_full = pd.DataFrame()

    current_start = start_dt
    while current_start <= end_dt:
        current_end = min(current_start + timedelta(days=CHUNK_DAYS-1), end_dt)
        chunk_successful = False

        for attempt in range(1, max_retries+1):
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
                    # Empty response — probably no data or rate limit returned empty
                    print(f"      ⚠️ Chunk returned empty response. Could be no data or API limit.")
                    chunk_successful = True  # mark as handled so it won't retry
                    break

                data = resp.json()

                if "articles" not in data or not data["articles"]:
                    # Real "no articles found" case
                    print(f"      ⚠️ No articles found in GDELT for this chunk (likely genuinely empty).")
                    chunk_successful = True
                    break

                df_chunk = pd.DataFrame(data["articles"])
                
                if not df_chunk.empty:
                    df_chunk.to_csv(output_file, mode='a', index=False, header=not os.path.exists(output_file))
                    print(f"      ✅ Chunk saved with {len(df_chunk)} articles")

                chunk_successful = True
                break  # Break retry loop on success

            except requests.exceptions.RequestException as e:
                print(f"      ⚠️ Request exception: {e}")
                if attempt < max_retries:
                    print("      ⏳ Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print("      ❌ Skipping this chunk after max retries.")
            except ValueError as ve:
                print(f"      ⚠️ Value error: {ve}")
                chunk_successful = True  # Treat as “handled” if it's just empty / no articles
                break
            except Exception as e:
                print(f"      ⚠️ Unexpected exception: {e}")
                if attempt < max_retries:
                    print("      ⏳ Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print("      ❌ Skipping this chunk after max retries.")

        if not chunk_successful:
            print(f"      ❌ Chunk {current_start.strftime('%Y%m%d')} → {current_end.strftime('%Y%m%d')} failed completely.")

        current_start = current_end + timedelta(days=1)

    print(f"✅ All chunks processed. Full file at {output_file}")
    return pd.read_csv(output_file) if os.path.exists(output_file) else pd.DataFrame()


# ---------- Step 3: Deduplicate headlines ----------
def deduplicate(df):
    print("🔹 Deduplicating headlines...")
    return df.drop_duplicates(subset=["title"], keep="first")

# ---------- Helper: Filter headlines by keywords ----------
def filter_headlines_by_keywords(df, keywords):
    print("🔹 Filtering headlines by keywords...")
    keywords_lower = [k.lower() for k in keywords]
    pattern = "|".join(keywords_lower)
    df_filtered = df[df["title"].str.lower().str.contains(pattern, na=False)].copy()
    return df_filtered

# ---------- Step 4: Sentiment analysis ----------
def run_sentiment(df, tokenizer, model, id2label):
    print("🔹 Running sentiment analysis...")
    texts = df["title"].fillna("").tolist()
    labels = []
    probs_list = []
    label_names = [lbl for _, lbl in sorted(id2label.items())]  # consistent order by id

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

# ---------- Step 5: Format dates ----------
def add_formatted_day(df):
    df["day"] = df["seendate"].apply(format_to_day)
    return df

# ---------- Step 6: Save full cleaned file ----------
def save_full_file(df, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    columns = ["day", "title", "url", "sentiment", "prob_negative", "prob_neutral", "prob_positive"]
    df_full = df[columns]
    df_full.to_csv(output_path, index=False)
    print(f"✅ Full sentiment file saved to {output_path}")
    return df_full

# ---------- Step 7: Aggregate daily ----------
def aggregate_daily(df_full):
    print("🔹 Aggregating daily sentiment...")
    daily_probs = df_full.groupby("day")[["prob_negative", "prob_neutral", "prob_positive"]].mean().reset_index()

    daily_probs["sentiment"] = daily_probs[["prob_negative", "prob_neutral", "prob_positive"]].idxmax(axis=1)
    daily_probs["sentiment"] = daily_probs["sentiment"].str.replace("prob_", "")
    daily_probs["mean"] = daily_probs.apply(lambda row: row[f"prob_{row['sentiment']}"], axis=1)

    return daily_probs[["day", "sentiment", "prob_negative", "prob_neutral", "prob_positive", "mean"]]

# ---------- Step 8: Save daily aggregated file ----------
def save_daily_file(daily_df, output_path):
    # safeguard: skip if empty
    if daily_df.empty:
        print(f"⚠️ No daily data to save for {output_path}. Skipping.")
        return
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    daily_df.to_csv(output_path, index=False)
    print(f"✅ Daily aggregated sentiment file saved to {output_path}")


# ---------- Step 9: Weekend & non-weekend holiday aggregation ----------
def aggregate_weekend_holiday(daily_df):
    print("🔹 Applying weekend and non-weekend holiday aggregation...")
    df = daily_df.copy()
    df["day"] = pd.to_datetime(df["day"])
    df = df.sort_values("day").reset_index(drop=True)

    # Build a dict: day -> vector (neg, neu, pos)
    vec_cols = ["prob_negative", "prob_neutral", "prob_positive"]
    day_to_vec = {
        row.day: [getattr(row, c) for c in vec_cols] for row in df.itertuples(index=False)
    }

    # ---- Weekend aggregation: fold Sat/Sun into Friday and drop Sat/Sun ----
    print("   • Folding weekends (Sat/Sun) into Friday…")
    consumed = set()
    out = {}

    for day in sorted(day_to_vec.keys()):
        if day in consumed:
            continue

        wd = day.weekday()
        if wd == 5 or wd == 6:
            # Skip Sat/Sun here; they will be folded when processing Friday
            continue

        if wd == 4:  # Friday
            vec = day_to_vec[day].copy()
            for offset in (1, 2):  # Saturday and Sunday
                d2 = day + timedelta(days=offset)
                if d2 in day_to_vec:
                    vec += day_to_vec[d2]
                    consumed.add(d2)
            out[day] = vec
        else:
            out[day] = day_to_vec[day]

    # Construct DataFrame from weekend-folded data (no Sat/Sun rows)
    df_agg = (
        pd.DataFrame(
            [
                {
                    "day": d,
                    "prob_negative": v[0],
                    "prob_neutral": v[1],
                    "prob_positive": v[2],
                }
                for d, v in out.items()
            ]
        )
        .sort_values("day")
        .reset_index(drop=True)
    )

    # Compute labels/means after weekend fold
    idxmax = df_agg[["prob_negative", "prob_neutral", "prob_positive"]].values.argmax(axis=1)
    id2name = {0: "negative", 1: "neutral", 2: "positive"}
    df_agg["sentiment"] = [id2name[i] for i in idxmax]
    df_agg["mean"] = df_agg.lookup(
        df_agg.index, "prob_" + df_agg["sentiment"]  # pandas <1.2; if newer, use .to_numpy trick below
    ) if hasattr(df_agg, "lookup") else df_agg.to_numpy()[range(len(df_agg)), idxmax + 1]  # safe fallback

    # ---- Non-weekend market holidays: fold weekday non-trading days into previous trading day ----
    print("   • Folding weekday market holidays into previous trading day…")
    # Fetch actual trading days (inclusive end: add +1 day to be safe)
    start_dt = df_agg["day"].min()
    end_dt = df_agg["day"].max() + timedelta(days=1)
    yf_data = yf.download(TICKER, start=start_dt, end=end_dt, progress=False)
    trading_days = set(pd.to_datetime(yf_data.index.date))

    # Work on an indexable structure
    df_agg.set_index("day", inplace=True)

    # Iterate over a snapshot of current dates to allow row drops
    for d in list(df_agg.index):
        # Consider only weekdays that are NOT trading days
        if d.weekday() < 5 and d.date() not in trading_days:
            # Find previous date in df_agg that is a trading weekday
            p = d - timedelta(days=1)
            while p >= start_dt:
                if (p in df_agg.index) and (p.weekday() < 5) and (p.date() in trading_days):
                    # Fold d into p
                    df_agg.loc[p, ["prob_negative", "prob_neutral", "prob_positive"]] += df_agg.loc[
                        d, ["prob_negative", "prob_neutral", "prob_positive"]
                    ].values
                    # Recompute label/mean at p
                    vec = df_agg.loc[p, ["prob_negative", "prob_neutral", "prob_positive"]].values
                    si = vec.argmax()
                    df_agg.loc[p, "sentiment"] = id2name[si]
                    df_agg.loc[p, "mean"] = vec[si]
                    # Drop holiday row d
                    df_agg.drop(index=d, inplace=True)
                    break
                p -= timedelta(days=1)
            # If no previous trading day exists (very early boundary), optionally push forward
            if d in df_agg.index:  # not folded yet
                n = d + timedelta(days=1)
                while n <= end_dt:
                    if (n in df_agg.index) and (n.weekday() < 5) and (n.date() in trading_days):
                        df_agg.loc[n, ["prob_negative", "prob_neutral", "prob_positive"]] += df_agg.loc[
                            d, ["prob_negative", "prob_neutral", "prob_positive"]
                        ].values
                        vec = df_agg.loc[n, ["prob_negative", "prob_neutral", "prob_positive"]].values
                        si = vec.argmax()
                        df_agg.loc[n, "sentiment"] = id2name[si]
                        df_agg.loc[n, "mean"] = vec[si]
                        df_agg.drop(index=d, inplace=True)
                        break
                    n += timedelta(days=1)

    df_agg.reset_index(inplace=True)
    df_agg = df_agg.sort_values("day").reset_index(drop=True)
    return df_agg

# ---------- Step 10: Save trading days daily output ----------
def save_trading_days_file(df, output_path):
    # safeguard: skip if empty
    if df.empty:
        print(f"⚠️ No trading days data to save for {output_path}. Skipping.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Trading days daily sentiment file saved to {output_path}")


# ---------- Main pipeline ----------
def main():
    tokenizer, model, id2label = load_sentiment_model(MODEL_NAME)
    articles_df = fetch_articles_robust(TICKER_KEYWORDS, DATE_START, DATE_END, FULL_OUTPUT_FILE, CHUNK_DAYS)

    if articles_df.empty:
        print("No articles found. Exiting.")
        return

    articles_df = deduplicate(articles_df)
    articles_df = filter_headlines_by_keywords(articles_df, TICKER_KEYWORDS)
    if articles_df.empty:
        print("No articles with Apple in the headline found. Exiting.")
        return

    articles_df = run_sentiment(articles_df, tokenizer, model, id2label)
    articles_df = add_formatted_day(articles_df)
    full_df = save_full_file(articles_df, FULL_OUTPUT_FILE)

    daily_df = aggregate_daily(full_df)
    save_daily_file(daily_df, DAILY_OUTPUT_FILE)

    trading_days_df = aggregate_weekend_holiday(daily_df)
    save_trading_days_file(trading_days_df, TRADING_DAYS_FILE)

if __name__ == "__main__":
    main()





