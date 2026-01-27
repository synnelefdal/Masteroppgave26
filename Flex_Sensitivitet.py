
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row


import statsmodels.api as sm
import patsy
import seaborn as sns
from pandas import to_datetime


data = pd.read_csv('Forbruk_NO1_NO5.csv')

price_NO1 = pd.read_csv('NO1_prices.csv')
price_NO5 = pd.read_csv('NO5_prices.csv')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')

def flex_sensitivitet(data, price_area, temp, price_data):
    # ------------------- Filterer for dato ---------- #
    start_date1 = '2024-10-01'
    end_date1 = '2024-12-31'

    start_date2 = '2025-10-01'
    end_date2 = '2025-12-31'

    # ----------------- Demand ------------------ #

    data_demand = data[data['price_area'] == price_area].copy()
    data_demand['Date'] = pd.to_datetime(data_demand['Date'])
    data_demand['Hour'] = data_demand['Hour'].astype(int)

    data_demand_filtered1 = data_demand[(data_demand['Date'] >= start_date1) &
                                        (data_demand['Date'] <= end_date1)].copy()

    data_demand_filtered2 = data_demand[(data_demand['Date'] >= start_date2) &
                                        (data_demand['Date'] <= end_date2)].copy()

    for index, rad in data_demand_filtered1.iterrows():
        data_demand_filtered1.loc[index, 'demand'] = rad['quantity_kwh'] / rad['metering_point_count']

    for index, rad in data_demand_filtered2.iterrows():
        data_demand_filtered2.loc[index, 'demand'] = rad['quantity_kwh'] / rad['metering_point_count']

    total_hour1 = data_demand_filtered1.groupby(['Date', 'Hour'])['demand'].sum().reset_index()
    total_hour2 = data_demand_filtered2.groupby(['Date', 'Hour'])['demand'].sum().reset_index()

    #print(total_hour1)

    # ----------------------- Pris -------------------- #
    #price_area = data_households[data_households['ID'].isin(liste_husstander)].iloc[0]['Price_area']
    price_data = price_data[price_data['Område'] == price_area].copy()                                          #blir dette riktig???
    price_data['Date'] = pd.to_datetime(price_data['Date'])
    price_data['Hour'] = price_data['Hour'].astype(int)

    price_filtered1 = price_data[(price_data['Date'] >= start_date1) & (price_data['Date'] <= end_date1)]    #gjør det bare for første året nå????
    price_filtered1 = price_filtered1.copy()
    price_filtered1['Pris'] = price_filtered1['Pris'].apply(lambda x: x if x > 0 else 0.01)
    #print('her e pris',price_filtered1)
    #må gjør det for det andre året også:)

    price_filtered2 = price_data[(price_data['Date'] >= start_date2) & (price_data['Date'] <= end_date2)]  # gjør det bare for første året nå????
    price_filtered2 = price_filtered2.copy()
    price_filtered2['Pris'] = price_filtered2['Pris'].apply(lambda x: x if x > 0 else 0.01)
    #print('her e pris', price_filtered2)
    #print(price_filtered2['Pris'])
    # ------------ Temperatur --------------------- #
    temp['Date'] = pd.to_datetime(temp['Date'])
    temp['Hour'] = temp['Hour'].astype(float)

    temp['Temperatur24'] = temp['Lufttemperatur'].rolling(window=24, min_periods=1).mean()
    temp['Temperatur72'] = temp['Lufttemperatur'].rolling(window=72, min_periods=1).mean()

    temp_filtered1 = temp[(temp['Date'] >= start_date1) &
                                      (temp['Date'] <= end_date1)]

    temp_filtered2 = temp[(temp['Date'] >= start_date2) &
                         (temp['Date'] <= end_date2)]

    # ------------------- Merge data ---------------- #
    merged_1 = pd.merge(total_hour1, price_filtered1, on=['Date', 'Hour'])
    merged__1 = pd.merge(merged_1, temp_filtered1, on=['Date', 'Hour'])

    merged_2 = pd.merge(total_hour2, price_filtered2, on=['Date', 'Hour'])
    #print('første sted', merged_2)
    merged__2 = pd.merge(merged_2, temp_filtered2, on=['Date', 'Hour'])
    pd.set_option('display.max_columns', None)
    #print('andre sted', merged__2)

    filtered1 = merged__1[(merged__1['demand'] > 0) & (merged__1['Pris'] > 0) &
                      (merged__1['Lufttemperatur'].notnull())].copy()

    #print(filtered1)

    filtered2 = merged__2[(merged__2['demand'] > 0) & (merged__2['Pris'] > 0) &
                      (merged__2['Lufttemperatur'].notnull())].copy()

    #print('filter',filtered2)

    df1 = pd.DataFrame(filtered1)
    df2 = pd.DataFrame(filtered2)

    #print('df2',df2)


    # ---------------- Beregeninger1 ---------------- #

    df1['Date'] = pd.to_datetime(df1['Date'])
    df1['Month'] = df1['Date'].dt.strftime('%B')

    df1['Hour'] = pd.Categorical(df1['Hour'].astype(str),
                                categories=[str(i) for i in range(1, 25)], ordered=True)
    df1['Month'] = pd.Categorical(df1['Month'],
                                 categories=['January', 'February', 'March', 'April', 'May', 'June',
                                             'July', 'August', 'September', 'October', 'November', 'December'],
                                 ordered=True)

    # ---------------- Beregeninger2 ---------------- #

    df2['Date'] = pd.to_datetime(df2['Date'])
    df2['Month'] = df2['Date'].dt.strftime('%B')

    df2['Hour'] = pd.Categorical(df2['Hour'].astype(str),
                                categories=[str(i) for i in range(1, 25)], ordered=True)
    df2['Month'] = pd.Categorical(df2['Month'],
                                 categories=['January', 'February', 'March', 'April', 'May', 'June',
                                             'July', 'August', 'September', 'October', 'November', 'December'],
                                 ordered=True)

    # ----------- FOR 1C MED TIMES ENDRINGER OG PRISGRUPPER -------
    '''df['Price_Group'] = np.where(df['Date'] < pd.to_datetime(start_date1), 'Before_ref', pd.cut(df['Price_NOK_kWh'],
                                                                                               bins=[0, 0.12, 0.55,
                                                                                                     1.77, 6.54],
                                                                                               labels=['Low', 'Medium',
                                                                                                       'High',
                                                                                                       'Very High'],
                                                                                               include_lowest=True)
                                 )

    df['Price_Group'] = pd.Categorical(df['Price_Group'],
                                       categories=['Before_ref', 'Low', 'Medium', 'High', 'Very High'],
                                       ordered=True)

    print(df['Price_Group'].value_counts())
    # ----------- 1C til hit -------------'''


    #her eg drive og styre:)))
    #fra copilot
    '''
    df1['Price_Group1'] = np.where(
        (df1['Date'] >= pd.to_datetime(start_date1)) &
        (df1['Date'] <= pd.to_datetime(end_date1)),
        'Before_ref',
        'After_ref'
    )

    print('her',df1)

    df2['Price_Group2'] = np.where(
        (df2['Date'] >= pd.to_datetime(start_date2)) &
        (df2['Date'] <= pd.to_datetime(end_date2)),
        'After_ref',
        'Before_ref'
    )

    
    # pris gruppering til år 1
    df1['Price_Group1'] = np.where(
        df1['Date'] < pd.to_datetime(start_date1),
        'Before_ref', 'After_ref'
    )

    df1['Price_Group1'] = pd.Categorical(df1['Price_Group1'],
                                       categories=['Before_ref'],
                                       ordered=True)

    print(df1['Price_Group1'].value_counts())

    # pris gruppering til år 2
    df2['Price_Group2'] = np.where(
        df2['Date'] < pd.to_datetime(start_date2),
        'After_ref', 'Before_ref'
    )

    df2['Price_Group2'] = pd.Categorical(df2['Price_Group2'],
                                        categories=['After_ref'],
                                        ordered=True)

    print(df2['Price_Group2'].value_counts())


'''
    # --- Regresjons analyse ---
    '''
    y, X = patsy.dmatrices('kWh/Metering_point ~ C(Price_Group1, Treatment(reference= "Before_ref" )) + Temperatur24 + '
                           'I(Temperatur24**2) + I(Temperatur24**3) + Temperatur72 + ' 
                           'C(Hour, Treatment(reference="1")) + C(Month, Treatment(reference="October"))',
                           data=df2, return_type='dataframe', NA_action='drop')
'''

    df1['Price_group'] = 'Before_ref'  # 2024-periode dette e pris
    df2['Price_group'] = 'After_ref'  # 2025-periode dette e pris

    df = pd.concat([df1, df2], ignore_index=True)


    pd.set_option('display.max_columns',None)
    print('hele dfen', df)

    formula = (
        'demand ~ '
        'Pris + C(Price_group, Treatment(reference="Before_ref"))  + '                                      # C(Price_group, Treatment(reference="Before_ref")) 
        'Temperatur24 + I(Temperatur24**2) + I(Temperatur24**3) + '
        'Temperatur72 + C(Hour, Treatment(reference="1")) + '
        'C(Month, Treatment(reference="October"))'
    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )


    model = sm.OLS(y, X).fit()
    print(model.summary())



    # ----------- PLOT AV RESULTATER ----------------- #



flex_sensitivitet(data,'NO1', Temp_Oslo, price_NO1)


