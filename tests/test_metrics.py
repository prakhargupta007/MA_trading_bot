import unittest
import pandas as pd
import numpy as np
from metrics.cagr import calculate_cagr
from metrics.profit import calculate_profit
from metrics.buy_hold_profit import calculate_profit_if_bought_and_held
from ma_trading_bot.backtest.transaction_fee import (
    get_accurate_number_of_stocks,
    calculate_transaction_fee,
)

class TestMetrics(unittest.TestCase):
    def setUp(self):
        """Set up test data that will be used in multiple tests"""
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.sample_data = pd.DataFrame({
            'Close': np.random.normal(100, 10, len(dates))
        }, index=dates)
        
        self.starting_balance = 10000
        self.ending_balance = 12000
        self.years = 1

    def test_cagr_calculation(self):
        """Test Compound Annual Growth Rate calculation"""
        cagr = calculate_cagr(self.starting_balance, self.years, self.ending_balance)
        
        # CAGR should be positive for profit
        self.assertGreater(cagr, 0)
        
        # Test with zero years
        cagr = calculate_cagr(self.starting_balance, 0, self.ending_balance)
        self.assertEqual(cagr, 0.0)
        
        # Test with negative balance
        cagr = calculate_cagr(self.starting_balance, self.years, -1000)
        self.assertLess(cagr, 0)

    def test_profit_calculation(self):
        """Test profit calculation"""
        profit_percent, profit = calculate_profit(self.starting_balance, self.ending_balance)
        
        # Check if profit is calculated correctly
        expected_profit = self.ending_balance - self.starting_balance
        self.assertEqual(profit, expected_profit)
        
        # Check if profit percentage is calculated correctly
        expected_percent = (self.ending_balance - self.starting_balance) / self.starting_balance * 100
        self.assertEqual(profit_percent, f'{expected_percent:.2f}%')

    def test_buy_hold_profit(self):
        """Test buy and hold profit calculation"""
        profit, final_cash = calculate_profit_if_bought_and_held(self.sample_data, self.starting_balance)
        
        # Check if profit is calculated
        self.assertIsNotNone(profit)
        self.assertIsNotNone(final_cash)
        
        # Check if final cash is positive
        self.assertGreaterEqual(final_cash, 0)
        
        # Check if profit is calculated correctly (absolute profit)
        first_price = self.sample_data['Close'].iloc[0]
        last_price = self.sample_data['Close'].iloc[-1]
        n_stocks_bought, fee, _ = get_accurate_number_of_stocks(self.starting_balance, first_price)
        proceeds = n_stocks_bought * last_price - calculate_transaction_fee(n_stocks_bought)
        expected_profit = proceeds - self.starting_balance
        self.assertAlmostEqual(profit, expected_profit, places=2)

if __name__ == '__main__':
    unittest.main() 
