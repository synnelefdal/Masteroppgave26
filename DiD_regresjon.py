import numpy as np
import pandas as pd
import points
import statsmodels.api as sm
import patsy
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')


def DifferenceinDifference(data_mNP, data_uNP, price_area):
    # ------------------- Filterer for dato ---------- #
    start_date_before = '2024-10-01'
    end_date_before = '2025-01-31'

    start_date_after = '2025-10-01'
    end_date_after = '2026-01-31'

    # ----------- Endring til Date og Hour ------------ #
    data_mNP['start_time_utc'] = pd.to_datetime(data_mNP['start_time_utc'],
                                                format = '%Y-%m-%d %H:%M:%S',
                                                errors = 'coerce',
                                                utc = True)

    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)

    data_uNP['start_time_utc'] = pd.to_datetime(data_uNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_uNP['Date'] = data_uNP['start_time_utc'].dt.date
    data_uNP['Hour'] = data_uNP['start_time_utc'].dt.hour.astype(int)

    # ----------------- Demand; NP-Gruppen ------------------ #

    data_demand_NP = data_mNP[data_mNP['price_area'] == price_area].copy()
    data_demand_NP['Date'] = pd.to_datetime(data_demand_NP['Date'])
    data_demand_NP['Hour'] = data_demand_NP['Hour'].astype(int)

    data_demand_NP_filtered_before = data_demand_NP[(data_demand_NP['Date'] >= start_date_before) &
                                        (data_demand_NP['Date'] <= end_date_before)].copy()

    data_demand_NP_filtered_after = data_demand_NP[(data_demand_NP['Date'] >= start_date_after) &
                                        (data_demand_NP['Date'] <= end_date_after)].copy()
    #print(data_demand_NP_filtered_before)
    #print(data_demand_NP_filtered_after)

    data_demand_NP_filtered_before['kWh/Metering_point'] = data_demand_NP_filtered_before['consumption_kwh'] / data_demand_NP_filtered_before['metering_point_count']
    #print(data_demand_NP_filtered_before.head(3))

    data_demand_NP_filtered_after['kWh/Metering_point'] = data_demand_NP_filtered_after['consumption_kwh'] / data_demand_NP_filtered_after['metering_point_count']
    #print(data_demand_NP_filtered_after.head(3))

    total_demand_hour_NP_before = data_demand_NP_filtered_before.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_NP_after = data_demand_NP_filtered_after.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    #print(total_demand_hour_NP_before)
    #print(total_demand_hour_NP_after)

    # ----------------- Demand; Uten NP-Gruppen ------------------ #

    data_demand_UtenNP = data_uNP[data_uNP['price_area'] == price_area].copy()
    data_demand_UtenNP['Date'] = pd.to_datetime(data_demand_UtenNP['Date'])
    data_demand_UtenNP['Hour'] = data_demand_UtenNP['Hour'].astype(int)

    data_demand_UtenNP_filtered_before = data_demand_UtenNP[(data_demand_UtenNP['Date'] >= start_date_before) &
                                        (data_demand_UtenNP['Date'] <= end_date_before)].copy()

    data_demand_UtenNP_filtered_after = data_demand_UtenNP[(data_demand_UtenNP['Date'] >= start_date_after) &
                                        (data_demand_UtenNP['Date'] <= end_date_after)].copy()
    #print(data_demand_filtered1)
    #print(data_demand_filtered2)


    data_demand_UtenNP_filtered_before['kWh/Metering_point'] = data_demand_UtenNP_filtered_before['consumption_kwh'] / data_demand_UtenNP_filtered_before['metering_point_count']
    #print(data_demand_UtenNP_filtered_before.head(3))

    data_demand_UtenNP_filtered_after['kWh/Metering_point'] = data_demand_UtenNP_filtered_after['consumption_kwh'] / data_demand_UtenNP_filtered_after['metering_point_count']
    #print(data_demand_UtenNP_filtered_after.head(3))

    total_demand_hour_UtenNP_before = data_demand_UtenNP_filtered_before.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_UtenNP_after = data_demand_UtenNP_filtered_after.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()

    #print(total_demand_hour_UtenNP_before)
    #print(total_demand_hour_UtenNP_after)

    # -------- Merge data; NP-Gruppen u/Temp ----------- #
    df_NP_before = pd.DataFrame(total_demand_hour_NP_before)
    df_NP_after = pd.DataFrame(total_demand_hour_NP_after)

    df_NP = pd.concat([df_NP_before,df_NP_after], ignore_index=True)

    pd.set_option('display.max_columns', None)
    #print(df_NP)

    # ------------ Merge data; Uten NP-gruppen u/Temp----------- #
    df_UtenNP_before = pd.DataFrame(total_demand_hour_UtenNP_before)
    df_UtenNP_after = pd.DataFrame(total_demand_hour_UtenNP_after)

    df_UtenNP = pd.concat([df_UtenNP_before, df_UtenNP_after], ignore_index=True)

    pd.set_option('display.max_columns', None)
    #print(df_UtenNP)

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
    #df_NP['Group'] = 'Norgespris'  # 2024-periode
    #df_UtenNP['Group'] = 'Uten Norgespris'  # 2025-periode

    df_NP['Norgespris'] = 'Med_NP'  #Treatment
    df_UtenNP['Norgespris'] = 'Uten_NP'  #Treatment


    df = pd.concat([df_NP, df_UtenNP], ignore_index=True)
    df = df[df['kWh/Metering_point'] > 0].copy()

    cutoff = pd.Timestamp('2025-10-01')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Group'] = np.where(df['Date'] < cutoff, 'Before_ref', 'After_ref')   #Post

    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month'] = pd.Categorical(df['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)

    df['Hour'] = pd.Categorical(df['Hour'].astype(str),
                                 categories=[str(i) for i in range(0, 23+1)], ordered=True)


    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.max_rows', None)
    #print(df[['Date', 'Norgespris','Group']])
    #print(df)

    formula = (
        'np.log(Q("kWh/Metering_point")) ~ '
        'C(Group, Treatment(reference="Before_ref")) '
        '* C(Norgespris, Treatment(reference="Uten_NP")) '
        '+ C(Hour) + C(Month)'
    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())




