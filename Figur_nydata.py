import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --------- DATA ---------- #

regions = ["NO1", "NO2", "NO5"]

vindu = [
    "October",
    "October w/Temp",
    "November",
    "November w/Temp",
    "December",
    "December w/Temp",
    "January",
    "January w/Temp",
    "February",
    "February w/Temp",
    "March",
    "March w/Temp"
]

# ----------------- FYLL INN VERDIER HER, VERDIER, KONFIDENSINTERVALL OG SÅ TEMP DIFF ---------------------

values = [
    [2.65, 3.49, 2.16],   #oct
    [2.57, 3.52, 2.09],        #oct med temp
    [2.50, 3.79, 2.50],  #nov
    [2.86, 3.70, 2.50],  #nov m temp osvosv
    [3.13, 4.57, 2.87],   #des
    [3.44, 4.57, 2.88],    #des m temp
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
    [-0.296808, -0.177694, -0.411089],    #oktober
    [ 1.3,  0.6,  0.3],                   # november
    [ 1.3,  0.8,  0.6],                  # desember
    [-3.2, -3.1, -3.4],                   # januar
    [-3.969351, -2.511806, -2.368161],    # februar
    [-0.466297, -0.195126, -0.154375]     #mars
]

# ----------------------- DONT TOUCH HERFRAAAA,DATAFRAME ---------------------------------

rows = []
for i, win in enumerate(vindu):
    for r in range(3):
        rows.append({
            "region": regions[r],
            "vindu": win,
            "value": values[i][r],
            "ci_high": ci_high[i][r],
            "ci_low": ci_low[i][r]
        })

df = pd.DataFrame(rows)



df["temp"] = df["vindu"].str.contains("Temp")
df["month"] = df["vindu"].str.replace(" w/Temp", "")

# Sortering
month_order = ["October" ,"November", "December", "January", "February", "March"]
df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)

# --------- PLOT ---------- #

def plot(df):

    months = df["month"].cat.categories
    regions = sorted(df["region"].unique())

    n_m = len(months)
    n_r = len(regions)

    x_idx = np.arange(n_m)
    width = 0.6
    offsets = np.linspace(-width/2, width/2, n_r)

    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_ylim(-4, 6)

    colors = sns.color_palette("tab10", n_r)
    color_map = dict(zip(regions, colors))

    # ---- PLOT ----
    for i, region in enumerate(regions):

        for temp_flag in [False, True]:

            sub = df[(df["region"] == region) & (df["temp"] == temp_flag)]
            sub = sub.set_index("month").reindex(months)

            xi = x_idx + offsets[i]

            y = sub["value"].values
            lo = sub["ci_low"].values
            hi = sub["ci_high"].values

            err_low = np.maximum(y - lo, 0)
            err_high = np.maximum(hi - y, 0)

            marker = "^" if temp_flag else "o"

            ax.errorbar(xi, y, yerr=[err_low, err_high],
                        fmt="none", color=color_map[region], capsize=5)

            ax.scatter(xi, y,
                       color=color_map[region],
                       marker=marker,
                       s=150,
                       edgecolor="white",
                       zorder=3)

    # ---- X-akse (måneder OG NO125) ----

    xticks = []
    xtick_labels = []

    for j in range(n_m):
        for region in regions:
            xticks.append(x_idx[j] + offsets[regions.index(region)])
            xtick_labels.append(region)

    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, fontsize=18)
    ax.set_ylabel("Change in Electricity Consumption [%]", color = 'black', fontsize=20)

    # Fargeee
    for tick, label in zip(ax.get_xticklabels(), xtick_labels):
        tick.set_color(color_map[label])

    # ---- SUB-LABELS (NO1, NO2, NO5) ----
    y_text = ax.get_ylim()[0] - 1.2

    # ---- MÅNEDER UNDER LENGER NED ----
    y_text = ax.get_ylim()[0] - 0.8

    for j, month in enumerate(months):
        # midtpunkt mellom NO1 NO2 NO5
        x_center = np.mean([x_idx[j] + off for off in offsets])

        ax.text(
            x_center,
            y_text,
            month,
            ha="center",
            va="top",
            fontsize=20,
            color="black"
        )

    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # ---- ANDRE Y-AKSE (TEMPERATUR) ----
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_ylabel("Temperature Difference [°C]", color = 'black', fontsize=20)
    ax2.tick_params(axis='y',labelcolor='black')

    temp_array = np.array(temp_forskjeller)

    for j in range(min(len(temp_array), n_m)):
        for i, region in enumerate(regions):
            ax2.scatter(
                x_idx[j] + offsets[i],
                temp_array[j][i],
                marker="s",
                color=color_map[region],
                s=80
            )

    ax.axhline(0, color="gray", linestyle="--")

    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    ax.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.4)

    plt.subplots_adjust(bottom=0.25)

    from matplotlib.lines import Line2D
    temp_legend_elements = [
        Line2D([0], [0], marker='s',
               color='black',
               linestyle='None',
               markersize=10,
               label="Temperature difference"),

        Line2D([0], [0], marker='o',
               color='black',
               linestyle='None',
               markersize=10,
               label='DiD without temperature control'
               ),
        Line2D(
            [0], [0],
            marker='^',
            color='black',
            linestyle='None',
            markersize=10,
            label='DiD with temperature control'
        )
    ]

    temp_legend = ax2.legend(
        handles=temp_legend_elements,
        loc="lower left",
        fontsize=19,
        framealpha=0.3,
        frameon=True
    )

    ax2.add_artist(temp_legend)

    plt.show()



# --------------- KJØH --------------- #

plot(df)



