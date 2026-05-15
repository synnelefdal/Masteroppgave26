
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from networkx.algorithms.bipartite.basic import color


dates = pd.date_range(
    start="2024-10-01",
    end="2026-03-31",
    freq="MS"
)

# -------- NO1 -------- #
#did_z1 = [-1,-0.04,-0.55,0.15,0.45,0.71,-0.65,2.18,0.9,-0.04,1.33,1.5,2.74,2.47,3.24,4.63
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26
#]

did_z1_temp = [0.36,0.87,1.18,1.47,0.60,1.11,0.78,0.55,0.96,1.20,1.12,0.93,1.70,2.28,2.79,3.39, 3.48, 3.59
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26, feb26, mars26
]

# -------- NO2 -------- #
#did_z2 = [-0.05,0.44,0.24,0.64,0.42,0.87,0.86,0.74,0.92,1.28,1.8,1.89, 3.3,3.76,4.79,4.97
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26, feb26, mars26
#]

did_z2_temp = [0.59,0.71,1.04,1.79,0.97,0.98,1.03,1.05,1.10,0.89,1.15,1.10,1.94,2.50,3.44,3.53, 3.92, 4.56
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26, feb26, mars26
]

# -------- NO5 -------- #
#did_z5 = [-0.24,0.62,0.28,0.56,0.03,1.31,0.08,1.19,0.57,0.92,1.09,1.37, 2.06,2.32,2.76,3.4
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26, feb26, mars26
#]

did_z5_temp = [0.39,0.91,1.02,1.07,0.45,1.46,0.82,0.93,0.87,1.43,1.18,1.34,1.77,1.92,2.37,2.67, 2.97, 3.45
    # okt24, nov24, des24, ..., sep25 + okt25, nov25, des25, jan26, feb26, mars26
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
axes[0].axvspan(pd.Timestamp("2025-10-01"), pd.Timestamp("2026-03-31"), color = 'lightcoral', alpha = 0.15, zorder=0)
axes[0].tick_params(axis='y', labelsize=20)
axes[0].grid(True)

# -------- NO2 --------
#axes[1].plot(dates, did_z2, label="NO2", color="blue", marker = 'o', linestyle = 'None')
axes[1].plot(dates, did_z2_temp, label="NO2 w/Temp",color="green", marker = 'o', linestyle = 'None')
axes[1].set_title("NO2", fontsize = 20)
axes[1].set_ylabel("Difference in Difference [%]", fontsize = 20)
axes[1].axvline(x = pd.Timestamp('2025-10-01'), color = 'red', linestyle = '--', linewidth = 2, alpha = 0.8)
axes[1].axvspan(pd.Timestamp("2025-10-01"), pd.Timestamp("2026-03-31"), color = 'lightcoral', alpha = 0.15, zorder=0)
axes[1].tick_params(axis='y', labelsize=20)
axes[1].grid(True)

# -------- NO5 --------
#axes[2].plot(dates, did_z5, label="NO5", color="blue", marker = 'o', linestyle = 'None')
axes[2].plot(dates, did_z5_temp, label="NO5 w/Temp", color="green", marker = 'o', linestyle = 'None')
axes[2].set_title("NO5", fontsize = 20)
#axes[2].set_ylabel("Difference in Difference", fontsize = 20)
axes[2].axvline(x = pd.Timestamp('2025-10-01'), color = 'red', linestyle = '--', linewidth = 2, alpha = 0.8)
axes[2].axvspan(pd.Timestamp("2025-10-01"), pd.Timestamp("2026-03-31"), color = 'lightcoral', alpha = 0.15, zorder=0)
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

