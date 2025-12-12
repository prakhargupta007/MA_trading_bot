"""Transaction fee utilities for backtesting."""

from config import TRANSACTION_FEE_PER_STOCK, MINIMUM_TRANSACTION_FEE

def calculate_transaction_fee(number_of_stocks):
    total_fee = number_of_stocks * TRANSACTION_FEE_PER_STOCK
    return max(total_fee, MINIMUM_TRANSACTION_FEE)

def get_accurate_number_of_stocks(starting_balance, price_of_stock):
    """
    Compute fractional shares purchasable after accounting for transaction fees.
    Iteratively refines quantity until fee impact converges.
    """
    estimated_stocks = starting_balance / price_of_stock

    while True:
        fee = calculate_transaction_fee(estimated_stocks)
        actual_stocks = (starting_balance - fee) / price_of_stock
        if abs(actual_stocks - estimated_stocks) < 1e-6:
            break
        estimated_stocks = actual_stocks

    fee = calculate_transaction_fee(actual_stocks)
    final_balance = starting_balance - (actual_stocks * price_of_stock) - fee
    return actual_stocks, fee, final_balance
