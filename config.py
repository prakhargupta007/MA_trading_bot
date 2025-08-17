MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED = '/Users/prakhar/MA_trading_bot/ML/saved_models/xgb_model_AAPL_5.joblib'

'sentiment_score'
    #lr_8 #rf_6 #xgb_5
FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10','mom_diff_pct_5d', 'mom_diff_pct_10d', 'mom_diff_pct_20d', 'mom_diff_pct_50d', 'mom_diff_pct_100d','gspc_daily_return', 'gspc_20d_volatility', 'ndx_daily_return', 'ndx_20d_volatility', 'ndx_20d_sma','volume_20d_ma', 'obv']
    #lr_7 #rf_5 #xgb_4 
#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10','mom_diff_pct_5d', 'mom_diff_pct_10d', 'mom_diff_pct_20d', 'mom_diff_pct_50d', 'mom_diff_pct_100d','gspc_daily_return', 'gspc_20d_volatility', 'ndx_daily_return', 'ndx_20d_volatility', 'ndx_20d_sma']
    #rf_3 #lr_5 #xgb_2 #lr_6 #rf_4 #xgb_3 
#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10','mom_diff_pct_5d', 'mom_diff_pct_10d', 'mom_diff_pct_20d', 'mom_diff_pct_50d', 'mom_diff_pct_100d']

#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10'] #lr_2 #rf_2 #xgb_1
#FEATURE_COLUMNS = ['macd', 'macd_signal', 'sma_200', 'bb_percent','volatility_14', 'momentum_10'] #lr_3
#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10'] #lr_4 #rf_1 


# Here you can choose from:
# 'sma' 'ema' 'sma_rsi' 'sma_rsi_macd'  'ema_rsi'
# 'logistic_regression' 'random_forest' 'xgboost'
# 'perfect_strategy'
CHOSEN_STRATEGY = 'xgboost'
LOG_REG_MODEL_PATH_FOR_STRATEGY = '/Users/prakhar/MA_trading_bot/ML/saved_models/lr_model_with_scaler_AAPL_2.joblib'
RANDOM_FOREST_MODEL_PATH_FOR_STRATEGY = '/Users/prakhar/MA_trading_bot/ML/saved_models/rf_model_AAPL_2.joblib'
XGBOOST_MODEL_PATH_FOR_STRATEGY = '/Users/prakhar/MA_trading_bot/ML/saved_models/xgb_model_AAPL_5.joblib'

















if (input('Did you determine the MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED ?\nDid you choose the correct backtesting dates / period\n')) == 'n':
    exit()

import os
    # If True, backtesting period settings as determined in main.py file will be used and ticker is automatically set as 'APPL'
    # If False, backtesting period settings as determined in this config file will be used
USE_STORED_DATA = True
VISUALISE_PLOTTED_SIGNAL_EXECUTIONS =  True 

TICKERS = 'AAPL'
#TICKERS =  "JNJ,KO,PG,D"
#TICKERS =  "MSFT,DIS,UNH,UPS"
#TICKERS =  "TSLA,NVDA,ARKK,META"

if (input('Does this stock / do these stocks belong to the tech sector?\n'))[0] == 'y':
    TECH_SECTOR_STOCK = True 
else: 
    TECH_SECTOR_STOCK = False 

# leave the following untouched unless the stored data ticker gets changed
if USE_STORED_DATA:
    TICKERS = 'AAPL'
    'When changing the following line to use a diffrent file of data for reading change the backtesting dates and period in the main.py file!!!'
    STORED_DATA_TO_BE_READ = '/Users/prakhar/MA_trading_bot/data/stored_data/data_AAPL_2020-2025.csv' # START_OF_BACKTESTING = '2010-01-04 , END_OF_BACKTESTING = '2020-12-31'

# If true: data will be fetched from yfinance
# If false: data will be fetched from Alpha Vantage
# reason for prefence for yfinance = I can access the adjusted close price for free whereas Alpha Vantage asks you to buy the premium version to get the adjusted close price
DATA_API_IS_YFINANCE = True #--> SHOULD BE TRUE AT ALL TIMES! 

# Probability of prediction variables:
USE_PROBABILITY_THRESHOLD = True 
PROBABILITY_THRESHOLD = 0.4       

'Training parameters for linear_regression'
MAX_ITER = 1000
SOLVER = 'saga'


