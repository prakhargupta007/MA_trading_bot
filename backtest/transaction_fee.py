from config import TRANSACTION_FEE_PER_STOCK, MINIMUM_TRANSACTION_FEE

def calculate_transaction_fee(number_of_stocks):
    total_fee = number_of_stocks * TRANSACTION_FEE_PER_STOCK
    transaction_fee =  max(total_fee, MINIMUM_TRANSACTION_FEE) 
    return transaction_fee

def get_accurate_number_of_stocks(starting_balance, price_of_stock):
    # Start with the estimated number of stocks
    estimated_stocks = starting_balance / price_of_stock
    
    # Loop to adjust the number of stocks and fee until it matches
    while True:
        # Calculate the transaction fee based on the estimated number of stocks
        transaction_fee = calculate_transaction_fee(estimated_stocks)
        
        # Calculate the amount of money after subtracting the fee
        remaining_balance = starting_balance - transaction_fee
        
        # Calculate how many stocks you can actually buy with the remaining balance
        actual_stocks = remaining_balance / price_of_stock
        
        # If the estimated number of stocks is equal to the calculated actual number of stocks, we're done
        if abs(estimated_stocks - actual_stocks) < 0.0001:  # Precision tolerance
            break
        
        # Otherwise, adjust the estimate and try again
        estimated_stocks = actual_stocks
    
    # Return the final number of stocks you can buy and the transaction fee
    return actual_stocks, transaction_fee
