
model_number = '22'
MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED = f'/Users/prakhar/Desktop/MA_trading_bot/ML/saved_models/xgb_model_{model_number}.joblib'
MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED = f"/Users/prakhar/Desktop/MA_trading_bot/ML/saved_models/mlp_{model_number}.keras"
PATH_FOR_SAVING_MLP_SCALAR = f'/Users/prakhar/Desktop/MA_trading_bot/ML/saved_models/mlp_scaler_{model_number}.pkl'



if (input('If using sentiment_score feature in model training, has the SENTIMENT_DATA_PATH_FOR_ML_MODEL_TRAINING_FEATURE path been set to the correct sentiment data file path?\n'))[0] == 'n':
    exit()
SENTIMENT_DATA_PATH_FOR_ML_MODEL_TRAINING_FEATURE = '/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/trading_days_daily_output/AAPL_1_sentiment_trading_days.csv'

'When backtesting or training my model that uses features from GSPC and NDX, update the TRAINING variable.'
TRAINING_MODE = False 

USE_STOP_LOSS = False  

    # Here you can choose from:
    # 'static'
    # 'trailing'
    # 'atr'
    # 'trailing_atr' 
CHOSEN_STOP_LOSS = 'trailing_atr'

COLUMN_NAME = 'Close'
STOP_LOSS_THRESHOLD = 0.05
ATR_PERIOD = 14
ATR_MULTIPLIER = 2.0


# Training model 
DATA_FOR_ML_MODEL_TRAINING = "/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_AAPL_train_test_2017-01-02--2022-12-30.csv"      # AAPL
#DATA_FOR_ML_MODEL_TRAINING = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_QQQ_train_2017-01-02--2022-12-30.csv'           # QQQ

    # If True, backtesting period settings as determined in main.py file will be used! SO make sure the correct dates are set!
    #  and ticker is automatically set as 'AAPL'
    # If False, backtesting period settings as determined in this config file will be used
USE_STORED_DATA = True
VISUALISE_PLOTTED_SIGNAL_EXECUTIONS =  False 
# leave the following untouched unless the stored data ticker gets changed

# FOR BACKTESTING USING STORED DATA
if USE_STORED_DATA:
    # If using stored data, the TICKERS variable can only be one ticker at a time, since the stored data file only contains data for one ticker
    TICKERS = 'AAPL'
    'When changing the following line to use a diffrent file of data for reading, change the backtesting dates and period in the main.py file!!!'
    #STORED_DATA_TO_BE_READ = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_AAPL_backtest_2023-01-03--2025-08-15.csv' # AAPL
    #STORED_DATA_TO_BE_READ = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_QQQ_backtest_2023-01-02--2025-08-16.csv' # QQQ

    STORED_DATA_TO_BE_READ = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_AAPL_train_test_2017-01-02--2025-08-16.csv'
    #STORED_DATA_TO_BE_READ = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_NVDA_backtest_2017-01-01--2025-08-17.csv'
    #STORED_DATA_TO_BE_READ = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_MSFT_backtest_2017-01-01--2025-08-17.csv'
    


# Here you can choose from:
# 'sma' 'ema' 'sma_rsi' 'sma_rsi_macd'  'ema_rsi'
# 'sentiment_strategy'
# 'logistic_regression' 'random_forest' 'xgboost' 'mlp'
# 'perfect_strategy'

#CHOSEN_STRATEGY = 'logistic_regression'
#CHOSEN_STRATEGY = 'random_forest'
CHOSEN_STRATEGY = 'mlp'

if (input('Did you choose correct DATA_PATH_FOR_SENTIMENT_STRATEGY if using sentiment_strategy?\n'))[0] == 'n':
    exit()
# this path is goven to strategy while backtesting 'sentiment strategy'
DATA_PATH_FOR_SENTIMENT_STRATEGY = '/Users/prakhar/Desktop/MA_trading_bot/sentiment_analysis/GDELT/trading_days_daily_output/AAPL_1_sentiment_trading_days.csv'

