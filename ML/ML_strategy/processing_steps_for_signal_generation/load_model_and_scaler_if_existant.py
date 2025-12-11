import joblib

def load_model_and_scaler_if_existant(filepath):
    """
    Load a saved model bundle from disk.

    Supports bundles containing {'model': ..., 'scaler': ...}; scaler may be None
    (e.g., Random Forest models).
    """
    bundle = joblib.load(filepath)
    model = bundle['model']
    scaler = bundle.get('scaler', None)  # returns None if 'scaler' key doesn't exist, which does happen while loading a random forest model 
    return model, scaler
