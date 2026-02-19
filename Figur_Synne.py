import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row

DiD = pd.DataFrame({
    "region":  ["NO1","NO1","NO1","NO2","NO2","NO2","NO5","NO5","NO5"],
    "vindu":   ["January","Afternoon (Hours: 17,18,19)","3 Winter Months(Nov,Dec,Jan)"] * 3,
    "value":    [4.7 , 5.66 , 3.45,    5.02, 5.66, 4.51,     3.5, 2.78, 2.83],
    "ci_high":  [6.4, 9.64, 5.22,      6.60,9.64, 6.3,       5.34, 4.2, 4.61],
    "ci_low":   [3.04, 1.82, 1.72 ,    3.46, 1.82, 2.76,     1.61, 1.41, 1.08],
})

delta_consump = pd.DataFrame({
    "region":  ["NO1","NO1","NO1","NO1","NO2","NO2","NO2","NO2","NO5","NO5","NO5","NO5"],
    "vindu":   ["γ_1: Effect of Norgespris","γ_1: Effect of no Norgespris", "γ_2: Effect of temperature with NP","γ_2: Effect of temperature without NP"] * 3,

    "value":    [2.74 ,  -0.61 , -3.16,  -2.85,    5.03,  0.6,-3.57, -3.39,      3.45, 0.76, -3.05, -2.87],
    "ci_high":  [3.12,   -0.29,  -3.12,  -2.81,    5.44, 0.94, -3.51, -3.34,     3.85, 1.13, -3.01, -2.82],
    "ci_low":   [2.36,   -0.94,  -3.21,  -2.89,    4.63, 0.26,-3.62, -3.44,      3.05, 0.4, -3.10, -2.91],
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
    point_size=100,
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


plot_errorbars_by_group(
    DiD,
    title="Difference in Difference 2024(5)->2025(6)",
    y_label=" Δ Consumption in Percent[%]",
    y_ref_lines=[0, 7]
    #annotate={"text": "3 mnd.", "xy": (0.72, 0.92), "axescoords": True}
)


plot_errorbars_by_group(
    delta_consump,
    title=" Coefficient Illustration Regression Model 2024(5)->2025(6)",
    y_label=" Δ Consumption in Percent [%]",
    y_ref_lines=[-4, 6]
    #annotate={"text": "3 mnd.", "xy": (0.72, 0.92), "axescoords": True}
)
