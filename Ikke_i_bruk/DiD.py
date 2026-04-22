# Difference in Difference
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row
#from sympy.benchmarks.bench_discrete_log import data_set_1

#data = pd.read_csv('Forbruk_NO1_NO5.csv')

Med_NP=pd.read_csv('../All_Demand_Data/NO1_mNP.csv', sep=';')

Uten_NP=pd.read_csv('../All_Demand_Data/NO1_uNP.csv', sep=';')


def Difference_in_Difference(dataset):
    # filterer for dato

    #ny måte å gjør datoene på
    start_date1 = pd.to_datetime('2025-01-01', utc=True)
    end_date1 = pd.to_datetime('2025-01-31',utc=True)

    start_date2 = pd.to_datetime('2026-01-01',utc=True)
    end_date2 = pd.to_datetime('2026-01-31', utc=True)


    #dette e for å ta ut timene i csv filen
    dataset['start_time_utc'] = pd.to_datetime(
        dataset['start_time_utc'],
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce',
        utc=True
    )

    # Extract date and hour
    dataset['Date'] = dataset['start_time_utc'].dt.date
    dataset['Hour'] = dataset['start_time_utc'].dt.hour.astype('Int64')  # nullable int

    # Sort by Date then Hour
    dataset = dataset.sort_values(['Date', 'Hour'])


    #filtere for prissone

    #dataset_updated_area = dataset[dataset['price_area'] == price_area].copy()
    #dataset_updated_area['start_time_utc'] = pd.to_datetime(dataset_updated_area['start_time_utc'])
    #dataset_updated_area['Hour'] = dataset_updated_area['Hour'].astype(int)

    #ny

    #gamle måten me testa på

    # filterer for dato videre
    #print(dataset_updated_area)

    #for første året
    data_set_1 = dataset[(dataset['start_time_utc'] >= start_date1) & (dataset['start_time_utc'] <= end_date1)]
    data_set_1 = data_set_1.copy()


    #for andre året
    data_set_2 = dataset[(dataset['start_time_utc'] >= start_date2) & (dataset['start_time_utc'] <= end_date2)]
    data_set_2 = data_set_2.copy()


    #Finne totalt forbruk over valgt tid for hvert målepunkt år 1

    forbruk1 = 0

    for index, rad in data_set_1.iterrows():
        forbruk1 += rad['consumption_kwh'] / rad['metering_point_count']
        #print(forbruk1)

    #print('forbruk år 1:',forbruk1)


    # Finne totalt forbruk over valgt tid for hvert målepunkt år 2

    forbruk2 = 0

    for index, rad in data_set_2.iterrows():
        forbruk2 += rad['consumption_kwh'] / rad['metering_point_count']
        # print(forbruk2)

    #print('forbruk år 2:', forbruk2)


    #Finne forskjell DiD

    prosent = ((forbruk2-forbruk1) / forbruk1 ) * 100
    endring_kwh=forbruk2-forbruk1
    #print('endring', endring_kwh)


    #print('-------------og så ordentlig med level: ------------')


    forbruk1 = 0
    mp1=0

    for index, rad in data_set_1.iterrows():
        forbruk1 += rad['consumption_kwh']
        mp1 += rad['metering_point_count']
        #print(forbruk1)

    #print('forbruk år 1 level:',forbruk1)


    # Finne totalt forbruk over valgt tid for hvert målepunkt år 2

    forbruk2 = 0
    mp2=0

    for index, rad in data_set_2.iterrows():
        forbruk2 += rad['consumption_kwh']
        mp2 += rad['metering_point_count']
        # print(forbruk2)

    #print('forbruk år 2 level :', forbruk2)

    delta_level1 = forbruk1/mp1
    delta_level2 = forbruk2/mp2

    #print('endring i level 1 per husholdning', delta_level1)
    #print('endring i level 2 per husholdning', delta_level2)

    delta=delta_level2-delta_level1

    #print('level endring', delta_level2-delta_level1 )


    return prosent, delta


prosentNP, deltaNP = Difference_in_Difference(Med_NP)

prosentuNP , deltauNP = Difference_in_Difference(Uten_NP)

print('DiD prosent: ',prosentNP-prosentuNP)
print('DiD level: ', deltaNP-deltauNP)


#print('Prosent endring m/Norgespris:',(f"{Difference_in_Difference(Med_NP)[0]:.3f}"), '\n', '\n')

#print('Prosent endring u/Norgespris:',(f"{Difference_in_Difference(Uten_NP)[0]:.3f}"), '\n', '\n')

#print('DiD: må så ta minus mellom prosentene og se på forskjellen i endring')

#print(Difference_in_Difference(Med_NP)-Difference_in_Difference(Uten_NP), ': ekstra endring i prosent med norgespris')




