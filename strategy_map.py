# =====================================
# strategy_map.py
# =====================================

# ----- Rule-Based Strategies -----
from rule_based_strategy.sma_strategy import sma_strategy
from rule_based_strategy.ema_strategy import ema_strategy
from rule_based_strategy.sma_rsi_strategy import sma_rsi_strategy
from rule_based_strategy.sma_rsi_macd_strategy import sma_rsi_macd_strategy
from rule_based_strategy.ema_rsi_strategy import ema_rsi_strategy
from rule_based_strategy.sentiment_strategy import sentiment_strategy

# ----- Machine Learning Strategies -----
from ML.ML_strategy.logistic_regression_strategy import logistic_regression_strategy
from ML.ML_strategy.random_forest_classification_strategy import random_forest_strategy
from ML.ML_strategy.xgboost_strategy import xgboost_strategy
from ML.ML_strategy.perfect_strategy import perfect_strategy

# Try importing MLP strategy only if TensorFlow is available
try:
    from ML.ML_strategy.mlp_strategy import mlp_strategy
except ImportError:
    mlp_strategy = None


# =====================================
# Strategy Map Dictionary
# =====================================

strategy_map = {
    # --- Rule-based strategies ---
    'sma': sma_strategy,
    'ema': ema_strategy,
    'sma_rsi': sma_rsi_strategy,
    'sma_rsi_macd': sma_rsi_macd_strategy,
    'ema_rsi': ema_rsi_strategy,
    'sentiment_strategy': sentiment_strategy,

    # --- ML-based strategies ---
    'logistic_regression': logistic_regression_strategy,
    'random_forest': random_forest_strategy,
    'xgboost': xgboost_strategy,
    'perfect_strategy': perfect_strategy,
}

# Add MLP dynamically only if TensorFlow is available
if mlp_strategy is not None:
    strategy_map['mlp'] = mlp_strategy
