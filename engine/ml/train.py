import os
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from engine.ml.features import make_features

data_path = "dataset/weekly.csv"
model_path= "models/next_week_model.joblib"

num_cols = ["lag1_points", "roll3_mean", "roll5_mean"]
cat_cols = ["position"]

def train_test_split_by_season(feat_df: pd.DataFrame):
    seasons = sorted(feat_df["season"].unique())
    if len(seasons) < 3:
        raise ValueError("Need at least 3 seasons for a safe season-based split.")

    test_seasons = [seasons[-1]]      # most recent season
    train_seasons = seasons[:-1]      # everything before

    train_df = feat_df[feat_df["season"].isin(train_seasons)].copy()
    test_df = feat_df[feat_df["season"].isin(test_seasons)].copy()
    return train_df, test_df, train_seasons, test_seasons

def build_pipeline():
    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imp", SimpleImputer(strategy="median"))]), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )

    model = HistGradientBoostingRegressor(
        max_depth=6,
        learning_rate=0.07,
        random_state=42
    )

    return Pipeline([("pre", pre), ("model", model)])

def main():
    df = pd.read_csv(data_path)
    feat_df = make_features(df)

    train_df, test_df, train_seasons, test_seasons = train_test_split_by_season(feat_df)

    X_train = train_df[num_cols + cat_cols]
    y_train = train_df["y_next_week"]

    X_test = test_df[num_cols + cat_cols]
    y_test = test_df["y_next_week"]

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    preds = pipe.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5

    print("Train seasons:", train_seasons)
    print("Test seasons:", test_seasons)
    print("Test MAE:", round(mae, 3))
    print("Test RMSE:", round(rmse, 3))

    os.makedirs("models", exist_ok=True)
    joblib.dump(pipe, model_path)
    print("Saved:", model_path)

if __name__ == "__main__":
    main()
