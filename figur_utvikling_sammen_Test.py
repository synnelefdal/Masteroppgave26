import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import copy
from matplotlib.lines import Line2D


# --------- MÅNEDER --------- #
months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
x = np.arange(len(months))

# -------------------- ORIGINAL DATA (WITH NONE) --------------------- #

orig_NO1 = [
    [2.57, 2.93, 3.49, 3.85, 3.67, 3.73],
    [None, 2.78, 3.36, 3.98, 3.89, 4.07],
    [None, None, 3.48, 4.02, 4.09, 4.38],
    [None, None, None, 3.77, 3.92, 4.20],
    [None, None, None, None, 3.19, 3.21],
    [None, None, None, None, None, 1.95]
]

orig_NO2 = [
    [3.52, 3.8, 4.77, 4.53, 4.84, 5.17],
    [None, 3.61, 4.71, 4.45, 4.86, 5.26],
    [None, None, 4.24, 4.02, 4.48, 5.24],
    [None, None, None, 3.92, 4.28, 4.96],
    [None, None, None, None, 3.24, 4.14],
    [None, None, None, None, None, 2.59]
]

orig_NO5 = [
    [2.09, 2.33, 2.83, 2.68, 2.94, 3.33],
    [None, 2.68, 3.11, 3.20, 3.57, 4.18],
    [None, None, 2.69, 3.09, 3.58, 3.9],
    [None, None, None, 2.99, 3.6, 4.19],
    [None, None, None, None, 2.72, 2.93],
    [None, None, None, None, None, 2.16]
]

# --------- COPY → HER KAN DU FYLLE INN TALL --------- #

data_NO1 = copy.deepcopy(orig_NO1)
data_NO2 = copy.deepcopy(orig_NO2)
data_NO5 = copy.deepcopy(orig_NO5)

# Fyll inn manglende verdier

#data_NO1[1][0] er Group november i mnd oktober
#data_NO1[2][1] er Group Decemver i mnd november

data_NO1[1][0] = 1
data_NO1[2][0] = 1
data_NO1[2][1] = 1
data_NO1[3][0] = 1
data_NO1[3][1] = 1
data_NO1[3][2] = 1
data_NO1[4][0] = 1
data_NO1[4][1] = 1
data_NO1[4][2] = 1
data_NO1[4][3] = 1
data_NO1[5][0] = 1
data_NO1[5][1] = 1
data_NO1[5][2] = 1
data_NO1[5][3] = 1
data_NO1[5][4] = 1

data_NO2[1][0] = 1
data_NO2[2][0] = 1
data_NO2[2][1] = 1
data_NO2[3][0] = 1
data_NO2[3][1] = 1
data_NO2[3][2] = 1
data_NO2[4][0] = 1
data_NO2[4][1] = 1
data_NO2[4][2] = 1
data_NO2[4][3] = 1
data_NO2[5][0] = 1
data_NO2[5][1] = 1
data_NO2[5][2] = 1
data_NO2[5][3] = 1
data_NO2[5][4] = 1

data_NO5[1][0] = 1
data_NO5[2][0] = 1
data_NO5[2][1] = 1
data_NO5[3][0] = 1
data_NO5[3][1] = 1
data_NO5[3][2] = 1
data_NO5[4][0] = 1
data_NO5[4][1] = 1
data_NO5[4][2] = 1
data_NO5[4][3] = 1
data_NO5[5][0] = 1
data_NO5[5][1] = 1
data_NO5[5][2] = 1
data_NO5[5][3] = 1
data_NO5[5][4] = 1

# --------- LAG MASKER (FRA ORIGINALDATA) --------- #

masks_NO1 = [[val is None for val in group] for group in orig_NO1]
masks_NO2 = [[val is None for val in group] for group in orig_NO2]
masks_NO5 = [[val is None for val in group] for group in orig_NO5]

labels = ['Group October', 'Group November', 'Group December',
          'Group January', 'Group February', 'Group March']


def plot_all(NO1, NO2, NO5, masks1, masks2, masks5):

    fig, axes = plt.subplots(3, 1, figsize=(10, 14), sharex=True)

    datasets = [NO1, NO2, NO5]
    masks_all = [masks1, masks2, masks5]
    titles = ["NO1", "NO2", "NO5"]

    for j, (data, masks) in enumerate(zip(datasets, masks_all)):

        ax = axes[j]
        colors = sns.color_palette("tab10", len(data))
        offsets = np.linspace(-0.2, 0.2, len(data))

        for i, (liste, mask_none) in enumerate(zip(data, masks)):

            y = np.array(liste, dtype=float)
            xi = x + offsets[i]

            # ----------- PLOTTING ----------- #
            for k in range(len(y)):

                if np.isnan(y[k]):
                    continue

                if mask_none[k]:

                    # siste None før ekte verdi
                    if k < len(mask_none) - 1 and not mask_none[k + 1]:


                        ax.scatter(
                            xi[k], y[k],
                            marker='o',
                            color=colors[i],
                            s=80,
                            alpha=0.25,
                            zorder=2
                            #label=labels[i]
                        )

                        ax.scatter(
                            xi[k], y[k],
                            marker='x',
                            color=colors[i],
                            s=120,
                            linewidths=2,
                            zorder=3
                        #label=label_i
                        )

                    else:
                        #label_i = labels[i] if j == 0 and k == 0 else None

                        ax.scatter(
                            xi[k], y[k],
                            marker='x',
                            color=colors[i],
                            s=120,
                            linewidths=2,
                            zorder=3
                            #label=labels[i]
                        )

                else:
                    label_i = labels[i] if j == 0 and k == 0 else None
                    ax.scatter(
                        xi[k], y[k],
                        marker='o',
                        color=colors[i],
                        s=80,
                        zorder=2
                        #label=label_i
                    )

            # ----------- TRENDLINJE (KUN ORIGINALDATA) ----------- #
            mask_original = np.array([not m for m in mask_none])

            x_valid = x[mask_original]
            y_valid = y[mask_original]

            if len(x_valid) > 1:
                coeffs = np.polyfit(x_valid, y_valid, 1)
                trend = np.poly1d(coeffs)

                x_smooth = np.linspace(x_valid.min(), x_valid.max(), 100)

                ax.plot(
                    x_smooth,
                    trend(x_smooth),
                    color=colors[i],
                    linestyle="--",
                    linewidth=2
                )

        ax.set_title(titles[j], fontsize=20)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.set_ylim(0, 5.5)
        ax.tick_params(axis='y', labelsize=20)

    axes[1].set_ylabel("Change in consumption [%]", fontsize=20)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(months, fontsize=20)
    axes[-1].set_xlabel("Month", fontsize=20)

    #handles, labels_legend = axes[0].get_legend_handles_labels()

    #fig.legend(handles, labels_legend, loc="center", bbox_to_anchor=(0.48, 0.4), ncol=3)

    colors = sns.color_palette("tab10", len(labels))

    custom_handles = [
        Line2D([0], [0],
               marker='o',
               color='none',
               markerfacecolor=colors[i],
               markersize=8,
               label=labels[i])
        for i in range(len(labels))
    ]

    fig.legend(
        handles=custom_handles,
        loc="center",
        bbox_to_anchor=(0.48, 0.4),
        ncol=3,
        fontsize=14
    )

    plt.tight_layout()
    plt.show()


plot_all(data_NO1, data_NO2, data_NO5, masks_NO1, masks_NO2, masks_NO5)