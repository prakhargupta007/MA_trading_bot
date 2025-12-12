# MA Trading Bot  
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Status](https://img.shields.io/badge/project-Maturaarbeit-orange)
![Models](https://img.shields.io/badge/strategies-ML%20%7C%20Rule--Based-blue)
![Backtester](https://img.shields.io/badge/backtester-next--day--execution-green)

A full algorithmic trading research toolkit developed as part of my Maturaarbeit.  
This repository contains everything required to:

- fetch and process financial & sentiment data  
- build technical indicators and engineered ML features  
- generate rule-based or ML-based trading signals  
- run realistic next-day backtests with slippage & fees  
- analyze performance using professional trading metrics  
- automate batch training/backtesting workflows  
- visualize signals and portfolio trajectories  

The system is modular, extensible, and designed for research-level experimentation.

---

# 🔥 Recruiter-Friendly Project Summary

This project demonstrates the complete lifecycle of designing, evaluating, and automating quantitative trading strategies.  
It integrates **data engineering**, **machine learning**, **sentiment modeling**, and a fully custom **backtesting engine** — all implemented from scratch.

This repo reflects real quant workflow experience, not toy examples.

---

# 🎯 Skills Demonstrated

### **Software Engineering**
- Modular Python architecture  
- Automation workflow design  
- Config-driven system behavior  
- Clean abstractions  
- Git-based version control  

### **Machine Learning**
- Logistic Regression, Random Forest, XGBoost, MLP  
- Feature engineering  
- Scaling and preprocessing  
- Train/test splits  
- Deployment-ready inference pipelines  

### **Natural Language Processing**
- Sentiment scoring with HuggingFace Transformers  
- CardiffNLP RoBERTa sentiment pipeline  
- News filtering and aggregation  
- Trading-day alignment  

### **Quantitative Finance**
- Technical indicators (SMA, EMA, RSI, MACD, BB, OBV)  
- Trend following and mean reversion  
- Regime-based strategies  
- Portfolio accounting and slippage  
- Stop-loss systems (static, trailing, ATR-based)  

### **Research & Experimentation**
- Multi-strategy A/B testing  
- Batch automated experimentation  
- Sharpe/Sortino/Calmar/MDD analysis  
- Visualization and result reporting  

---

# 🏗️ Architecture Diagram

```mermaid
flowchart TD
    A[Load Config] --> B[Fetch or Load Price Data]
    B --> C[Compute Indicators]
    C --> D{Strategy Type?}

    D -->|Rule-Based| E[Generate Signals via Rule Strategies]
    D -->|ML-Based| F[Compute Features & Predict Signals]
    D -->|Sentiment| G[Load GDELT Sentiment & Generate Signals]

    E --> H[Apply Stop-Loss (Optional)]
    F --> H
    G --> H

    H --> I[Backtest Engine (Next-Day Execution)]
    I --> J[Performance Metrics]
    J --> K[Plot Results (Plotly/Matplotlib)]
    K --> L[Export CSV/Excel/PDF Summaries]




MA_trading_bot/
├── main.py                           # Fetch → Indicators → Signals → Backtest → Reports
├── rule_based_strategy/              # SMA, EMA, RSI, MACD, BB, OBV, sentiment, buy & hold
├── ML/
│   ├── ML_strategy/                  # LR, RF, XGB, MLP, Perfect Strategy
│   ├── train_models/                 # Training scripts for ML models
│   ├── saved_models/                 # Serialized model artifacts
│   └── ml_feature_store.py           # Feature column resolver
├── data/
│   ├── fetch_data/                   # Yahoo/AlphaVantage loaders
│   ├── stored_data2/                 # Offline price CSVs (2021–2025)
│   └── funcs_for_data_prep_for_ML/   # Feature engineering, labeling, scaling
├── sentiment_analysis/
│   └── GDELT/
│       ├── gdelt_sentiment_2.py      # Main pipeline for sentiment scoring
│       ├── load_sentiment_data.py    # Aligns sentiment to trading days
│       ├── daily_output/             
│       ├── full_output/              
│       └── trading_days_daily_output/
├── indicators/                       # Technical indicators
├── ma_trading_bot/
│   ├── backtest/                     # Engine, fees, slippage, summaries
│   ├── automation_bunch_backtesting/ # JSON-driven batch experiments
│   └── plotly_plot_backtesting/      # Equity & signal charts
├── risk_management/                  # Stop-loss modules
├── metrics/                          # Sharpe, Sortino, MDD, IR, CAGR
├── config.py                         # Runtime configuration
└── README.md                         # This file




# 📘 Strategies

## **Rule-Based Strategies**
- SMA / EMA crossovers  
- SMA-RSI / EMA-RSI hybrids  
- SMA-RSI-MACD  
- RSI trend filter  
- MACD trend following  
- Bollinger mean reversion  
- Bollinger squeeze breakout  
- OBV trend confirmation  
- MA distance reversion  
- Vol-adjusted momentum  
- Sentiment strategy  
- Sentiment momentum confirmation  
- Sentiment regime filter  
- Buy & Hold  

## **ML Strategies**
- Logistic Regression  
- Random Forest  
- XGBoost  
- MLP (TensorFlow/Keras)  
- Perfect Strategy (upper bound benchmark)  

All ML strategies support:
- feature prep  
- NaN handling  
- model loading  
- label → signal translation  
- next-day execution alignment  

---

# 📰 Sentiment Pipeline (GDELT)

- Fetch news from GDELT  
- Filter using ticker keyword lists  
- Score with **CardiffNLP RoBERTa**  
- Aggregate daily sentiment  
- Align with trading-day calendars  
- Export into `daily_output/`, `full_output/`, `trading_days_daily_output/`

Only “2” versions of files (e.g. `AAPL_2_sentimentfull.csv`) are used.

---

# 📈 Backtesting Engine

Located in `ma_trading_bot/backtest/`.

Features:

- **Next-day execution** (core design)  
- Fractional shares  
- Transaction costs  
- Slippage modeling  
- Global portfolio state tracking  
- Forced last-day liquidation  
- CSV/Excel summary writers  
- Plotly & Matplotlib charts  

Metrics include:

- CAGR  
- Sharpe  
- Sortino  
- Calmar  
- Max Drawdown  
- Win Rate  
- Information Ratio  

---

# 🧬 ML Pipeline

Training scripts handle:

- feature generation  
- Train/test splitting  
- scaling  
- model fitting  
- evaluation  
- saving artifacts  

Inference strategies:

- rebuild features  
- load saved models  
- classify signals  
- apply position rules  

---

# ⚙️ Automation

`automate_train_and_backtest.py` provides:

- multi-ticker batch testing  
- multiple feature-set experiments  
- training + backtesting loops  
- consolidated Excel reports with hyperlinks  

Driven by JSON configs.

---

# 🔧 Configuration

`config.py` controls:

- tickers  
- strategy selection  
- stop-loss type  
- indicator periods  
- sentiment paths  
- ML hyperparameters  
- slippage & fees  
- stored CSV paths  
- model artifact paths  
- starting capital  

Feature selection may be overridden with:





---

# ▶️ Running the Project

## **Single Backtest**
```bash
python main.py

## **Train models**
python -m ML.train_models.train_logistic_regression
python -m ML.train_models.train_random_forest
python -m ML.train_models.train_xgboost
python -m ML.train_models.train_mlp

## **Batch Experiments**
python -m ma_trading_bot.automation_bunch_backtesting.automate_train_and_backtest

## **Installing Dependencies**
pip install -r requirements.txt

## **Dependency List**
alpha_vantage
fpdf2
joblib
keras
matplotlib
numpy
openpyxl
pandas
plotly
requests
scikit-learn
seaborn
ta
TA-Lib
tabulate
tensorflow
torch
transformers
xgboost
yfinance





# ⚠️ Disclaimer
This project is for research and educational use only.
It is not investment advice and should not be used for live trading.


# 📄 License
Academic and research use only.