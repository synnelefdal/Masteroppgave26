


import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm


data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')
Temp_Stavanger = pd.read_csv('Temp_Stavanger.csv')


start_date_before = '2024-11-01'
end_date_before   = '2025-01-31'
start_date_after  = '2025-11-01'
end_date_after    = '2026-01-31'

# ============================================================
# 4) Funksjonen (ingen price_area-parameter, hour er valgfri)
# ============================================================
def DifferenceinDifference(data_mNP, data_uNP, hour=None):
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
        '+ C(Hour, Treatment(reference="1") ) + C(Month, Treatment(reference = "November"))'
    )
    y, X = patsy.dmatrices(
        formula, data=df, return_type="dataframe", NA_action="drop"
    )
    model = sm.OLS(y, X).fit()
    print(model.summary())

    beta3 = model.params[
        'C(Group, Treatment(reference="Before_ref"))[T.After_ref]:C(Norgespris, Treatment(reference="Uten_NP"))[T.Med_NP]']
    DiD = (np.exp(beta3) - 1) * 100

    ci_low, ci_high = model.conf_int().loc[
        'C(Group, Treatment(reference="Before_ref"))[T.After_ref]:C(Norgespris, Treatment(reference="Uten_NP"))[T.Med_NP]']
    DiD_low = (np.exp(ci_low) - 1) * 100
    DiD_high = (np.exp(ci_high) - 1) * 100

    print(f'DiD prosent for: {DiD:.2f}%')
    print(f'KI: [{DiD_low:.2f}%, {DiD_high:.2f}%]')

    return model, df


#DifferenceinDifference(data_mNP, data_uNP,hour=[7,8,9,10,16,17,18,19,20])


