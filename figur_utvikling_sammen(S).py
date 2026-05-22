import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --------- MÅNEDER --------- #
months = ["October", "November", "December", "January", "February", "March"]
x = np.arange(len(months))

# -------------------- FYLL INN DATA HER --------------------- #
# Husk: én verdi per måned (6 verdier)

Group_October_NO1 = [2.57, 2.93, 3.49, 3.85, 3.67, 3.73]
Group_November_NO1 = [None, 2.78, 3.36, 3.98, 3.89, 4.07]
Group_December_NO1 = [None, None, 3.48, 4.02, 4.09, 4.38]
Group_January_NO1 = [None, None, None, 3.77, 3.92, 4.20]
Group_February_NO1 = [None, None, None, None, 3.19, 3.21]
Group_March_NO1 = [None, None, None, None, None, 1.95]

Group_October_NO2 = [3.52, 3.8, 4.77, 4.53, 4.84, 5.17]
Group_November_NO2 = [None, 3.61, 4.71, 4.45, 4.86, 5.26]
Group_December_NO2 = [None, None, 4.24, 4.02, 4.48, 5.24]
Group_January_NO2 = [None, None, None, 3.92, 4.28, 4.96]
Group_February_NO2 = [None, None, None, None, 3.24, 4.14]
Group_March_NO2 = [None, None, None, None, None, 2.59]

Group_October_NO5 = [2.09, 2.33, 2.83, 2.68, 2.94, 3.33]
Group_November_NO5 = [None, 2.68, 3.11, 3.20, 3.57, 4.18]
Group_December_NO5 = [None, None, 2.69, 3.09, 3.58, 3.9]
Group_January_NO5 = [None, None, None, 2.99, 3.6, 4.19]
Group_February_NO5 = [None, None, None, None, 2.72, 2.93]
Group_March_NO5 = [None, None, None, None, None, 2.16]

# X-axis (months you already use)
months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
x = np.arange(len(months))

# ---------- NO1 ----------
data_NO1 = [
    Group_October_NO1,
    Group_November_NO1,
    Group_December_NO1,
    Group_January_NO1,
    Group_February_NO1,
    Group_March_NO1
]

# ---------- NO2 ----------
data_NO2 = [
    Group_October_NO2,
    Group_November_NO2,
    Group_December_NO2,
    Group_January_NO2,
    Group_February_NO2,
    Group_March_NO2
]

# ---------- NO5 ----------
data_NO5 = [
    Group_October_NO5,
    Group_November_NO5,
    Group_December_NO5,
    Group_January_NO5,
    Group_February_NO5,
    Group_March_NO5
]

labels = ['Group October', 'Group November', 'Group December', 'Group January', 'Group February', 'Group March']
#def transpose_data(data):
#    return list(map(list, zip(*data)))

#data_NO1_t = transpose_data(data_NO1)
#data_NO2_t = transpose_data(data_NO2)
#data_NO5_t = transpose_data(data_NO5)


def plot_all(NO1, NO2, NO5):

    fig, axes = plt.subplots(3, 1, figsize=(10, 14), sharex=True)

    datasets = [NO1, NO2, NO5]
    titles = ["NO1", "NO2", "NO5"]

    for j, data in enumerate(datasets):

        ax = axes[j]
        colors = sns.color_palette("tab10", len(data))
        offsets = np.linspace(-0.2, 0.2, len(data))

        for i, liste in enumerate(data):

            y = np.array(liste, dtype=object)
            mask = np.array([val is not None for val in y])

            x_valid = x[mask]
            y_valid = y[mask].astype(float)

            xi = x + offsets[i]

            ax.scatter(
                xi,
                liste,
                color=colors[i],
                s=80,
                label=labels[i],
                zorder=2
            )

            if len(x_valid) > 1:
                coeffs = np.polyfit(x_valid, y_valid, 1)
                trend = np.poly1d(coeffs)

                x_smooth = np.linspace(x_valid.min(), x_valid.max(), 100)

                ax.plot(
                    x_smooth,
                    trend(x_smooth),
                    color=colors[i],
                    linestyle="--",
                    linewidth=2,
                    zorder=1
                )


        ax.set_title(titles[j], fontsize=20)
        plt.yticks(fontsize=20)
        ax.axhline(0, color="gray", linestyle="--")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        #ax.set_ylabel("Change [%]", fontsize=20)
        ax.set_ylim(0, 5.5)
        #ax.set_xticklabels(months, fontsize=20)
        #ax.set_xlabel("Month", fontsize=20)
        plt.yticks(fontsize=20)
        #ax.set_ylabel(fontsize=20)
        ax.tick_params(axis='y', labelsize=20)  # change 16 → whatever you want

    axes[1].set_ylabel("Change in consumption [%]", fontsize=20)
    ax.set_xlabel("Month", fontsize=20)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(months, fontsize=20)
    axes[-1].set_xlabel("Month")
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=20)
    #ax.set_ylim(1, 6)
    #ax.set_ylim(1, 6)
    #ax.set_ylim(1, 6)
    #ax.legend(fontsize=20)

    handles, labels_legend = axes[0].get_legend_handles_labels()

    fig.legend(
        handles,
        labels_legend,
        fontsize=14,
        loc="center",
        bbox_to_anchor=(0.48 , 0.405),  # (x, y)
        ncol=3
    )

    plt.tight_layout()
    plt.show()
    fig.savefig("my_plot_ny_ny_ny2.png", dpi=300, bbox_inches="tight")


plot_all(data_NO1, data_NO2, data_NO5) 