LOG_REG_MODEL_PATH_FOR_STRATEGY = '/Users/prakhar/Desktop/MA_trading_bot/ML/saved_models/lr_model_19.joblib'
RANDOM_FOREST_MODEL_PATH_FOR_STRATEGY = '/Users/prakhar/Desktop/MA_trading_bot/ML/saved_models/rf_model_19.joblib'
XGBOOST_MODEL_PATH_FOR_STRATEGY = '/Users/prakhar/Desktop/MA_trading_bot/ML/saved_models/xgb_model_19.joblib'
MLP_MODEL_PATH_FOR_STRATEGY = "/Users/prakhar/Desktop/MA_trading_bot/ML/saved_models/mlp_1.keras"
MLP_SCALAR_PATH_FOR_STRATEGY = '/Users/prakhar/Desktop/MA_trading_bot/ML/saved_models/mlp_scaler_1.pkl'

FEATURES_WITH_SENTIMENT = True # If True, the sentiment score feature will be used in the model training and backtesting, if False, it will not be used

    # If True, backtesting period settings as determined in main.py file will be used and ticker is automatically set as 'AAPL'
    # If False, backtesting period settings as determined in this config file will be used

if (input('Did you set TRAINING_MODE as per your requirement?\n'))[0] == 'n':
    exit()












#(lr_21) #rf_21 #xgb_21
FEATURE_COLUMNS = ['sma_200', 'sma_50', 'bb_upper', 'bb_lower', 'ndx_20d_sma', 'ndx_20d_volatility', 'volume_20d_ma', 'volatility_14', 'ema_diff_pct_50d', 'mom_diff_pct_50d']

'''
#lr_20 (#rf_21 #xgb_21)
FEATURE_COLUMNS = ['volume_20d_ma', 'bb_percent', 'bb_lower', 'vix_mean20', 'rsi_14', 'ndx_20d_volatility', 'sma_50', 'bb_upper', 'sma_200', 'gspc_20d_volatility']
'''
'''
#lr_19 #rf_19 #xgb_19
FEATURE_COLUMNS = ['volume_20d_ma', 'bb_percent', 'bb_lower', 'vix_mean20', 'rsi_14']
'''
# If I change/modify this feature column list I need to add/remove that feature to/from the function calculate_and_add_features_to_data as well!!!
#lr_17 #rf_17 #xgb_17
#lr_18 #rf_18 #xgb_18

'''
FEATURE_COLUMNS = [
        # Momentum & Trend
        'ema_diff_pct_10d',
        'ema_diff_pct_50d',
        'ema_diff_pct_200d',
        'rsi_14',
        'vix_roc1',
        'vix_mean20',
        'vix_std20'
    ] 
'''


'''
#lr_15 #rf_15 #xgb_15
#lr_16 #rf_16 #xgb_16
FEATURE_COLUMNS = [
        # Momentum & Trend
        'ema_diff_pct_10d',
        'ema_diff_pct_50d',
        'ema_diff_pct_200d',
        'rsi_14'
    ] 
'''



'''
#lr_13 #rf_11 #xgb_10
#lr_14 #rf_12 #xgb_11
FEATURE_COLUMNS = [
        # Momentum & Trend
        'ema_diff_pct_10d',
        'ema_diff_pct_50d',
        'ema_diff_pct_200d'
    ]
'''

'''
#lr_11 #rf_9 #xgb_8 
#lr_12 #rf_10 #xgb_9

FEATURE_COLUMNS = [
        # Momentum & Trend
        'ema_diff_pct_50d',
        'ema_diff_pct_200d'
    ]
'''




