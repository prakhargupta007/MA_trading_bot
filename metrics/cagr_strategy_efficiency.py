def cagr_strategy_efficiency(strategy_cagr, buy_and_hold_cagr):
    if buy_and_hold_cagr in (None, 0):
        return None

    cagr_efficiency = 1 + (strategy_cagr - buy_and_hold_cagr) / abs(buy_and_hold_cagr)
    rounded_cagr_strategy_efficiency = round(cagr_efficiency * 100, 2)
    return rounded_cagr_strategy_efficiency
