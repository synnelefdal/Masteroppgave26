import numpy as np
import pandas as pd
import statsmodels.api as sm
import patsy
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from linearmodels.panel.utility import AbsorbingEffectWarning
from matplotlib.patches import FancyArrowPatch
from linearmodels.panel import PanelOLS

from sklearn.linear_model import LinearRegression



data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO1 = pd.read_csv('All_Demand_Data/NO1_resten.csv', skiprows= [1, 2, 3], sep =';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO2 = pd.read_csv('All_Demand_Data/NO2_resten.csv', skiprows= [1, 2, 3], sep =';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO5 = pd.read_csv('All_Demand_Data/NO5_resten.csv', skiprows= [1, 2, 3], sep =';')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')
Temp_Stavanger = pd.read_csv('Temp_Stavanger.csv')

# ------------------------------- MODELL 2 M/TEMP ------------------------------- #


def Difference_in_Difference_temp(data_mNP, data_uNP, data_resten, price_area, Temp):

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

    df_temp = Temp[['Date', 'Hour', 'Lufttemperatur','Temp24']]
    #print(df_temp)

    # ------------ Dataframe ----------- #
    df_NP = pd.DataFrame(total_demand_NP)
    df_uNP = pd.DataFrame(total_demand_uNP)
    df_resten = pd.DataFrame(total_demand_resten)

    df = pd.concat([df_NP, df_uNP, df_resten], ignore_index=True)
    df = pd.merge(df, df_temp, on = ['Date', 'Hour'], how = 'left')

    df = df[df['kWh/Metering_point'] > 0].copy()
    #print(df.columns)

    df['Date'] = pd.to_datetime(df['Date'])

    reference_start = pd.Timestamp('2024-10-01')
    reference_end = pd.Timestamp('2024-10-31')

    treat_start = pd.Timestamp('2024-11-01')
    treat_end = pd.Timestamp('2025-09-30')

    df['treat_day'] = np.nan
    mask = (df['Date'] >= '2024-11-01') & (df['Date'] <= '2025-09-30')
    df.loc[mask, 'treat_day'] = (
            df.loc[mask, 'Date'] - pd.Timestamp('2024-11-01')
    ).dt.days
    df = df[
        ((df['Date'] >= reference_start) & (df['Date'] <= reference_end)) |
        ((df['Date'] >= treat_start) & (df['Date'] <= treat_end))
        ].copy()


    '''before_ref = (df['Date'] >= reference_start) & (df['Date'] <= reference_end)
    after_ref = (df['Date'] >= treat_start) & (df['Date'] <= treat_end)

    df['Period'] = np.select([before_ref, after_ref],
                              ['Reference', 'Treatment'],
                              default='Rest')

    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month'] = pd.Categorical(df['Month'],
                                 categories=['January', 'February', 'March', 'April', 'May', 'June',
                                             'July', 'August', 'September', 'October', 'November', 'December'],
                                 ordered=True)'''

    # --------- Model ------------ #
    df['entity'] = pd.Categorical(df['group_definition'],
                                  categories=['Uten Norgespris', 'Med Norgespris', 'Resten'],
                                  # Referanse = Uten Norgespris
                                  ordered=True)
    '''df['period'] = pd.Categorical(df['Period'],
                                  categories=['Reference', 'Treatment', 'Rest'],  # Reference = Reference
                                  ordered=True)'''

    df['log_y'] = np.log(df['kWh/Metering_point'])
    panel_df = df.set_index(['entity', 'time'], drop=False).sort_index()

    model = PanelOLS.from_formula(
        'log_y ~ 1 + C(entity, Treatment(reference="Uten Norgespris"))*C(treat_day) '
                '+ Temp24 + I(Temp24**2) + I(Temp24**3)'
                '+ C(entity, Treatment(reference="Uten Norgespris")):Temp24 '
                '+ C(entity, Treatment(reference="Uten Norgespris")):I(Temp24**2) '
                '+ C(entity, Treatment(reference="Uten Norgespris")):I(Temp24**3) '
                '+ TimeEffects',
        data=panel_df,
        drop_absorbed=True
    )

    res = model.fit(cov_type='clustered', cluster_time=True)

    #print(res)

    #print(res.params.head(20))
    #print(res.params.tail(20))
    #print(res.params.index)

    # --------- PLOT ----------

    params = res.params
    #conf_int = res.conf_int()
    mask = params.index.str.contains( r"\[T\.Med Norgespris\]:C\(treat_day\)")

    effects = params[mask]
    #conf = conf_int.loc[effects.index]

    df_plot = pd.DataFrame({
        'day': effects.index.str.extract(r'\[T\.(\d+)\.0\]')[0].astype(int),
        'beta': effects.values
    }).sort_values('day')

    df_plot['date'] = (
            pd.Timestamp('2024-11-01') +
            pd.to_timedelta(df_plot['day'], unit='D')
    )

    df_plot['pct'] = 100 * (np.exp(df_plot['beta']) - 1)
    #df_plot['pct_low'] = 100 * (np.exp(df_plot['ci_low']) - 1)
    #df_plot['pct_high'] = 100 * (np.exp(df_plot['ci_high']) - 1)

    plt.figure(figsize=(13, 6))

    plt.plot(
        df_plot['date'],
        df_plot['pct'],
        label='Estimated change in consumption relative to October 2024 for households with Norway price',
        color='black',
        linewidth = 1.5
    )

    '''plt.fill_between(
        df_plot['date'],
        df_plot['pct_low'],
        df_plot['pct_high'],
        color='gray',
        alpha=0.3,
        label='95 % KI'
    )'''

    # Referanser
    plt.axhline(0, color='red', linestyle='--', linewidth=1)
    plt.axvline(pd.Timestamp('2024-11-01'), color='blue', linestyle=':', linewidth=1)

    plt.xlabel('Date')
    plt.ylabel('Change in consumption (%)')
    plt.title('Daily DiD effect relative to October 2024')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


data_NO1 = Difference_in_Difference_temp(data_mNP_NO1,data_uNP_NO1,data_rest_NO1,'NO1',Temp_Oslo)
data_NO2 = Difference_in_Difference_temp(data_mNP_NO2,data_uNP_NO2,data_rest_NO2,'NO2',Temp_Stavanger)
data_NO5 = Difference_in_Difference_temp(data_mNP_NO5,data_uNP_NO5,data_rest_NO5,'NO5',Temp_Bergen)


