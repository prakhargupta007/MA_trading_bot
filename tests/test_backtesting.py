import unittest
import pandas as pd
import numpy as np
from backtest.backtest_strategy import backtest_strategy
from backtest.transaction_fee import calculate_transaction_fee
from config import MINIMUM_TRANSACTION_FEE, TRANSACTION_FEE_PER_STOCK

class TestBacktesting(unittest.TestCase):
    def setUp(self):
        """Set up test data that will be used in multiple tests"""
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.sample_data = pd.DataFrame({
            'Close': np.random.normal(100, 10, len(dates))
        }, index=dates)
        
        # Create sample signals
        self.sample_signals = ['HOLD'] * len(dates)
        for i in range(0, len(dates), 30):  # Add some BUY/SELL signals every 30 days
            self.sample_signals[i] = 'BUY' if i % 60 == 0 else 'SELL'
        
        self.starting_balance = 10000

    def test_backtest_strategy(self):
        """Test the main backtesting function"""
        actions, dates, stocks, prices, cash_flows = backtest_strategy(
            self.sample_data,
            self.sample_signals,
            self.starting_balance
        )
        
        self.assertIsNotNone(actions)
        self.assertIsInstance(actions, list)
        self.assertEqual(len(actions), len(dates))
        self.assertEqual(len(actions), len(stocks))
        self.assertEqual(len(actions), len(prices))
        self.assertEqual(len(actions), len(cash_flows))
        
        # Check if all actions are valid
        valid_actions = ['BUY', 'SELL', 'HOLD', 'SELL (forced at end)']
        self.assertTrue(all(action in valid_actions or 'STAY for' in action or 'HOLD for' in action for action in actions))
        
        # Check if cash flows are valid
        for i, action in enumerate(actions):
            if action == 'BUY':
                self.assertLess(cash_flows[i], 0)  # Negative cash flow for buys
            elif action == 'SELL' or action == 'SELL (forced at end)':
                self.assertGreater(cash_flows[i], 0)  # Positive cash flow for sells

    def test_transaction_fee(self):
        """Test transaction fee calculation"""
        from backtest.transaction_fee import calculate_transaction_fee
        from config import TRANSACTION_FEE_PER_STOCK, MINIMUM_TRANSACTION_FEE

        # Test minimum fee
        fee = calculate_transaction_fee(1)
        self.assertEqual(fee, MINIMUM_TRANSACTION_FEE)

        # Test percentage fee
        amount = 1000
        expected_fee = amount * TRANSACTION_FEE_PER_STOCK
        fee = calculate_transaction_fee(amount)
        self.assertEqual(fee, expected_fee)

        # Test zero amount
        fee = calculate_transaction_fee(0)
        self.assertEqual(fee, MINIMUM_TRANSACTION_FEE)

    def test_backtest_results_consistency(self):
        """Test if backtest results are consistent"""
        actions, dates, stocks, prices, cash_flows = backtest_strategy(
            self.sample_data,
            self.sample_signals,
            self.starting_balance
        )
        
        # Check if all lists have the same length
        self.assertEqual(len(actions), len(dates))
        self.assertEqual(len(actions), len(stocks))
        self.assertEqual(len(actions), len(prices))
        self.assertEqual(len(actions), len(cash_flows))
        
        # Check if dates are valid
        for date in dates:
            if date != ' ':  # Skip empty dates (for HOLD/STAY actions)
                self.assertIsInstance(date, pd.Timestamp)
        
        # Check if stocks and prices are valid numbers
        for stock, price in zip(stocks, prices):
            if stock != ' ':  # Skip empty values
                self.assertIsInstance(stock, (int, float))
                self.assertIsInstance(price, (int, float))
                self.assertGreaterEqual(price, 0)

if __name__ == '__main__':
    unittest.main() 