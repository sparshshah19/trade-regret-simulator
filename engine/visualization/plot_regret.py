#plotting the graph

import matplotlib.pyplot as plt

def plot_regret(weeks, with_trade, without_trade, cumulative):
    plt.figure(figsize=(20,20))
    plt.plot(weeks, with_trade, label="With Trade")
    plt.plot(weeks, without_trade, label="Without Trade")
    plt.legend()
    plt.title("Weekly Points Comparison")
    plt.show()

    plt.figure(figsize=(10,6))
    plt.plot(weeks, cumulative, label="Cumulative Regret")
    plt.axhline(0, linestyle="--")
    plt.legend()
    plt.title("Trade Regret Curve")
    plt.show()
