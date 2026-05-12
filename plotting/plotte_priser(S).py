import pandas as pd
from matplotlib.lines import lineStyles

#prices= pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Prosjektoppgave2/prices.csv')


# === FILNAVN ===
'''
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ======= FILNAVN (endre ved behov) ===========================================
#CSV_PATH = Path("spotpriser_in.csv")
CSV_PATH = Path('/Users/synnelefdal/Desktop/spotpriser(in).csv')
# Hvis du vil velge prissone eksplisitt: skriv inn 3 navn her.
# Eksempel: selected_zones = ["Oslo", "Bergen", "Trondheim"]
selected_zones = None  # <-- sett til None for automatisk valg av topp 3

# ======= HJELPEFUNKSJONER =====================================================
def clean_number_series(s: pd.Series) -> pd.Series:
    """Rydd tall med både punkt/komma og evt. '0.24.' etc."""
    s = s.astype(str).str.strip()
    s = s.str.replace(r"[^\d,\.-]", "", regex=True)
    has_comma = s.str.contains(",", regex=False)
    has_dot   = s.str.contains(r"\.", regex=True)
    # Hvis begge finnes: tolker komma som tusenskille
    s1 = np.where(has_comma & has_dot, s.str.replace(",", "", regex=False), s)
    s1 = pd.Series(s1, index=s.index)
    # Hvis kun komma: tolker komma som desimal
    s2 = np.where(~has_dot & s1.str.contains(",", regex=False),
                  s1.str.replace(",", ".", regex=False), s1)
    return pd.to_numeric(pd.Series(s2), errors="coerce")

def parse_datetime(date_series: pd.Series, hour_series: pd.Series) -> pd.Series:
    """
    Slå sammen Dato + Time til en timesoppløst datetime.
    Antar Time = 1..24 -> konverteres til 0..23 ved å trekke 1 time.
    """
    d = pd.to_datetime(date_series, errors="coerce", dayfirst=False, infer_datetime_format=True)
    h = pd.to_numeric(hour_series, errors="coerce")
    h_adj = (h - 1).clip(lower=0, upper=23)  # 1->0, 24->23
    return d + pd.to_timedelta(h_adj, unit="h")

def week_monday(dt: pd.Series) -> pd.Series:
    """Returner mandagsdato (start av ISO-uke) for hver datetime."""
    dt = pd.to_datetime(dt, errors="coerce")
    return (dt.dt.normalize() - pd.to_timedelta(dt.dt.weekday, unit="D"))

# ======= LES DATA =============================================================
# For CSV'er med ; som separator (vanlig i norsk Windows), sett sep=";"
try:
    df = pd.read_csv(CSV_PATH)
except Exception:
    df = pd.read_csv(CSV_PATH, sep=";")

# Rens kolonnenavn
df.columns = [c.strip() for c in df.columns]

# Forventede kolonner
required = {"Tidspunkt", "Dato", "Time", "Prissone", "Spotpris_NOK_MWh", "Spotpris_NOK_kWh"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Mangler kolonner i CSV: {missing}\nFant: {list(df.columns)}")

# Rydd tallkolonner
df["Spotpris_NOK_kWh"] = clean_number_series(df["Spotpris_NOK_kWh"])
df["Spotpris_NOK_MWh"] = clean_number_series(df["Spotpris_NOK_MWh"])

# Slå sammen Dato + Time -> Datetime
df["Datetime"] = parse_datetime(df["Dato"], df["Time"])

# Normaliser navn på prissone (trim + bevar stor/liten)
df["Prissone"] = df["Prissone"].astype(str).str.strip()

# ======= AGGREGER TIL UKE (MANDAG) ===========================================
# Ukesnitt per prissone
df["UkeStart"] = week_monday(df["Datetime"])
weekly = (
    df.groupby(["Prissone", "UkeStart"], as_index=False)["Spotpris_NOK_kWh"]
      .mean()
)
# Konsistent MWh = kWh * 1000
weekly["Spotpris_NOK_MWh"] = weekly["Spotpris_NOK_kWh"] * 1000.0

# Sett format-kolonner for kompatibilitet med tidligere datasett
weekly = weekly.rename(columns={"UkeStart": "Date"})
weekly["Hour"] = 1  # ukedata -> fast timeverdi
weekly = weekly[["Prissone", "Date", "Hour", "Spotpris_NOK_MWh", "Spotpris_NOK_kWh"]]

# ======= VELG TRE PRISSONER ===================================================
if selected_zones is None:
    # Ta topp-3 prissone etter antall ukepunkter
    counts = weekly["Prissone"].value_counts().index.tolist()
    selected = counts[:3]
else:
    selected = selected_zones

if len(selected) < 3:
    print(f"Advarsel: fant færre enn 3 prissone å plotte. Valgt: {selected}")

weekly_sel = weekly[weekly["Prissone"].isin(selected)].copy()
weekly_sel = weekly_sel.sort_values(["Date", "Prissone"])

# ======= PLOTT: ÉN FIGUR, TRE LINJER =========================================
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

# Farger/linjestiler (kan endres)
styles = ["-", "--", ":"]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

# Anta at weekly_sel (med kolonnene Prissone, Date, Spotpris_NOK_kWh) og selected, styles, colors finnes fra før

legend_names = {
    "Oslo": "NO1",
    "Kristiansand": "NO2",
    "Bergen": "NO5",
}

plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

for i, zone in enumerate(selected):
    zdf = weekly_sel[weekly_sel["Prissone"] == zone]
    if zdf.empty:
        continue
    ax.plot(
        zdf["Date"],
        zdf["Spotpris_NOK_kWh"],
        label=legend_names.get(zone, zone),  # <- her settes visningsnavnet
        linestyle=styles[i % len(styles)],
        color=colors[i % len(colors)],
        linewidth=2.0,
    )

#ax.set_title("Ukentlig gjennomsnittlig spotpris (NOK/kWh) – tre prissoner", fontsize=14)
ax.set_xlabel("Year")
ax.set_ylabel("NOK/kWh")

# Legend: tittel og layout (navnene er allerede bestemt av label= over)
ax.legend(title="Price Zone", ncols=3 if len(selected) >= 3 else 1)

fig.autofmt_xdate()
plt.tight_layout()
plt.show()'''

# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ===================== FILSTI ===============================================
CSV_PATH = Path('/Users/synnelefdal/Desktop/spotpriser(in).csv')

# Sett til None for automatisk valg av alle 5 prissoner
selected_zones = None

# ===================== HJELPEFUNKSJONER ======================================
def clean_number_series(s: pd.Series) -> pd.Series:
    """Rydd tall med både punkt/komma og evt. ugyldige tegn."""
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

# ===================== LES DATA ==============================================
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

# ===================== UKESAGGREGERING =======================================
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

# ===================== VELG FEM PRISSONER ====================================
if selected_zones is None:
    selected = weekly["Prissone"].value_counts().index.tolist()[:5]
else:
    selected = selected_zones

weekly_sel = weekly[weekly["Prissone"].isin(selected)].copy()
weekly_sel = weekly_sel.sort_values(["Date", "Prissone"])

# ===================== PLOTT =================================================
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

styles = ["-", "--", ":", "-.", (0, (3, 1, 1, 1))]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

legend_names = {
    "Oslo": "NO1",
    "Kristiansand": "NO2",
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

fig.autofmt_xdate()
plt.tight_layout()
plt.show()
