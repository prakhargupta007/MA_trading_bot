def cagr_strategy_efficiency(strategy_cagr, buy_and_hold_cagr):
   strategy_efficiency = strategy_cagr / buy_and_hold_cagr
   rounded_cagr_strategy_efficiency = round(strategy_efficiency*100, 2)
   return rounded_cagr_strategy_efficiency
