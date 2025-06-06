import unittest
import pandas as pd
import numpy as np
from strategy.sma_strategy import sma_strategy
from strategy.ema_strategy import ema_strategy
from strategy.sma_rsi_strategy import sma_rsi_strategy
from strategy.ema_rsi_strategy import ema_rsi_strategy
from strategy.sma_rsi_macd_strategy import sma_rsi_macd_strategy

class TestStrategies(unittest.TestCase):
    def setUp(self):
        """Set up test data that will be used in multiple tests"""
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.sample_data = pd.DataFrame({
            'Close': np.random.normal(100, 10, len(dates))
        }, index=dates)

    def test_sma_strategy(self):
        """Test Simple Moving Average strategy"""
        signals = sma_strategy(self.sample_data, sma_long_period=20, sma_short_period=10)
        
        self.assertIsInstance(signals, list)
        self.assertEqual(len(signals), len(self.sample_data))
        self.assertTrue(all(signal in ['BUY', 'SELL', 'HOLD'] for signal in signals))

    def test_ema_strategy(self):
        """Test Exponential Moving Average strategy"""
        signals = ema_strategy(self.sample_data, ema_long_period=20, ema_short_period=10)
        
        self.assertIsInstance(signals, list)
        self.assertEqual(len(signals), len(self.sample_data))
        self.assertTrue(all(signal in ['BUY', 'SELL', 'HOLD'] for signal in signals))

    def test_sma_rsi_strategy(self):
        """Test SMA with RSI strategy"""
        signals = sma_rsi_strategy(
            self.sample_data,
            sma_long_period=20,
            sma_short_period=10,
            rsi_period=14,
            rsi_overbought=70,
            rsi_oversold=30
        )
        
        self.assertIsInstance(signals, list)
        self.assertEqual(len(signals), len(self.sample_data))
        self.assertTrue(all(signal in ['BUY', 'SELL', 'HOLD'] for signal in signals))

    def test_ema_rsi_strategy(self):
        """Test EMA with RSI strategy"""
        signals = ema_rsi_strategy(
            self.sample_data,
            ema_long_period=20,
            ema_short_period=10,
            rsi_period=14,
            rsi_overbought=70,
            rsi_oversold=30
        )
        
        self.assertIsInstance(signals, list)
        self.assertEqual(len(signals), len(self.sample_data))
        self.assertTrue(all(signal in ['BUY', 'SELL', 'HOLD'] for signal in signals))

    def test_sma_rsi_macd_strategy(self):
        """Test SMA with RSI and MACD strategy"""
        signals = sma_rsi_macd_strategy(
            self.sample_data,
            sma_long_period=20,
            sma_short_period=10,
            rsi_period=14,
            rsi_overbought=70,
            rsi_oversold=30
        )
        
        self.assertIsInstance(signals, list)
        self.assertEqual(len(signals), len(self.sample_data))
        self.assertTrue(all(signal in ['BUY', 'SELL', 'HOLD'] for signal in signals))

if __name__ == '__main__':
    unittest.main() 