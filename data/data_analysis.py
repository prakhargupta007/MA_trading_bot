# Because of the fact that the sentiment analysis scores are only available from 2017 till 2025, only this exact date range needs to be used across all features for the data analysis.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data.funcs_for_data_prep_for_ML.label_data_with_future_window import label_data_with_future_window
from data.funcs_for_data_prep_for_ML.calculate_and_add_features_to_data import calculate_and_add_features_to_data
from sklearn.feature_selection import f_classif, mutual_info_classif
from sklearn.preprocessing import LabelEncoder, StandardScaler
from config import LOOKAHEAD_DAYS
from config_for_data_analysis import DATA_FOR_DATA_ANALYSIS, ALL_FEATURES
from config_for_data_analysis import DA_GSPC_DATA_FILE_PATH, DA_NDX_DATA_FILE_PATH, DA_VIX_DATA_FILE_PATH


def clean_data_for_feature_analysis(df, feature_list, target_col='Label'):
    """
    Drop NaN rows and show missing value diagnostics for the given features and target.
    Returns cleaned DataFrame ready for analysis.
    """
    print("\n--- Missing values per feature ---")
    missing_summary = df[feature_list + [target_col]].isna().sum().sort_values(ascending=False)
    print(missing_summary[missing_summary > 0])

    print("\nDropping rows with NaN values in features or target...")
    df_clean = df.dropna(subset=feature_list + [target_col]).copy()
    
    return df_clean



def analyze_feature_relationships(df, feature_list, target_col = 'Label', top_n=10, plot_corr=False, plot_distributions=False):
    """
    Analyze how features relate to each other and to a multiclass target.
    
    Returns:
        topFeaturesLinear (pd.DataFrame): Top features ranked by F-statistic (linear)
        topFeaturesTree (pd.DataFrame): Top features ranked by Mutual Information (non-linear)
    """

    # Ensure target is numeric
    y = df[target_col]
    if y.dtype == 'object' or y.dtype.name == 'category':
        y = LabelEncoder().fit_transform(y)

    X = df[feature_list].copy()

    # Optional: correlation heatmap
    if plot_corr:
        corr_matrix = X.corr(method='pearson')
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, cmap='coolwarm', center=0)
        plt.title("Feature-to-Feature Correlation Matrix")
        plt.tight_layout()
        plt.show()

    # === Feature vs Target ===
    f_vals, _ = f_classif(X, y)
    mi_vals = mutual_info_classif(X, y, discrete_features=False, random_state=42)

    f_scores = pd.Series(f_vals, index=feature_list).sort_values(ascending=False)
    mi_scores = pd.Series(mi_vals, index=feature_list).sort_values(ascending=False)

    # Combine into DataFrame
    summary_df = pd.DataFrame({
        'F_stat': f_scores,
        'MI_score': mi_scores
    })

    # Rank by linear (F-stat) and non-linear (MI)
    topFeaturesLinear = summary_df.sort_values(by='F_stat', ascending=False).head(top_n)
    topFeaturesTree = summary_df.sort_values(by='MI_score', ascending=False).head(top_n)

    # Optional: distributions
    if plot_distributions:
        for feat in topFeaturesLinear.index[:min(top_n, 5)]:
            plt.figure(figsize=(6, 4))
            sns.boxplot(x=df[target_col], y=df[feat])
            plt.title(f"Distribution of {feat} by Target Class")
            plt.xlabel("Target Class")
            plt.ylabel(feat)
            plt.tight_layout()
            plt.show()

    return topFeaturesLinear, topFeaturesTree

    # --- Optional plotting of top-n (commented out for flexibility) ---
    # top_features = summary_df.sort_values(by='F_stat', ascending=False).head(top_n).index
    # for feat in top_features:
    #     plt.figure(figsize=(6, 4))
    #     sns.boxplot(x=df[target_col], y=df[feat])
    #     plt.title(f"Distribution of {feat} by Target Class")
    #     plt.xlabel("Target Class")
    #     plt.ylabel(feat)
    #     plt.tight_layout()
    #     plt.show()









# --- Load original data ---
data = pd.read_csv(DATA_FOR_DATA_ANALYSIS)

# --- Calculate features ---
data_with_features = calculate_and_add_features_to_data(
    data,
    DA_GSPC_DATA_FILE_PATH,
    DA_NDX_DATA_FILE_PATH,
    DA_VIX_DATA_FILE_PATH,
    ALL_FEATURES,
)

labeled_data = label_data_with_future_window(data_with_features, LOOKAHEAD_DAYS)
print(f'Data labeled with future window of {LOOKAHEAD_DAYS} days\n')

df_clean = clean_data_for_feature_analysis(labeled_data, ALL_FEATURES, target_col='Label')
print(f"Remaining rows after cleaning: {len(df_clean)}")

top_linear, top_tree = analyze_feature_relationships(df_clean, ALL_FEATURES)
print("\n=== Top Linear Features (F-stat) ===")
print(top_linear)
print("\n=== Top Non-Linear Features (Mutual Information) ===")
print(top_tree)


print("\nFeature analysis complete!")
