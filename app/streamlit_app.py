import sys
from pathlib import Path

# Ensure repo root is on Python path so `engine` imports work
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from engine.loading_data.load import load_weekly_csv, build_weekly_indexes, get_season_week_range
from engine.simulator.simulate import Trade, counterfactual_replay, apply_trade_to_roster
from engine.simulator.lineup import optimal_lineup_points
from engine.ml.predict import load_model
from engine.simulator.expected import simulate_expected_points

data_path = "dataset/weekly.csv"

@st.cache_data #caches function outputs. so the function of load_data, the outputs of this function will be cached, sort of stored in the database
def load_data():
    return load_weekly_csv(data_path)

@st.cache_resource #caches long-lived resources such as ml models
def load_ml_model():
    return load_model("models/next_week_model.joblib")

def plot_lines(x, y1, y2, label1, label2, title):
    fig = plt.figure()
    plt.plot(x, y1, label=label1)
    plt.plot(x, y2, label=label2)
    plt.title(title)
    plt.legend()
    st.pyplot(fig)

def plot_cumulative(x, cum, title):
    fig = plt.figure()
    plt.plot(x, cum, label="Cumulative delta")
    plt.axhline(0, linestyle="--")
    plt.title(title)
    plt.legend()
    st.pyplot(fig)

def main():
    st.title("TradeZone — Trade Regret Simulator + ML")

    df = load_data()

    seasons = sorted(df["season"].unique())
    season = st.selectbox("Season", seasons, index=len(seasons) - 1)

    min_w, max_w = get_season_week_range(df, season)
    trade_week = st.slider("Trade week", min_value=min_w, max_value=max_w - 1, value=min(6, max_w - 1))

    mode = st.radio(
        "Mode",
        ["Historical Replay (real points)", "ML Expected Replay (predicted)"]
    )

    season_df = df[df["season"] == season]
    name_to_id = (
        season_df[["player_name", "player_id"]]
        .drop_duplicates()
        .set_index("player_name")["player_id"]
        .to_dict()
    )

    all_names = sorted(name_to_id.keys())

    st.subheader("Roster")
    roster_names = st.multiselect("Starting roster", all_names, default=all_names[:20])
    roster_ids = [name_to_id[n] for n in roster_names]

    st.subheader("Trade")
    give_names = st.multiselect("You give away", roster_names)
    get_names = st.multiselect("You receive", [n for n in all_names if n not in roster_names])

    if st.button("Run Simulation"):
        if not roster_ids or not give_names or not get_names:
            st.error("Please select a roster and trade players.")
            return

        trade = Trade(
            week=int(trade_week),
            give=[name_to_id[n] for n in give_names],
            get=[name_to_id[n] for n in get_names],
        )

        points_index, pos_index, _ = build_weekly_indexes(df)

        if mode.startswith("Historical"):
            res = counterfactual_replay(
                original_roster=roster_ids,
                trade=trade,
                points_index=points_index,
                pos_index=pos_index,
                season=int(season),
                end_week=int(max_w),
            )

            weeks = list(range(trade_week, max_w + 1))
            st.write("Total delta points:", round(res["total_delta"], 2))

            plot_lines(
                weeks,
                res["weekly_with_trade"],
                res["weekly_without_trade"],
                "With trade",
                "Without trade",
                "Weekly Points"
            )
            plot_cumulative(weeks, res["cumulative_delta"], "Cumulative Regret")

        else:
            model = load_ml_model()

            roster_without = roster_ids.copy()
            roster_with = apply_trade_to_roster(roster_ids, trade)

            weekly_without, _ = simulate_expected_points(model=model, history_df=df, roster=roster_without)
