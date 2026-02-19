

#NY VERSJON FRA CHAT
# ============================================================
# 1) Importer pakker
# ============================================================
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm


# ============================================================
# 2) Les CSV-filer (semikolon-separert)
#    Kolonner: usage_date_id;group_definition;price_area;start_time_utc;consumption_kwh;metering_point_count
# ============================================================
# Juster filnavn/paths etter behov
data_mNP = pd.read_csv(
    'All_Demand_Data/NO2_mNP.csv',
    sep=';',
    dtype={
        'usage_date_id': str,
        'group_definition': str,
        'price_area': str
    }
)

data_uNP = pd.read_csv(
    'All_Demand_Data/NO2_uNP.csv',
    sep=';',
    dtype={
        'usage_date_id': str,
        'group_definition': str,
        'price_area': str
    }
)

# ============================================================
# 3) Sett dato-intervaller utenfor funksjonen (globalt)
# ============================================================
start_date_before = '2024-11-01'
end_date_before   = '2025-01-31'
start_date_after  = '2025-11-01'
end_date_after    = '2026-01-31'

# ============================================================
# 4) Funksjonen (ingen price_area-parameter, hour er valgfri)
# ============================================================
def DifferenceinDifference(data_mNP, data_uNP, Temp=None, hour=None):
    """
    Difference-in-Difference med timefilter.
    - Ingen filtrering på price_area (tas fra CSV, men brukes ikke)
    - Dato-intervaller hentes fra globale variabler:
        start_date_before, end_date_before, start_date_after, end_date_after
    - hour kan være None/int/tuple/list for å velge time(r) på døgnet (0–23)
    """

    # ------------------- Hent dato-intervaller som globale ---------- #
    global start_date_before, end_date_before, start_date_after, end_date_after

    # ------------------- Endring til Date og Hour ------------------- #
    data_mNP = data_mNP.copy()
    data_uNP = data_uNP.copy()

    data_mNP['start_time_utc'] = pd.to_datetime(
        data_mNP['start_time_utc'],
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce',
        utc=True
    )
    data_uNP['start_time_utc'] = pd.to_datetime(
        data_uNP['start_time_utc'],
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce',
        utc=True
    )

    # Merk: dt.hour gir 0–23
    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)
    data_uNP['Date'] = data_uNP['start_time_utc'].dt.date
    data_uNP['Hour'] = data_uNP['start_time_utc'].dt.hour.astype(int)

    # ------------------- Valgfritt time-filter ---------------------- #
    # hour kan være None / int / tuple(start, slutt) / liste
    def _build_hour_list(h):
        if h is None:
            return None
        if isinstance(h, int):
            if not (0 <= h <= 23):
                raise ValueError("hour (int) må være i [0, 23]")
            return [h]
        if isinstance(h, tuple) and len(h) == 2:
            h0, h1 = h
            if not (0 <= h0 <= 23 and 0 <= h1 <= 23 and h0 <= h1):
                raise ValueError("hour (tuple) må være (start, slutt) med 0<=start<=slutt<=23")
            return list(range(h0, h1 + 1))
        if isinstance(h, (list, set, np.ndarray, pd.Series)):
            hours = sorted(set(int(x) for x in h))
            if any((x < 0 or x > 23) for x in hours):
                raise ValueError("alle timer i hour-listen må være i [0, 23]")
            return hours
        raise TypeError("hour må være None, int, tuple(start, slutt) eller list/set/array")

    hours_to_keep = _build_hour_list(hour)
    if hours_to_keep is not None:
        data_mNP = data_mNP[data_mNP['Hour'].isin(hours_to_keep)].copy()
        data_uNP = data_uNP[data_uNP['Hour'].isin(hours_to_keep)].copy()

    # ------------------- Filterer for dato -------------------------- #
    # Konverter 'Date' til Timestamp for sammenligning
    data_mNP['Date'] = pd.to_datetime(data_mNP['Date'])
    data_uNP['Date'] = pd.to_datetime(data_uNP['Date'])

    start_date_before_ts = pd.to_datetime(start_date_before)
    end_date_before_ts   = pd.to_datetime(end_date_before)
    start_date_after_ts  = pd.to_datetime(start_date_after)
    end_date_after_ts    = pd.to_datetime(end_date_after)

    data_demand_NP_filtered_before = data_mNP[
        (data_mNP['Date'] >= start_date_before_ts) & (data_mNP['Date'] <= end_date_before_ts)
    ].copy()
    data_demand_NP_filtered_after = data_mNP[
        (data_mNP['Date'] >= start_date_after_ts) & (data_mNP['Date'] <= end_date_after_ts)
    ].copy()

    data_demand_UtenNP_filtered_before = data_uNP[
        (data_uNP['Date'] >= start_date_before_ts) & (data_uNP['Date'] <= end_date_before_ts)
    ].copy()
    data_demand_UtenNP_filtered_after = data_uNP[
        (data_uNP['Date'] >= start_date_after_ts) & (data_uNP['Date'] <= end_date_after_ts)
    ].copy()

    # ----------------- KPI: kWh per målepunkt ---------------------- #
    data_demand_NP_filtered_before['kWh/Metering_point'] = (
        data_demand_NP_filtered_before['consumption_kwh'] /
        data_demand_NP_filtered_before['metering_point_count']
    )
    data_demand_NP_filtered_after['kWh/Metering_point'] = (
        data_demand_NP_filtered_after['consumption_kwh'] /
        data_demand_NP_filtered_after['metering_point_count']
    )

    data_demand_UtenNP_filtered_before['kWh/Metering_point'] = (
        data_demand_UtenNP_filtered_before['consumption_kwh'] /
        data_demand_UtenNP_filtered_before['metering_point_count']
    )
    data_demand_UtenNP_filtered_after['kWh/Metering_point'] = (
        data_demand_UtenNP_filtered_after['consumption_kwh'] /
        data_demand_UtenNP_filtered_after['metering_point_count']
    )

    # -------------- Aggreger per Dato / Time / Gruppe ------------- #
    # Merk: Vi grupperer IKKE på price_area her (samme som din kode),
    # så eventuelle flere prisområder i filene blir summert sammen.
    total_demand_hour_NP_before = (
        data_demand_NP_filtered_before
        .groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point']
        .sum().reset_index()
    )
    total_demand_hour_NP_after = (
        data_demand_NP_filtered_after
        .groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point']
        .sum().reset_index()
    )

    total_demand_hour_UtenNP_before = (
        data_demand_UtenNP_filtered_before
        .groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point']
        .sum().reset_index()
    )
    total_demand_hour_UtenNP_after = (
        data_demand_UtenNP_filtered_after
        .groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point']
        .sum().reset_index()
    )

    # ------------ Slå sammen før/etter for hver gruppe ------------ #
    df_NP = pd.concat(
        [total_demand_hour_NP_before, total_demand_hour_NP_after],
        ignore_index=True
    )
    df_UtenNP = pd.concat(
        [total_demand_hour_UtenNP_before, total_demand_hour_UtenNP_after],
        ignore_index=True
    )

    # ----------------- Beregninger; NP-gruppen --------------------- #
    df_NP['Date'] = pd.to_datetime(df_NP['Date'])
    df_NP['Month'] = df_NP['Date'].dt.strftime('%B')
    df_NP['Hour'] = df_NP['Hour'].astype(int)

    # ----------------- Beregninger; Uten NP-gruppen --------------- #
    df_UtenNP['Date'] = pd.to_datetime(df_UtenNP['Date'])
    df_UtenNP['Month'] = df_UtenNP['Date'].dt.strftime('%B')
    df_UtenNP['Hour'] = df_UtenNP['Hour'].astype(int)

    # --------------- Regresjonsdatasett ---------------------------- #
    df_NP['Norgespris'] = 'Med_NP'
    df_UtenNP['Norgespris'] = 'Uten_NP'
    df = pd.concat([df_NP, df_UtenNP], ignore_index=True)

    # Sett Before/After basert på de globale periodene
    df['Group'] = np.where(
        (df['Date'] >= start_date_after_ts) & (df['Date'] <= end_date_after_ts),
        'After_ref', 'Before_ref'
    )

    # (Valgfritt) ordnede kategorier for Month
    df['Month'] = pd.Categorical(
        df['Month'],
        categories=['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'],
        ordered=True
    )

    # Log-transformasjon krever positivt nivå
    df = df[df['kWh/Metering_point'] > 0].copy()

    # ----------------- DID-regresjon ------------------------------- #
    formula = (
        'np.log(Q("kWh/Metering_point")) ~ '
        'C(Group, Treatment(reference="Before_ref")) '
        '* C(Norgespris, Treatment(reference="Uten_NP"))'
    )
    y, X = patsy.dmatrices(
        formula, data=df, return_type="dataframe", NA_action="drop"
    )
    model = sm.OLS(y, X).fit()
    print(model.summary())

    return model, df

# ============================================================
# 5) Eksempler på bruk
# ============================================================
# A) Kun kl. 17 (timer er 0–23)
# model, used_df = DifferenceinDifference(data_mNP, data_uNP, hour=17)

# B) Intervall 17–20
# model, used_df = DifferenceinDifference(data_mNP, data_uNP, hour=(17, 20))

# C) Vilkårlig liste timer (morgen + kveld)
# model, used_df = DifferenceinDifference(data_mNP, data_uNP, hour=[7, 8, 9, 17])

DifferenceinDifference(data_mNP, data_uNP,hour=[17,18,19])