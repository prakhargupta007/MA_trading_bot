import numpy as np
import pandas as pd

def logistic_coefficient_importance(model, feature_names):
    """
    This function  calculates feature importance for a logistic regression model
    based on the average absolute coefficient values.
    This works only for logistic regression models 

    Parameters:
    - model: Trained LogisticRegression model
    - feature_names: list of feature names in the same order as model input

    Returns:
    - Pandas DataFrame with features and their importance scores
    """

    if not hasattr(model, "coef_"):
        raise ValueError("This method works only for linear models with coef_ attribute.")

    coef = model.coef_  # shape: (n_classes, n_features)
    avg_importance = np.mean(np.abs(coef), axis=0)  # average across classes

    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': avg_importance
    }).sort_values(by='Importance', ascending=False).reset_index(drop=True)

    return importance_df