'''
if FEATURES_WITH_SENTIMENT:
        # lr_10 #rf_8 #xgb_7
    FEATURE_COLUMNS = [
        # Momentum & Trend
        'rsi_14',
        'macd',
        'mom_diff_pct_10d',
        'mom_diff_pct_100d',

        # Volatility
        'volatility_14',
        'gspc_20d_volatility',  # broad market
        'ndx_20d_volatility',   # tech sector vol

        # Returns
        'daily_return',
        'gspc_daily_return',    # market return
        'ndx_daily_return',     # tech sector return

        # Volume
        'obv',
        'volume_20d_ma',

        # Bands
        'bb_percent',

        # Sentiment
        'sentiment_score'
    ]
else:
        # lr_9 #rf_7 #xgb_6
    FEATURE_COLUMNS = [
        # Momentum & Trend
        'rsi_14',
        'macd',
        'mom_diff_pct_10d',
        'mom_diff_pct_100d',

        # Volatility
        'volatility_14',
        'gspc_20d_volatility',  # broad market
        'ndx_20d_volatility',   # tech sector vol

        # Returns
        'daily_return',
        'gspc_daily_return',    # market return
        'ndx_daily_return',     # tech sector return

        # Volume
        'obv',
        'volume_20d_ma',

        # Bands
        'bb_percent'

        # Sentiment
        #'sentiment_score'
    ]
    '''


    #lr_8 #rf_6 #xgb_5
#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10','mom_diff_pct_5d', 'mom_diff_pct_10d', 'mom_diff_pct_20d', 'mom_diff_pct_50d', 'mom_diff_pct_100d','gspc_daily_return', 'gspc_20d_volatility', 'ndx_daily_return', 'ndx_20d_volatility', 'ndx_20d_sma','volume_20d_ma', 'obv']
    #lr_7 #rf_5 #xgb_4
#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10','mom_diff_pct_5d', 'mom_diff_pct_10d', 'mom_diff_pct_20d', 'mom_diff_pct_50d', 'mom_diff_pct_100d','gspc_daily_return', 'gspc_20d_volatility', 'ndx_daily_return', 'ndx_20d_volatility', 'ndx_20d_sma']
    #rf_3 #lr_5 #xgb_2 #lr_6 #rf_4 #xgb_3 
#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10','mom_diff_pct_5d', 'mom_diff_pct_10d', 'mom_diff_pct_20d', 'mom_diff_pct_50d', 'mom_diff_pct_100d']

#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_upper', 'bb_lower', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10'] #lr_2 #rf_2 #xgb_1
#FEATURE_COLUMNS = ['macd', 'macd_signal', 'sma_200', 'bb_percent','volatility_14', 'momentum_10'] #lr_3
#FEATURE_COLUMNS = ['rsi_14', 'macd', 'macd_signal', 'sma_50', 'sma_200', 'bb_percent', 'daily_return', 'volatility_14', 'momentum_10'] #lr_4 #rf_1 









if TRAINING_MODE:
    GSPC_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^GSPC_train_2017-01-02--2022-12-30.csv'
    NDX_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^NDX_train_2017-01-02--2022-12-30.csv'
    VIX_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^VIX_train_2017-01-01--2022-12-31.csv'
else:
    GSPC_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^GSPC_backtest_2023-01-03--2025-08-15.csv'
    NDX_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^NDX_backtest_2023-01-03--2025-08-15.csv'
    VIX_DATA_FILE_PATH = '/Users/prakhar/Desktop/MA_trading_bot/data/stored_data/data_^VIX_backtest_2023-01-01--2025-08-17.csv'











if (input('Did you determine the MODEL_PATH_WHERE_TRAINED_MODEL_SHOULD_GET_SAVED ?\n')) == 'n':
    exit()

if (input('Did you choose the correct backtesting dates / period\n')) == 'n':
    exit()

TICKERS = 'AAPL'
#TICKERS =  "JNJ,KO,PG,D"
#TICKERS =  "MSFT,DIS,UNH,UPS"
#TICKERS =  "TSLA,NVDA,ARKK,META"

if (input('Does this stock / do these stocks belong to the tech sector?\n'))[0] == 'y':
    TECH_SECTOR_STOCK = True 
else: 
    TECH_SECTOR_STOCK = False 


# If true: data will be fetched from yfinance
# If false: data will be fetched from Alpha Vantage
# reason for prefence for yfinance = I can access the adjusted close price for free whereas Alpha Vantage asks you to buy the premium version to get the adjusted close price
DATA_API_IS_YFINANCE = True #--> SHOULD BE TRUE AT ALL TIMES! 

# Probability of prediction variables:
USE_PROBABILITY_THRESHOLD = False 
PROBABILITY_THRESHOLD = 0.4       

