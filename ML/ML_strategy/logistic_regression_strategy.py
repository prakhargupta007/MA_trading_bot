import joblib

data = joblib.load('models/saved_models/lr_model_AAPL.joblib')
model = data['model']
scaler = data['scaler']
