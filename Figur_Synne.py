import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row

data1 = pd.DataFrame({
    "region":  ["NO1","NO1","NO1","NO2","NO2","NO2","NO5","NO5","NO5"],
    "vindu":   ["January","December","4 Winter Months(Oct,Nov,Dec,Jan)"] * 3,
    "value":   [4.7 , 3.25 , 3.69,  5.02, 4.82, 4.24,  3.5, 2.78, 2.65],
    "ci_high":  [6.4, 5.02, 4.29,  6.60, 6.5, 5.23,  5.34, 4.2, 3.67],
    "ci_low": [3.04, 1.61, 2.33 ,  3.46, 3.25, 3.25,  1.61, 1.41, 1.61],
})

data2 = pd.DataFrame({
    "region":  ["NO1","NO1","NO1","NO2","NO2","NO2","NO5","NO5","NO5"],
    "vindu":   ["With Norgespris","Without Norgespris","Noe mer"] * 3,
    "value":   [4.53 , 0.93 , 0,  7.38, 2.83, 0,  6.09, 3.21, 0],
    "ci_high":  [0, 0, 0,  0, 0, 0,  0, 0, 0],
    "ci_low": [10, 10, 10,  10, 10, 10,  10, 10, 10,],
})


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
    point_size=60,
    capsize=0.15
):
    """
    Lager en multi-series errorbar-figur per kategori (x),
    med flere serier (series), og viser figuren på skjerm.

    Ingen lagring skjer (ingen PNG/PDF).
    """

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
    ax.set_xticklabels(cats, fontsize=11)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if y_ref_lines is None:
        y_ref_lines = [0]

    for ref in y_ref_lines:
        ax.axhline(ref, color="gray", linestyle="--", linewidth=0.9, alpha=0.6)

    ax.margins(x=0.08)
    ax.legend(loc="best")
    ax.grid(axis="y", color="0.9")
    sns.despine(ax=ax)

    if annotate:
        ax.annotate(
            annotate.get("text",""),
            xy=annotate.get("xy",(0,0)),
            xytext=annotate.get("xytext",(0.2,0.2)),
            textcoords="axes fraction" if annotate.get("axescoords", True) else "data",
            arrowprops=dict(arrowstyle="->", color="0.3"),
            fontsize=11
        )

    plt.tight_layout()
    plt.show()


plot_errorbars_by_group(
    data1,
    title="Difference in Difference 2025->2026",
    y_label=" Change in Consumption for With Norgespris and Without Norgespris (%)",
    y_ref_lines=[0, 7]
    #annotate={"text": "3 mnd.", "xy": (0.72, 0.92), "axescoords": True}
)


plot_errorbars_by_group(
    data2,
    title="Change in Consumption 2025->2026",
    y_label=" Change in Consumption in Categories (%)",
    y_ref_lines=[0, 7]
    #annotate={"text": "3 mnd.", "xy": (0.72, 0.92), "axescoords": True}
)