'Training parameters for logistic_regression'
MAX_ITER = 1000
SOLVER = 'saga'
CLASS_WEIGHT = 'balanced'
RANDOM_STATE = 42  # Use balanced class weights to handle class imbalance

'Training parameters for random_forest'
RF_N_ESTIMATORS = 300      # more trees → stabler predictions (but slower)
RF_MAX_DEPTH = 10         # limits complexity; helps reduce overfitting
RF_MIN_SAMPLES_LEAF = 5   # avoid tiny leaves that overfit noisy patterns
RF_MIN_SAMPLES_SPLIT = 10 # min samples to split an internal node
RF_MAX_FEATURES = 'sqrt'  # features considered per split; 'sqrt' often works well
RF_CLASS_WEIGHT = 'balanced'    # set to 'balanced' if classes are imbalanced
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

'Training parameters for mlp'
RANDOM_STATE = 42
ML_EPOCHS = 100
ML_BATCH_SIZE = 32



# Backtesting parameters
STARTING_BALANCE = 10000  # Starting balance for backtesting

#      For the backtesting period, 2 options are available: 
#       1. Just enter the x number of years as a string, and the backtesting period will be set from today to exactly that many years ago 
#       2. Enter the start and end dates as strings, and the backtesting period will be set from the start date to the end date
#    --> If choosing option 1, comment out option 2 and vice versa!
#BACKTESTING_PERIOD = '10'# in years as a string 
        #Format of the date should be YYYY-MM-DD
'If USE_STORED_DATA is false, then the following dates will be used'
START_OF_BACKTESTING = ''
END_OF_BACKTESTING = '2025-07-09'



OPEN_INDIVIDUAL_PROCESS_EXCEL_FILES_AFTER_SAVING = False
OPEN_SUMMARY_EXCEL_FILE_AFTER_SAVING = False

INDICATORS_WHICH_ARE_NOT_TO_BE_CHECKED_FOR_LENGTH = ['data','rsi_overbought','rsi_oversold','data_path_for_sentiment_strategy']







#Strategy parameters for indicators
SMA_SHORT_PERIOD = 25
SMA_LONG_PERIOD = 70

EMA_SHORT_PERIOD = 50
EMA_LONG_PERIOD = 200

RSI_PERIOD = 14  # period for RS (Relative Strength) index
RSI_OVERBOUGHT_WARNING = 70  
RSI_OVERSOLD_WARNING = 30

MACD_SLOW_PERIOD = 12  
MACD_FAST_PERIOD = 26  
MACD_SIGNAL_PERIOD = 9  






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
FOLDER_PATH_FOR_INDIVIDUAL_BACKTEST_TABLE = '/Users/prakhar/Desktop/MA_trading_bot/saved_files/csv_trial_files_backtesting'
FOLDER_PATH_FOR_SUMMARY_BACKTEST_TABLE = '/Users/prakhar/Desktop/MA_trading_bot/saved_files/csv_summary_files_backtesting'
# The folder I want my excel file to be saved in
FOLDER_PATH_FOR_EXCEL_FILE = '/Users/prakhar/Desktop/MA_trading_bot/saved_files/excel_trial_files_backtesting'
FOLDER_PATH_FOR_CSV_FILE = '/Users/prakhar/Desktop/MA_trading_bot/saved_files/csv_trial_files_backtesting'
FOLDER_PATH_FOR_SUMMARIZED_EXCEL_FILE = '/Users/prakhar/Desktop/MA_trading_bot/saved_files/excel_summary_files_backtesting'
FOLDER_PATH_FOR_PDF_SUMMARIZED_BACKTESTING_FILE = '/Users/prakhar/Desktop/MA_trading_bot/saved_files/pdf_summary_files-backtesting'
#Here the last symbol should be '/' because I am combining this path with the file name and hence creating a new path where the html portly chart gets saved
OUTPUT_FOLDER_PATH_FOR_PLOTLY_CHART = '/Users/prakhar/Desktop/MA_trading_bot/saved_files/charts_plotted_portly' 
