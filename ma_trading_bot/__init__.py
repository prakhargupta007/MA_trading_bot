"""
ma_trading_bot
==============

Top-level namespace package that contains all internal subpackages
such as automation_bunch_backtesting and backtest. Keeping this file
lightweight ensures clean absolute imports like
ma_trading_bot.backtest.<module>.
"""

__all__ = ["automation_bunch_backtesting", "backtest"]
