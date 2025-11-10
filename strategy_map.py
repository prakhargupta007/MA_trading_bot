# =====================================
# strategy_map.py
# =====================================

# ----- Rule-Based Strategies -----
from rule_based_strategy.sma_strategy import sma_strategy
from rule_based_strategy.ema_strategy import ema_strategy
from rule_based_strategy.sma_rsi_strategy import sma_rsi_strategy

from rule_based_strategy.rsi_trend_filter_strategy import rsi_trend_filter_strategy
from rule_based_strategy.macd_trend_follow_strategy import macd_trend_follow_strategy
from rule_based_strategy.bollinger_mean_reversion_strategy import bollinger_mean_reversion_strategy
from rule_based_strategy.bb_squeeze_breakout_strategy import bb_squeeze_breakout_strategy
from rule_based_strategy.obv_trend_confirmation_strategy import obv_trend_confirmation_strategy
from rule_based_strategy.ma_distance_reversion_strategy import ma_distance_reversion_strategy
from rule_based_strategy.vol_adjusted_momentum_strategy import vol_adjusted_momentum_strategy
from rule_based_strategy.sentiment_strategy import sentiment_strategy
from rule_based_strategy.sentiment_momentum_confirmation_strategy import sentiment_momentum_confirmation_strategy
from rule_based_strategy.sentiment_regime_filter_strategy import sentiment_regime_filter_strategy

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

    'rsi_trend_filter': rsi_trend_filter_strategy,
    'macd_trend_follow': macd_trend_follow_strategy,
    'bollinger_mean_reversion': bollinger_mean_reversion_strategy,
    'bb_squeeze_breakout': bb_squeeze_breakout_strategy,
    'obv_trend_confirmation': obv_trend_confirmation_strategy,
    'ma_distance_reversion': ma_distance_reversion_strategy,
    'vol_adjusted_momentum': vol_adjusted_momentum_strategy,
    'sentiment_strategy': sentiment_strategy,
    'sentiment_momentum_confirmation': sentiment_momentum_confirmation_strategy,
    'sentiment_regime_filter': sentiment_regime_filter_strategy,

    # --- ML-based strategies ---
    'logistic_regression': logistic_regression_strategy,
    'random_forest': random_forest_strategy,
    'xgboost': xgboost_strategy,
    'perfect_strategy': perfect_strategy,
}

# Add MLP dynamically only if TensorFlow is available
if mlp_strategy is not None:
    strategy_map['mlp'] = mlp_strategy