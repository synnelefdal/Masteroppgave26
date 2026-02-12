import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row
import statsmodels.api as sm
import patsy

data_mNP = pd.read_csv('Forbruk_NO1_NO5.csv')
data_uNP = pd.read_csv('Forbruk_NO1_NO5.csv')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')


def DifferenceinDifference(data, price_area, Temp):
    # ------------------- Filterer for dato ---------- #
    start_date_before = '2024-10-01'
    end_date_before = '2025-01-31'

    start_date_after = '2025-10-01'
    end_date_after = '2025-01-31'

    # ----------------- Demand; NP-Gruppen ------------------ #

    data_demand_NP = data_mNP[data['price_area'] == price_area].copy()
    data_demand_NP['Date'] = pd.to_datetime(data_demand_NP['Date'])
    data_demand_NP['Hour'] = data_demand_NP['Hour'].astype(int)

    data_demand_NP_filtered_before = data_demand_NP[(data_demand_NP['Date'] >= start_date_before) &
                                        (data_demand_NP['Date'] <= end_date_before)].copy()

    data_demand_NP_filtered_after = data_demand_NP[(data_demand_NP['Date'] >= start_date_after) &
                                        (data_demand_NP['Date'] <= end_date_after)].copy()
    # print(data_demand_filtered1)
    # print(data_demand_filtered2)

    for index, rad in data_demand_NP_filtered_before.iterrows():
        data_demand_NP_filtered_before.loc[index, 'kWh/Metering_point'] = rad['quantity_kwh'] / rad['metering_point_count']

    for index, rad in data_demand_NP_filtered_after.iterrows():
        data_demand_NP_filtered_after.loc[index, 'kWh/Metering_point'] = rad['quantity_kwh'] / rad['metering_point_count']
    # print(data_demand_filtered2.head(3))

    total_demand_hour_NP_before = data_demand_NP_filtered_before.groupby(['Date', 'Hour'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_NP_after = data_demand_NP_filtered_after.groupby(['Date', 'Hour'])['kWh/Metering_point'].sum().reset_index()
    # print(total_hour1)
    # print(total_hour2)

    # ----------------- Demand; Uten NP-Gruppen ------------------ #

    data_demand_UtenNP = data_uNP[data['price_area'] == price_area].copy()
    data_demand_UtenNP['Date'] = pd.to_datetime(data_demand_UtenNP['Date'])
    data_demand_UtenNP['Hour'] = data_demand_UtenNP['Hour'].astype(int)

    data_demand_UtenNP_filtered_before = data_demand_UtenNP[(data_demand_NP['Date'] >= start_date_before) &
                                        (data_demand_UtenNP['Date'] <= end_date_before)].copy()

    data_demand_UtenNP_filtered_after = data_demand_UtenNP[(data_demand_NP['Date'] >= start_date_after) &
                                        (data_demand_UtenNP['Date'] <= end_date_after)].copy()
    # print(data_demand_filtered1)
    # print(data_demand_filtered2)

    for index, rad in data_demand_NP_filtered_before.iterrows():
        data_demand_UtenNP_filtered_before.loc[index, 'kWh/Metering_point'] = rad['quantity_kwh'] / rad['metering_point_count']

    for index, rad in data_demand_NP_filtered_after.iterrows():
        data_demand_UtenNP_filtered_after.loc[index, 'kWh/Metering_point'] = rad['quantity_kwh'] / rad['metering_point_count']

    # print(data_demand_filtered2.head(3))

    total_demand_hour_UtenNP_before = data_demand_UtenNP_filtered_before.groupby(['Date', 'Hour'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_UtenNP_after = data_demand_UtenNP_filtered_after.groupby(['Date', 'Hour'])['kWh/Metering_point'].sum().reset_index()

    # print(total_hour1)
    # print(total_hour2)

    # -------------- Temperatur --------------- #

    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(float)

    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(window=24, min_periods=1).mean()
    Temp['Temp72'] = Temp['Lufttemperatur'].rolling(window=72, min_periods=1).mean()

    Temp_filtered_before = Temp[(Temp['Date'] >= start_date_before) &
                          (Temp['Date'] <= end_date_before)].copy()

    Temp_filtered_after = Temp[(Temp['Date'] >= start_date_after) &
                          (Temp['Date'] <= end_date_after)].copy()

    # total_temp_hour1 = Temp_filtered1.groupby(['Date', 'Hour'])['Lufttemperatur'].sum().reset_index()
    # total_temp_hour2 = Temp_filtered2.groupby(['Date', 'Hour'])['Lufttemperatur'].sum().reset_index()

    # print(total_temp_hour2.head(3))

    # -------- Merge data; NP-Gruppen ----------- #
    merged_NP = pd.merge(total_demand_hour_NP_before, total_demand_hour_NP_after, Temp_filtered_before, on=['Date', 'Hour'])
    filtered_NP = merged_NP[(merged_NP['kWh/Metering_point'] > 0) & (merged_NP['Lufttemperatur'].notnull())].copy()

    df_NP = pd.DataFrame(filtered_NP)

    # pd.set_option('display.max_columns', None)
    # print(df1.head(3))

    # ------------ Merge data; Uten NP-gruppen ----------- #
    merged_UtenNP = pd.merge(total_demand_hour_UtenNP_before, total_demand_hour_UtenNP_after, Temp_filtered_after, on=['Date', 'Hour'])
    filtered_UtenNP = merged_UtenNP[(merged_UtenNP['kWh/Metering_point'] > 0) & (merged_UtenNP['Lufttemperatur'].notnull())].copy()

    df_UtenNP = pd.DataFrame(filtered_UtenNP)

    # pd.set_option('display.max_columns', None)
    # print(df2.head(3))

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
    df_NP['Group'] = 'Before_ref'  # 2024-periode
    df_UtenNP['Group'] = 'After_ref'  # 2025-periode

    df_NP['Norgespris'] = 'Med_NP'  #
    df_UtenNP['Norgespris'] = 'Uten_NP'  #


    df = pd.concat([df_NP, df_UtenNP], ignore_index=True)

    pd.set_option('display.max_columns', None)
    print(df)

    formula = (
        'Q("kWh/Metering_point") ~ '
        'C(Group, Treatment(reference="Before_ref")) + C(Norgespris, Treatment(reference="Uten_NP"))'


    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())


DifferenceinDifference(data_mNP, 'NO1', Temp_Oslo)  # Ved NO1 bruk Temp_Oslo, og ved NO5 bruk Temp_Bergen





