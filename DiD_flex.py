from cProfile import label

import numpy as np
import pandas as pd
import statsmodels.api as sm
import patsy
from linearmodels.panel import PanelOLS
import matplotlib.pyplot as plt


data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')
data_rest_NO1 = pd.read_csv('All_Demand_Data/NO1_resten.csv', sep = ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')
data_rest_NO2 = pd.read_csv('All_Demand_Data/NO2_resten.csv', sep = ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')
data_rest_NO5 = pd.read_csv('All_Demand_Data/NO5_resten.csv', sep = ';')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')
Temp_Stavanger = pd.read_csv('Temp_Stavanger.csv')


def Difference_in_Difference_Flex(data_mNP, data_uNP, data_resten, Temp, price_area):

    # ----------- Norgespris gruppen -------------- #
    '''data_mNP['start_time_utc'] = pd.to_datetime(data_mNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)
    data_demand_NP = data_mNP[data_mNP['price_area'] == price_area].copy()

    data_demand_NP['kWh/Metering_point'] = data_demand_NP['consumption_kwh'] / data_demand_NP['metering_point_count']
    total_demand_NP= data_demand_NP.groupby(['Date', 'Hour', 'group_definition'])[ 'kWh/Metering_point'].sum().reset_index()

    total_demand_NP['Date'] = pd.to_datetime(total_demand_NP['Date'], errors='coerce')

    total_demand_NP['time'] = (
            total_demand_NP['Date'] +
            pd.to_timedelta(total_demand_NP['Hour'], unit='h')
    )

    total_demand_NP['time'] = total_demand_NP['time'].dt.tz_localize('UTC')

    #print(total_demand_NP)

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

    #print(total_demand_uNP)

    # ------------ Resten ------------- #
    data_resten['start_time_utc'] = pd.to_datetime(data_resten['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_resten['Date'] = data_resten['start_time_utc'].dt.date
    data_resten['Hour'] = data_resten['start_time_utc'].dt.hour.astype(int)
    data_demand_resten = data_resten[data_resten['price_area'] == price_area].copy()

    data_demand_resten['kWh/Metering_point'] = data_demand_resten['consumption_kwh'] / data_demand_resten['metering_point_count']
    total_demand_resten = data_demand_resten.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()

    total_demand_resten['Date'] = pd.to_datetime(total_demand_resten['Date'], errors='coerce')

    total_demand_resten['time'] = (
            total_demand_resten['Date'] +
            pd.to_timedelta(total_demand_resten['Hour'], unit='h')
    )

    total_demand_resten['time'] = total_demand_resten['time'].dt.tz_localize('UTC')

    #print(total_demand_resten)

    # ------------ Dataframe ----------- #
    df_NP = pd.DataFrame(total_demand_NP)
    df_uNP = pd.DataFrame(total_demand_uNP)
    df_resten = pd.DataFrame(total_demand_resten)

    df = pd.concat([df_NP,df_uNP,df_resten],ignore_index=True)
    df = df[df['kWh/Metering_point'] > 0].copy()

    start_date_before = pd.Timestamp('2024-11-01', tz=None)
    end_date_before = pd.Timestamp('2025-01-31', tz = None)

    start_date_after = pd.Timestamp('2025-11-01', tz = None)
    end_date_after = pd.Timestamp('2026-01-31', tz = None)

    reference = (df['Date'] >= start_date_before) & (df['Date'] <= end_date_before)
    treatment = (df['Date'] >= start_date_after) & (df['Date'] <= end_date_after)

    df['Period'] = np.select([reference, treatment],
                              ['Reference', 'Treatment'],
                              default = 'Rest')

    # --------- Model ------------ #

    df['entity'] = pd.Categorical(df['group_definition'],
                                  categories=['Uten Norgespris', 'Med Norgespris', 'Resten'],   # Referanse = Uten Norgespris
                                  ordered = True)
    df['period'] = pd.Categorical(df['Period'],
                                  categories = ['Reference', 'Treatment', 'Rest'],     # Reference = Reference
                                  ordered = True)

    df['log_y'] = np.log(df['kWh/Metering_point'])'''


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

    df_temp = Temp[['Date', 'Hour', 'Temp24']]
    #print(df_temp)

    # ------------ Dataframe ----------- #
    df_NP = pd.DataFrame(total_demand_NP)
    df_uNP = pd.DataFrame(total_demand_uNP)
    df_resten = pd.DataFrame(total_demand_resten)

    df = pd.concat([df_NP, df_uNP, df_resten], ignore_index=True)
    df = pd.merge(df, df_temp, on = ['Date', 'Hour'], how = 'left')

    df = df[df['kWh/Metering_point'] > 0].copy()
    #print(df)

    start_date_before = '2025-01-01'
    end_date_before = '2025-01-31'

    start_date_after = '2026-01-01'
    end_date_after = '2026-01-31'

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

    results = []
    results_temp = []
    for h in range(24):
        sub = df[df['Hour'] == h].copy()

        if sub.empty:
            results.append({
                'Hour': h,
                'DiD': np.nan,
                'CI_low': np.nan,
                'CI_high': np.nan
            })
            continue

        panel_df = sub.set_index(['entity', 'time'], drop = False)

        model = PanelOLS.from_formula(
        'log_y ~ 1 + C(entity)*C(period) + TimeEffects',
            data = panel_df,
            drop_absorbed=True
        )

        model_temp = PanelOLS.from_formula(
        'log_y ~ 1 + C(entity)*C(period) '
                '+  Temp24 + I(Temp24**2) + I(Temp24**3)'
                '+ C(entity):Temp24 '
                '+ C(entity):I(Temp24**2)'
                '+ C(entity):I(Temp24**3)'
                '+ TimeEffects',
            data = panel_df,
            drop_absorbed=True
        )

        res = model.fit(cov_type='clustered', cluster_time=True)
        #print(res)
        res_temp = model_temp.fit(cov_type='clustered', cluster_time=True)
        #print(res_temp)
        key = "C(entity)[T.Med Norgespris]:C(period)[T.Treatment]"
        key_temp = "C(entity)[T.Med Norgespris]:C(period)[T.Treatment]"

        if key not in res.params.index:
            results.append({
                'Hour': h,
                'DiD' : np.nan,
                'CI_low': np.nan,
                'CI_high': np.nan,
            })
            continue

        beta3 = res.params[key]
        ci_low, ci_high = res.conf_int().loc[key]
        DiD = (np.exp(beta3)-1)*100
        CI_low = (np.exp(ci_low)-1)*100
        CI_high = (np.exp(ci_high)-1)*100

        results.append({
            'Hour': h,
            'DiD': DiD,
            'CI_low': CI_low,
            'CI_high': CI_high
        })

        if key_temp not in res_temp.params.index:
            results_temp.append({
                'Hour': h,
                'DiD_temp' : np.nan,
                'CI_low_temp': np.nan,
                'CI_high_temp': np.nan,
            })
            continue

        beta3_temp = res_temp.params[key]
        ci_low_temp, ci_high_temp = res_temp.conf_int().loc[key]
        DiD_temp = (np.exp(beta3_temp)-1)*100
        CI_low_temp = (np.exp(ci_low_temp)-1)*100
        CI_high_temp = (np.exp(ci_high_temp)-1)*100

        results_temp.append({
            'Hour': h,
            'DiD_temp': DiD_temp,
            'CI_low_temp': CI_low_temp,
            'CI_high_temp': CI_high_temp
        })

    results_df = pd.DataFrame(results).sort_values('Hour').reset_index(drop=True)
    results_df_temp = pd.DataFrame(results_temp).sort_values('Hour').reset_index(drop=True)

    print('----------- DiD per time -----------------')
    for _, r in results_df.iterrows():
        if pd.isna(r['DiD']):
            print(f"Time {int(r['Hour']):02d}")
        else:
            print(
                f"Time {int(r['Hour']):02d}: DiD = {r['DiD']:.2f}%  | KI [{r['CI_low']:.2f}%, {r['CI_high']:.2f}%]")

    for _, r in results_df_temp.iterrows():
        if pd.isna(r['DiD_temp']):
            print(f"Time {int(r['Hour']):02d}")
        else:
            print(
                f"Time {int(r['Hour']):02d}: DiD = {r['DiD_temp']:.2f}%  | KI [{r['CI_low_temp']:.2f}%, {r['CI_high_temp']:.2f}%]")

    return results_df, results_df_temp

    # --------- PLOTT DØGNPROFIL ---------- #
def plot_dognprofil(results_df_NO1, results_df_NO1_temp,
                    results_df_NO2, results_df_NO2_temp,
                    results_df_NO5, results_df_NO5_temp):
    # ---------- NO1 ---------- #
    hours_NO1 = results_df_NO1['Hour']
    DiD_NO1 = results_df_NO1['DiD']
    DiD_NO1_temp = results_df_NO1_temp['DiD_temp']
    ci_low_temp_NO1 = results_df_NO1_temp['CI_low_temp']
    ci_high_temp_NO1 = results_df_NO1_temp['CI_high_temp']

    # ---------- NO2 ---------- #
    hours_NO2 = results_df_NO2['Hour']
    DiD_NO2 = results_df_NO2['DiD']
    DiD_NO2_temp = results_df_NO2_temp['DiD_temp']
    ci_low_temp_NO2 = results_df_NO2_temp['CI_low_temp']
    ci_high_temp_NO2 = results_df_NO2_temp['CI_high_temp']

    # ---------- NO1 ---------- #
    hours_NO5 = results_df_NO5['Hour']
    DiD_NO5 = results_df_NO5['DiD']
    DiD_NO5_temp = results_df_NO5_temp['DiD_temp']
    ci_low_temp_NO5 = results_df_NO5_temp['CI_low_temp']
    ci_high_temp_NO5 = results_df_NO5_temp['CI_high_temp']

    plt.figure(figsize=(12, 6))

    plt.plot(hours_NO1, DiD_NO1, label='DiD - NO1', color='royalblue', linewidth=2, linestyle = 'dotted')
    plt.plot(hours_NO1, DiD_NO1_temp, label='DiD w/Temp- NO1', color='royalblue', linewidth=2)
    plt.fill_between(hours_NO1, ci_low_temp_NO1, ci_high_temp_NO1, color = 'royalblue', alpha=0.1)
    plt.plot(hours_NO2, DiD_NO2, label='DiD - NO2', color='red', linewidth=2, linestyle = 'dotted')
    plt.plot(hours_NO2, DiD_NO2_temp, label='DiD w/Temp- NO2', color='red', linewidth=2)
    plt.fill_between(hours_NO2, ci_low_temp_NO2, ci_high_temp_NO2, color='red', alpha=0.1)
    plt.plot(hours_NO5, DiD_NO5, label='DiD - NO5', color='green', linewidth=2, linestyle = 'dotted')
    plt.plot(hours_NO5, DiD_NO5_temp, label='DiD w/Temp- NO5', color='green', linewidth=2)
    plt.fill_between(hours_NO5, ci_low_temp_NO5, ci_high_temp_NO5, color='green', alpha=0.1)


    plt.xticks(range(0, 24))
    plt.xlabel("Hour", fontsize=25)
    plt.ylabel("Difference in Difference of Consumption Changes [%]", fontsize=20)
    #plt.title(f"Daily Profile for the DiD Estimate for NO1, NO2, and NO5", fontsize=20)
    plt.grid(alpha=0.3)
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    plt.legend(fontsize=20)
    plt.tight_layout()
    plt.show()






results_NO1, results_NO1_temp = Difference_in_Difference_Flex(data_mNP_NO1, data_uNP_NO1, data_rest_NO1, Temp_Oslo, 'NO1')
results_NO2, results_NO2_temp = Difference_in_Difference_Flex(data_mNP_NO2, data_uNP_NO2, data_rest_NO2, Temp_Stavanger, 'NO2')
results_NO5, results_NO5_temp = Difference_in_Difference_Flex(data_mNP_NO5, data_uNP_NO5, data_rest_NO5, Temp_Bergen, 'NO5')
plot_dognprofil(results_NO1, results_NO1_temp,
                results_NO2, results_NO2_temp,
                results_NO5, results_NO5_temp)

