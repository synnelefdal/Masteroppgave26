
import matplotlib.pyplot as plt
import pandas as pd

# --------------------------------------------------
# 1. Månedlig tidsakse: jan 2024 – sep 2025 (21 mnd)
# --------------------------------------------------
dates = pd.date_range(
    start="2024-01-01",
    end="2025-09-01",
    freq="MS"
)

# --------------------------------------------------
# 2. Fyll inn DINE DiD-verdier her
#    (21 tall i hver liste – én per måned)
# --------------------------------------------------

# ===== PRISSONE 1 =====
did_z1 = [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
    # jan24, feb24, mar24, ..., sep25
]

did_z1_temp = [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
    # jan24, feb24, mar24, ..., sep25
]

# ===== PRISSONE 2 =====
did_z2 = [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
    # jan24, feb24, mar24, ..., sep25
]

did_z2_temp = [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
    # jan24, feb24, mar24, ..., sep25
]

# ===== PRISSONE 3 =====
did_z3 = [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
    # jan24, feb24, mar24, ..., sep25
]

did_z3_temp = [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
    # jan24, feb24, mar24, ..., sep25
]

# --------------------------------------------------
# 3. Plot: alle 6 serier i samme figur
# --------------------------------------------------
plt.figure(figsize=(14, 7))

plt.plot(dates, did_z1, label="Sone 1", linewidth=2)
plt.plot(dates, did_z1_temp, "--", label="Sone 1 (temp.korr)")

plt.plot(dates, did_z2, label="Sone 2", linewidth=2)
plt.plot(dates, did_z2_temp, "--", label="Sone 2 (temp.korr)")

plt.plot(dates, did_z3, label="Sone 3", linewidth=2)
plt.plot(dates, did_z3_temp, "--", label="Sone 3 (temp.korr)")

# --------------------------------------------------
# 4. Aksen og utseende
# --------------------------------------------------
plt.axhline(0, color="black", linewidth=1)
plt.xlabel("Måned")
plt.ylabel("DiD-verdi")
plt.title("Difference-in-Differences – månedlige estimater")
plt.legend(ncol=2)
plt.grid(True)

# --------------------------------------------------
# 5. Vis figuren
# --------------------------------------------------
plt.tight_layout()
plt.show()