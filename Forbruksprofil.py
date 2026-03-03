import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')
data_rest_NO1 = pd.read_csv('All_Demand_Data/NO1_resten.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')
data_rest_NO2 = pd.read_csv('All_Demand_Data/NO2_resten.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')
data_rest_NO5 = pd.read_csv('All_Demand_Data/NO5_resten.csv', sep= ';')


def plot_timer(data_mNP, data_uNP, data_resten, price_area):

    # -------- REFERENCE ---------- #

    def prep_ref(df):
        df = df.copy()

        start_dato = '2024-11-01'
        slutt_dato = '2025-01-31'

        df['start_time_utc'] = pd.to_datetime((df['start_time_utc']), utc=True)
        df = df[(df['start_time_utc'] >= start_dato) & (df['start_time_utc'] <= slutt_dato)]

        df['Hour'] = df['start_time_utc'].dt.hour
        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']

        #print('her er gjennonsmittet?;', df['kWh/metering_point'].mean(), df['price_area'])
        return df

    df_mNP_ref = prep_ref(data_mNP)
    df_uNP_ref = prep_ref(data_uNP)

    mNP_prof_ref = df_mNP_ref.groupby('Hour')['kWh/metering_point'].mean()
    uNP_prof_ref = df_uNP_ref.groupby('Hour')['kWh/metering_point'].mean()

    # --------- TREATMENT ---------- #
    def prep_tre(df):
        df = df.copy()

        start_dato = '2025-11-01'
        slutt_dato = '2026-01-31'

        df['start_time_utc'] = pd.to_datetime((df['start_time_utc']), utc=True)
        df = df[(df['start_time_utc'] >= start_dato) & (df['start_time_utc'] <= slutt_dato)]

        df['Hour'] = df['start_time_utc'].dt.hour
        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']
        return df

    df_mNP_tre = prep_tre(data_mNP)
    df_uNP_tre = prep_tre(data_uNP)

    mNP_prof_tre = df_mNP_tre.groupby('Hour')['kWh/metering_point'].mean()
    uNP_prof_tre = df_uNP_tre.groupby('Hour')['kWh/metering_point'].mean()

    # --------- PLOT ------------- #
    plt.figure(figsize=(10,5))
    plt.plot(mNP_prof_ref.index, mNP_prof_ref.values, marker = 'o', label = 'With Norgespris 24/25')
    plt.plot(uNP_prof_ref.index, uNP_prof_ref.values, marker = 'o', label = 'Without Norgespris 24/25')

    plt.plot(mNP_prof_tre.index, mNP_prof_tre.values, marker='o', label= 'With Norgespris 25/26')
    plt.plot(uNP_prof_tre.index, uNP_prof_tre.values, marker='o', label= 'Without Norgespris 25/26')

    plt.xlabel('Hour', fontsize=20)
    plt.ylabel('kWh/metering_point', fontsize=20)
    plt.title(f'Consumption - kWh per metering point in {price_area}', fontsize=20)
    plt.xticks(range(24))
    plt.grid(True, alpha = 0.3)
    plt.legend(fontsize=20)
    plt.tight_layout()
    plt.show()

plot_timer(data_mNP_NO5, data_uNP_NO5, data_rest_NO5, 'NO5')


def print_gjennomsnitt(data_mNP, data_uNP, data_resten, price_area):


    df_mNP = data_mNP.copy()
    df_uNP = data_uNP.copy()
    df_resten = data_resten.copy()

    start_dato = '2023-10-01'
    slutt_dato = '2026-01-31'

    df_mNP['start_time_utc'] = pd.to_datetime((df_mNP['start_time_utc']), utc=True)
    df_mNP = df_mNP[(df_mNP['start_time_utc'] >= start_dato) & (df_mNP['start_time_utc'] <= slutt_dato)]

    df_uNP['start_time_utc'] = pd.to_datetime((df_uNP['start_time_utc']), utc=True)
    df_uNP = df_uNP[(df_uNP['start_time_utc'] >= start_dato) & (df_uNP['start_time_utc'] <= slutt_dato)]

    df_resten['start_time_utc'] = pd.to_datetime((df_resten['start_time_utc']), utc=True)
    df_resten = df_resten[(df_resten['start_time_utc'] >= start_dato) & (df_resten['start_time_utc'] <= slutt_dato)]

    df_mNP['Hour'] = df_mNP['start_time_utc'].dt.hour
    df_mNP['kWh/metering_point'] = df_mNP['consumption_kwh'] / df_mNP['metering_point_count']
    print('Gjennomsnittsforbruk med NP for area:', price_area, df_mNP['kWh/metering_point'].mean())

    df_uNP['Hour'] = df_uNP['start_time_utc'].dt.hour
    df_uNP['kWh/metering_point'] = df_uNP['consumption_kwh'] / df_uNP['metering_point_count']
    print('Gjennomsnittsforbruk uten NP for area:', price_area, df_uNP['kWh/metering_point'].mean())

    df_resten['Hour'] = df_resten['start_time_utc'].dt.hour
    df_resten['kWh/metering_point'] = df_resten['consumption_kwh'] / df_resten['metering_point_count']
    print('Gjennomsnittsforbruk for resten for area:', price_area, df_resten['kWh/metering_point'].mean())

print_gjennomsnitt(data_mNP_NO1, data_uNP_NO1, data_rest_NO1, 'NO1')
