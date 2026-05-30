import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------- FILSTI, denne e for stor for å laste inn i github  -----------------------------
CSV_PATH = Path('/Users/synnelefdal/Desktop/spotpriser(in).csv')

# Sett til None for automatisk valg av alle 5 prissoner
selected_zones = None

# --------------- HJELPEFUNKSJONER ---------------
def clean_number_series(s: pd.Series) -> pd.Series:

    s = s.astype(str).str.strip()
    s = s.str.replace(r"[^\d,\.-]", "", regex=True)

    has_comma = s.str.contains(",", regex=False)
    has_dot = s.str.contains(r"\.", regex=True)

    # Hvis både komma og punkt: komma tolkes som tusenskille
    s1 = np.where(has_comma & has_dot, s.str.replace(",", "", regex=False), s)
    s1 = pd.Series(s1, index=s.index)

    # Hvis bare komma: komma = desimal
    s2 = np.where(~has_dot & s1.str.contains(",", regex=False),
                  s1.str.replace(",", ".", regex=False), s1)

    return pd.to_numeric(pd.Series(s2), errors="coerce")


def parse_datetime(date_series: pd.Series, hour_series: pd.Series) -> pd.Series:
    """
    Kombiner Dato + Time til datetime.
    Antar Time = 1–24 → konverteres til 0–23.
    """
    d = pd.to_datetime(date_series, errors="coerce", dayfirst=False)
    h = pd.to_numeric(hour_series, errors="coerce")
    h_adj = (h - 1).clip(lower=0, upper=23)
    return d + pd.to_timedelta(h_adj, unit="h")


def week_monday(dt: pd.Series) -> pd.Series:
    """Returner mandag (start på ISO-uke)."""
    dt = pd.to_datetime(dt, errors="coerce")
    return dt.dt.normalize() - pd.to_timedelta(dt.dt.weekday, unit="D")

# --------------- LES DATA ---------------
try:
    df = pd.read_csv(CSV_PATH)
except Exception:
    df = pd.read_csv(CSV_PATH, sep=";")

df.columns = [c.strip() for c in df.columns]

required_cols = {
    "Tidspunkt", "Dato", "Time", "Prissone",
    "Spotpris_NOK_MWh", "Spotpris_NOK_kWh"
}

missing = required_cols - set(df.columns)
if missing:
    raise ValueError(f"Mangler kolonner i CSV: {missing}")

# Rens tall
df["Spotpris_NOK_kWh"] = clean_number_series(df["Spotpris_NOK_kWh"])
df["Spotpris_NOK_MWh"] = clean_number_series(df["Spotpris_NOK_MWh"])

# Lag datetime
df["Datetime"] = parse_datetime(df["Dato"], df["Time"])



# Normaliser prissonenavn
df["Prissone"] = df["Prissone"].astype(str).str.strip()

# --------------- UKESAGGREGERING ---------------
df["UkeStart"] = week_monday(df["Datetime"])

weekly = (
    df.groupby(["Prissone", "UkeStart"], as_index=False)
      .agg({"Spotpris_NOK_kWh": "mean"})
)

weekly["Spotpris_NOK_MWh"] = weekly["Spotpris_NOK_kWh"] * 1000
weekly = weekly.rename(columns={"UkeStart": "Date"})
weekly["Hour"] = 1

weekly = weekly[
    ["Prissone", "Date", "Hour", "Spotpris_NOK_MWh", "Spotpris_NOK_kWh"]
]

# --------------- VELG PRISSONER ---------------
if selected_zones is None:
    selected = weekly["Prissone"].value_counts().index.tolist()[:5]
else:
    selected = selected_zones

weekly_sel = weekly[weekly["Prissone"].isin(selected)].copy()
weekly_sel = weekly_sel.sort_values(["Date", "Prissone"])

# --------------- PLOT ---------------
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

styles = ["-", "--", ":", "-.", (0, (3, 1, 1, 1))]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

legend_names = {
    "Oslo": "NO1",
    "Stavanger": "NO2",
    "Trondheim": "NO3",
    "Tromsø": "NO4",
    "Bergen": "NO5",
}

for i, zone in enumerate(selected):
    zdf = weekly_sel[weekly_sel["Prissone"] == zone]
    if zdf.empty:
        continue

    ax.plot(
        zdf["Date"],
        zdf["Spotpris_NOK_kWh"],
        label=legend_names.get(zone, zone),
        linestyle=styles[i % len(styles)],
        color=colors[i % len(colors)],
        linewidth=2.0,
    )

ax.set_xlabel("Year")
ax.set_ylabel("NOK/kWh")
ax.legend(title="Price Zone", ncols=5)


# --------------- MÅNEDLIG GJENNOMSNITT ---------------

# Lag kolonner for år og måned
df["Year"] = df["Datetime"].dt.year
df["Month"] = df["Datetime"].dt.month

df_2026 = df[(df["Year"] == 2026) & (df["Month"].isin([2, 3]))]         # Filtrer for februar og mars 2026

# Beregn gjennomsnitt per prissone og måned
monthly_avg = (
    df_2026.groupby(["Prissone", "Year", "Month"], as_index=False)
    .agg({"Spotpris_NOK_kWh": "mean"})
)

monthly_avg = monthly_avg.sort_values(["Month", "Prissone"])

print("\n--- Gjennomsnittlig spotpris per måned (NOK/kWh) ---")
for _, row in monthly_avg.iterrows():
    month_name = "February" if row["Month"] == 2 else "March"
    print(f"{row['Prissone']} | {month_name} 2026: {row['Spotpris_NOK_kWh']:.4f} NOK/kWh")

fig.autofmt_xdate()
plt.tight_layout()
plt.show()
