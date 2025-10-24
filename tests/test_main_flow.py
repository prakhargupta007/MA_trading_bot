import unittest
import os
import pandas as pd
from main import main
from config import AAPL_STOCK_TEST_MODE

class TestMainFlow(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Ensure we're using test mode
        self.original_test_mode = AAPL_STOCK_TEST_MODE
        os.environ['AAPL_STOCK_TEST_MODE'] = 'True'
        
        # Define output paths
        self.csv_output = '/Users/prakhar/Desktop/MA_trading_bot/csv_trial_files_backtesting'
        self.excel_output = '/Users/prakhar/Desktop/MA_trading_bot/excel_trial_files_backtesting'
        self.plotly_output = '/Users/prakhar/Desktop/MA_trading_bot/charts_plotted_portly'

    def tearDown(self):
        """Clean up after tests"""
        # Restore original test mode
        os.environ['AAPL_STOCK_TEST_MODE'] = str(self.original_test_mode)

    def test_main_flow_with_mock_data(self):
        """Test the main program flow using mock data"""
        # Run the main program
        main()
        
        # Check if output files were created
        self.assertTrue(os.path.exists(self.csv_output))
        self.assertTrue(os.path.exists(self.excel_output))
        self.assertTrue(os.path.exists(self.plotly_output))
        
        # Check if the output files contain valid data
        csv_files = [f for f in os.listdir(self.csv_output) if f.endswith('.csv')]
        self.assertGreater(len(csv_files), 0)
        
        # Check content of a CSV file
        if csv_files:
            df = pd.read_csv(os.path.join(self.csv_output, csv_files[0]))
            self.assertFalse(df.empty)
            self.assertIn('Cash Flow', df.columns)

    def test_main_flow_error_handling(self):
        """Test error handling in main flow"""
        # Set environment to disable test mode and use an invalid ticker
        os.environ['AAPL_STOCK_TEST_MODE'] = 'False'
        os.environ['TICKERS'] = 'INVALID_TICKER_123'
        main()

    def test_main_flow_with_live_data(self):
        os.environ['AAPL_STOCK_TEST_MODE'] = 'False'
        # ... existing code ...

    def test_plot_files_generated(self):
        """Test that plot files are generated and are not empty"""
        # Run the main program
        main()
        
        # Check for plot files in the expected directory
        plot_dir = '/Users/prakhar/Desktop/MA_trading_bot/charts_plotted_portly'
        self.assertTrue(os.path.exists(plot_dir), f"Plot directory {plot_dir} does not exist")
        
        plot_files = [f for f in os.listdir(plot_dir) if f.endswith('.html')]
        self.assertGreater(len(plot_files), 0, "No plot files were generated")
        
        # Check that each plot file is not empty
        for plot_file in plot_files:
            file_path = os.path.join(plot_dir, plot_file)
            self.assertGreater(os.path.getsize(file_path), 0, f"Plot file {plot_file} is empty")

    def test_plot_content_matches_backtest_table(self):
        """Test that the content of the generated plot file matches the backtesting table"""
        # Run the main program
        main()
        
        # Load the backtesting table
        backtest_table_path = os.path.join('csv_trial_files_backtesting', 'AAPL_backtesting_table.csv')
        self.assertTrue(os.path.exists(backtest_table_path), f"Backtest table file {backtest_table_path} does not exist")
        backtest_table = pd.read_csv(backtest_table_path)
        
        # Only check the AAPL plot file
        plot_file = os.path.join('charts_plotted_portly', 'AAPL_strategy_plot.html')
        self.assertTrue(os.path.exists(plot_file), f"Plot file {plot_file} does not exist")
        with open(plot_file, 'r') as f:
            plot_content = f.read()
        self.assertTrue(len(plot_content) > 0, "Plot file is empty")
        self.assertIn('AAPL', plot_content, "Plot file does not contain the expected ticker 'AAPL'")
        # Check that at least one date from the backtest table is in the plot content
        dates = backtest_table['Date'].dropna().astype(str).tolist()
        self.assertTrue(any(date[:10] in plot_content for date in dates if date), "None of the backtest table dates found in plot content")

if __name__ == '__main__':
    unittest.main() 