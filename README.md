**🏈 TradeZone — Fantasy Football Trade Regret Simulator (with ML)**

TradeZone is an end-to-end fantasy football trade analysis system that lets users replay the rest of a season with and without a trade, using either:
- Historical outcomes (what actually happened), or
- Machine-learning predictions (what was expected to happen)

The result is a counterfactual regret curve that answers:
“If I made this trade in Week X, how would my season have changed?”

**🔥 Key Features**
1. Deterministic Historical Replay - Replays the remainder of a season using real weekly fantasy points, and automatically selects the optimal lineup each week:

Outputs: 
- Weekly points (with vs without trade)
- Cumulative regret curve
- Total point delta

**2. ML-Based Expected Replay**
- Trains a regression model to predict next-week fantasy points
- Uses only past information (no data leakage)
- Replays the season using expected points instead of actual outcomes

**3. Interactive Streamlit App**
- Pick season, trade week, roster, and trade
- Switch between: Historical replay or ML-expected replay
- Visualize regret over time with plots

📁 Project Structure
tradezone/
│
├── app/
│   └── streamlit_app.py        # Interactive UI
│
├── engine/
│   ├── loading_data/
│   │   └── load.py             # Dataset loading + indexing
│   │
│   ├── simulator/
│   │   ├── lineup.py           # Optimal lineup optimizer
│   │   ├── simulate.py         # Historical counterfactual replay
│   │   └── expected.py         # ML expected replay
│   │
│   └── ml/
│       ├── features.py         # Feature engineering
│       ├── train.py            # Model training
│       └── predict.py          # Model inference
│
├── dataset/
│   └── weekly.csv    # NFL weekly stats (see below) #this is not commited here because the dataset is too big but you will have to download the dataset yourself (instructions below)
│
├── models/
│   └── next_week_model.joblib  # Trained ML model
│
├── requirements.txt
└── README.md

**📊 Dataset Instructions**
Dataset Used: This project uses weekly NFL player statistics from nfl_data_py, specifically:

- weekly_player_stats_offense.csv

1. Download the dataset from:
   https://www.kaggle.com/datasets/philiphyde1/nfl-stats-1999-2022/data?select=weekly_player_stats_offense.csv

2. Unzip the files

3. Place them in:
   tradezone/dataset/

Required Columns

The pipeline expects the following columns (present in the dataset):
- season, week, player_id, player_name, position, fantasy_points_ppr

**Setup Instructions**

Download the dataset (from Kaggle or nfl_data_py)

Place it in the project as:

dataset/weekly.csv

Verify it loads correctly:

python -c "import pandas as pd; df=pd.read_csv('dataset/weekly.csv'); print(df.shape)"

**🤖 Machine Learning Details**
Target: Predict next week’s fantasy points (PPR)

Features:
- Built using only past information:
- lag1_points — last week’s points
- roll3_mean — rolling 3-week mean
- roll5_mean — rolling 5-week mean
- position — one-hot encoded

**Model**

- HistGradientBoostingRegressor

- Season-based train/test split

- Handles non-linear player performance patterns

**Train the Model**
python -m engine.ml.train


This creates:
models/next_week_model.joblib

**▶️ Running the App**
- Start Streamlit
From the project root:
streamlit run app/streamlit_app.py
Open the local URL shown in the terminal.

