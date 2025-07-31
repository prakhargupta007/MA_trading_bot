def apply_positioning_rule_to_translated_signals(translated_signals):
    final_signals = []
    state = "NEUTRAL"  # can be NEUTRAL, BOUGHT, or SOLD

    for signal in translated_signals:
        if signal == "BUY":
            if state == "NEUTRAL" or state == "SOLD":
                final_signals.append("BUY")
                state = "BOUGHT"
            elif state == "BOUGHT":
                final_signals.append("HOLD")

        elif signal == "SELL":
            if state == "BOUGHT":
                final_signals.append("SELL")
                state = "SOLD"
            elif state == "NEUTRAL" or state == "SOLD":
                final_signals.append("HOLD")

        elif signal == "HOLD":
            final_signals.append("HOLD")

        else:
            raise ValueError(f"Unexpected signal: {signal}")

    return final_signals
