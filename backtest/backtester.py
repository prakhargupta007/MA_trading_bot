import pandas as pd
#After first iteration starting_balance essentially becomes current_bank_balance. So technically the varibale name doesnt di complete justice to its function 
def backtest(data, signals, sma_long_period, sma_series_length, starting_balance):
    
    list_actions = []
    list_dates = []
    list_number_of_stocks = []
    list_price_per_stock = []
    list_total_cash_flow = []

    for i in range(sma_long_period-1,sma_series_length):
        price_of_stock = data['Close'].iloc[i]
        if signals[i] == 'BUY':
            n_stocks_bought = (starting_balance) / price_of_stock
            starting_balance -= (n_stocks_bought * price_of_stock)
                
            list_price_per_stock.append(round(price_of_stock,2))
            list_number_of_stocks.append(round(n_stocks_bought,2))
            list_total_cash_flow.append(round(starting_balance*(-1),2))
            
        elif signals[i] == 'SELL':
            n_stocks_sold = n_stocks_bought
            starting_balance += (n_stocks_sold * price_of_stock)
        
            list_price_per_stock.append(round(price_of_stock,2))
            list_number_of_stocks.append(round(n_stocks_sold * -1))
            list_total_cash_flow.append(round(starting_balance))
        list_actions.append(signals[i])
        list_dates.append(data.index[i])
    # This check converts your holdings of stock into cash, if your last action was 'BUY' 
    # Here I haven't deducted the transaction_fee as we won't really be making a transaction 
    if signals[-1] == 'BUY':
        starting_balance += data["Close"].iloc[-1] * n_stocks_bought

        list_actions.append('STAY, but stock value converted into cash')
        list_dates.append(f'last date of data: {data.index[-1]}')
        list_number_of_stocks.append(round(n_stocks_bought,2))
        list_price_per_stock.append(round(data["Close"].iloc[-1],2))
        list_total_cash_flow.append(f'+{round(starting_balance,2)}')
    
    return list_actions, list_dates, list_number_of_stocks, list_price_per_stock, list_total_cash_flow


                

