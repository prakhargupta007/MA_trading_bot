def xgboost_gain_importance(model, feature_names):
    booster = model.get_booster()
    importance_dict = booster.get_score(importance_type='gain')
    return sorted(
        [(k, v) for k, v in importance_dict.items()],
        key=lambda x: x[1],
        reverse=True
    )