import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
import matplotlib.pyplot as plt
import time

start = time.time()



# -------------------------------- ALLE CSV FILER MED FORBRUKSDATA -------------------------------- #

data_NO1_uNP = pd.read_csv('NY_All_Demand_Data/NO1_uNP.csv', sep= ';')
data_NO1_NPoct = pd.read_csv('NY_All_Demand_Data/NO1_NP_oct.csv', sep= ';')
data_NO1_NPnov = pd.read_csv('NY_All_Demand_Data/NO1_NP_nov.csv', sep= ';')
data_NO1_NPdec = pd.read_csv('NY_All_Demand_Data/NO1_NP_dec.csv', sep= ';')
data_NO1_NPjan = pd.read_csv('NY_All_Demand_Data/NO1_NP_jan.csv', sep= ';')
data_NO1_NPfeb = pd.read_csv('NY_All_Demand_Data/NO1_NP_feb.csv', sep= ';')
data_NO1_NPmars = pd.read_csv('NY_All_Demand_Data/NO1_NP_mars.csv', sep= ';')
data_NO1_NPapril = pd.read_csv('NY_All_Demand_Data/NO1_NP_april.csv', sep= ';')


data_NO2_uNP = pd.read_csv('NY_All_Demand_Data/NO2_uNP.csv', sep= ';')
data_NO2_NPoct = pd.read_csv('NY_All_Demand_Data/NO2_NP_oct.csv', sep= ';')
data_NO2_NPnov = pd.read_csv('NY_All_Demand_Data/NO2_NP_nov.csv', sep= ';')
data_NO2_NPdec = pd.read_csv('NY_All_Demand_Data/NO2_NP_dec.csv', sep= ';')
data_NO2_NPjan = pd.read_csv('NY_All_Demand_Data/NO2_NP_jan.csv', sep= ';')
data_NO2_NPfeb = pd.read_csv('NY_All_Demand_Data/NO2_NP_feb.csv', sep= ';')
data_NO2_NPmars = pd.read_csv('NY_All_Demand_Data/NO2_NP_mars.csv', sep= ';')
data_NO2_NPapril = pd.read_csv('NY_All_Demand_Data/NO2_NP_april.csv', sep= ';')


data_NO5_uNP = pd.read_csv('NY_All_Demand_Data/NO5_uNP.csv', sep= ';')
data_NO5_NPoct = pd.read_csv('NY_All_Demand_Data/NO5_NP_oct.csv', sep= ';')
data_NO5_NPnov = pd.read_csv('NY_All_Demand_Data/NO5_NP_nov.csv', sep= ';')
data_NO5_NPdec = pd.read_csv('NY_All_Demand_Data/NO5_NP_dec.csv', sep= ';')
data_NO5_NPjan = pd.read_csv('NY_All_Demand_Data/NO5_NP_jan.csv', sep= ';')
data_NO5_NPfeb = pd.read_csv('NY_All_Demand_Data/NO5_NP_feb.csv', sep= ';')
data_NO5_NPmars = pd.read_csv('NY_All_Demand_Data/NO5_NP_mars.csv', sep= ';')
data_NO5_NPapril = pd.read_csv('NY_All_Demand_Data/NO5_NP_april.csv', sep= ';')


# -------------------------------- Temperatur data for alle prissoner -------------------------------- #

Temp_Bergen = pd.read_csv('Temperature_Files/bergen_converted.csv')
Temp_Oslo = pd.read_csv('Temperature_Files/oslo_converted.csv')
Temp_Stavanger = pd.read_csv('Temperature_Files/stavanger_converted.csv')

# -------------------------------- START PÅ KODE, DONT TOUCH -------------------------------- #