def DifferenceinDifferenceTemp(data_mNP, data_uNP, price_area, Temp):
    # ------------------- Filterer for dato ---------- #
    start_date_before = '2024-10-01'
    end_date_before = '2025-01-31'

    start_date_after = '2025-10-01'
    end_date_after = '2026-01-31'

    # ----------- Endring til Date og Hour ------------ #
    data_mNP['start_time_utc'] = pd.to_datetime(data_mNP['start_time_utc'],
                                                format = '%Y-%m-%d %H:%M:%S',
                                                errors = 'coerce',
                                                utc = True)

    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)

    data_uNP['start_time_utc'] = pd.to_datetime(data_uNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_uNP['Date'] = data_uNP['start_time_utc'].dt.date
    data_uNP['Hour'] = data_uNP['start_time_utc'].dt.hour.astype(int)

    # ----------------- Demand; NP-Gruppen ------------------ #

    data_demand_NP = data_mNP[data_mNP['price_area'] == price_area].copy()
    data_demand_NP['Date'] = pd.to_datetime(data_demand_NP['Date'])
    data_demand_NP['Hour'] = data_demand_NP['Hour'].astype(int)

    data_demand_NP_filtered_before = data_demand_NP[(data_demand_NP['Date'] >= start_date_before) &
                                        (data_demand_NP['Date'] <= end_date_before)].copy()

    data_demand_NP_filtered_after = data_demand_NP[(data_demand_NP['Date'] >= start_date_after) &
                                        (data_demand_NP['Date'] <= end_date_after)].copy()
    #print(data_demand_NP_filtered_before)
    #print(data_demand_NP_filtered_after)

    data_demand_NP_filtered_before['kWh/Metering_point'] = data_demand_NP_filtered_before['consumption_kwh'] / data_demand_NP_filtered_before['metering_point_count']
    #print(data_demand_NP_filtered_before.head(3))

    data_demand_NP_filtered_after['kWh/Metering_point'] = data_demand_NP_filtered_after['consumption_kwh'] / data_demand_NP_filtered_after['metering_point_count']
    #print(data_demand_NP_filtered_after.head(3))

    total_demand_hour_NP_before = data_demand_NP_filtered_before.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_NP_after = data_demand_NP_filtered_after.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    #print(total_demand_hour_NP_before)
    #print(total_demand_hour_NP_after)

    # ----------------- Demand; Uten NP-Gruppen ------------------ #

    data_demand_UtenNP = data_uNP[data_uNP['price_area'] == price_area].copy()
    data_demand_UtenNP['Date'] = pd.to_datetime(data_demand_UtenNP['Date'])
    data_demand_UtenNP['Hour'] = data_demand_UtenNP['Hour'].astype(int)

    data_demand_UtenNP_filtered_before = data_demand_UtenNP[(data_demand_UtenNP['Date'] >= start_date_before) &
                                        (data_demand_UtenNP['Date'] <= end_date_before)].copy()

    data_demand_UtenNP_filtered_after = data_demand_UtenNP[(data_demand_UtenNP['Date'] >= start_date_after) &
                                        (data_demand_UtenNP['Date'] <= end_date_after)].copy()
    #print(data_demand_filtered1)
    #print(data_demand_filtered2)


    data_demand_UtenNP_filtered_before['kWh/Metering_point'] = data_demand_UtenNP_filtered_before['consumption_kwh'] / data_demand_UtenNP_filtered_before['metering_point_count']
    #print(data_demand_UtenNP_filtered_before.head(3))

    data_demand_UtenNP_filtered_after['kWh/Metering_point'] = data_demand_UtenNP_filtered_after['consumption_kwh'] / data_demand_UtenNP_filtered_after['metering_point_count']
    #print(data_demand_UtenNP_filtered_after.head(3))

    total_demand_hour_UtenNP_before = data_demand_UtenNP_filtered_before.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_UtenNP_after = data_demand_UtenNP_filtered_after.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()

    #print(total_demand_hour_UtenNP_before)
    #print(total_demand_hour_UtenNP_after)

    # -------------- Temperatur --------------- #

    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(float)

    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(window=24, min_periods=1).mean()
    Temp['Temp72'] = Temp['Lufttemperatur'].rolling(window=72, min_periods=1).mean()

    Temp_filtered_before = Temp[(Temp['Date'] >= start_date_before) &
                          (Temp['Date'] <= end_date_before)].copy()

    Temp_filtered_after = Temp[(Temp['Date'] >= start_date_after) &
                          (Temp['Date'] <= end_date_after)].copy()

    total_temp_hour_before = Temp_filtered_before.groupby(['Date', 'Hour', 'Temp24', 'Temp72'])['Lufttemperatur'].sum().reset_index()
    total_temp_hour_after = Temp_filtered_after.groupby(['Date', 'Hour', 'Temp24', 'Temp72'])['Lufttemperatur'].sum().reset_index()

    #print(total_temp_hour_before)
    #print(total_temp_hour_after)

    # -------- Merge data; NP-Gruppen m/Temp ----------- #
    df_NP_before = pd.DataFrame(total_demand_hour_NP_before)
    df_NP_after = pd.DataFrame(total_demand_hour_NP_after)

    df_NP = pd.concat([df_NP_before, df_NP_after], ignore_index=True)

    pd.set_option('display.max_columns', None)

    # pd.set_option('display.max_columns', None)
    # print(df_NP.head(3))

    # ------------ Merge data; Uten NP-gruppen m/temp ----------- #
    df_UtenNP_before = pd.DataFrame(total_demand_hour_UtenNP_before)
    df_UtenNP_after = pd.DataFrame(total_demand_hour_UtenNP_after)

    df_UtenNP = pd.concat([df_UtenNP_before, df_UtenNP_after], ignore_index=True)

    pd.set_option('display.max_columns', None)

    # pd.set_option('display.max_columns', None)
    # print(df_NP.head(3))

    # ----------------- Beregninger; NP-Gruppen ------------------- #
    '''df_NP['Date'] = pd.to_datetime(df_NP['Date'])
    df_NP['Month'] = df_NP['Date'].dt.strftime('%B')

    df_NP['Hour'] = pd.Categorical(df_NP['Hour'].astype(str),
                                 categories=[str(i) for i in range(1, 25)], ordered=True)
    df_NP['Month'] = pd.Categorical(df_NP['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)'''

    # ----------------- Beregninger; Uten NP-Gruppen ------------------- #
    '''df_UtenNP['Date'] = pd.to_datetime(df_UtenNP['Date'])
    df_UtenNP['Month'] = df_UtenNP['Date'].dt.strftime('%B')

    df_UtenNP['Hour'] = pd.Categorical(df_UtenNP['Hour'].astype(str),
                                 categories=[str(i) for i in range(1, 25)], ordered=True)
    df_UtenNP['Month'] = pd.Categorical(df_UtenNP['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)'''

    # --------------- Regresjonsanalyse ------------- #
    df_Temp_before = pd.DataFrame(total_temp_hour_before)
    df_Temp_after = pd.DataFrame(total_temp_hour_after)
    df_Temp = pd.concat([df_Temp_before, df_Temp_after], ignore_index=True)

    #df_NP['Group'] = 'Norgespris'  # 2024-periode
    #df_UtenNP['Group'] = 'Uten Norgespris'  # 2025-periode

    df_NP['Norgespris'] = 'Med_NP'  #
    df_UtenNP['Norgespris'] = 'Uten_NP'  #

    df_NP = pd.concat([df_NP, df_UtenNP], ignore_index = True)

    df = pd.merge(df_NP, df_Temp, on = ['Date', 'Hour'], how = 'left')
    df = df[df['kWh/Metering_point'] > 0].copy()

    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.max_rows', None)
    #print(df)

    cutoff = pd.Timestamp('2025-10-01')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Group'] = np.where(df['Date'] < cutoff, 'Before_ref', 'After_ref')

    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month'] = pd.Categorical(df['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)

    df['Hour'] = pd.Categorical(df['Hour'].astype(str),
                                 categories=[str(i) for i in range(0, 23+1)], ordered=True)

    df['Lufttemperatur'] = df['Lufttemperatur']



    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.max_rows', None)
    #print(df[['Date', 'Norgespris','Group']])
    #print(df)

    formula = (
        'np.log(Q("kWh/Metering_point")) ~ '
        'C(Group, Treatment(reference="Before_ref")) * C(Norgespris, Treatment(reference="Uten_NP")) '
        '+ Temp24'
        '+ Temp24 * C(Norgespris, Treatment(reference="Uten_NP"))'
        '+ C(Hour) + C(Month)'
    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())




DifferenceinDifference(data_mNP_NO1, data_uNP_NO1, 'NO1')  # Ved NO1 bruk Temp_Oslo, og ved NO5 bruk Temp_Bergen
#DifferenceinDifferenceTemp(data_mNP_NO1, data_uNP_NO1, 'NO1', Temp_Oslo)
#DifferenceinDifferenceTemp2(data_mNP_NO1, data_uNP_NO1, 'NO1', Temp_Oslo, use_log=True, verbose=True)
#DifferenceinDifferenceTemp3(data_mNP_NO1, data_uNP_NO1, 'NO1', Temp_Oslo, verbose=True)






