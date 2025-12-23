import pandas as pd

def load_weekly_csv(path: str = "data/weekly.csv") -> pd.DataFrame:
    """
    Loads the weekly player dataset into a pandas DataFrame and keeps only columns we need.

    Expected columns in the CSV (based on your dataset):
    season, week, player_id, player_name, position, fantasy_points_ppr
    """
    df = pd.read_csv(path)

    needed_cols = [
        "season",
        "week",
        "player_id",
        "player_name",
        "position",
        "fantasy_points_ppr",
    ]
    df = df[needed_cols].copy()

    # Normalize types (so keys are consistent)
    df["season"] = df["season"].astype(int)
    df["week"] = df["week"].astype(int)
    df["player_id"] = df["player_id"].astype(str)
    df["player_name"] = df["player_name"].astype(str)
    df["position"] = df["position"].astype(str)

    # Missing points -> treat as 0.0 (player did not score / did not play / missing data)
    df["fantasy_points_ppr"] = df["fantasy_points_ppr"].fillna(0.0).astype(float)

    return df


def build_weekly_indexes(df: pd.DataFrame):
    """
    Turns the DataFrame into fast lookup structures:

    points_index[(season, week)][player_id] = points
    pos_index[(season, week)][player_id] = position
    name_by_id[player_id] = player_name

    Why do this?
      - DataFrame filtering each time is slow and annoying.
      - Dict lookups are fast and simple for a simulator.
    """
    points_index = {}
    pos_index = {}
    name_by_id = {}

    # Iterate row by row (beginner-friendly + explicit)
    for _, row in df.iterrows():
        season = int(row["season"])
        week = int(row["week"])
        player_id = str(row["player_id"])
        player_name = str(row["player_name"])
        position = str(row["position"])
        points = float(row["fantasy_points_ppr"])

        key = (season, week)

        if key not in points_index:
            points_index[key] = {}
            pos_index[key] = {}

        points_index[key][player_id] = points
        pos_index[key][player_id] = position

        # Keep a mapping for UI/debug
        # (If a player name repeats, it's fine — it should be consistent)
        name_by_id[player_id] = player_name

    return points_index, pos_index, name_by_id


def get_season_week_range(df: pd.DataFrame, season: int):
    """
    Returns (min_week, max_week) for a given season present in the data.
    """
    season_df = df[df["season"] == season]
    if len(season_df) == 0:
        raise ValueError(f"No rows found for season={season}")

    min_week = int(season_df["week"].min())
    max_week = int(season_df["week"].max())
    return min_week, max_week