'''


def total_forbruk_per_malepunkt(data):
    return (data['quantity_kwh'] / data['metering_point_count']).sum()

def Difference_in_Difference2(dataset, treatment_area, control_area):

    # Perioder
    start_date1 = '2024-10-01'
    end_date1   = '2024-12-31'

    start_date2 = '2025-10-01'
    end_date2   = '2025-12-31'

    dataset = dataset.copy()
    dataset['Date'] = pd.to_datetime(dataset['Date'])
    dataset['Hour'] = dataset['Hour'].astype(int)

    # -------------------------
    # TREATMENT AREA
    # -------------------------
    treat = dataset[dataset['price_area'] == treatment_area]

    treat_before = treat[(treat['Date'] >= start_date1) & (treat['Date'] <= end_date1)]
    treat_after  = treat[(treat['Date'] >= start_date2) & (treat['Date'] <= end_date2)]

    forbruk_treat_before = total_forbruk_per_malepunkt(treat_before)
    forbruk_treat_after  = total_forbruk_per_malepunkt(treat_after)

    # -------------------------
    # CONTROL AREA
    # -------------------------
    control = dataset[dataset['price_area'] == control_area]

    control_before = control[(control['Date'] >= start_date1) & (control['Date'] <= end_date1)]
    control_after  = control[(control['Date'] >= start_date2) & (control['Date'] <= end_date2)]

    forbruk_control_before = total_forbruk_per_malepunkt(control_before)
    forbruk_control_after  = total_forbruk_per_malepunkt(control_after)

    # -------------------------
    # DIFFERENCE-IN-DIFFERENCE
    # -------------------------
    change_treat = (forbruk_treat_after - forbruk_treat_before) / forbruk_treat_before
    change_control = (forbruk_control_after - forbruk_control_before) / forbruk_control_before

    DiD = change_treat - change_control

    return {
        "Treatment change": change_treat,
        "Control change": change_control,
        "DiD": DiD
    }

resultat = Difference_in_Difference2(
    dataset=data,
    treatment_area="NO1",
    control_area="NO1"
)

print(resultat)'''
'''
#ny did fra chat
import pandas as pd
import numpy as np


Med_NP=pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep=';')

Uten_NP=pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep=';')


def aggregate_avg_per_mp(df, start, end):
    df = df.copy()
    # Parse timestamp
    df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True, errors='coerce')
    # Filter period
    mask = df['start_time_utc'].between(pd.to_datetime(start, utc=True),
                                        pd.to_datetime(end,   utc=True),
                                        inclusive='both')
    dfp = df.loc[mask].copy()

    # Clean
    dfp = dfp.dropna(subset=['consumption_kwh', 'metering_point_count'])
    dfp = dfp[dfp['metering_point_count'] > 0]

    # Correct aggregation: sum first, then divide
    total_kwh = dfp['consumption_kwh'].sum()
    total_mp_hours = dfp['metering_point_count'].sum()
    avg_kwh_per_mp = total_kwh / total_mp_hours if total_mp_hours > 0 else np.nan
    return avg_kwh_per_mp

def did_two_periods_percent(med_df, uten_df,
                            pre_start='2024-10-01', pre_end='2025-01-31',
                            post_start='2025-10-01', post_end='2026-01-31',
                            percent_baseline='T_pre'):
    """
    percent_baseline ∈ {'T_pre','C_pre','pooled_pre'}
      - 'T_pre'      : divides by Treatment pre (default)
      - 'C_pre'      : divides by Control pre
      - 'pooled_pre' : divides by average of T_pre and C_pre
    """

    # Averages (kWh per metering point) in each period
    T_pre  = aggregate_avg_per_mp(med_df,  pre_start,  pre_end)
    T_post = aggregate_avg_per_mp(med_df,  post_start, post_end)
    C_pre  = aggregate_avg_per_mp(uten_df, pre_start,  pre_end)
    C_post = aggregate_avg_per_mp(uten_df, post_start, post_end)

    # Changes in levels
    dT = T_post - T_pre
    dC = C_post - C_pre

    # DiD in levels
    did_level = dT - dC

    # Choose denominator for percent
    if percent_baseline == 'T_pre':
        denom = T_pre
    elif percent_baseline == 'C_pre':
        denom = C_pre
    elif percent_baseline == 'pooled_pre':
        denom = np.nanmean([T_pre, C_pre])
    else:
        raise ValueError("percent_baseline must be 'T_pre', 'C_pre', or 'pooled_pre'.")

    did_percent = (did_level / denom) * 100 if denom and not np.isnan(denom) and denom != 0 else np.nan

    # Also report each group’s own percent change (for context, not the DiD)
    pct_T = (dT / T_pre) * 100 if T_pre and not np.isnan(T_pre) and T_pre != 0 else np.nan
    pct_C = (dC / C_pre) * 100 if C_pre and not np.isnan(C_pre) and C_pre != 0 else np.nan

    return {
        'T_pre_avg_kWh_per_MP': T_pre,
        'T_post_avg_kWh_per_MP': T_post,
        'C_pre_avg_kWh_per_MP': C_pre,
        'C_post_avg_kWh_per_MP': C_post,
        'Treat_change_level': dT,
        'Ctrl_change_level': dC,
        'DiD_level': did_level,
        'DiD_percent_baseline': percent_baseline,
        'DiD_percent': did_percent,
        'Treatment_own_pct_change': pct_T,
        'Control_own_pct_change': pct_C
    }

# ---- Example usage ----
# Med_NP = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep=';')
# Uten_NP = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep=';')

res = did_two_periods_percent(
    Med_NP, Uten_NP,
    pre_start='2024-10-01', pre_end='2025-01-31',
    post_start='2025-10-01', post_end='2026-01-31',
    percent_baseline='T_pre'  # or 'C_pre' or 'pooled_pre'
)

print("\n--- Difference-in-Differences (percent) ---")
print(f"Baseline for percent: {res['DiD_percent_baseline']}")
print(f"DiD (level): {res['DiD_level']:.6f} kWh per MP-hour")
print(f"DiD (percent): {res['DiD_percent']:.3f}%\n")

print("--- Context ---")
print(f"Treatment change (level): {res['Treat_change_level']:.6f}")
print(f"Control change   (level): {res['Ctrl_change_level']:.6f}")
print(f"Treatment own % change: {res['Treatment_own_pct_change']:.3f}%")
print(f"Control   own % change: {res['Control_own_pct_change']:.3f}%")'''