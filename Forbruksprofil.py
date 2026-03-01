import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')

def plot_timer(data_mNP, data_uNP, price_area):

    def prep(df):
        df = df.copy()

        start_dato = '2025-11-01'
        slutt_dato = '2026-01-31'

        df['start_time_utc'] = pd.to_datetime((df['start_time_utc']), utc=True)
        df = df[(df['start_time_utc'] >= start_dato) & (df['start_time_utc'] <= slutt_dato)]

        df['Hour'] = df['start_time_utc'].dt.hour
        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']
        return df

    df_mNP = prep(data_mNP)
    df_uNP = prep(data_uNP)

    mNP_prof = df_mNP.groupby('Hour')['kWh/metering_point'].mean()
    uNP_prof = df_uNP.groupby('Hour')['kWh/metering_point'].mean()

    plt.figure(figsize=(10,5))
    plt.plot(mNP_prof.index, mNP_prof.values, marker = 'o', label = 'With Norgespris')
    plt.plot(uNP_prof.index, uNP_prof.values, marker = 'o', label = 'Without Norgespris')

    plt.xlabel('Hour')
    plt.ylabel('kWh/metering_point')
    plt.title(f'Consumption - kWh per metering point for period {df_mNP['start_time_utc'].min().date()} to {df_mNP['start_time_utc'].max().date()} in {price_area}')
    plt.xticks(range(24))
    plt.grid(True, alpha = 0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

plot_timer(data_mNP_NO5, data_uNP_NO5, 'NO5')