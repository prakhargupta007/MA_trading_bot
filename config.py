import os
    # If True, backtesting period settings as determined in main.py file will be used and ticker is automatically set as 'APPL'
    # If False, backtesting period settings as determined in this config file will be used
USE_STORED_DATA = True 

TICKERS = 'AMD,NVDA,GOOG'
#TICKERS =  "JNJ,KO,PG,D"
#TICKERS =  "MSFT,DIS,UNH,UPS"
#TICKERS =  "TSLA,NVDA,ARKK,META"

# leave the following untouched unless the stored data ticker gets changed
if USE_STORED_DATA:
    TICKERS = 'AAPL'

# If true: data will be fetched from yfinance
# If false: data will be fetched from Alpha Vantage
# reason for prefence for yfinance = I can access the adjusted close price for free whereas Alpha Vantage asks you to buy the premium version to get the adjusted close price
DATA_API_IS_YFINANCE = True #--> SHOULD BE TRUE AT ALL TIMES! 

# Here you can choose from:
# 'sma' 'ema' 'sma_rsi' 'sma_rsi_macd'  'ema_rsi'
# 'logistic_regression'
CHOSEN_STRATEGY = 'logistic_regression'

# Backtesting parameters
STARTING_BALANCE = 10000  # Starting balance for backtesting

#      For the backtesting period, 2 options are available: 
#       1. Just enter the x number of years as a string, and the backtesting period will be set from today to exactly that many years ago 
#       2. Enter the start and end dates as strings, and the backtesting period will be set from the start date to the end date
#    --> If choosing option 1, comment out option 2 and vice versa!
#BACKTESTING_PERIOD = '10'# in years as a string 
        #Format of the date should be YYYY-MM-DD
START_OF_BACKTESTING = '2010-06-01'
END_OF_BACKTESTING = '2025-07-09'

OPEN_INDIVIDUAL_PROCESS_EXCEL_FILES_AFTER_SAVING = False
OPEN_SUMMARY_EXCEL_FILE_AFTER_SAVING = False

INDICATORS_WHICH_ARE_NOT_TO_BE_CHECKED_FOR_LENGTH = ['data','rsi_overbought','rsi_oversold','logistic_regression']






#Strategy parameters for indicators
SMA_SHORT_PERIOD = 50 
SMA_LONG_PERIOD = 200

EMA_SHORT_PERIOD = 50
EMA_LONG_PERIOD = 200

RSI_PERIOD = 14  # period for RS (Relative Strength) index
RSI_OVERBOUGHT_WARNING = 70  
RSI_OVERSOLD_WARNING = 30

MACD_SLOW_PERIOD = 12  
MACD_FAST_PERIOD = 26  
MACD_SIGNAL_PERIOD = 9  






# If I change/modify this feature column list I need to add/remove that feature to the function calculate_and_add_features_to_data as well!!!
FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10']
MINIMUM_PERCENTAGE_THRESHOLD = 0.01 # This minimum percentage threshold is used to determine whether to buy or sell and to reduce unneccesary tiny trades. At the moment this threshold is set to 1% which is reasonable, however this can be adjusted to possibly improve perfromance 
TRAIN_SIZE = 0.8 # This is the percentage of the data that is used for training and the rest is used for testing.







RISK_FREE_RATE = 0.052 # current risk free rate in the US ==> yield on the 3-month US treasury bill
TRANSACTION_FEE_PER_STOCK = 0.05
MINIMUM_TRANSACTION_FEE = 1 
# Hardcoded folder paths for backtesting and API key
#The csv folder paths in which the resepctive files should be saved in. 
FOLDER_PATH_FOR_INDIVIDUAL_BACKTEST_TABLE = '/Users/prakhar/MA_trading_bot/csv_trial_files_backtesting'
FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE = '/Users/prakhar/MA_trading_bot/csv_summary_files_backtesting '

# The folder I want my excel file to be saved in
FOLDER_PATH_FOR_EXCEL_FILE = '/Users/prakhar/MA_trading_bot/excel_trial_files_backtesting'
FOLDER_PATH_FOR_CSV_FILE = '/Users/prakhar/MA_trading_bot/csv_trial_files_backtesting'

FOLDER_PATH_FOR_SUMMARIZED_EXCEL_FILE = '/Users/prakhar/MA_trading_bot/excel_summary_files_backtesting'

FOLDER_PATH_FOR_PDF_SUMMARIZED_BACKTESTING_FILE = '/Users/prakhar/MA_trading_bot/pdf_summary_files-backtesting'

#Here the last symbol should be '/' because I am combining this path with the file name and hence creating a new path where the html portly chart gets saved
OUTPUT_FOLDER_PATH_FOR_PLOTLY_CHART = '/Users/prakhar/MA_trading_bot/charts_plotted_portly' 

ALPHA_VANTAGE_API_KEY = '9VTDPFM0O0LXNZ41'