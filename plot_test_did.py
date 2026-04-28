
import matplotlib.pyplot as plt
import pandas as pd
from networkx.algorithms.bipartite.basic import color

# --------------------------------------------------
# 1. Månedlig tidsakse: jan 2024 – sep 2025 (21 mnd)
# --------------------------------------------------
dates = pd.date_range(
    start="2024-10-01",
    end="2025-09-01",
    freq="MS"
)

# --------------------------------------------------
# 2. Fyll inn DINE DiD-verdier her
#    (21 tall i hver liste – én per måned)
# --------------------------------------------------

# ===== PRISSONE 1 =====
did_z1 = [-1,-0.04,-0.55,0.15,0.45,0.71,-0.65,2.18,0.9,-0.04,1.33,1.5
    # okt24, nov24, des24, ..., sep25
]

did_z1_temp = [-0.16,0.75,0.96,1.5,0.43,1.09,0.48,0.33,0.8,1.59,1.37,1.56
    # okt24, nov24, des24, ..., sep25
]

# ===== PRISSONE 2 =====
did_z2 = [-0.05,0.44,0.24,0.64,0.42,0.87,0.86,0.74,0.92,1.28,1.8,1.89
    # okt24, nov24, des24, ..., sep25
]

did_z2_temp = [-0.52,0.29,0.41,1.75,0.32,0.82,0.56,1.56,0.86,1.05,1.83,1.68
    # okt24, nov24, des24, ..., sep25
]

# ===== PRISSONE 3 =====
did_z5 = [-0.24,0.62,0.28,0.56,0.03,1.31,0.08,1.19,0.57,0.92,1.09,1.37
    # okt24, nov24, des24, ..., sep25
]

did_z5_temp = [-0.05,0.74,0.81,0.8,0.04,1.34,0.19,0.48,0.49,1.52,1.16,1.3
    # okt24, nov24, des24, ..., sep25
]

# --------------------------------------------------
# 3. Plot: alle 6 serier i samme figur
# --------------------------------------------------
'''plt.figure(figsize=(14, 7))

plt.plot(dates, did_z1,"--", label="NO1", linewidth=2, color= 'blue')
plt.plot(dates, did_z1_temp, label="NO1 w/Temp", color = 'blue')

plt.plot(dates, did_z2, "--", label="NO2", linewidth=2, color = 'red')
plt.plot(dates, did_z2_temp,  label="NO2 w/Temp", color = 'red')

plt.plot(dates, did_z5, "--", label="NO5", linewidth=2, color = 'green')
plt.plot(dates, did_z5_temp,  label="NO5 w/Temp", color = 'green')

# --------------------------------------------------
# 4. Aksen og utseende
# --------------------------------------------------
plt.axhline(0, color="black", linewidth=1)
plt.xlabel("Month")
plt.ylabel("Difference in Difference ")
plt.title("Difference in Differences – Monthly estimates")
plt.legend(ncol=2)
plt.grid(True)'''

fig, axes = plt.subplots(
    nrows=3,
    ncols=1,
    figsize=(14, 10),
    sharex=True
)

# Plot prissone 1
axes[0].plot(dates, did_z1, label="NO1", color="blue")
axes[0].plot(dates, did_z1_temp, label="NO1 w/Temp",color="green")
axes[0].set_title("DiD – NO1")
axes[0].set_ylabel("Difference in Difference")
axes[0].grid(True)

# Plot prissone 2
axes[1].plot(dates, did_z2, label="NO2", color="blue")
axes[1].plot(dates, did_z2_temp, label="NO2 w/Temp",color="green")
axes[1].set_title("DiD – NO2")
axes[1].set_ylabel("Difference in Difference")
axes[1].grid(True)

# Plot prissone 3
axes[2].plot(dates, did_z5, label="NO5", color="blue")
axes[2].plot(dates, did_z5_temp, label="NO5 w/Temp", color="green")
axes[2].set_title("DiD – NO5")
axes[2].set_ylabel("Difference in Difference")
axes[2].set_xlabel("Date")
axes[2].grid(True)

# --------------------------------------------------
# 4. Vis alt i ett vindu
# --------------------------------------------------
from matplotlib.lines import Line2D

temp_legend_elements = [
    Line2D([0], [0], marker = 's',
           color='blue',
           linestyle='None',
           markersize=10,
           label="Without temperature correction"),

    Line2D([0], [0], marker = 's',
           color='green',
           linestyle='None',
           markersize=10,
           label='With temperature correction'
           )
]

temp_legend = fig.legend(
    handles=temp_legend_elements,
    loc="upper right",
    fontsize=17,
    framealpha=0.3,
    frameon=True
)

fig.add_artist(temp_legend)

plt.tight_layout()
plt.show()