def Difference_in_Difference_Flex(data_mNP, data_uNP, data_resten, Temp, price_area, start_date_before, end_date_before, start_date_after, end_date_after):

    # -------------- Norgespris gruppen -------------- #
    data_mNP['start_time_utc'] = pd.to_datetime(data_mNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)
    data_mNP['group_definition'] = "Med Norgespris"
    data_demand_NP = data_mNP[data_mNP['price_area'] == price_area].copy()

    #print(data_mNP)

    data_demand_NP['kWh/Metering_point'] = data_demand_NP['consumption_kwh'] / data_demand_NP['metering_point_count']


    total_demand_NP = data_demand_NP.groupby(['Date', 'Hour', 'norgespris_group', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()


    #print(total_demand_NP)

    total_demand_NP['Date'] = pd.to_datetime(total_demand_NP['Date'], errors='coerce')

    total_demand_NP['time'] = (
            total_demand_NP['Date'] +
            pd.to_timedelta(total_demand_NP['Hour'], unit='h')
    )

    total_demand_NP['time'] = total_demand_NP['time'].dt.tz_localize('UTC')

    # print(total_demand_NP)

    # -------------- Ikke Norgespris gruppen -------------- #
    data_uNP['start_time_utc'] = pd.to_datetime(data_uNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_uNP['Date'] = data_uNP['start_time_utc'].dt.date
    data_uNP['Hour'] = data_uNP['start_time_utc'].dt.hour.astype(int)
    data_uNP['group_definition'] = "Uten Norgespris"
    data_demand_uNP = data_uNP[data_uNP['price_area'] == price_area].copy()

    data_demand_uNP['kWh/Metering_point'] = data_demand_uNP['consumption_kwh'] / data_demand_uNP['metering_point_count']
    total_demand_uNP = data_demand_uNP.groupby(['Date', 'Hour', 'norgespris_group', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()

    total_demand_uNP['Date'] = pd.to_datetime(total_demand_uNP['Date'], errors='coerce')

    total_demand_uNP['time'] = (
            total_demand_uNP['Date'] +
            pd.to_timedelta(total_demand_uNP['Hour'], unit='h')
    )

    total_demand_uNP['time'] = total_demand_uNP['time'].dt.tz_localize('UTC')

    # print(total_demand_uNP)

    # -------------- Resten -------------- #
    data_resten['start_time_utc'] = pd.to_datetime(data_resten['start_time_utc'],
                                                   format='%Y-%m-%d %H:%M:%S',
                                                   errors='coerce',
                                                   utc=True)

    data_resten['Date'] = data_resten['start_time_utc'].dt.date
    data_resten['Hour'] = data_resten['start_time_utc'].dt.hour.astype(int)
    data_resten['group_definition'] = "Resten"
    data_demand_resten = data_resten[data_resten['price_area'] == price_area].copy()

    data_demand_resten['kWh/Metering_point'] = data_demand_resten['consumption_kwh'] / data_demand_resten[
        'metering_point_count']
    total_demand_resten = data_demand_resten.groupby(['Date', 'Hour', 'norgespris_group', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()

    total_demand_resten['Date'] = pd.to_datetime(total_demand_resten['Date'], errors='coerce')

    total_demand_resten['time'] = (
            total_demand_resten['Date'] +
            pd.to_timedelta(total_demand_resten['Hour'], unit='h')
    )

    total_demand_resten['time'] = total_demand_resten['time'].dt.tz_localize('UTC')

    # print(total_demand_resten)

    # -------------- Temperatur -------------- #
    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(float)
    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(window=24, min_periods=1).mean()
    #Temp['Temp24^2'] = Temp['Temp24'] **2
    #Temp['Temp24^3'] = Temp['Temp24'] ** 3

    df_temp = Temp[['Date', 'Hour', 'Temp24']]
    #print(df_temp)

    # -------------- Dataframe -------------- #
    df_NP = pd.DataFrame(total_demand_NP)
    df_uNP = pd.DataFrame(total_demand_uNP)
    df_resten = pd.DataFrame(total_demand_resten)

    #print(df_uNP)

    df = pd.concat([df_NP, df_uNP, df_resten], ignore_index=True)
    df = pd.merge(df, df_temp, on = ['Date', 'Hour'], how = 'left')

    df = df[df['kWh/Metering_point'] > 0].copy()
    #print(df)

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

    # -------------- Model -------------- #
    df['entity'] = pd.Categorical(df['group_definition'],
                                  categories = ['Uten Norgespris','Med Norgespris', 'Resten'],
                                  # Referanse = Uten Norgespris
                                  ordered=True)
    df['period'] = pd.Categorical(df['Period'],
                                  categories=['Reference', 'Treatment', 'Rest'],  # Reference = Reference
                                  ordered=True)
    df['log_y'] = df['kWh/Metering_point']    # -------------- HER MÅ NP.LOG LEGGES TIL FOR Å FÅ PROSENT IGJEN -------------- #

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
        'np.log(log_y) ~ 1 + C(entity)*C(period) + TimeEffects',
            data = panel_df,
            drop_absorbed=True
            #check_rank=False

        )

        model_temp = PanelOLS.from_formula(
        'np.log(log_y) ~ 1 + C(entity)*C(period) '
                '+  Temp24 + I(Temp24**2) + I(Temp24**3)'
                '+ C(entity):Temp24 '
                '+ C(entity):I(Temp24**2)'
                '+ C(entity):I(Temp24**3)'
                '+ TimeEffects',
            data = panel_df,
            drop_absorbed=True
            #check_rank=False
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
        CI_low = (np.exp(ci_low)-1)*100        # -------------- DISSE MÅ TILBAKE NÅR PROSENT SKA TEBAKE -------------- #
        CI_high = (np.exp(ci_high)-1)*100      # -------------- DISSE MÅ TILBAKE NÅR PROSENT SKA TEBAKE -------------- #

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
        CI_low_temp = (np.exp(ci_low_temp)-1)*100   # -------------- DISSE MÅ TILBAKE NÅR PROSENT SKA TEBAKE -------------- #
        CI_high_temp = (np.exp(ci_high_temp)-1)*100 # -------------- DISSE MÅ TILBAKE NÅR PROSENT SKA TEBAKE -------------- #

        results_temp.append({
            'Hour': h,
            'DiD_temp': DiD_temp,
            'CI_low_temp': CI_low_temp,
            'CI_high_temp': CI_high_temp
        })

    results_df = pd.DataFrame(results).sort_values('Hour').reset_index(drop=True)
    results_df_temp = pd.DataFrame(results_temp).sort_values('Hour').reset_index(drop=True)

    print('----------- DiD per time uten temp -----------------')
    for _, r in results_df.iterrows():
        if pd.isna(r['DiD']):
            print(f"Time {int(r['Hour']):02d}")
        else:
            print(
                f"Time {int(r['Hour']):02d}: DiD = {r['DiD']:.2f}%  | KI [{r['CI_low']:.2f}%, {r['CI_high']:.2f}%]")

    print('----------- DiD per time med temp -----------------')
    for _, r in results_df_temp.iterrows():
        if pd.isna(r['DiD_temp']):
            print(f"Time {int(r['Hour']):02d}")
        else:
            print(
                f"Time {int(r['Hour']):02d}: DiD = {r['DiD_temp']:.2f}%  | KI [{r['CI_low_temp']:.2f}%, {r['CI_high_temp']:.2f}%]")

    return results_df, results_df_temp



    # ---------- PLOTT DØGNPROFIL ---------- #
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

    # ---------- NO5 ---------- #
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



def plot_dognprofil_flex(results_list):

    plt.figure(figsize=(12, 6))
    plt.ylim(0,6)


    for res in results_list:
        name = res["name"]
        #df = res["df"]
        df_temp = res["df_temp"]
        color = res["color"]

        hours = df_temp['Hour']
        #DiD = df_temp['DiD']

        DiD_temp = df_temp['DiD_temp']
        ci_low_temp = df_temp['CI_low_temp']
        ci_high_temp = df_temp['CI_high_temp']

        #plt.plot(hours, DiD, label=f'DiD - {name}', color=color, linewidth=2, linestyle='dotted')
        plt.plot(hours, DiD_temp, label=f'DiD w/Temp - {name}', color=color, linewidth=2)

        #plt.fill_between(hours, ci_low_temp, ci_high_temp, color=color, alpha=0.1)

    plt.xticks(range(0, 24))

    plt.xlabel("Hour", fontsize=25)
    plt.ylabel("Difference in Difference of Consumption Changes [%]", fontsize=20)
    plt.grid(alpha=0.3)
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    plt.legend(fontsize=20)
    plt.tight_layout()
    plt.savefig("Flex_Alle.png", dpi=300, bbox_inches="tight")
    plt.show()

# ------------------------------------ BESTEMMELSE AV HVILKE MND SOM ER MED OG UTEN NORGESPRIS ------------------------------------ #


#BACKUP N01: data_NO1_NPoct, data_NO1_NPnov, data_NO1_NPdec,data_NO1_NPjan,data_NO1_NPfeb,data_NO1_NPmars,data_NO1_NPapril
#BACKUP N02: data_NO2_NPoct, data_NO2_NPnov, data_NO2_NPdec,data_NO2_NPjan,data_NO2_NPfeb,data_NO2_NPmars,data_NO2_NPapril
#BACKUP N05: data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec,data_NO5_NPjan,data_NO5_NPfeb,data_NO5_NPmars,data_NO5_NPapril


# ------------------------------------ ENDRE PARAMETER MELLOM HER FOR Å ENDRE ANALYSEN ------------------------------------ #

#start_date_before = '2025-03-01'
#end_date_before = '2025-03-31'

#start_date_after = '2026-03-01'
#end_date_after = '2026-03-31'


'''data_NO1_mNP_oct = pd.concat( [data_NO5_NPoct], ignore_index=True)
data_NO1_mNP_nov = pd.concat( [data_NO5_NPoct, data_NO5_NPnov], ignore_index=True)
data_NO1_mNP_dec = pd.concat( [data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec], ignore_index=True)
data_NO1_mNP_jan = pd.concat( [data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec, data_NO5_NPjan], ignore_index=True)
data_NO1_mNP_feb = pd.concat( [data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec, data_NO5_NPjan, data_NO5_NPfeb], ignore_index=True)
data_NO1_mNP_mar = pd.concat( [data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec, data_NO5_NPjan, data_NO5_NPfeb, data_NO5_NPmars], ignore_index=True)'''

data_NO1_mNP_oct = pd.concat([data_NO1_NPoct], ignore_index=True)
data_NO1_mNP_nov = pd.concat([data_NO1_NPoct, data_NO1_NPnov], ignore_index=True)
data_NO1_mNP_dec = pd.concat([data_NO1_NPoct, data_NO1_NPnov, data_NO1_NPdec], ignore_index=True)
data_NO1_mNP_jan = pd.concat([data_NO1_NPoct, data_NO1_NPnov, data_NO1_NPdec, data_NO1_NPjan], ignore_index=True)
data_NO1_mNP_feb = pd.concat([data_NO1_NPoct, data_NO1_NPnov, data_NO1_NPdec, data_NO1_NPjan, data_NO1_NPfeb], ignore_index=True)
data_NO1_mNP_mar = pd.concat([data_NO1_NPoct, data_NO1_NPnov, data_NO1_NPdec, data_NO1_NPjan, data_NO1_NPfeb, data_NO1_NPmars], ignore_index=True)

data_NO2_mNP_oct = pd.concat([data_NO2_NPoct], ignore_index=True)
data_NO2_mNP_nov = pd.concat([data_NO2_NPoct, data_NO2_NPnov], ignore_index=True)
data_NO2_mNP_dec = pd.concat([data_NO2_NPoct, data_NO2_NPnov, data_NO2_NPdec], ignore_index=True)
data_NO2_mNP_jan = pd.concat([data_NO2_NPoct, data_NO2_NPnov, data_NO2_NPdec, data_NO2_NPjan], ignore_index=True)
data_NO2_mNP_feb = pd.concat([data_NO2_NPoct, data_NO2_NPnov, data_NO2_NPdec, data_NO2_NPjan, data_NO2_NPfeb], ignore_index=True)
data_NO2_mNP_mar = pd.concat([data_NO2_NPoct, data_NO2_NPnov, data_NO2_NPdec, data_NO2_NPjan, data_NO2_NPfeb, data_NO2_NPmars], ignore_index=True)

data_NO5_mNP_oct = pd.concat([data_NO5_NPoct], ignore_index=True)
data_NO5_mNP_nov = pd.concat([data_NO5_NPoct, data_NO5_NPnov], ignore_index=True)
data_NO5_mNP_dec = pd.concat([data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec], ignore_index=True)
data_NO5_mNP_jan = pd.concat([data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec, data_NO5_NPjan], ignore_index=True)
data_NO5_mNP_feb = pd.concat([data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec, data_NO5_NPjan, data_NO5_NPfeb], ignore_index=True)
data_NO5_mNP_mar = pd.concat([data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec, data_NO5_NPjan, data_NO5_NPfeb, data_NO5_NPmars], ignore_index=True)

data_NO1_rest_oct = pd.concat([data_NO1_NPnov, data_NO1_NPdec, data_NO1_NPjan, data_NO1_NPfeb, data_NO1_NPmars, data_NO1_NPapril], ignore_index=True)
data_NO1_rest_nov = pd.concat([data_NO1_NPdec, data_NO1_NPjan, data_NO1_NPfeb, data_NO1_NPmars, data_NO1_NPapril], ignore_index=True)
data_NO1_rest_dec = pd.concat([data_NO1_NPjan, data_NO1_NPfeb, data_NO1_NPmars, data_NO1_NPapril], ignore_index=True)
data_NO1_rest_jan = pd.concat([data_NO1_NPfeb, data_NO1_NPmars, data_NO1_NPapril], ignore_index=True)
data_NO1_rest_feb = pd.concat([data_NO1_NPmars, data_NO1_NPapril], ignore_index=True)
data_NO1_rest_mar = pd.concat([data_NO1_NPapril], ignore_index=True)

data_NO2_rest_oct = pd.concat([data_NO2_NPnov, data_NO2_NPdec, data_NO2_NPjan, data_NO2_NPfeb, data_NO2_NPmars, data_NO2_NPapril], ignore_index=True)
data_NO2_rest_nov = pd.concat([data_NO2_NPdec, data_NO2_NPjan, data_NO2_NPfeb, data_NO2_NPmars, data_NO2_NPapril], ignore_index=True)
data_NO2_rest_dec = pd.concat([data_NO2_NPjan, data_NO2_NPfeb, data_NO2_NPmars, data_NO2_NPapril], ignore_index=True)
data_NO2_rest_jan = pd.concat([data_NO2_NPfeb, data_NO2_NPmars, data_NO2_NPapril], ignore_index=True)
data_NO2_rest_feb = pd.concat([data_NO2_NPmars, data_NO2_NPapril], ignore_index=True)
data_NO2_rest_mar = pd.concat([data_NO2_NPapril], ignore_index=True)

data_NO5_rest_oct = pd.concat([data_NO5_NPnov, data_NO5_NPdec, data_NO5_NPjan, data_NO5_NPfeb, data_NO5_NPmars, data_NO5_NPapril], ignore_index=True)
data_NO5_rest_nov = pd.concat([data_NO5_NPdec, data_NO5_NPjan, data_NO5_NPfeb, data_NO5_NPmars, data_NO5_NPapril], ignore_index=True)
data_NO5_rest_dec = pd.concat([data_NO5_NPjan, data_NO5_NPfeb, data_NO5_NPmars, data_NO5_NPapril], ignore_index=True)
data_NO5_rest_jan = pd.concat([data_NO5_NPfeb, data_NO5_NPmars, data_NO5_NPapril], ignore_index=True)
data_NO5_rest_feb = pd.concat([data_NO5_NPmars, data_NO5_NPapril], ignore_index=True)
data_NO5_rest_mar = pd.concat([data_NO5_NPapril], ignore_index=True)



# ------------------------------------ STOPP AV ENDRING HER, DONT TOUCH ------------------------------------ #

results_NO1_oct, results_NO1_temp_oct = Difference_in_Difference_Flex(data_NO1_mNP_oct, data_NO1_uNP, data_NO1_rest_oct, Temp_Oslo, 'NO1', '2024-10-01', '2024-10-31', '2025-10-01', '2025-10-31')
results_NO1_nov, results_NO1_temp_nov = Difference_in_Difference_Flex(data_NO1_mNP_nov, data_NO1_uNP, data_NO1_rest_nov, Temp_Oslo, 'NO1', '2024-11-01', '2024-11-30', '2025-11-01', '2025-11-30')
results_NO1_dec, results_NO1_temp_dec = Difference_in_Difference_Flex(data_NO1_mNP_dec, data_NO1_uNP, data_NO1_rest_dec, Temp_Oslo, 'NO1', '2024-12-01', '2024-12-31', '2025-12-01', '2025-12-31')
results_NO1_jan, results_NO1_temp_jan = Difference_in_Difference_Flex(data_NO1_mNP_jan, data_NO1_uNP, data_NO1_rest_jan, Temp_Oslo, 'NO1', '2025-01-01', '2025-01-31', '2026-01-01', '2026-01-31')
results_NO1_feb, results_NO1_temp_feb = Difference_in_Difference_Flex(data_NO1_mNP_feb, data_NO1_uNP, data_NO1_rest_feb, Temp_Oslo, 'NO1', '2025-02-01', '2025-02-28', '2026-02-01', '2026-02-28')
results_NO1_mar, results_NO1_temp_mar = Difference_in_Difference_Flex(data_NO1_mNP_mar, data_NO1_uNP, data_NO1_rest_mar, Temp_Oslo, 'NO1', '2025-03-01', '2025-03-31', '2026-03-01', '2026-03-31')

results_NO2_oct, results_NO2_temp_oct = Difference_in_Difference_Flex(data_NO2_mNP_oct, data_NO2_uNP, data_NO2_rest_oct, Temp_Stavanger, 'NO2', '2024-10-01', '2024-10-31', '2025-10-01', '2025-10-31')
results_NO2_nov, results_NO2_temp_nov = Difference_in_Difference_Flex(data_NO2_mNP_nov, data_NO2_uNP, data_NO2_rest_nov, Temp_Stavanger, 'NO2', '2024-11-01', '2024-11-30', '2025-11-01', '2025-11-30')
results_NO2_dec, results_NO2_temp_dec = Difference_in_Difference_Flex(data_NO2_mNP_dec, data_NO2_uNP, data_NO2_rest_dec, Temp_Stavanger, 'NO2', '2024-12-01', '2024-12-31', '2025-12-01', '2025-12-31')
results_NO2_jan, results_NO2_temp_jan = Difference_in_Difference_Flex(data_NO2_mNP_jan, data_NO2_uNP, data_NO2_rest_jan, Temp_Stavanger, 'NO2', '2025-01-01', '2025-01-31', '2026-01-01', '2026-01-31')
results_NO2_feb, results_NO2_temp_feb = Difference_in_Difference_Flex(data_NO2_mNP_feb, data_NO2_uNP, data_NO2_rest_feb, Temp_Stavanger, 'NO2', '2025-02-01', '2025-02-28', '2026-02-01', '2026-02-28')
results_NO2_mar, results_NO2_temp_mar = Difference_in_Difference_Flex(data_NO2_mNP_mar, data_NO2_uNP, data_NO2_rest_mar, Temp_Stavanger, 'NO2', '2025-03-01', '2025-03-31', '2026-03-01', '2026-03-31')

results_NO5_oct, results_NO5_temp_oct = Difference_in_Difference_Flex(data_NO5_mNP_oct, data_NO5_uNP, data_NO5_rest_oct, Temp_Bergen, 'NO5', '2024-10-01', '2024-10-31', '2025-10-01', '2025-10-31')
results_NO5_nov, results_NO5_temp_nov = Difference_in_Difference_Flex(data_NO5_mNP_nov, data_NO5_uNP, data_NO5_rest_nov, Temp_Bergen, 'NO5', '2024-11-01', '2024-11-30', '2025-11-01', '2025-11-30')
results_NO5_dec, results_NO5_temp_dec = Difference_in_Difference_Flex(data_NO5_mNP_dec, data_NO5_uNP, data_NO5_rest_dec, Temp_Bergen, 'NO5', '2024-12-01', '2024-12-31', '2025-12-01', '2025-12-31')
results_NO5_jan, results_NO5_temp_jan = Difference_in_Difference_Flex(data_NO5_mNP_jan, data_NO5_uNP, data_NO5_rest_jan, Temp_Bergen, 'NO5', '2025-01-01', '2025-01-31', '2026-01-01', '2026-01-31')
results_NO5_feb, results_NO5_temp_feb = Difference_in_Difference_Flex(data_NO5_mNP_feb, data_NO5_uNP, data_NO5_rest_feb, Temp_Bergen, 'NO5', '2025-02-01', '2025-02-28', '2026-02-01', '2026-02-28')
results_NO5_mar, results_NO5_temp_mar = Difference_in_Difference_Flex(data_NO5_mNP_mar, data_NO5_uNP, data_NO5_rest_mar, Temp_Bergen, 'NO5', '2025-03-01', '2025-03-31', '2026-03-01', '2026-03-31')

#results_NO1_1, results_NO1_temp_1 = Difference_in_Difference_Flex(data_NO1_NPapril, data_NO1_uNP, data_NO1_rest, Temp_Oslo, 'NO1', start_date_before, end_date_before, start_date_after, end_date_after)
#results_NO2, results_NO2_temp = Difference_in_Difference_Flex(data_NO1_mNP_1, data_NO1_uNP, data_NO1_rest, Temp_Oslo, 'NO1', start_date_before, end_date_before, start_date_after, end_date_after)
#results_NO5, results_NO5_temp = Difference_in_Difference_Flex(data_NO1_mNP_2, data_NO1_uNP, data_NO1_rest, Temp_Oslo, 'NO1', start_date_before, end_date_before, start_date_after, end_date_after)


# ------------------------------------ ENDRE HER IGJEN ------------------------------------ #
for i in range(1_000_000):
    pass

end = time.time()

print(f"Kjøretid: {end - start:.4f} sekunder")

'''plot_dognprofil_flex([
    {
        "name": "Group October",
        "df": results_NO1,
        "df_temp": results_NO1_temp,
        "color": "royalblue"
    },
    {
        "name": "Group January",
        "df": results_NO2,
        "df_temp": results_NO2_temp,
        "color": "red"
    },
    {
        "name": "Group March",
        "df": results_NO5,
        "df_temp": results_NO5_temp,
        "color": "green"
    }
])'''

'''plot_dognprofil_flex([
    {
        "name": "October",
        #"df": results_NO2,
        "df_temp": results_NO1_temp_oct,
        "color": "goldenrod"
    },
    {
        "name": "November",
        #"df": results_NO2,
        "df_temp": results_NO1_temp_nov,
        "color": "steelblue"
    },
    {
        "name": "December",
        #"df": results_NO5,
        "df_temp": results_NO1_temp_dec,
        "color": "indianred"
    },
    {
        "name": "January",
        #"df": results_NO5,
        "df_temp": results_NO1_temp_jan,
        "color": "seagreen"
    },
    {
        "name": "February",
        #"df": results_NO5,
        "df_temp": results_NO1_temp_feb,
        "color": "darkorange"
    },
    {
        "name": "March",
        #"df": results_NO5,
        "df_temp": results_NO1_temp_mar,
        "color": "mediumpurple"
    }
])'''


# ------------------------------------ STOPP AV ENDRE KA SOM SKA PLOTTES ------------------------------------ #


'''plot_dognprofil(results_NO1, results_NO1_temp,
               results_NO2, results_NO2_temp,
                results_NO5, results_NO5_temp)'''



# ------------------------------- KODE FOR Å FÅ ALLE UT I SAMME VINDU --------------------------

def plot_dognprofil_flex_all(NO1, NO2, NO5):

    fig, axes = plt.subplots(3, 1, figsize=(12, 16), sharex=True)

    datasets = [NO1, NO2, NO5]
    titles = ["NO1", "NO2", "NO5"]

    for j, results_list in enumerate(datasets):

        ax = axes[j]

        for res in results_list:
            name = res["name"]
            df_temp = res["df_temp"]
            color = res["color"]

            hours = df_temp['Hour']
            DiD_temp = df_temp['DiD_temp']
            ci_low_temp = df_temp['CI_low_temp']
            ci_high_temp = df_temp['CI_high_temp']

            ax.plot(
                hours,
                DiD_temp,
                label=name,
                color=color,
                linewidth=2
            )

            # (valgfritt) konfidensintervall
            # ax.fill_between(hours, ci_low_temp, ci_high_temp, color=color, alpha=0.1)

        ax.set_title(titles[j], fontsize=20)
        ax.set_ylim(0, 6)

        ax.grid(alpha=0.3)
        ax.axhline(0, color="gray", linestyle="--")

        ax.tick_params(axis='y', labelsize=18)

    # Felles labels
    axes[1].set_ylabel(
        "Difference in Difference of Consumption Changes [%]",
        fontsize=18
    )

    axes[-1].set_xticks(range(0, 24))
    axes[-1].set_xlabel("Hour", fontsize=20)
    axes[-1].tick_params(axis='x', labelsize=18)

    # Legend (samlet)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="center",
        bbox_to_anchor=(0.5, 0.4),
        ncol=3,
        fontsize=14
    )

    plt.tight_layout()
    plt.show()

    fig.savefig("Flex_Alle.png", dpi=300, bbox_inches="tight")


NO1_list = [
    {"name": "October", "df_temp": results_NO1_temp_oct, "color": "goldenrod"},
    {"name": "November", "df_temp": results_NO1_temp_nov, "color": "steelblue"},
    {"name": "December", "df_temp": results_NO1_temp_dec, "color": "indianred"},
    {"name": "January", "df_temp": results_NO1_temp_jan, "color": "seagreen"},
    {"name": "February", "df_temp": results_NO1_temp_feb, "color": "darkorange"},
    {"name": "March", "df_temp": results_NO1_temp_mar, "color": "mediumpurple"},
]

# gjør tilsvarende for NO2 og NO5:
NO2_list = [
    {"name": "October", "df_temp": results_NO2_temp_oct, "color": "goldenrod"},
    {"name": "November", "df_temp": results_NO2_temp_nov, "color": "steelblue"},
    {"name": "December", "df_temp": results_NO2_temp_dec, "color": "indianred"},
    {"name": "January", "df_temp": results_NO2_temp_jan, "color": "seagreen"},
    {"name": "February", "df_temp": results_NO2_temp_feb, "color": "darkorange"},
    {"name": "March", "df_temp": results_NO2_temp_mar, "color": "mediumpurple"},
]


NO5_list = [
    {"name": "October", "df_temp": results_NO5_temp_oct, "color": "goldenrod"},
    {"name": "November", "df_temp": results_NO5_temp_nov, "color": "steelblue"},
    {"name": "December", "df_temp": results_NO5_temp_dec, "color": "indianred"},
    {"name": "January", "df_temp": results_NO5_temp_jan, "color": "seagreen"},
    {"name": "February", "df_temp": results_NO5_temp_feb, "color": "darkorange"},
    {"name": "March", "df_temp": results_NO5_temp_mar, "color": "mediumpurple"},
]

plot_dognprofil_flex_all(NO1_list, NO2_list, NO5_list)