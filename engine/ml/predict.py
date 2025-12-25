import joblib
import pandas as pd
from typing import Optional

model_path= "models/next_week_model.joblib"

def load_model(path: str = model_path):
    return joblib.load(path)

def predict_next_week_points(
    model,
    features_df: pd.DataFrame,
    position_col: str = "position"
) -> pd.Series:
    """
    features_df must include:
    - lag1_points, roll3_mean, roll5_mean, position
    Returns a Series of predictions aligned to features_df index.
    """
    required = ["lag1_points", "roll3_mean", "roll5_mean", position_col]
    missing = [c for c in required if c not in features_df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    X = features_df[["lag1_points", "roll3_mean", "roll5_mean", position_col]]
    preds = model.predict(X)
    return pd.Series(preds, index=features_df.index, name="pred_next_week")
