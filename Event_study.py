import numpy as np
import pandas as pd
import statsmodels.api as sm
import patsy
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from linearmodels.panel.utility import AbsorbingEffectWarning
from matplotlib.patches import FancyArrowPatch
from linearmodels.panel import PanelOLS

from sklearn.linear_model import LinearRegression



data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO1 = pd.read_csv('All_Demand_Data/NO1_resten.csv', skiprows= [1, 2, 3], sep =';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO2 = pd.read_csv('All_Demand_Data/NO2_resten.csv', skiprows= [1, 2, 3], sep =';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO5 = pd.read_csv('All_Demand_Data/NO5_resten.csv', skiprows= [1, 2, 3], sep =';')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')
Temp_Stavanger = pd.read_csv('Temp_Stavanger.csv')

# ------------------------------- MODELL 2 M/TEMP ------------------------------- #


def Difference_in_Difference_temp(data_mNP, data_uNP, data_resten, price_area, Temp):

    # ----------- Norgespris gruppen -------------- #
    data_mNP['start_time_utc'] = pd.to_datetime(data_mNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)
    data_demand_NP = data_mNP[data_mNP['price_area'] == price_area].copy()

    data_demand_NP['kWh/Metering_point'] = data_demand_NP['consumption_kwh'] / data_demand_NP['metering_point_count']
    total_demand_NP = data_demand_NP.groupby(['Date', 'Hour', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()

    total_demand_NP['Date'] = pd.to_datetime(total_demand_NP['Date'], errors='coerce')

    total_demand_NP['time'] = (
            total_demand_NP['Date'] +
            pd.to_timedelta(total_demand_NP['Hour'], unit='h')
    )

    total_demand_NP['time'] = total_demand_NP['time'].dt.tz_localize('UTC')

    # print(total_demand_NP)

    # -------------- Ikke Norgespris gruppen ---------- #
    data_uNP['start_time_utc'] = pd.to_datetime(data_uNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_uNP['Date'] = data_uNP['start_time_utc'].dt.date
    data_uNP['Hour'] = data_uNP['start_time_utc'].dt.hour.astype(int)
    data_demand_uNP = data_uNP[data_uNP['price_area'] == price_area].copy()

    data_demand_uNP['kWh/Metering_point'] = data_demand_uNP['consumption_kwh'] / data_demand_uNP['metering_point_count']
    total_demand_uNP = data_demand_uNP.groupby(['Date', 'Hour', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()

    total_demand_uNP['Date'] = pd.to_datetime(total_demand_uNP['Date'], errors='coerce')

    total_demand_uNP['time'] = (
            total_demand_uNP['Date'] +
            pd.to_timedelta(total_demand_uNP['Hour'], unit='h')
    )

    total_demand_uNP['time'] = total_demand_uNP['time'].dt.tz_localize('UTC')

    # print(total_demand_uNP)

    # ------------ Resten ------------- #
    data_resten['start_time_utc'] = pd.to_datetime(data_resten['start_time_utc'],
                                                   format='%Y-%m-%d %H:%M:%S',
                                                   errors='coerce',
                                                   utc=True)

    data_resten['Date'] = data_resten['start_time_utc'].dt.date
    data_resten['Hour'] = data_resten['start_time_utc'].dt.hour.astype(int)
    data_demand_resten = data_resten[data_resten['price_area'] == price_area].copy()

    data_demand_resten['kWh/Metering_point'] = data_demand_resten['consumption_kwh'] / data_demand_resten[
        'metering_point_count']
    total_demand_resten = data_demand_resten.groupby(['Date', 'Hour', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()

    total_demand_resten['Date'] = pd.to_datetime(total_demand_resten['Date'], errors='coerce')

    total_demand_resten['time'] = (
            total_demand_resten['Date'] +
            pd.to_timedelta(total_demand_resten['Hour'], unit='h')
    )

    total_demand_resten['time'] = total_demand_resten['time'].dt.tz_localize('UTC')

    # print(total_demand_resten)

    # ------------ Temperatur -------------- #
    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(float)
    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(window=24, min_periods=1).mean()
    #Temp['Temp24^2'] = Temp['Temp24'] **2
    #Temp['Temp24^3'] = Temp['Temp24'] ** 3

    df_temp = Temp[['Date', 'Hour', 'Lufttemperatur','Temp24']]
    #print(df_temp)

    # ------------ Dataframe ----------- #
    df_NP = pd.DataFrame(total_demand_NP)
    df_uNP = pd.DataFrame(total_demand_uNP)
    df_resten = pd.DataFrame(total_demand_resten)

    df = pd.concat([df_NP, df_uNP, df_resten], ignore_index=True)
    df = pd.merge(df, df_temp, on = ['Date', 'Hour'], how = 'left')

    df = df[df['kWh/Metering_point'] > 0].copy()
    #print(df.columns)

    start_date_before = '2024-10-01'
    end_date_before = '2024-10-31'

    start_date_after = '2024-11-01'
    end_date_after = '2025-09-30'

    before_ref = (df['Date'] >= start_date_before) & (df['Date'] <= end_date_before)
    after_ref = (df['Date'] >= start_date_after) & (df['Date'] <= end_date_after)

    df['Period'] = np.select([before_ref, after_ref],
                              ['Reference', 'Treatment'],
                              default='Rest')

    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month'] = pd.Categorical(df['Month'],
                                 categories=['January', 'February', 'March', 'April', 'May', 'June',
                                             'July', 'August', 'September', 'October', 'November', 'December'],
                                 ordered=True)

    # --------- Model ------------ #
    df['entity'] = pd.Categorical(df['group_definition'],
                                  categories=['Uten Norgespris', 'Med Norgespris', 'Resten'],
                                  # Referanse = Uten Norgespris
                                  ordered=True)
    df['period'] = pd.Categorical(df['Period'],
                                  categories=['Reference', 'Treatment', 'Rest'],  # Reference = Reference
                                  ordered=True)
    df['log_y'] = np.log(df['kWh/Metering_point'])
    panel_df = df.set_index(['entity', 'time'], drop=False).sort_index()

    model = PanelOLS.from_formula(
        'log_y ~ 1 + C(entity, Treatment(reference="Uten Norgespris"))*C(period) '
                '+  Temp24 + I(Temp24**2) + I(Temp24**3)'
                '+ C(entity, Treatment(reference="Uten Norgespris")):Temp24 '
                '+ C(entity, Treatment(reference="Uten Norgespris")):I(Temp24**2) '
                '+ C(entity, Treatment(reference="Uten Norgespris")):I(Temp24**3) '
                '+ TimeEffects',
        data=panel_df,
        drop_absorbed=True
    )

    res = model.fit(cov_type='clustered', cluster_time=True)

    print(res)

    # -------- Utregning --------- #
    print('----------- PanelOLS -----------------')
    beta3 = res.params["C(entity, Treatment(reference='Uten Norgespris'))[T.Med Norgespris]:C(period)[T.Treatment]"]
    DiD = (np.exp(beta3) - 1) * 100

    ci_low, ci_high = res.conf_int().loc["C(entity, Treatment(reference='Uten Norgespris'))[T.Med Norgespris]:C(period)[T.Treatment]"]
    DiD_low = (np.exp(ci_low) - 1) * 100
    DiD_high = (np.exp(ci_high) - 1) * 100

    print(f'DiD prosent for {price_area}: {DiD:.2f}%')
    print(f'KI: [{DiD_low:.2f}%, {DiD_high:.2f}%]')

    # -------- Figur ---------- #
    #df_before = df[df['Period'] == 'Reference'].copy()
    '''df_plot = df[df['Period'].isin(['Reference', 'Rest'])].copy()
    df_plot = df_plot[df_plot['entity'].isin(['Uten Norgespris', 'Med Norgespris'])]

    remove_oct = (df_plot['Date'] >= pd.to_datetime('2025-10-01')) & \
                      (df_plot['Date'] <= pd.to_datetime('2025-10-31'))

    df_plot = df_plot[~remove_oct]

    df_plot = df_plot.dropna(subset=['Temp24'])
    group_means = df_plot.groupby('entity')['kWh/Metering_point'].mean()

    df_plot['rel_consumption'] = df_plot.apply(
        lambda r: r['kWh/Metering_point'] / group_means.loc[r['entity']],
        axis=1
    )

    # Plot
    plt.figure(figsize=(9, 6))

    colors = {
        'Uten Norgespris': '#1f77b4',
        'Med Norgespris': '#d62728'
    }
    df_plot['entity'] = df_plot['entity'].cat.remove_unused_categories()
    df_plot['temp_bin'] = (df_plot['Temp24'] / 0.5).round() * 0.5

    for grp, sub in df_plot.groupby('entity'):
        trend = sub.groupby('temp_bin')['rel_consumption'].mean().reset_index()
        trend = trend.sort_values('temp_bin')
        plt.plot(
            trend['temp_bin'], trend['rel_consumption'],
            color=colors.get(grp, 'gray'), linewidth=2,
            label=f'{grp}'
        )

    plt.axhline(1.0, linestyle='--', color='gray', alpha=0.7)
    plt.xlabel('Temperatur [°C]')
    plt.ylabel('Gjennomsnits forbruk [kWh/målepunkt]')
    plt.title(f'Temperaturfølsomhet før Norgespris – {price_area}')
    plt.grid(True, alpha=0.25)
    plt.legend()

    plt.tight_layout()
    plt.show()'''

    return panel_df


#data_NO1 = Difference_in_Difference_temp(data_mNP_NO1,data_uNP_NO1,data_rest_NO1,'NO1',Temp_Oslo)
#data_NO2 = Difference_in_Difference_temp(data_mNP_NO2,data_uNP_NO2,data_rest_NO2,'NO2',Temp_Stavanger)
#data_NO5 = Difference_in_Difference_temp(data_mNP_NO5,data_uNP_NO5,data_rest_NO5,'NO5',Temp_Bergen)


def Difference_in_Difference_pretrend(data_mNP, data_uNP, data_rest, price_area, Temp):

    # ===============================
    # 1. DATAKLARGJØRING (UENDRET)
    # ===============================

    for df in [data_mNP, data_uNP, data_rest]:
        df['start_time_utc'] = pd.to_datetime(
            df['start_time_utc'],
            format='%Y-%m-%d %H:%M:%S',
            errors='coerce',
            utc=True
        )
        df['Date'] = df['start_time_utc'].dt.date
        df['Hour'] = df['start_time_utc'].dt.hour.astype(int)

    def prep_group(data):
        d = data[data['price_area'] == price_area].copy()
        d['kWh/Metering_point'] = d['consumption_kwh'] / d['metering_point_count']
        g = d.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
        g['Date'] = pd.to_datetime(g['Date'])
        g['time'] = (g['Date'] + pd.to_timedelta(g['Hour'], unit='h')).dt.tz_localize('UTC')
        return g

    df_NP = prep_group(data_mNP)
    df_uNP = prep_group(data_uNP)
    df_resten = prep_group(data_rest)

    df = pd.concat([df_NP, df_uNP, df_resten], ignore_index=True)

    #print(df)

    # ===============================
    # 2. TEMPERATUR (UENDRET)
    # ===============================

    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(float)
    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(window=24, min_periods=1).mean()

    df = pd.merge(
        df,
        Temp[['Date', 'Hour', 'Temp24']],
        on=['Date', 'Hour'],
        how='left'
    )

    df = df[df['kWh/Metering_point'] > 0].copy()
    df['log_y'] = np.log(df['kWh/Metering_point'])

    #print(df)

    # ======================================================
    # 3. >>> NYTT <<< TIDSAVGRENSNING: KUN PRE-NORGESPRIS
    # ======================================================

    df = df[
        (df['Date'] >= '2024-10-01') &
        (df['Date'] <= '2025-09-30')
    ].copy()

    #print(df.columns)
    #print(df)

    # ======================================================
    # 4. >>> NYTT <<< EVENT-TIME (TIMER SIDEN OKTOBER 2024)
    # ======================================================

    df['october'] = (
            (df['Date'] >= '2024-10-01') &
            (df['Date'] <= '2024-10-31')
    )

    post_ref_time = pd.Timestamp('2024-11-01 00:00:00', tz='UTC')

    df['event_time'] = np.where(
        df['time'] >= post_ref_time,
        ((df['time'] - post_ref_time).dt.total_seconds() / 3600).astype(int),
        np.nan
    )


    #print(df.columns)
    #print(df)

    # ======================================================
    # 5. PANELSTRUKTUR (LITEN ENDRET)
    # ======================================================
    df = df[df['event_time'].notna()].copy()

    df = df[df['group_definition'].isin(
        ['Uten Norgespris', 'Med Norgespris']
    )].copy()

    df['entity'] = pd.Categorical(
        df['group_definition'],
        categories=['Uten Norgespris', 'Med Norgespris'],
        ordered=True
    )

    df['event_time_cat'] = pd.Categorical(df['event_time'])

    panel_df = df.set_index(['entity', 'time'], drop=False).sort_index()
    #print(panel_df)

    # ======================================================
    # 6. >>> NYTT <<< EVENT-STUDY / PRE-TREND MODELL
    # ======================================================

    model = PanelOLS.from_formula(
        'log_y ~ 1 + C(entity, Treatment(reference="Uten Norgespris")):C(event_time_cat) '
        '+ Temp24 + I(Temp24**2) + I(Temp24**3)'
        '+ C(entity, Treatment(reference="Uten Norgespris")):Temp24 '
        '+ C(entity, Treatment(reference="Uten Norgespris")):I(Temp24**2) '
        '+ C(entity, Treatment(reference="Uten Norgespris")):I(Temp24**3) ',
        data=panel_df,
        drop_absorbed=True
    )

    res = model.fit(cov_type='clustered', cluster_time=True)

    print(res)

    # ======================================================
    # 7. >>> NYTT <<< HENT UT ~8000 PRE-ESTIMATER
    # ======================================================

    ci = res.conf_int()
    results = []

    for name, beta in res.params.items():
        if "Med Norgespris" in name and "event_time_cat" in name:
            hour = int(name.split(']')[-2].split('[')[-1])
            results.append({
                'event_time': hour,
                'beta': beta,
                'low': ci.loc[name][0],
                'high': ci.loc[name][1]
            })

    df_event = pd.DataFrame(results).sort_values('event_time')

    df_event['effect_pct'] = (np.exp(df_event['beta']) - 1) * 100
    df_event['low_pct'] = (np.exp(df_event['low']) - 1) * 100
    df_event['high_pct'] = (np.exp(df_event['high']) - 1) * 100

    return df_event

def plot(df_event):

    plt.figure(figsize=(12, 6))

    plt.plot(df_event['event_time'], df_event['effect_pct'], label='Estimert forskjell')
    plt.fill_between(
        df_event['event_time'],
        df_event['low_pct'],
        df_event['high_pct'],
        alpha=0.3
    )

    plt.axhline(0, linestyle='--', color='black')
    plt.axvline(0, linestyle=':', color='red', label='Referansemåned')

    plt.xlabel('Timer siden oktober 2024')
    plt.ylabel('Forskjell i forbruk (%)')
    plt.title('Pre-trend / event study før Norgespris')
    plt.legend()
    plt.tight_layout()
    plt.show()


result_NO1 = Difference_in_Difference_pretrend(data_mNP_NO1, data_uNP_NO1, data_rest_NO1, 'NO1', Temp_Oslo)
result_NO2 = Difference_in_Difference_pretrend(data_mNP_NO2, data_uNP_NO2, data_rest_NO2, 'NO2', Temp_Stavanger)
result_NO5 = Difference_in_Difference_pretrend(data_mNP_NO5, data_uNP_NO5, data_rest_NO5, 'NO5', Temp_Bergen)

plot(result_NO1)
plot(result_NO2)
plot(result_NO5)
