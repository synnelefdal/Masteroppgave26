import numpy as np
import pandas as pd
import statsmodels.api as sm
import patsy
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from linearmodels.panel.utility import AbsorbingEffectWarning
from matplotlib.patches import FancyArrowPatch
from linearmodels.panel import PanelOLS


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

    df_temp = Temp[['Date', 'Hour', 'Temp24']]
    #print(df_temp)

    # ------------ Dataframe ----------- #
    df_NP = pd.DataFrame(total_demand_NP)
    df_uNP = pd.DataFrame(total_demand_uNP)
    df_resten = pd.DataFrame(total_demand_resten)

    df = pd.concat([df_NP, df_uNP, df_resten], ignore_index=True)
    df = pd.merge(df, df_temp, on = ['Date', 'Hour'], how = 'left')

    df = df[df['kWh/Metering_point'] > 0].copy()
    #print(df)

    start_date_before = '2025-01-01'
    end_date_before = '2025-01-31'

    start_date_after = '2026-01-01'
    end_date_after = '2026-01-31'

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

    # --------- Model ------------ #
    df['entity'] = pd.Categorical(df['group_definition'],
                                  categories=['Uten Norgespris', 'Med Norgespris', 'Resten'],
                                  # Referanse = Uten Norgespris
                                  ordered=True)
    df['period'] = pd.Categorical(df['Period'],
                                  categories=['Reference', 'Treatment', 'Rest'],  # Reference = Reference
                                  ordered=True)
    df['log_y'] = np.log(df['kWh/Metering_point'])
    panel_df = df.set_index(['entity', 'time'], drop=False).sort_index()

    model = PanelOLS.from_formula(
        'log_y ~ 1 + C(entity, Treatment(reference="Uten Norgespris"))*C(period) '
                '+  Temp24 + I(Temp24**2) + I(Temp24**3)'
                '+ C(entity, Treatment(reference="Uten Norgespris")):Temp24 '
                '+ C(entity, Treatment(reference="Uten Norgespris")):I(Temp24**2) '
                '+ C(entity, Treatment(reference="Uten Norgespris")):I(Temp24**3) '
                '+ TimeEffects',
        data=panel_df,
        drop_absorbed=True
    )

    res = model.fit(cov_type='clustered', cluster_time=True)

    #print(res)

    # -------- Utregning --------- #
    print('----------- PanelOLS -----------------')
    beta3 = res.params["C(entity, Treatment(reference='Uten Norgespris'))[T.Med Norgespris]:C(period)[T.Treatment]"]
    DiD = (np.exp(beta3) - 1) * 100

    ci_low, ci_high = res.conf_int().loc["C(entity, Treatment(reference='Uten Norgespris'))[T.Med Norgespris]:C(period)[T.Treatment]"]
    DiD_low = (np.exp(ci_low) - 1) * 100
    DiD_high = (np.exp(ci_high) - 1) * 100

    print(f'DiD prosent for {price_area}: {DiD:.2f}%')
    print(f'KI: [{DiD_low:.2f}%, {DiD_high:.2f}%]')

    # -------- Figur ---------- #
    #df_before = df[df['Period'] == 'Reference'].copy()
    df_plot = df[df['Period'].isin(['Reference', 'Rest'])].copy()
    df_plot = df_plot[df_plot['entity'].isin(['Uten Norgespris', 'Med Norgespris'])]

    remove_oct = (df_plot['Date'] >= pd.to_datetime('2025-10-01')) & \
                      (df_plot['Date'] <= pd.to_datetime('2025-10-31'))

    df_plot = df_plot[~remove_oct]

    df_plot = df_plot.dropna(subset=['Temp24'])
    group_means = df_plot.groupby('entity')['kWh/Metering_point'].mean()

    df_plot['rel_consumption'] = df_plot.apply(
        lambda r: r['kWh/Metering_point'] / group_means.loc[r['entity']],
        axis=1
    )

    # Plot
    plt.figure(figsize=(9, 6))

    colors = {
        'Uten Norgespris': '#1f77b4',
        'Med Norgespris': '#d62728'
    }
    df_plot['entity'] = df_plot['entity'].cat.remove_unused_categories()
    df_plot['temp_bin'] = (df_plot['Temp24'] / 0.5).round() * 0.5

    for grp, sub in df_plot.groupby('entity'):
        trend = sub.groupby('temp_bin')['rel_consumption'].mean().reset_index()
        trend = trend.sort_values('temp_bin')
        plt.plot(
            trend['temp_bin'], trend['rel_consumption'],
            color=colors.get(grp, 'gray'), linewidth=2,
            label=f'{grp}'
        )

    plt.axhline(1.0, linestyle='--', color='gray', alpha=0.7)
    plt.xlabel('Temperatur [°C]')
    plt.ylabel('Gjennomsnits forbruk [kWh/målepunkt]')
    plt.title(f'Temperaturfølsomhet før Norgespris – {price_area}')
    plt.grid(True, alpha=0.25)
    plt.legend()

    plt.tight_layout()
    plt.show()

    return panel_df

