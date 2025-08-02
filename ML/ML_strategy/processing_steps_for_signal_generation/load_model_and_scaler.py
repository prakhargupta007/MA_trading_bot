import joblib
def load_model_and_scaler(filepath):
    bundle = joblib.load(filepath)
    return bundle['model'], bundle['scaler']
