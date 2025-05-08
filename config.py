TICKER = "QQQ"  # Example: Apple stock

# Strategy parameters
# For the first step of the strategy i'll either use the EMA paramteres or the SMA paramteres.
#EMA_SHORT_PERIOD = 9
#EMA_LONG_PERIOD = 21

SMA_SHORT_PERIOD = 50 
SMA_LONG_PERIOD = 200

RSI_PERIOD = 14  # period for RS (Relative Strength) index
RSI_OVERBOUGHT_WARNING = 70  
RSI_OVERSOLD_WARNING = 30 

MACD_SLOW_PERIOD = 12  
MACD_FAST_PERIOD = 26  
MACD_SIGNAL_PERIOD = 9  

# Backtesting parameters
STARTING_BALANCE = 10000  # Starting balance for backtesting
BACKTESTING_PERIOD = '10'# in years as a string

TRANSACTION_FEE_PER_STOCK = 0.05
MINIMUM_TRANSACTION_FEE = 1 

#The folder path in which the created backtest_table should be saved in. 
FOLDER_PATH = '/Users/prakhar/MA_trading_bot/csv_trial_files_backtesting'

# The folder I want my excel file to be saved in
OUTPUT_FOLDER_PATH_FOR_EXCEL_FILE = '/Users/prakhar/MA_trading_bot/excel_trial_files_backtesting'  