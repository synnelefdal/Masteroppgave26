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


#--------------------------VELG HVILKEN PRISSONE SOM SKAL PLOTTES HER ---------------------------


#data = [Group_October_NO1, Group_November_NO1, Group_December_NO1, Group_January_NO1, Group_February_NO1, Group_March_NO1]
#data = [Group_October_NO2, Group_November_NO2, Group_December_NO2, Group_January_NO2, Group_February_NO2, Group_March_NO2]
data = [Group_October_NO5, Group_November_NO5, Group_December_NO5, Group_January_NO5, Group_February_NO5, Group_March_NO5]

#-------------------------- IKKJE RØR NOE HERFRAAAAA og ned --------------------------------------------

labels = ['Group October', 'Group November', 'Group December', 'Group January', 'Group February', 'Group March']

# --------- PLOT --------- #

def plot(data):

    fig, ax = plt.subplots(figsize=(10,6))

    colors = sns.color_palette("tab10", len(data))

    # Litt horisontal spredning så punktene ikke ligger oppå hverandre
    offsets = np.linspace(-0.2, 0.2, len(data))

    for i, liste in enumerate(data):

        #--- Fjerne None - --
        y = np.array(liste, dtype=object)
        mask = np.array([val is not None for val in y])

        x_valid = x[mask]
        y_valid = y[mask].astype(float)

        xi = x + offsets[i]

        ax.scatter(
            xi,
            liste,
            color=colors[i],
            s=180,
            label=labels[i]

        )

        # --- Trendlinje ---
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


# X-akse = måneder
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=20)

    # Y-akse
    ax.set_ylabel("Change in consumption [%]", fontsize=20)
    ax.set_xlabel("Month", fontsize=20)

    # Linje ved 0
    ax.axhline(0, color="gray", linestyle="--")

    # Grid
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Legende
    ax.legend(fontsize=20, loc= "lower left")

    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    plt.show()


# --------- KJØR --------- #
plot(data)