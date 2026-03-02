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


def plot_errorbars_by_group(
    df: pd.DataFrame,
    x="region",
    series="vindu",
    y="value",
    ylow="ci_low",
    yhigh="ci_high",
    title="Estimert effekt med 95% KI",
    y_label="Endring relativt til baseline (%)",
    y_ref_lines=None,
    annotate=None,
    palette="Set2",
    point_size=100,
    capsize=0.15
):

    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Definér posisjoner
    cats = df[x].cat.categories if isinstance(df[x].dtype, pd.CategoricalDtype) else sorted(df[x].unique())
    ser  = df[series].cat.categories if isinstance(df[series].dtype, pd.CategoricalDtype) else sorted(df[series].unique())
    n_x, n_s = len(cats), len(ser)

    x_idx = np.arange(n_x)
    group_width = 0.7
    step = group_width / (n_s if n_s > 1 else 1)
    offsets = (np.arange(n_s) - (n_s - 1)/2) * step

    pal = sns.color_palette(palette, n_colors=n_s)

    # Figur
    fig, ax = plt.subplots(figsize=(9, 5))

    for i, s in enumerate(ser):
        sub = df[df[series] == s].set_index(x).reindex(cats)
        xi = x_idx + offsets[i]

        # Errorbars
        yval = sub[y].values
        lo   = sub[ylow].values
        hi   = sub[yhigh].values
        err_low  = yval - lo
        err_high = hi - yval

        # Ingen negative feil
        err_low = np.maximum(err_low, 0)
        err_high = np.maximum(err_high, 0)
        yerr = np.vstack([err_low, err_high])

        ax.errorbar(
            xi, yval, yerr=yerr,
            fmt="none", ecolor=pal[i], elinewidth=1.6, capsize=6
        )

        ax.scatter(
            xi, yval, s=point_size,
            color=pal[i], edgecolor="white", linewidth=0.8,
            zorder=3, label=str(s)
        )

    ax.set_xticks(x_idx)
    ax.set_xticklabels(cats, fontsize=15)
    ax.set_ylabel(y_label, fontsize= 15)
    ax.set_title(title, fontsize = 17)

    if y_ref_lines is None:
        y_ref_lines = [0]

    for ref in y_ref_lines:
        ax.axhline(ref, color="gray", linestyle="--", linewidth=0.9, alpha=0.6)

    ax.margins(x=0.08)
    ax.legend(loc="best", fontsize = 15)
    ax.grid(axis="y", color="0.9")
    sns.despine(ax=ax)

    if annotate:
        ax.annotate(
            annotate.get("text",""),
            xy=annotate.get("xy",(0,0)),
            xytext=annotate.get("xytext",(0.2,0.2)),
            textcoords="axes fraction" if annotate.get("axescoords", True) else "data",
            arrowprops=dict(arrowstyle="->", color="0.3"),
            fontsize=15
        )

    plt.tight_layout()
    plt.show()


DiD["vindu"] = pd.Categorical(
    DiD["vindu"],
    categories=vindu,
    ordered=True
)

plot_errorbars_by_group(
    DiD,
    title="Difference in Difference",
    y_label=" Δ Consumption in Percent[%]",
    y_ref_lines=[0, 7]
    #annotate={"text": "3 mnd.", "xy": (0.72, 0.92), "axescoords": True}
)

