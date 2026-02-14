import pandas as pd
import numpy as np
from statsmodels.graphics.tukeyplot import results

data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')

def prep_time(df, time_col='start_time_utc'):
    # Gjør tid kolonnen timezone-aware og lag hour/date
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce', utc=True)
    if df[time_col].isna().any():
        # dropp rader uten gyldig tid
        df = df.dropna(subset=[time_col])
    return df

def period_value_per_mp(df, start, end,
                         time_col='start_time_utc',
                         kwh_col='consumption_kwh',
                         mp_col='metering_point_count'):
    """
    Returnerer kWh per (gjennomsnittlig) målepunkt i perioden:
    sum_t( kWh_t / MP_t ).
    Dette er likt summen i koden deres, men vektoriserer og er tryggere.
    """
    sub = df[(df[time_col] >= start) & (df[time_col] <= end)].copy()
    if sub.empty:
        return np.nan

    # Sikre numeriske kolonner
    sub[kwh_col] = pd.to_numeric(sub[kwh_col], errors='coerce')
    sub[mp_col]  = pd.to_numeric(sub[mp_col],  errors='coerce')

    sub = sub.dropna(subset=[kwh_col, mp_col])

    # Unngå deling på null
    sub = sub[sub[mp_col] > 0]

    if sub.empty:
        return np.nan

    # kWh per målepunkt, tidsvektet (time-for-time)
    per_mp_series = sub[kwh_col] / sub[mp_col]
    return per_mp_series.sum()

def did_simple(Med_NP, Uten_NP,
               pre_start='2024-10-01', pre_end='2025-01-31',
               post_start='2025-10-01', post_end='2026-01-31',
               treat_dataset='Med_NP',
               time_col='start_time_utc',
               kwh_col='consumption_kwh',
               mp_col='metering_point_count'):
    """
    Beregner 2x2 DiD 'minus-minus' med to datasett:
    - Med_NP = ett scenario (f.eks. behandlet)
    - Uten_NP = annet scenario (f.eks. kontroll)

    treat_dataset: 'Med_NP' eller 'Uten_NP' for å angi hvem som er 'T' i formelen.
    Returnerer et dict med alle fire celler + DiD.
    """

    # Forbered tid
    Med_NP  = prep_time(Med_NP, time_col=time_col)
    Uten_NP = prep_time(Uten_NP, time_col=time_col)

    # Sett periodegrenser
    pre_start  = pd.to_datetime(pre_start,  utc=True)
    pre_end    = pd.to_datetime(pre_end,    utc=True)
    post_start = pd.to_datetime(post_start, utc=True)
    post_end   = pd.to_datetime(post_end,   utc=True)

    # Beregn kWh per MP for hver celle
    M_pre  = period_value_per_mp(Med_NP,  pre_start,  pre_end,  time_col, kwh_col, mp_col)
    M_post = period_value_per_mp(Med_NP,  post_start, post_end, time_col, kwh_col, mp_col)
    U_pre  = period_value_per_mp(Uten_NP, pre_start,  pre_end,  time_col, kwh_col, mp_col)
    U_post = period_value_per_mp(Uten_NP, post_start, post_end, time_col, kwh_col, mp_col)

    # Hvem er "T" (treated) i formelen?
    if treat_dataset == 'Med_NP':
        T_pre, T_post = M_pre, M_post
        C_pre, C_post = U_pre, U_post
    elif treat_dataset == 'Uten_NP':
        T_pre, T_post = U_pre, U_post
        C_pre, C_post = M_pre, M_post
    else:
        raise ValueError("treat_dataset må være 'Med_NP' eller 'Uten_NP'.")

    # Minus–minus DiD
    did = (T_post - T_pre) - (C_post - C_pre)

    # For tolkning kan det også være nyttig med prosent-endring relativt til T_pre
    pct_T = np.nan
    if pd.notna(T_pre) and T_pre != 0:
        pct_T = 100 * (T_post - T_pre) / T_pre

    results = {
        'M_pre_kWh_per_MP':  M_pre,
        'M_post_kWh_per_MP': M_post,
        'U_pre_kWh_per_MP':  U_pre,
        'U_post_kWh_per_MP': U_post,
        'T_pre_kWh_per_MP':  T_pre,
        'T_post_kWh_per_MP': T_post,
        'C_pre_kWh_per_MP':  C_pre,
        'C_post_kWh_per_MP': C_post,
        'DiD_kWh_per_MP':    did,
        'T_pct_change_%':    pct_T,
    }

    return results





print(did_simple(data_mNP_NO1, data_uNP_NO1, pre_start='2024-10-01', pre_end='2025-01-31', post_start='2025-10-01',
                 post_end='2026-01-31', treat_dataset='Med_NP', time_col='start_time_utc',
                 kwh_col='consumption_kwh', mp_col='metering_point_count'))


