
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row
import statsmodels.api as sm
import patsy


data = pd.read_csv('Forbruk_NO1_NO5.csv')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')

def metode2(data, price_area, Temp):

    # ------------------- Filterer for dato ---------- #
    start_date1 = '2024-10-01'
    end_date1 = '2024-12-31'

    start_date2 = '2025-10-01'
    end_date2 = '2025-12-31'

    # ----------------- Demand ------------------ #

    data_demand = data[data['price_area'] == price_area].copy()
    data_demand['Date'] = pd.to_datetime(data_demand['Date'])
    data_demand['Hour'] = data_demand['Hour'].astype(int)

    data_demand_filtered1 = data_demand[ (data_demand['Date'] >= start_date1) &
                                       (data_demand['Date'] <= end_date1)].copy()

    data_demand_filtered2 = data_demand[(data_demand['Date'] >= start_date2) &
                                        (data_demand['Date'] <= end_date2)].copy()
    #print(data_demand_filtered1)
    #print(data_demand_filtered2)

    for index, rad in data_demand_filtered1.iterrows():
        data_demand_filtered1.loc[index,'kWh/Metering_point'] = rad['quantity_kwh'] / rad['metering_point_count']

    for index, rad in data_demand_filtered2.iterrows():
        data_demand_filtered2.loc[index,'kWh/Metering_point'] = rad['quantity_kwh'] / rad['metering_point_count']
    #print(data_demand_filtered2.head(3))

    total_demand_hour1 = data_demand_filtered1.groupby(['Date', 'Hour'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour2 = data_demand_filtered2.groupby(['Date', 'Hour'])['kWh/Metering_point'].sum().reset_index()
    #print(total_hour1)
    #print(total_hour2)

    # -------------- Temperatur --------------- #

    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(float)

    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(window=24, min_periods=1).mean()
    Temp['Temp72'] = Temp['Lufttemperatur'].rolling(window=72, min_periods=1).mean()

    Temp_filtered1 = Temp[(Temp['Date'] >= start_date1) &
                                       (Temp['Date'] <= end_date1)].copy()

    Temp_filtered2 = Temp[(Temp['Date'] >= start_date2) &
                          (Temp['Date'] <= end_date2)].copy()

    #total_temp_hour1 = Temp_filtered1.groupby(['Date', 'Hour'])['Lufttemperatur'].sum().reset_index()
    #total_temp_hour2 = Temp_filtered2.groupby(['Date', 'Hour'])['Lufttemperatur'].sum().reset_index()

    #print(total_temp_hour2.head(3))

    # -------- Merge data 1 ----------- #
    merged1 = pd.merge(total_demand_hour1, Temp_filtered1, on = ['Date', 'Hour'])
    filtered1 = merged1[(merged1['kWh/Metering_point'] > 0) & (merged1['Lufttemperatur'].notnull())].copy()

    df1 = pd.DataFrame(filtered1)

    #pd.set_option('display.max_columns', None)
    #print(df1.head(3))

    # ------------ Merge data 2 ----------- #
    merged2 = pd.merge(total_demand_hour2, Temp_filtered2, on = ['Date', 'Hour'])
    filtered2 = merged2[(merged2['kWh/Metering_point'] > 0) & (merged2['Lufttemperatur'].notnull())].copy()

    df2 = pd.DataFrame(filtered2)

    #pd.set_option('display.max_columns', None)
    #print(df2.head(3))

    # ----------------- Beregninger1 ------------------- #
    df1['Date'] = pd.to_datetime(df1['Date'])
    df1['Month'] = df1['Date'].dt.strftime('%B')

    df1['Hour'] = pd.Categorical(df1['Hour'].astype(str),
                                 categories=[str(i) for i in range(1, 25)], ordered=True)
    df1['Month'] = pd.Categorical(df1['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)

    # ----------------- Beregninger2 ------------------- #
    df2['Date'] = pd.to_datetime(df2['Date'])
    df2['Month'] = df2['Date'].dt.strftime('%B')

    df2['Hour'] = pd.Categorical(df2['Hour'].astype(str),
                                 categories=[str(i) for i in range(1, 25)], ordered=True)
    df2['Month'] = pd.Categorical(df2['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)

    # --------------- Regresjonsanalyse ------------- #
    df1['Group'] = 'Before_ref'  # 2024-periode
    df2['Group'] = 'After_ref'  # 2025-periode

    df = pd.concat([df1, df2], ignore_index=True)

    pd.set_option('display.max_columns', None)
    print(df)

    formula = (
        'Q("kWh/Metering_point") ~ '
        'C(Group, Treatment(reference="Before_ref")) + (norgespris eller ikke, ref = ikke norgespris)'
        
        
        '''+ '
        'Temp24 + I(Temp24**2) + I(Temp24**3) + '
        'Temp72 + C(Hour, Treatment(reference="1")) + '
        'C(Month, Treatment(reference="October"))'''
    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())


metode2(data, 'NO1', Temp_Oslo)      # Ved NO1 bruk Temp_Oslo, og ved NO5 bruk Temp_Bergen