def DifferenceinDifferenceFlex(data_mNP, data_uNP, price_area, selected_hours = None):
    # ------------------- Filterer for dato ---------- #
    start_date_before = '2025-01-01'
    end_date_before = '2025-01-31'

    start_date_after = '2026-01-01'
    end_date_after = '2026-01-31'

    # ----------- Endring til Date og Hour ------------ #
    data_mNP['start_time_utc'] = pd.to_datetime(data_mNP['start_time_utc'],
                                                format = '%Y-%m-%d %H:%M:%S',
                                                errors = 'coerce',
                                                utc = True)

    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)

    data_uNP['start_time_utc'] = pd.to_datetime(data_uNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_uNP['Date'] = data_uNP['start_time_utc'].dt.date
    data_uNP['Hour'] = data_uNP['start_time_utc'].dt.hour.astype(int)

    # ----------------- Demand; NP-Gruppen ------------------ #

    data_demand_NP = data_mNP[data_mNP['price_area'] == price_area].copy()
    data_demand_NP['Date'] = pd.to_datetime(data_demand_NP['Date'])
    data_demand_NP['Hour'] = data_demand_NP['Hour'].astype(int)

    data_demand_NP_filtered_before = data_demand_NP[(data_demand_NP['Date'] >= start_date_before) &
                                        (data_demand_NP['Date'] <= end_date_before)].copy()

    data_demand_NP_filtered_after = data_demand_NP[(data_demand_NP['Date'] >= start_date_after) &
                                        (data_demand_NP['Date'] <= end_date_after)].copy()
    #print(data_demand_NP_filtered_before)
    #print(data_demand_NP_filtered_after)

    data_demand_NP_filtered_before['kWh/Metering_point'] = data_demand_NP_filtered_before['consumption_kwh'] / data_demand_NP_filtered_before['metering_point_count']
    #print(data_demand_NP_filtered_before.head(3))

    data_demand_NP_filtered_after['kWh/Metering_point'] = data_demand_NP_filtered_after['consumption_kwh'] / data_demand_NP_filtered_after['metering_point_count']
    #print(data_demand_NP_filtered_after.head(3))

    total_demand_hour_NP_before = data_demand_NP_filtered_before.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_NP_after = data_demand_NP_filtered_after.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    #print(total_demand_hour_NP_before)
    #print(total_demand_hour_NP_after)

    # ----------------- Demand; Uten NP-Gruppen ------------------ #

    data_demand_UtenNP = data_uNP[data_uNP['price_area'] == price_area].copy()
    data_demand_UtenNP['Date'] = pd.to_datetime(data_demand_UtenNP['Date'])
    data_demand_UtenNP['Hour'] = data_demand_UtenNP['Hour'].astype(int)

    data_demand_UtenNP_filtered_before = data_demand_UtenNP[(data_demand_UtenNP['Date'] >= start_date_before) &
                                        (data_demand_UtenNP['Date'] <= end_date_before)].copy()

    data_demand_UtenNP_filtered_after = data_demand_UtenNP[(data_demand_UtenNP['Date'] >= start_date_after) &
                                        (data_demand_UtenNP['Date'] <= end_date_after)].copy()
    #print(data_demand_filtered1)
    #print(data_demand_filtered2)


    data_demand_UtenNP_filtered_before['kWh/Metering_point'] = data_demand_UtenNP_filtered_before['consumption_kwh'] / data_demand_UtenNP_filtered_before['metering_point_count']
    #print(data_demand_UtenNP_filtered_before.head(3))

    data_demand_UtenNP_filtered_after['kWh/Metering_point'] = data_demand_UtenNP_filtered_after['consumption_kwh'] / data_demand_UtenNP_filtered_after['metering_point_count']
    #print(data_demand_UtenNP_filtered_after.head(3))

    total_demand_hour_UtenNP_before = data_demand_UtenNP_filtered_before.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_UtenNP_after = data_demand_UtenNP_filtered_after.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()

    #print(total_demand_hour_UtenNP_before)
    #print(total_demand_hour_UtenNP_after)

    # -------- Merge data; NP-Gruppen u/Temp ----------- #
    df_NP_before = pd.DataFrame(total_demand_hour_NP_before)
    df_NP_after = pd.DataFrame(total_demand_hour_NP_after)

    df_NP = pd.concat([df_NP_before,df_NP_after], ignore_index=True)

    pd.set_option('display.max_columns', None)
    #print(df_NP)

    # ------------ Merge data; Uten NP-gruppen u/Temp----------- #
    df_UtenNP_before = pd.DataFrame(total_demand_hour_UtenNP_before)
    df_UtenNP_after = pd.DataFrame(total_demand_hour_UtenNP_after)

    df_UtenNP = pd.concat([df_UtenNP_before, df_UtenNP_after], ignore_index=True)

    pd.set_option('display.max_columns', None)
    #print(df_UtenNP)

    # ----------------- Beregninger; NP-Gruppen ------------------- #
    df_NP['Date'] = pd.to_datetime(df_NP['Date'])
    df_NP['Month'] = df_NP['Date'].dt.strftime('%B')

    df_NP['Hour'] = pd.Categorical(df_NP['Hour'].astype(str),
                                 categories=[str(i) for i in range(1, 25)], ordered=True)
    df_NP['Month'] = pd.Categorical(df_NP['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)

    # ----------------- Beregninger; Uten NP-Gruppen ------------------- #
    df_UtenNP['Date'] = pd.to_datetime(df_UtenNP['Date'])
    df_UtenNP['Month'] = df_UtenNP['Date'].dt.strftime('%B')

    df_UtenNP['Hour'] = pd.Categorical(df_UtenNP['Hour'].astype(str),
                                 categories=[str(i) for i in range(1, 25)], ordered=True)
    df_UtenNP['Month'] = pd.Categorical(df_UtenNP['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)


    # --------------- Regresjonsanalyse ------------- #
    #df_NP['Group'] = 'Norgespris'  # 2024-periode
    #df_UtenNP['Group'] = 'Uten Norgespris'  # 2025-periode

    df_NP['Norgespris'] = 'Med_NP'  #Treatment
    df_UtenNP['Norgespris'] = 'Uten_NP'  #Treatment

    df_NP["price_area"] = price_area
    df_UtenNP["price_area"] = price_area

    df = pd.concat([df_NP, df_UtenNP], ignore_index=True)

    df = df[df['kWh/Metering_point'] > 0].copy()

    # ----------- Valgte timer ------------ #
    if selected_hours is not None:
        selected_hours = [str(h) for h in selected_hours]
        df = df[df['Hour'].astype(str).isin(selected_hours)]

    cutoff = pd.Timestamp('2025-10-01')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Group'] = np.where(df['Date'] < cutoff, 'Before_ref', 'After_ref')   #Post

    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month'] = pd.Categorical(df['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)

    df['Hour'] = pd.Categorical(df['Hour'].astype(str),
                                 categories=[str(i) for i in range(0, 23+1)], ordered=True)


    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.max_rows', None)
    #print(df[['Date', 'Norgespris','Group']])
    #print(df)

    formula = (
        'np.log(Q("kWh/Metering_point")) ~ '
        'C(Group, Treatment(reference="Before_ref")) '
        '* C(Norgespris, Treatment(reference="Uten_NP")) '
        '+ C(Hour, Treatment(reference="1") ) + C(Month, Treatment(reference = "November"))'
    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())

    beta3 = model.params['C(Group, Treatment(reference="Before_ref"))[T.After_ref]:C(Norgespris, Treatment(reference="Uten_NP"))[T.Med_NP]']
    DiD = (np.exp(beta3) - 1)*100

    ci_low, ci_high = model.conf_int().loc['C(Group, Treatment(reference="Before_ref"))[T.After_ref]:C(Norgespris, Treatment(reference="Uten_NP"))[T.Med_NP]']
    DiD_low = (np.exp(ci_low) - 1)*100
    DiD_high = (np.exp(ci_high) - 1)*100

    print(f'DiD prosent for {price_area}: {DiD:.2f}%')
    print(f'KI: [{DiD_low:.2f}%, {DiD_high:.2f}%]')

DifferenceinDifferenceFlex(data_mNP_NO1, data_uNP_NO1, 'NO1',[7,8,9,17,18,19,20] )
DifferenceinDifferenceFlex(data_mNP_NO2, data_uNP_NO2, 'NO2',[7,8,9,17,18,19,20] )
DifferenceinDifferenceFlex(data_mNP_NO5, data_uNP_NO5, 'NO5',[7,8,9,17,18,19,20] )