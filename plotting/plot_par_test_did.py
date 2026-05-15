
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from networkx.algorithms.bipartite.basic import color


dates = pd.date_range(
    start="2024-10-01",
    end="2026-01-01",
    freq="MS"
)

# -------- NO1 -------- #
#did_z1 = [-1,-0.04,-0.55,0.15,0.45,0.71,-0.65,2.18,0.9,-0.04,1.33,1.5,2.74,2.47,3.24,4.63
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26
#]

did_z1_temp = [-0.16,0.75,0.96,1.5,0.43,1.09,0.48,0.33,0.8,1.59,1.37,1.56,2.66,2.89,3.59,3.97
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26
]

# -------- NO2 -------- #
#did_z2 = [-0.05,0.44,0.24,0.64,0.42,0.87,0.86,0.74,0.92,1.28,1.8,1.89, 3.3,3.76,4.79,4.97
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26
#]

did_z2_temp = [-0.52,0.29,0.41,1.75,0.32,0.82,0.56,1.56,0.86,1.05,1.83,1.68,3.34,3.59,4.59,4.54
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26
]

# -------- NO5 -------- #
#did_z5 = [-0.24,0.62,0.28,0.56,0.03,1.31,0.08,1.19,0.57,0.92,1.09,1.37, 2.06,2.32,2.76,3.4
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26
#]

did_z5_temp = [-0.05,0.74,0.81,0.8,0.04,1.34,0.19,0.48,0.49,1.52,1.16,1.3,2.01,2.32,2.76,2.72
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26
]
 # ----------- PLOT ----------- #

fig, axes = plt.subplots(
    nrows=3,
    ncols=1,
    figsize=(14, 10),
    sharex=True
)

# -------- NO1 --------
#axes[0].plot(dates, did_z1, label="NO1", color="blue", marker = 'o', linestyle = 'None')
axes[0].plot(dates, did_z1_temp, label="NO1 w/Temp",color="green", marker = 'o', linestyle = 'None')
axes[0].set_title("NO1", fontsize = 20)
#axes[0].set_ylabel("Difference in Difference", fontsize = 20)
axes[0].axvline(x = pd.Timestamp('2025-10-01'), color = 'red', linestyle = '--', linewidth = 2, alpha = 0.8)
axes[0].axvspan(pd.Timestamp("2025-10-01"), pd.Timestamp("2026-01-01"), color = 'lightcoral', alpha = 0.15, zorder=0)
axes[0].tick_params(axis='y', labelsize=20)
axes[0].grid(True)

# -------- NO2 --------
#axes[1].plot(dates, did_z2, label="NO2", color="blue", marker = 'o', linestyle = 'None')
axes[1].plot(dates, did_z2_temp, label="NO2 w/Temp",color="green", marker = 'o', linestyle = 'None')
axes[1].set_title("NO2", fontsize = 20)
axes[1].set_ylabel("Difference in Difference [%]", fontsize = 20)
axes[1].axvline(x = pd.Timestamp('2025-10-01'), color = 'red', linestyle = '--', linewidth = 2, alpha = 0.8)
axes[1].axvspan(pd.Timestamp("2025-10-01"), pd.Timestamp("2026-01-01"), color = 'lightcoral', alpha = 0.15, zorder=0)
axes[1].tick_params(axis='y', labelsize=20)
axes[1].grid(True)

# -------- NO5 --------
#axes[2].plot(dates, did_z5, label="NO5", color="blue", marker = 'o', linestyle = 'None')
axes[2].plot(dates, did_z5_temp, label="NO5 w/Temp", color="green", marker = 'o', linestyle = 'None')
axes[2].set_title("NO5", fontsize = 20)
#axes[2].set_ylabel("Difference in Difference", fontsize = 20)
axes[2].axvline(x = pd.Timestamp('2025-10-01'), color = 'red', linestyle = '--', linewidth = 2, alpha = 0.8)
axes[2].axvspan(pd.Timestamp("2025-10-01"), pd.Timestamp("2026-01-01"), color = 'lightcoral', alpha = 0.15, zorder=0)
axes[2].set_xlabel("Month", fontsize = 20)
axes[2].tick_params(axis='y', labelsize=20)
axes[2].grid(True)



plt.xticks(fontsize=20)

ymin, ymax = -0.7, 4.8
yticks = np.arange(0, 5, 2)  # 0, 2, 4

for ax in axes:
    ax.set_ylim(ymin, ymax)
    ax.set_yticks(yticks)

plt.tight_layout()
plt.show()

