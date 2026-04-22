import pandas as pd

# --- KONFIGURASJON ---
input_fil = "ntnu_norgespris_mba sortert.csv"
output_fil = "NO5_resten.csv"

kolonne1 = "group_definition"
kolonne2 = "price_area"
verdi1 = "Resten"
verdi2 = "NO5"

# Bruk sep=';' for semikolonseparert
df = pd.read_csv(input_fil, sep=";", dtype=str)  # dtype=str for å unngå NaN-problemer
# Fyll NaN med tom streng og strip whitespace
df = df.fillna("").applymap(lambda s: s.strip() if isinstance(s, str) else s)

# Filtrer (case-insensitivt)
maske = (df[kolonne1].str.lower() == verdi1.lower()) & (df[kolonne2].str.lower() == verdi2.lower())
df_filtrert = df[maske]

# Skriv ut (bevar semikolon)
df_filtrert.to_csv(output_fil, index=False, sep=";")
print(f"Ferdig! {len(df_filtrert)} rader skrevet til: {output_fil}")