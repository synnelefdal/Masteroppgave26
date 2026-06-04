import pandas as pd


# --------- DiD ---------- #
regions = ["NO1", "NO2", "NO5"]

vindu = [
    "November",
    "November w/Temp",
    "December",
    "December w/Temp",
    "January",
    "January w/Temp",
    "Winter months (Nov,Dec,Jan)",
    "Winter months (Nov,Dec,Jan) w/Temp"
]

values = [
    [2.47, 3.76, 2.32],   # November
    [2.89, 3.59, 2.32],   # November med temp
    [3.20, 4.79, 2.76],   # Desember
    [3.59, 4.59, 2.76],   # Desember med temp
    [4.63, 4.97, 3.40],   # January
    [3.97, 4.54, 2.72],   # January med temp
    [3.45, 4.51, 2.83],   # 3 vinter måneder
    [3.42, 4.18, 2.61]    # 3 vinter måneder med temp
]

ci_high = [
    [2.90, 4.14, 2.60],  # November
    [3.29, 3.98, 2.60],  # November med temp
    [3.58, 5.10, 2.99],  # Desember
    [3.91, 4.91, 2.99],  # Desember med temp
    [4.97, 5.27, 3.65],  # January
    [4.29, 4.84, 2.97],  # January med temp
    [3.67, 4.71, 2.98],  # 3 vinter måneder
    [3.62, 4.39, 2.76]   # 3 vinter måneder med temp
]

ci_low = [
    [2.04, 3.38, 2.04],  # November
    [2.48, 3.20, 2.05],  # November med temp
    [2.91, 4.48, 2.52],  # Desember
    [3.28, 4.28, 2.53],  # Desember med temp
    [4.29, 4.67, 3.14],  # January
    [3.66, 4.23, 2.48],  # January med temp
    [3.23, 4.32, 2.68],  # 3 vinter måneder
    [3.21, 3.98, 2.46]   # 3 vinter måneder med temp
]

andre_yakse = [-3,-2,-1,0,1,2,3]

'''temp_forskjeller = [[1.3,0.6,0.3],
                    [1.3,0.8,0.6],
                    [-3.2,-3.1,-3.4],
                    [-0.6,-1.7,-2.5]]'''


