import pandas as pd

target_col = "fantasy_points_ppr"

def make_features(df: pd.DataFrame) -> pd.DataFrame:
#the arrow means to basically return something with the type "pd.DataFrame" in this case
    needed = ["season", "week", "player_id", "player_name", "position", target_col]
    df = df[needed].copy()

    df["season"] = df["season"].astype(int)
    df["week"] = df["week"].astype(int)
    df["player_id"] = df["player_id"].astype(str)
    df["position"] = df["position"].astype(str)
    df[target_col] = df[target_col].fillna(0.0).astype(float)

    df = df.sort_values(["player_id", "season", "week"])

    g = df.groupby(["player_id", "season"], sort=False)

    # Lag features
    df["lag1_points"] = g[target_col].shift(1)

    # Rolling features based only on past weeks
    df["roll3_mean"] = g[target_col].transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    df["roll5_mean"] = g[target_col].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())

    # Target: next week's points
    df["y_next_week"] = g[target_col].shift(-1)

    # Fill early-week missing lag (week 1 has no lag)
    df["lag1_points"] = df["lag1_points"].fillna(0.0)

    # Drop rows with no next week target (last week of each player-season)
    df = df.dropna(subset=["y_next_week"]).copy()
    df["y_next_week"] = df["y_next_week"].astype(float)

    return df
