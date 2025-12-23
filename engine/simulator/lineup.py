from typing import Dict, List, Tuple, Set

SLOTS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1}
FLEX_ALLOWED: Set[str] = {"RB", "WR", "TE"}

def optimal_lineup_points(
    roster_points: Dict[str, float],
    roster_position: Dict[str, str],
) -> Tuple[float, List[str]]:
    """
    Greedy:
        1) Pick top scorers for QB/RB/WR/TE
        2) Pick top remaining RB/WR/TE for FLEX
    """
    # Group player_ids by position (O(n))
    by_pos: Dict[str, List[str]] = {"QB": [], "RB": [], "WR": [], "TE": []}
    for pid in roster_points:
        pos = roster_position.get(pid)
        if pos in by_pos:
            by_pos[pos].append(pid)

    # Sort each list by points descending (total ~ O(n log n))
    for pos, pids in by_pos.items():
        pids.sort(key=lambda pid: roster_points[pid], reverse=True)

    chosen: List[str] = []
    remaining = set(roster_points.keys())

    # Fill fixed slots (O(n) across all picks)
    for pos in ["QB", "RB", "WR", "TE"]:
        need = SLOTS[pos]
        picked = 0
        for pid in by_pos[pos]:
            if picked == need:
                break
            if pid in remaining:
                chosen.append(pid)
                remaining.remove(pid)
                picked += 1

    # FLEX: consider remaining RB/WR/TE only
    flex_candidates = [
        pid for pid in remaining
        if roster_position.get(pid) in FLEX_ALLOWED
    ]
    flex_candidates.sort(key=lambda pid: roster_points[pid], reverse=True)

    for pid in flex_candidates[:SLOTS["FLEX"]]:
        chosen.append(pid)
        remaining.remove(pid)

    total = sum(roster_points[pid] for pid in chosen)
    return total, chosen
