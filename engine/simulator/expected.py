from __future__ import annotations #stores hints as strings

from typing import Dict, List, Tuple
import pandas as pd

from engine.ml.predict import predict_next_week_points


def _build_features_for_week(
    history_df: pd.DataFrame,
    season: int,
    week: int,
    roster_ids: List[str],
) -> pd.DataFrame:
    """
    Build per-player features to predict points for (season, week),
    using only weeks < week (no leakage).
    Returns DF with: player_id, position, lag1_points, roll3_mean, roll5_mean
    """
    df = history_df[
        (history_df["season"] == season)
        & (history_df["player_id"].isin(roster_ids))
        & (history_df["week"] < week)
    ].copy()

    base = pd.DataFrame({"player_id": roster_ids})

    if df.empty:
        base["position"] = "UNK"
        base["lag1_points"] = 0.0
        base["roll3_mean"] = 0.0
        base["roll5_mean"] = 0.0
        return base

    df = df.sort_values(["player_id", "week"])
    g = df.groupby("player_id", sort=False)

    # rolling means based on past observed points
    df["roll3_mean"] = g["fantasy_points_ppr"].rolling(3, min_periods=1).mean().reset_index(level=0, drop=True)
    df["roll5_mean"] = g["fantasy_points_ppr"].rolling(5, min_periods=1).mean().reset_index(level=0, drop=True)

    # lag1 = last observed points (same as "last row" fantasy_points_ppr)
    last = g.tail(1).copy()
    last["lag1_points"] = last["fantasy_points_ppr"]

    last = last[["player_id", "position", "lag1_points", "roll3_mean", "roll5_mean"]]

    feat = base.merge(last, on="player_id", how="left")
    feat["position"] = feat["position"].fillna("UNK")
    feat["lag1_points"] = feat["lag1_points"].fillna(0.0)
    feat["roll3_mean"] = feat["roll3_mean"].fillna(0.0)
    feat["roll5_mean"] = feat["roll5_mean"].fillna(0.0)

    return feat


def simulate_expected_points(
    model,
    history_df: pd.DataFrame,
    roster_ids: List[str],
    season: int,
    start_week: int,
    end_week: int,
    optimal_lineup_fn,
) -> Tuple[List[float], List[List[str]]]:
    """
    For each week in [start_week, end_week], predict player points using ML,
    then select optimal lineup and sum points.
    Returns (weekly_totals, weekly_lineups).
    """
    weekly_totals: List[float] = []
    weekly_lineups: List[List[str]] = []

    for wk in range(start_week, end_week + 1):
        feat = _build_features_for_week(history_df, season, wk, roster_ids)

        preds = predict_next_week_points(model, feat)
        pred_points: Dict[str, float] = dict(zip(feat["player_id"], preds.astype(float).tolist()))
        pred_pos: Dict[str, str] = dict(zip(feat["player_id"], feat["position"].astype(str).tolist()))

        total, chosen = optimal_lineup_fn(pred_points, pred_pos)
        weekly_totals.append(float(total))
        weekly_lineups.append(chosen)

    return weekly_totals, weekly_lineups
