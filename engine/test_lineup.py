#testing the lineup functionality

from engine.simulator.lineup import optimal_lineup_points

roster_points = {
    "qb1": 22, "rb1": 18, "rb2": 10, "rb3": 6,
    "wr1": 14, "wr2": 13, "wr3": 9,
    "te1": 11, "te2": 4,
}

roster_position = {
    "qb1": "QB",
    "rb1": "RB", "rb2": "RB", "rb3": "RB",
    "wr1": "WR", "wr2": "WR", "wr3": "WR",
    "te1": "TE", "te2": "TE",
}

total, chosen = optimal_lineup_points(roster_points, roster_position)

print("Chosen:", chosen)
print("Total:", total)
