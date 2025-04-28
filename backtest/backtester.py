import pandas as pd
#After first iteration starting_balance essentially becomes current_bank_balance. So technically the varibale name doesnt di complete justice to its function 
def backtest(data, signals, sma_long_period, sma_series_length, starting_balance):
    
    list_actions = []
    list_dates = []
    list_number_of_stocks = []
    list_price_per_stock = []
    list_total_cash_flow = []

    n_stocks_bought = 0  # Initially, you have 0 stocks
    hold_counter = 0
    stay_counter = 0
    position = False #False means: No stock held

    for i in range(sma_long_period-1,sma_series_length):
        price_of_stock = data['Close'].iloc[i]
        signal = signals[i]

        if signal == 'BUY':
            if stay_counter > 0:
                list_actions.append(f'STAY for {stay_counter} days')
                list_dates.append(data.index[i - stay_counter])
                list_number_of_stocks.append('')
                list_price_per_stock.append('')
                list_total_cash_flow.append('')
                stay_counter = 0

            list_actions.append('BUY')
            list_dates.append(data.index[i])    
            n_stocks_bought = (starting_balance) / price_of_stock
            starting_balance -= (n_stocks_bought * price_of_stock)
                
            list_price_per_stock.append(round(price_of_stock,2))
            list_number_of_stocks.append(round(n_stocks_bought,2))
            list_total_cash_flow.append(round(starting_balance*(-1),2))

            position= True 
            
        elif signal == 'SELL':
            if hold_counter > 0:
                list_actions.append(f'HOLD for {hold_counter} days')
                list_dates.append(data.index[i - hold_counter])
                list_number_of_stocks.append('')
                list_price_per_stock.append('')
                list_total_cash_flow.append('')
                hold_counter = 0

            list_actions.append('SELL')
            list_dates.append(data.index[i])
            n_stocks_sold = n_stocks_bought
            starting_balance += (n_stocks_sold * price_of_stock)

            list_price_per_stock.append(round(price_of_stock, 2))
            list_number_of_stocks.append(round(n_stocks_sold * -1, 2))
            list_total_cash_flow.append(round(n_stocks_sold * price_of_stock, 2))

            position = False 

        elif signal == 'HOLD' and position:
            hold_counter += 1

        elif signal == 'HOLD' and not position:
            stay_counter += 1

    # This check converts your holdings of stock into cash, if your last action was 'BUY' 
    if position:  # If still holding stock, sell it at last price
        if hold_counter > 0:
            list_actions.append(f'HOLD for {hold_counter} days')
            list_dates.append(data.index[-hold_counter])
            list_number_of_stocks.append('')
            list_price_per_stock.append('')
            list_total_cash_flow.append('')

        list_actions.append('SELL (forced at end)')
        list_dates.append(data.index[-1])
        price_of_stock = data['Close'].iloc[-1]
        n_stocks_sold = n_stocks_bought
        starting_balance += (n_stocks_sold * price_of_stock)
    
    return list_actions, list_dates, list_number_of_stocks, list_price_per_stock, list_total_cash_flow


                

