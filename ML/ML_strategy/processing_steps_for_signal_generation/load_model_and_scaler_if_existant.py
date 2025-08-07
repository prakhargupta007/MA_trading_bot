import joblib

def load_model_and_scaler_if_existant(filepath):
    bundle = joblib.load(filepath)
    model = bundle['model']
    scaler = bundle.get('scaler', None)  # returns None if 'scaler' key doesn't exist, which does happen while loading a random forest model 
    return model, scaler
