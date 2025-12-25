from engine.loading_data.load import load_weekly_csv, build_weekly_indexes, get_season_week_range
from simulator.simulate import Trade, counterfactual_replay

def main():
    #1 let's load + index data
    df = load_weekly_csv("data/weekly.csv")
    points_index, pos_index, name_by_id = build_weekly_indexes(df)

    #2 choose a season and week range
    season = int(df["season"].max())  # most recent season in file
    min_w, max_w = get_season_week_range(df, season)

    print(f"Using season={season}, weeks={min_w}..{max_w}")

    # 3) Define a fake roster (will replace with real roster IDs later)
    # Pick a handful of known player_ids from your dataset later.
    # For now we’ll just take the first 25 unique player_ids as a dummy roster.


    #first part is boolean, so true, .dropna removes missing player ids, astype(str) converts ids to str
    #then .unique keeps the unique ids, .tolist() makes it a list, and :25 keeps the first 25 ids. 
    #the df outside is going to filter the dataframe to only that. 

    roster = df[df["season"] == season]["player_id"].dropna().astype(str).unique().tolist()[:25]

    # 4) Define a sample trade at some week
    trade_week = max(min_w, 5)
    trade = Trade(
        week=trade_week,
        give=roster[:1],       # give away 1 player
        get=roster[1:2],       # receive 1 player (dummy)
    )

    # 5) Run replay from trade week to end of season
    result = counterfactual_replay(
        original_roster=roster,
        trade=trade,
        points_index=points_index,
        pos_index=pos_index,
        season=season,
        end_week=max_w,
    )

    print("Total delta points (with - without):", result["total_delta"])

    # Show first few weeks deltas
    print("Weekly delta (first 5):", result["weekly_delta"][:5])
    print("Cumulative delta (first 5):", result["cumulative_delta"][:5])

if __name__ == "__main__":
    main()
