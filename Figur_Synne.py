import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row

data = pd.DataFrame({
    "region":  ["NO1","NO1","NO1","NO2","NO2","NO2","NO5","NO5","NO5"],
    "vindu":   ["Med Norgespris(3 mnd)","Uten Norgespris(3 mnd)","Januar med Norgespris"] * 3,
    "value":   [5, 4.6, 4.2,  6.8, 6.1, 5.9,  6.5, 6.0, 6.1],
    "ci_high":  [6, 5.3, 4.9,  7.3, 6.6, 6.3,  6.9, 6.3, 6.5],
    "ci_low": [4, 3.9, 3.5,  6.2, 5.6, 5.5,  6.1, 5.7, 5.8],
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
    data,
    title="Change in Consumption 2025->2026",
    y_label=" Change in consumtption for different categories (%)",
    y_ref_lines=[3, 7],
    annotate={"text": "3 mnd.", "xy": (0.72, 0.92), "axescoords": True}
)
