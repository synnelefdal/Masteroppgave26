import pandas as pd
import matplotlib.pyplot as plt

# === LAST INN EXCEL-FIL ===
df = pd.read_excel("/Users/synnelefdal/Desktop/timespriser.xlsx", engine="openpyxl")


# === SJEKK KOLONNENE ===
print(df.columns)

# === GI RIKTIGE NAVN (basert på din fil) ===
df = df.iloc[:, :3]  # tar kun de 3 første kolonnene
df.columns = ["Tidspunkt", "Pris_ore_kWh", "Prissone"]

# === FJERN RADER SOM IKKE ER DATA (header som har sneket seg inn) ===
df = df[df["Pris_ore_kWh"] != "Gjennomsnitt Pris (øre/kWh)"]

# === KONVERTER PRIS (fikser komma) ===
df["Pris_ore_kWh"] = (
    df["Pris_ore_kWh"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)

df["Pris_ore_kWh"] = pd.to_numeric(df["Pris_ore_kWh"], errors="coerce")

# === FJERN EVENTUELLE NA ===
df = df.dropna(subset=["Pris_ore_kWh"])

# === DATO ===
df["Tidspunkt"] = pd.to_datetime(df["Tidspunkt"], dayfirst=True, errors="coerce")

# === TIME ===
df["Time"] = df["Tidspunkt"].dt.hour

# === ØRE → KR ===
df["Pris_kroner"] = df["Pris_ore_kWh"] #/ 100

# === FILTRER ===
start_date = pd.Timestamp("2025-10-01")
end_date = pd.Timestamp("2026-03-31")

filtered = df[(df["Tidspunkt"] >= start_date) & (df["Tidspunkt"] <= end_date)]

if filtered.empty:
    print("Ingen data etter 1. oktober 2025 → bruker 2024\n")
    start_date = pd.Timestamp("2024-10-01")
    filtered = df[(df["Tidspunkt"] >= start_date) & (df["Tidspunkt"] <= end_date)]

# === GJENNOMSNITT PER TIME/SONE ===
result = (
    filtered
    .groupby(["Prissone", "Time"])["Pris_kroner"]
    .mean()
    .reset_index()
    .sort_values(["Prissone", "Time"])
)

# === PRINT ===
print("\n=== RESULTAT ===\n")
print(result.to_string(index=False))

# === GRAFER ===
for zone in result["Prissone"].unique():
    zone_data = result[result["Prissone"] == zone]

    '''plt.figure()
    plt.plot(zone_data["Time"], zone_data["Pris_kroner"], marker='o')
    #plt.title(f"Gjennomsnittlig timepris - {zone}")
    plt.xlabel("Hour (0-23)", fontsize = 20 )
    plt.xlim(0, 23.3)
    plt.ylim(0.78, 1.3)
    plt.xticks(range(0, 23), fontsize = 20)
    plt.yticks(fontsize = 20)
    plt.ylabel("NOK/kWh", fontsize = 20)
    plt.grid()
    plt.show()'''

# === GRAFER (ALLE I SAMME VINDU) ===
plt.figure()

for zone in result["Prissone"].unique():
    zone_data = result[result["Prissone"] == zone]

    # Velg farger
    if zone == "NO1":
        color = "#5DADE2"
    elif zone == "NO2":
        color = "#F5B041"
    elif zone == "NO5":
        color = "#7F8C8D"
    else:
        color = "black"

    plt.plot(zone_data["Time"], zone_data["Pris_kroner"],
             marker='o', label=zone, color=color)

# Felles akser og styling
plt.xlabel("Hour (0-23)", fontsize=20)
plt.ylabel("Price (øre/kWh)", fontsize=20)


plt.xlim(0, 23.3)
plt.ylim(75, 130)

plt.xticks(range(0, 24), fontsize=20)   # ✅ ALLE TIMER
plt.yticks(fontsize=20)

plt.grid()
plt.legend(fontsize=20)  # ✅ viser NO1, NO2, NO5

plt.show()
