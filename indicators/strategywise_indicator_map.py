indicator_map = {
    # --- Your originals ---
    "sma": ["sma_short", "sma_long"],
    "ema": ["ema_short", "ema_long"],
    "sma_rsi": ["sma_short", "sma_long", "rsi"],

    # --- New rule-based (4–13) ---
    "rsi_trend_filter": ["sma_long", "rsi"],                         # uses long SMA (e.g., 200) + RSI
    "macd_trend_follow": ["macd", "macd_signal"],                    # MACD line + signal line
    "bollinger_mean_reversion": ["bb_upper", "bb_lower"],            # Bollinger bands (no mid needed here)
    "bb_squeeze_breakout": ["bb_upper", "bb_lower", "bb_mid"],       # needs band width / mid
    "obv_trend_confirmation": ["obv", "sma"],                        # OBV + a single SMA trend filter
    "ma_distance_reversion": ["sma"],                                # single MA for % deviation
    "vol_adjusted_momentum": ["sma_short", "sma_long", "volatility_14"]
}