import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------ ALLE CSV FILER MED FORBRUKSDATA --------------------------------

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



def print_gjennomsnitt(data_mNP, data_uNP, price_area):

    df_mNP = data_mNP.copy()
    df_uNP = data_uNP.copy()

    start_dato = '2023-09-30'
    slutt_dato = ('2026-03-31')

    df_mNP['start_time_utc'] = pd.to_datetime((df_mNP['start_time_utc']), utc=True)
    df_mNP = df_mNP[(df_mNP['start_time_utc'] >= start_dato) & (df_mNP['start_time_utc'] <= slutt_dato)]

    df_uNP['start_time_utc'] = pd.to_datetime((df_uNP['start_time_utc']), utc=True)
    df_uNP = df_uNP[(df_uNP['start_time_utc'] >= start_dato) & (df_uNP['start_time_utc'] <= slutt_dato)]

    df_mNP['Hour'] = df_mNP['start_time_utc'].dt.hour
    df_mNP['kWh/metering_point'] = df_mNP['consumption_kwh'] / df_mNP['metering_point_count']
    print('Gjennomsnittsforbruk med NP for area:', price_area, df_mNP['kWh/metering_point'].mean())

    df_uNP['Hour'] = df_uNP['start_time_utc'].dt.hour
    df_uNP['kWh/metering_point'] = df_uNP['consumption_kwh'] / df_uNP['metering_point_count']
    print('Gjennomsnittsforbruk uten NP for area:', price_area, df_uNP['kWh/metering_point'].mean())


data_mNP_NO1 = data_NO1_NPapril
data_uNP_NO1 = data_NO1_uNP

data_mNP_NO2 = data_NO2_NPapril
data_uNP_NO2 = data_NO2_uNP

data_mNP_NO5 = data_NO5_NPapril
data_uNP_NO5 = data_NO5_uNP

print('NO1')
print_gjennomsnitt(data_mNP_NO1, data_uNP_NO1, 'NO1')
print('-------------------')

print('NO2')
print_gjennomsnitt(data_mNP_NO2, data_uNP_NO2, 'NO2')
print('-------------------')

print('NO5')
print_gjennomsnitt(data_mNP_NO5, data_uNP_NO5, 'NO5')
print('-------------------')
