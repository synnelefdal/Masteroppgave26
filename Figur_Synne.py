import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row

# --------- DiD ---------- #
regions = ["NO1", "NO2", "NO5"]

vindu = [
    "November",
    "Desember",
    "January",
    "3 Winter Months (Nov,Dec,Jan)"
]

values = [
    [2.47, 3.76, 2.32],   # November
    [3.20, 4.79, 2.76],   # Desember
    [4.63, 4.97, 3.40],   # January
    [3.45, 4.51, 2.83]    # 3 vinter måneder
]

ci_high = [
    [2.90, 4.14, 2.60],  # November
    [3.58, 5.10, 2.99],  # Desember
    [4.97, 5.27, 3.65],  # January
    [3.67, 4.71, 2.98]   # 3 vinter måneder
]

ci_low = [
    [2.04, 3.38, 2.04],  # November
    [2.91, 4.48, 2.52],  # Desember
    [4.29, 4.67, 3.14],  # January
    [3.23, 4.32, 2.68]   # 3 vinter måneder
]

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

DiD = pd.DataFrame(rows)

# --------- DiD m/Temp ---------- #

regions_temp = ["NO1", "NO2", "NO5"]

vindu_temp = [
    "November w/Temp",
    "Desember w/Temp",
    "January w/Temp",
    "3 Winter Months (Nov,Dec,Jan) w/Temp"
]

values_temp = [
    [2.89, 3.59, 2.32],   # November
    [3.59, 4.59, 2.76],   # Desember
    [3.97, 4.54, 2.72],   # January
    [3.42, 4.18, 2.61]    # 3 vinter måneder
]

ci_high_temp = [
    [3.29, 3.98, 2.60],  # November
    [3.91, 4.91, 2.99],  # Desember
    [4.29, 4.84, 2.97],  # January
    [3.62, 4.39, 2.76]   # 3 vinter måneder
]

ci_low_temp = [
    [2.48, 3.20, 2.05],  # November
    [3.28, 4.28, 2.53],  # Desember
    [3.66, 4.23, 2.48],  # January
    [3.21, 3.98, 2.46]   # 3 vinter måneder
]

rows_temp = []

for i, win in enumerate(vindu_temp):
    for r in range(3):
        rows_temp.append({
            "region": regions_temp[r],
            "vindu": win,
            "value": values_temp[i][r],
            "ci_high": ci_high_temp[i][r],
            "ci_low": ci_low_temp[i][r]
        })

DiD_temp = pd.DataFrame(rows_temp)


def plot_errorbars_two_groups(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    x="region",
    series="vindu",
    y="value",
    ylow="ci_low",
    yhigh="ci_high",
    label1="DiD",
    label2="DiD_temp",
    title="Estimert effekt med 95% KI",
    y_label="Endring relativt til baseline (%)",
    y_ref_lines=None,
    palette="Set2",
    point_size=100,
    x_order = None,
    series_order = None
):

    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd

    # --- KATEGORIER ---
    cats = df1[x].cat.categories
    ser  = df1[series].cat.categories

    n_x, n_s = len(cats), len(ser)

    x_idx = np.arange(n_x)
    group_width = 0.7

    # Nå har vi *TO* grupper → de skal side-om-side
    offsets = [-0.15, 0.15]

    pal = sns.color_palette(palette, n_colors=n_s)

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, df in enumerate([df1, df2]):
        label = label1 if i == 0 else label2
        offset = offsets[i]

        for j, s in enumerate(ser):
            sub = (
                df[df[series] == s]
                .set_index(x)
                .reindex(cats)
            )

            xi = x_idx + offset

            yval = sub[y].values
            lo   = sub[ylow].values
            hi   = sub[yhigh].values
            err_low  = np.maximum(yval - lo, 0)
            err_high = np.maximum(hi - yval, 0)
            yerr = np.vstack([err_low, err_high])

            ax.errorbar(
                xi, yval, yerr=yerr,
                fmt="none", ecolor=pal[j], capsize=5, elinewidth=1.5
            )

            ax.scatter(
                xi, yval, s=point_size,
                color=pal[j], edgecolor="white", linewidth=0.8,
                label=f"{label} – {s}" if i == 0 else None
            )

    ax.set_xticks(x_idx)
    ax.set_xticklabels(cats, fontsize=14)
    ax.set_ylabel(y_label, fontsize=14)
    ax.set_title(title, fontsize=18)

    if y_ref_lines is None:
        y_ref_lines = [0]
    for ref in y_ref_lines:
        ax.axhline(ref, color="gray", linestyle="--", linewidth=1, alpha=0.6)

    ax.grid(axis="y", color="0.9")
    sns.despine(ax=ax)
    ax.legend(fontsize=12)
    plt.tight_layout()
    plt.show()


DiD["vindu"] = pd.Categorical(
    DiD["vindu"],
    categories=vindu,
    ordered=True
)

DiD["region"] = pd.Categorical(
    DiD["region"],
    categories=regions,
    ordered=True
)

DiD_temp["vindu"] = pd.Categorical(
    DiD_temp["vindu"],
    categories=vindu_temp,
    ordered=True
)

DiD_temp["region"] = pd.Categorical(
    DiD_temp["region"],
    categories=regions_temp,
    ordered=True
)


region_order = ["NO1", "NO2", "NO5"]
vindu_order = ["November", "Desember", "January", "3 Winter Months (Nov,Dec,Jan)"]


plot_errorbars_two_groups(
    DiD,
    DiD_temp,
    x = 'region',
    series='vindu',
    x_order = region_order,
    series_order=vindu_order,
    title="Difference in Difference – begge datasett",
    y_label="Δ Consumption (%)",
    y_ref_lines=[0, 7],
    label1="DiD",
    label2="DiD_temp"
)


