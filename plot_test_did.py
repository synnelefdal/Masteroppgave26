
import matplotlib.pyplot as plt
import pandas as pd

# --------------------------------------------------
# 1. Lag månedlig tidsakse: jan 2024 – sep 2025
# --------------------------------------------------
dates = pd.date_range(
    start="2024-01-01",
    end="2025-09-01",
    freq="MS"   # Monthly Start
)

# --------------------------------------------------
# 2. Fyll inn månedlige DiD-verdier
#    ÉN verdi per måned (totalt 21)
# --------------------------------------------------
did_zone_1 = [
    0.12, 0.15, 0.10, 0.08, 0.11, 0.14,
    0.16, 0.18, 0.17, 0.19, 0.20, 0.22,  # 2024
    0.21, 0.23, 0.25, 0.24, 0.26, 0.28,
    0.30, 0.29, 0.31                    # 2025 jan–sep
]

did_zone_2 = [
    0.05, 0.07, 0.06, 0.04, 0.05, 0.08,
    0.09, 0.10, 0.11, 0.12, 0.13, 0.14,
    0.15, 0.16, 0.18, 0.17, 0.19, 0.20,
    0.21, 0.22, 0.23
]

did_zone_3 = [
    -0.02, -0.01, 0.00, 0.01, 0.03, 0.02,
    0.04, 0.05, 0.06, 0.07, 0.06, 0.08,
    0.09, 0.10, 0.11, 0.12, 0.13, 0.14,
    0.15, 0.16, 0.17
]

# --------------------------------------------------
# 3. Plot – tre grafer i samme vindu
# --------------------------------------------------
fig, axes = plt.subplots(
    nrows=3,
    ncols=1,
    figsize=(14, 10),
    sharex=True
)

axes[0].plot(dates, did_zone_1, marker="o")
axes[0].set_title("DiD – Prissone 1")
axes[0].set_ylabel("DiD")
axes[0].grid(True)

axes[1].plot(dates, did_zone_2, marker="o")
axes[1].set_title("DiD – Prissone 2")
axes[1].set_ylabel("DiD")
axes[1].grid(True)

axes[2].plot(dates, did_zone_3, marker="o")
axes[2].set_title("DiD – Prissone 3")
axes[2].set_ylabel("DiD")
axes[2].set_xlabel("Måned")
axes[2].grid(True)

# --------------------------------------------------
# 4. Vis alt i ett vindu
# --------------------------------------------------
plt.tight_layout()
plt.show()