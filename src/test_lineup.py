from engine.simulator.lineup import optimal_lineup_points

def test_optimal_lineup_basic():
    roster_points = {
        "qb": 20,
        "rb1": 15, "rb2": 10,
        "wr1": 14, "wr2": 13,
        "te": 8,
    }
    roster_pos = {
        "qb": "QB",
        "rb1": "RB", "rb2": "RB",
        "wr1": "WR", "wr2": "WR",
        "te": "TE",
    }

    total, chosen = optimal_lineup_points(roster_points, roster_pos)

    assert total == 20 + 15 + 10 + 14 + 13 + 8
    assert len(chosen) == 7