def plot_temp_all_zones(datasets):

    plt.figure(figsize=(10, 6))

    colors = {
        "NO1": "#1f77b4",
        "NO2": "#2ca02c",
        "NO5": "#d62728"
    }

    for zone_name, df in datasets:
        df = df.copy()
        df = df.reset_index(drop=True)

        # --- Filtrering ---
        df_plot = df[df['Period'].isin(['Reference', 'Rest'])].copy()
        df_plot = df_plot[df_plot['entity'].isin(['Uten Norgespris', 'Med Norgespris'])]

        translation_map = {
            'Med Norgespris': 'With Norway Price',
            'Uten Norgespris': 'Without Norway Price'
        }

        df_plot['entity'] = df_plot['entity'].map(translation_map)

        df_plot['entity'] = df_plot['entity'].astype('category')
        df_plot['entity'] = df_plot['entity'].cat.remove_unused_categories()

        # Fjern oktober
        remove_oct = (df_plot['Date'] >= pd.to_datetime('2025-10-01')) & \
                     (df_plot['Date'] <= pd.to_datetime('2025-10-31'))
        df_plot = df_plot[~remove_oct]

        df_plot = df_plot.dropna(subset=['Temp24'])

        # --- Normalisering ---
        group_means = df_plot.groupby('entity')['kWh/Metering_point'].mean()
        df_plot['rel_consumption'] = df_plot.apply(
            lambda r: r['kWh/Metering_point'] / group_means.loc[r['entity']],
            axis=1
        )

        # Temperatur-bin
        df_plot['temp_bin'] = (df_plot['Temp24'] / 0.5).round() * 0.5

        entity_linestyle = {
            "Without Norway Price": "--",
            "With Norway Price": "-"
        }

        # --- Beregn trend per sone ---
        for entity_name, sub in df_plot.groupby('entity'):
            trend = (
                sub.groupby('temp_bin')['rel_consumption'].mean().reset_index().sort_values('temp_bin')
            )
            plt.plot(
                trend['temp_bin'],
                trend['rel_consumption'],
                label=f"{zone_name} – {entity_name}",
                linewidth=2,
                color=colors.get(zone_name, 'gray'),
                linestyle=entity_linestyle[entity_name]

            )
        #trend = df_plot.groupby('temp_bin')['rel_consumption'].mean().reset_index()

        '''# --- Print data ---
        print(f"\n===== Temperaturdata for {zone_name} =====")
        print(trend)

        # --- Plot ---
        plt.plot(
            trend['temp_bin'], trend['rel_consumption'],
            label=zone_name,
            linewidth=2,
            color=colors.get(zone_name, 'gray')
        )'''

    plt.axhline(1.0, linestyle='--', color='gray', alpha=0.7)
    plt.xlabel('Temperature [°C]')
    plt.ylabel('Average Consumption [kWh/metering point]')
    plt.title('Temperature Sensitivity Before Norway Price – NO1, NO2, NO5')
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.show()

data_NO1 = Difference_in_Difference_temp(data_mNP_NO1,data_uNP_NO1,data_rest_NO1,'NO1',Temp_Oslo)
data_NO2 = Difference_in_Difference_temp(data_mNP_NO2,data_uNP_NO2,data_rest_NO2,'NO2',Temp_Stavanger)
data_NO5 = Difference_in_Difference_temp(data_mNP_NO5,data_uNP_NO5,data_rest_NO5,'NO5',Temp_Bergen)


print(type(data_NO1))
print(type(data_NO2))
print(type(data_NO5))



plot_temp_all_zones([
    ("NO1", data_NO1),
    ("NO2", data_NO2),
    ("NO5", data_NO5)
])