'Training parameters for random_forest'
RF_N_ESTIMATORS = 300      # more trees → stabler predictions (but slower)
RF_MAX_DEPTH = 10         # limits complexity; helps reduce overfitting
RF_MIN_SAMPLES_LEAF = 5   # avoid tiny leaves that overfit noisy patterns
RF_MIN_SAMPLES_SPLIT = 10 # min samples to split an internal node
RF_MAX_FEATURES = 'sqrt'  # features considered per split; 'sqrt' often works well
RF_CLASS_WEIGHT = None    # set to 'balanced' if classes are imbalanced
RF_OOB_SCORE = True       # out-of-bag estimate for quick validation
RF_RANDOM_STATE = 42
RF_N_JOBS = -1


'Training parameters for xgboost'
# Core XGBoost parameters (most important to tune)
XGB_N_ESTIMATORS = 100              # Number of trees in the model
XGB_MAX_DEPTH = 5                   # Max depth of each tree (controls complexity)
XGB_LEARNING_RATE = 0.1             # Step size shrinkage (learning rate)
XGB_SUBSAMPLE = 0.8                 # Fraction of samples used per tree (for randomness)
XGB_COLSAMPLE_BYTREE = 0.8          # Fraction of features used per tree (random feature selection)
XGB_RANDOM_STATE = 42               # Seed for reproducibility

# Parameters that are usually kept as default, but are here just for consistency sake 
XGB_N_JOBS = -1                     # Number of parallel threads (-1 uses all cores)
VERBOSITY = 1                       # Verbosity level: 0 = silent, 1 = warnings, etc.
EVAL_METRIC = 'logloss'             # Evaluation metric for training (log loss for classification)
BASE_SCORE=0.5   
OBJECTIVE='multi:softprob'          # multiclass objective






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

# Training model 
DATA_FOR_ML_MODEL_TRAINING = "/Users/prakhar/MA_trading_bot/data/stored_data/data_AAPL_2010-2020.csv"  # This is the data file that is used for training the model, it should be in the data/stored_data folder

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









# If I change/modify this feature column list I need to add/remove that feature to/from the function calculate_and_add_features_to_data as well!!!
GSPC_DATA_FILE_PATH = '/Users/prakhar/MA_trading_bot/data/stored_data/data_^GSPC_(SP500)_2010-2020.csv'
NDX_DATA_FILE_PATH = '/Users/prakhar/MA_trading_bot/data/stored_data/data_^NDX_(QQQ)_2010-2020.csv'

TRAIN_SIZE = 0.8 # This is the percentage of the data that is used for training and the rest is used for testing.

# Parameters for labeling system  
MINIMUM_PERCENTAGE_THRESHOLD = 0.02 # This minimum percentage threshold is used to determine whether to buy or sell and to reduce unneccesary tiny trades. At the moment this threshold is set to 2% which is reasonable, however this can be adjusted to possibly improve perfromance 
LOOKAHEAD_DAYS = 5









SLIPPAGE_RATE = 0.0005
RISK_FREE_RATE = 0.052 # current risk free rate in the US ==> yield on the 3-month US treasury bill, used for sharpe ratio calculation 
TRANSACTION_FEE_PER_STOCK = 0.05
MINIMUM_TRANSACTION_FEE = 1 

ALPHA_VANTAGE_API_KEY = '9VTDPFM0O0LXNZ41'

# Hardcoded folder paths for backtesting and API key
#The csv folder paths in which the resepctive files should be saved in. 
FOLDER_PATH_FOR_INDIVIDUAL_BACKTEST_TABLE = '/Users/prakhar/MA_trading_bot/saved_files/csv_trial_files_backtesting'
FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE = '/Users/prakhar/MA_trading_bot/saved_files/csv_summary_files_backtesting'
# The folder I want my excel file to be saved in
FOLDER_PATH_FOR_EXCEL_FILE = '/Users/prakhar/MA_trading_bot/saved_files/excel_trial_files_backtesting'
FOLDER_PATH_FOR_CSV_FILE = '/Users/prakhar/MA_trading_bot/saved_files/csv_trial_files_backtesting'
FOLDER_PATH_FOR_SUMMARIZED_EXCEL_FILE = '/Users/prakhar/MA_trading_bot/saved_files/excel_summary_files_backtesting'
FOLDER_PATH_FOR_PDF_SUMMARIZED_BACKTESTING_FILE = '/Users/prakhar/MA_trading_bot/saved_files/pdf_summary_files-backtesting'
#Here the last symbol should be '/' because I am combining this path with the file name and hence creating a new path where the html portly chart gets saved
OUTPUT_FOLDER_PATH_FOR_PLOTLY_CHART = '/Users/prakhar/MA_trading_bot/saved_files/charts_plotted_portly' 
