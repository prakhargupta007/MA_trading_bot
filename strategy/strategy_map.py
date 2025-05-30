from strategy.sma_strategy import sma_strategy 
from strategy.ema_strategy import ema_strategy
from strategy.sma_rsi_strategy import sma_rsi_strategy 
from strategy.sma_rsi_macd_strategy import sma_rsi_macd_strategy
from strategy.ema_rsi_strategy import ema_rsi_strategy

# Here every new startegy must be added

strategy_map = {
    'sma': sma_strategy,
    'ema': ema_strategy,
    'sma_rsi': sma_rsi_strategy,
    'sma_rsi_macd': sma_rsi_macd_strategy,
    'ema_rsi': ema_rsi_strategy
}