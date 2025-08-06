import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

def universal_permutation_importance_score(model, X_test, y_test, feature_names, scoring='accuracy', n_repeats=10, random_state=42):

    '''
    (df is shortform for data frame)
    Calculates permutation-based feature importance.

    Parameters:
    - model: Trained model
    - X_test: Test feature set (scaled or unscaled depending on model)
    - y_test: Test labels
    - feature_names: list of feature names in the same order as model input
    - scoring: metric to evaluate drop in performance
    - n_repeats: number of shuffles for each feature
    - random_state: reproducibility

    Returns:
    - Pandas DataFrame with features and their importance scores

    --> This fucntion is slower than  the logistic_coefffcient_importance method, as this process gets iterated n_repeats times
    '''

    result = permutation_importance(
        model, X_test, y_test,
        scoring=scoring,
        n_repeats=n_repeats,
        random_state=random_state
    )

    permutation_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': result.importances_mean
    }).sort_values(by='Importance', ascending=False).reset_index(drop=True)

    return permutation_importance_df