temp_forskjeller = [
    [ 1.3,  0.6,  0.3],   # periode 1
    [ 1.3,  0.8,  0.6],   # periode 2
    [-3.2, -3.1, -3.4],   # periode 3
    [-0.6, -1.7, -2.5]    # periode 4
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



def plot_errorbars_by_group(
    df: pd.DataFrame,
    x="region",
    series="vindu",
    y="value",
    ylow="ci_low",
    yhigh="ci_high",
    #title="Estimert effekt med 95% KI",
    y_label="Endring relativt til baseline (%)",
    y_ref_lines=None,
    annotate=None,
    palette="Set2",
    point_size=180,
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

    # ---- Figur ---- #
    fig, ax = plt.subplots(figsize=(9, 5))

    ax.set_ylim(-3.5,7)

    base_names = [str(s).replace(" w/Temp", "") for s in ser]
    unique_base = list(dict.fromkeys(base_names))
    base_palette = sns.color_palette("tab10", n_colors=len(unique_base))
    base_color_map = dict(zip(unique_base, base_palette))

    for i, s in enumerate(ser):
        sub = df[df[series] == s].set_index(x).reindex(cats)
        xi = x_idx + offsets[i]

        yval = sub[y].values
        lo   = sub[ylow].values
        hi   = sub[yhigh].values
        err_low  = yval - lo
        err_high = hi - yval

        err_low = np.maximum(err_low, 0)
        err_high = np.maximum(err_high, 0)
        yerr = np.vstack([err_low, err_high])

        base = str(s).replace(" w/Temp", "")
        color = base_color_map[base]

        '''ax.errorbar(
            xi, yval, yerr=yerr,
            fmt="none", ecolor=color, elinewidth=1.6, capsize=6
        )'''

        if "Temp" in str(s):
            alpha_line = 1.0  # tydelig
        else:
            alpha_line = 0.3  # dus

        ax.errorbar(
            xi, yval, yerr=yerr,
            fmt="none",
            ecolor=color,
            elinewidth=1.6,
            capsize=6,
            alpha=alpha_line
        )

        marker_style = "^" if "Temp" in str(s) else "o"
        #size = point_size * 1.4 if "Temp" in str(s) else point_size
        #edge_w = 1.5 if "Temp" in str(s) else 0.8

        '''ax.scatter(
            xi, yval, s=size,
            color=color, edgecolor="white", linewidth=edge_w,
            marker= marker_style,
            zorder=3, label=str(s), alpha = 1
        )'''

        if "Temp" in str(s):
            alpha_val = 1.0  # behold tydelig for trekant
            size = point_size * 1.4
            edge_w = 1.5
        else:
            alpha_val = 0.35  # ↓ gjør rund prikk dus
            size = point_size
            edge_w = 0.8

        ax.scatter(
            xi, yval, s=size,
            color=color,
            edgecolor="white",
            linewidth=edge_w,
            marker=marker_style,
            zorder=3,
            label=str(s),
            alpha=alpha_val
        )

    ax.set_xticks(x_idx)
    ax.set_xticklabels(cats, fontsize=25)
    ax.tick_params(axis="x", pad=25)
    ax.set_ylabel(y_label, fontsize= 25)
    from matplotlib.ticker import MultipleLocator
    ax.yaxis.set_major_locator(MultipleLocator(1))
    #ax.set_title(title, fontsize = 20)

    if y_ref_lines is None:
        y_ref_lines = [0]

    for ref in y_ref_lines:
        ax.axhline(ref, color="gray", linestyle="--", linewidth=0.9, alpha=0.6)

    ax.margins(x=0.08)
    #ax.legend(loc="best", fontsize = 18) #originalt 15
    ax.grid(axis="y", color="0.9")
    sns.despine(ax=ax)

    if annotate:
        ax.annotate(
            annotate.get("text",""),
            xy=annotate.get("xy",(0,0)),
            xytext=annotate.get("xytext",(0.2,0.2)),
            textcoords="axes fraction" if annotate.get("axescoords", True) else "data",
            arrowprops=dict(arrowstyle="->", color="0.3"),
            fontsize=25   #originalt 15
        )

    # ---- Andre y-akse: Temperaturpunkter for ALLE perioder ---- #
    ax2 = ax.twinx()

    temp_array = np.array(temp_forskjeller)  # shape (n_perioder, 3)

    # --- Vi bruker samme ser og offsets som DiD-plottet --- #
    temp_i = 0
    for i, s in enumerate(ser):

        if " w/Temp" in str(s):
            continue

        if temp_i >= temp_array.shape[0]:  # Hopp over perioder som ikke har temperaturdata
            continue


        xi = x_idx + offsets[i] #+ i*1.25*step     # X-posisjonene er IDENTISKE til DiD for denne perioden
        temp_points = temp_array[temp_i]    # Temperaturverdier for NO1, NO2, NO5


        base = str(s)
        temp_color = base_color_map[base]

        ax2.scatter(
            xi,
            temp_points,
            marker="s",
            s=100,
            color=temp_color,
            edgecolor="white",
            linewidth=1.2,
            alpha=0.9,
            zorder=4
        )

        temp_i += 1

    from matplotlib.ticker import MultipleLocator
    #ax2.set_ylim(-3.5, 1.4)
    #ax2.yaxis.set_major_locator(MultipleLocator(0.4))
    ax2.set_ylim(ax.get_ylim())
    ax2.yaxis.set_major_locator(MultipleLocator(1))


    ax2.set_ylabel("Difference in Temperature [°C]", color="black", fontsize=25)
    ax2.tick_params(axis="y", labelcolor="black")

    # ---- EKSTRA X-ETIKETTER FOR MÅNEDER ---- #

    month_labels = [
        ("November", "Nov"),
        ("December", "Dec"),
        ("January", "Jan"),
        ("Winter months (Nov,Dec,Jan)", "Winter")
    ]

    y_text = ax.get_ylim()[0] - 0.10

    for r in range(len(x_idx)):                # Loop over regioner: NO1, NO2, NO5
        for base, short_label in month_labels:

            s_index = ser.get_loc(base)        # Finn riktig offset for måneden

            x_pos = x_idx[r] + offsets[s_index]

            ax.text(
                x_pos,
                y_text,
                short_label,
                ha="center",
                va="top",
                fontsize=20,
                color=base_color_map[base]
            )

    plt.tight_layout()
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)

    ax.tick_params(axis="y", labelsize=25)
    ax2.tick_params(axis="y", labelsize=25)


    #ax.add_artist(symbol_legend)

    # ---- TITTELBOKS ---- #

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
        loc="upper right",
        fontsize=19,
        framealpha=0.3,
        frameon=True
    )

    ax2.add_artist(temp_legend)

    plt.show()


DiD["vindu"] = pd.Categorical(
    DiD["vindu"],
    categories=vindu,
    ordered=True
)

plot_errorbars_by_group(
    DiD,
    #title="Difference in Difference",
    y_label= "Change in electricity consumption [%]",
    y_ref_lines=[0, 7]
    #annotate={"text": "3 mnd.", "xy": (0.72, 0.92), "axescoords": True}
)