import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --------- DATA ---------- #

regions = ["NO1", "NO2", "NO5"]

vindu = [
    "October", "October w/Temp",
    "November", "November w/Temp",
    "December", "December w/Temp",
    "January", "January w/Temp",
    "February", "February w/Temp",
    "March", "March w/Temp"
]

values = [
    [2.65, 3.49, 2.16],
    [2.57, 3.52, 2.09],
    [2.50, 3.79, 2.50],
    [2.86, 3.70, 2.50],
    [3.13, 4.57, 2.87],
    [3.44, 4.57, 2.88],
    [4.51, 4.85, 3.60],
    [3.90, 4.23, 2.99],
    [4.55, 4.82, 3.59],
    [3.75, 4.34, 3.28],
    [3.76, 4.54, 3.45],
    [3.59, 4.56, 3.45]
]

ci_high = [
    [3.23, 3.98, 2.53],
    [3.14, 4.01, 2.46],
    [2.93, 4.16, 2.78],
    [3.26, 4.07, 2.78],
    [3.45, 4.85, 3.10],
    [3.75, 4.84, 3.10],
    [4.81, 5.09, 3.83],
    [4.19, 4.47, 3.22],
    [4.90, 5.09, 3.85],
    [4.10, 4.61, 3.53],
    [4.15, 4.81, 3.68],
    [3.97, 4.83, 3.68]
]

ci_low = [
    [2.08, 3.00, 1.79],
    [2.01, 3.03, 1.72],
    [2.08, 3.42, 2.21],
    [2.46, 3.34, 2.23],
    [2.81, 4.30, 2.64],
    [3.13, 4.30, 2.66],
    [4.20, 4.61, 3.36],
    [3.62, 3.99, 2.76],
    [4.19, 4.55, 3.34],
    [3.41, 4.07, 3.03],
    [3.38, 4.27, 3.21],
    [3.21, 4.29, 3.21]
]

temp_forskjeller = [
    [-0.296808, -0.177694, -0.411089],
    [1.3, 0.6, 0.3],
    [1.3, 0.8, 0.6],
    [-3.2, -3.1, -3.4],
    [-3.969351, -2.511806, -2.368161],
    [-0.466297, -0.195126, -0.154375]
]

# ✅ NY: Dynamic group data
dynamic_values = [
    [1.37, 2.51, 1.07], #okt
    [1.37, 2.51, 1.07],  #okt m temp
    [1.49, 2.63, 1.64], #nov
    [1.49, 2.63, 1.64],  #nov m temp
    [2.32, 3.59, 2.04], #des
    [2.32, 3.59, 2.04],  #des m temp
    [2.70, 3.31, 2.31], #jan
    [2.70, 3.31, 2.31],  #jan m temp
    [3.24, 3.80, 3.12], #feb
    [3.24, 3.80, 3.12],  #feb m temp
    [3.59, 4.56, 3.45], #mars
    [3.59, 4.56, 3.45]   #mars m temp
]

# -------- REORGANISER --------
values = np.array(values).T
ci_high = np.array(ci_high).T
ci_low = np.array(ci_low).T
temp_forskjeller = np.array(temp_forskjeller).T
dynamic_values = np.array(dynamic_values).T

# -------- DATAFRAME --------
rows = []
for r, region in enumerate(regions):
    for i, win in enumerate(vindu):
        rows.append({
            "region": region,
            "vindu": win,
            "value": values[r][i],
            "ci_high": ci_high[r][i],
            "ci_low": ci_low[r][i],
            "dynamic": dynamic_values[r][i]
        })

df = pd.DataFrame(rows)

df["temp"] = df["vindu"].str.contains("Temp")
df["month"] = df["vindu"].str.replace(" w/Temp", "")

month_order = ["October", "November", "December", "January", "February", "March"]
month_short = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)

# --------- PLOT ---------- #
def plot(df):

    months = df["month"].cat.categories
    regions = sorted(df["region"].unique())

    n_m = len(months)
    x_idx = np.arange(n_m)

    fig, ax = plt.subplots(figsize=(12,6))
    ax.set_ylim(-4, 6)

    color_map = {
        "NO1": "#2C7FB8",
        "NO2": "#1A9641",
        "NO5": "tomato"
    }

    for i, region in enumerate(regions):

        for temp_flag in [False, True]:

            sub = df[(df["region"] == region) & (df["temp"] == temp_flag)]
            sub = sub.set_index("month").reindex(months)

            xi = i * n_m + x_idx

            y = sub["value"].values
            lo = sub["ci_low"].values
            hi = sub["ci_high"].values
            y_dyn = sub["dynamic"].values

            marker = "^" if temp_flag else "o"

            ax.errorbar(xi, y,
                        yerr=[np.maximum(y-lo,0), np.maximum(hi-y,0)],
                        fmt="none",
                        color=color_map[region],
                        capsize=5)

            ax.scatter(xi, y,
                       color=color_map[region],
                       marker=marker,
                       s=150,
                       edgecolor="white",
                       zorder=3)

            # ✅ Dynamic group (X)
            ax.scatter(xi, y_dyn,
                       color=color_map[region],
                       marker="x",
                       s=120,
                       linewidths=2.5,
                       zorder=4)

    # ---- X-akse ----
    xticks = []
    xtick_labels = []

    for i in range(len(regions)):
        for j in range(n_m):
            xticks.append(i * n_m + j)
            xtick_labels.append(month_short[j])

    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, fontsize=20)

    # ---- FARGER ----
    for i, tick in enumerate(ax.get_xticklabels()):
        region_index = i // n_m
        region = regions[region_index]
        tick.set_color(color_map[region])

    plt.yticks(fontsize=20)

    # ---- REGION LABEL ----
    y_text = ax.get_ylim()[0] - 1.2

    for i, region in enumerate(regions):
        x_center = i * n_m + (n_m - 1) / 2
        ax.text(x_center, y_text, region,
                ha="center", va="top",
                fontsize=20, fontweight="bold")

    ax.set_ylabel("Change in Electricity Consumption [%]", fontsize=20)

    # ---- Temperatur ----
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_ylabel("Temperature Difference [°C]", fontsize=20)
    plt.yticks(fontsize=20)

    for i, region in enumerate(regions):
        for j in range(n_m):
            ax2.scatter(i * n_m + j,
                        temp_forskjeller[i][j],
                        marker="s",
                        color=color_map[region],
                        s=80)

    ax.axhline(0, color="gray", linestyle="--")
    ax.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.4)

    plt.subplots_adjust(bottom=0.25)

    # ---- LEGEND ----
    from matplotlib.lines import Line2D
    ax2.legend([
        Line2D([0],[0],marker='s',color='black',linestyle='None',markersize=10),
        Line2D([0],[0],marker='o',color='black',linestyle='None',markersize=10),
        Line2D([0],[0],marker='^',color='black',linestyle='None',markersize=10),
        Line2D([0],[0],marker='x',color='black',linestyle='None',markersize=10)
    ],
    ["Temperature difference",
     "DiD without temp",
     "DiD with temp",
     "DiD w/Dynamic group"],
    loc="center", bbox_to_anchor = (0.85,0.89) ,fontsize=14, framealpha=0.3)

    plt.show()

# -------- RUN -------- #
plot(df)