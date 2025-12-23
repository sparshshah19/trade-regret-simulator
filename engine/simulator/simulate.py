from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from simulator.lineup import optimal_lineup_points


@dataclass(frozen=True)
class Trade:
    """
    week: the week the trade happens (inclusive)
    give: player_ids you are sending away
    get: player_ids you are receiving
    """
    week: int
    give: List[str]
    get: List[str]


def apply_trade_to_roster(roster: List[str], trade: Trade) -> List[str]:
    """
    Returns a NEW roster list after applying the trade.
    We do not modify the original roster in-place (simpler to reason about).
    """
    new_roster = roster.copy()

    # Remove "give" players if present
    for pid in trade.give:
        if pid in new_roster:
            new_roster.remove(pid)

    # Add "get" players (avoid duplicates)
    for pid in trade.get:
        if pid not in new_roster:
            new_roster.append(pid)

    return new_roster


def build_roster_week_views(
    roster: List[str],
    points_for_week: Dict[str, float],
    pos_for_week: Dict[str, str],
) -> Tuple[Dict[str, float], Dict[str, str]]:
    """
    Given a roster (list of player_ids) and the global week dictionaries,
    build just the data needed by the lineup optimizer:

      roster_points[player_id] = points
      roster_positions[player_id] = position

    If a player doesn't appear in the data for that week, we assume 0 points.
    """
    roster_points = {}
    roster_positions = {}

    for pid in roster:
        # points default to 0 if player has no entry that week
        pts = points_for_week.get(pid, 0.0)
        roster_points[pid] = pts

        # position might be missing if player didn't appear that week
        # in that case we skip their position (optimizer will ignore unknowns)
        if pid in pos_for_week:
            roster_positions[pid] = pos_for_week[pid]

    return roster_points, roster_positions


def simulate_season_points(
    roster: List[str],
    points_index: Dict[Tuple[int, int], Dict[str, float]],
    pos_index: Dict[Tuple[int, int], Dict[str, str]],
    season: int,
    start_week: int,
    end_week: int,
) -> Tuple[List[float], List[List[str]]]:
    """
    Simulates team points from start_week..end_week (inclusive).
    Each week:
      - pull each roster player's real historical points
      - choose optimal lineup
      - sum points

    Returns:
      weekly_totals: list of floats
      weekly_lineups: list of chosen-player-id lists
    """
    weekly_totals = []
    weekly_lineups = []

    for week in range(start_week, end_week + 1):
        key = (season, week)

        # If week isn't in dataset, treat as no data (0 points)
        points_for_week = points_index.get(key, {})
        pos_for_week = pos_index.get(key, {})

        roster_points, roster_positions = build_roster_week_views(
            roster=roster,
            points_for_week=points_for_week,
            pos_for_week=pos_for_week,
        )

        total_points, chosen_players = optimal_lineup_points(
            roster_points=roster_points,
            roster_position=roster_positions,
        )

        weekly_totals.append(total_points)
        weekly_lineups.append(chosen_players)

    return weekly_totals, weekly_lineups


def counterfactual_replay(
    original_roster: List[str],
    trade: Trade,
    points_index: Dict[Tuple[int, int], Dict[str, float]],
    pos_index: Dict[Tuple[int, int], Dict[str, str]],
    season: int,
    end_week: int,
) -> Dict[str, object]:
    """
    Runs two simulations from trade.week .. end_week:

    World A: trade happens
    World B: trade does NOT happen

    Returns a dict with:
      - weekly_with_trade
      - weekly_without_trade
      - weekly_delta
      - cumulative_delta
      - total_delta
      - lineups_with_trade
      - lineups_without_trade
    """
    start_week = trade.week

    roster_without = original_roster.copy()
    roster_with = apply_trade_to_roster(original_roster, trade)

    weekly_without, lineups_without = simulate_season_points(
        roster=roster_without,
        points_index=points_index,
        pos_index=pos_index,
        season=season,
        start_week=start_week,
        end_week=end_week,
    )

    weekly_with, lineups_with = simulate_season_points(
        roster=roster_with,
        points_index=points_index,
        pos_index=pos_index,
        season=season,
        start_week=start_week,
        end_week=end_week,
    )

    weekly_delta = []
    cumulative_delta = []
    running = 0.0

    for i in range(len(weekly_with)):
        d = weekly_with[i] - weekly_without[i]
        weekly_delta.append(d)

        running += d
        cumulative_delta.append(running)

    result = {
        "weekly_with_trade": weekly_with,
        "weekly_without_trade": weekly_without,
        "weekly_delta": weekly_delta,
        "cumulative_delta": cumulative_delta,
        "total_delta": cumulative_delta[-1] if cumulative_delta else 0.0,
        "lineups_with_trade": lineups_with,
        "lineups_without_trade": lineups_without,
    }
    return result
