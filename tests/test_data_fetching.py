import unittest
import pandas as pd
from data.fetch_data_from_yfinance import fetch_data_from_yfinance

class TestYFinanceDataFetching(unittest.TestCase):
    def test_fetch_data_success(self):
        """Test successful data fetching for a known good ticker (AAPL)"""
        # Arrange
        ticker = "AAPL"
        option_1_chosen = False
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        backtesting_period = "1"

        # Act
        data = fetch_data_from_yfinance(
            ticker,
            option_1_chosen,
            backtesting_period,
            end_date,
            start_date
        )
        
        # Assert
        # Check if we got data back
        self.assertIsNotNone(data)
        # Check if it's a DataFrame
        self.assertIsInstance(data, pd.DataFrame)
        # Check if it's not empty
        self.assertFalse(data.empty)
        # Check if it has the required columns
        self.assertIn('Close', data.columns)
        # Check if dates are within range
        self.assertTrue(data.index.min() >= pd.to_datetime(start_date))
        self.assertTrue(data.index.max() <= pd.to_datetime(end_date))

    def test_fetch_data_invalid_ticker(self):
        """Test handling of invalid ticker"""
        with self.assertRaises(ValueError):
            data = fetch_data_from_yfinance(
                ticker='INVALID_TICKER_123',
                option_1_chosen=True,
                backtesting_period='1',
                end_of_backtesting=None,
                start_of_backtesting=None
            )

    def test_fetch_data_date_range(self):
        """Test if data is within specified date range"""
        # Arrange
        ticker = "AAPL"
        option_1_chosen = False
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        backtesting_period = "1"

        # Act
        data = fetch_data_from_yfinance(
            ticker,
            option_1_chosen,
            backtesting_period,
            end_date,
            start_date
        )
        
        # Assert
        # Check if dates are within range
        self.assertTrue(data.index.min() >= pd.to_datetime(start_date))
        self.assertTrue(data.index.max() <= pd.to_datetime(end_date))
        # Check if we have data for most days (allowing for weekends and holidays)
        expected_min_days = 200  # Assuming at least 200 trading days in a year
        self.assertGreaterEqual(len(data), expected_min_days)

if __name__ == '__main__':
    unittest.main() 