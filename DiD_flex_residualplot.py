import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
import matplotlib.pyplot as plt
import time

start = time.time()



# -------------------------------- ALLE CSV FILER MED FORBRUKSDATA -------------------------------- #

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


# -------------------------------- Temperatur data for alle prissoner -------------------------------- #

Temp_Bergen = pd.read_csv('Temperature_Files/bergen_converted.csv')
Temp_Oslo = pd.read_csv('Temperature_Files/oslo_converted.csv')
Temp_Stavanger = pd.read_csv('Temperature_Files/stavanger_converted.csv')

# -------------------------------- START PÅ KODE, DONT TOUCH -------------------------------- #

def Difference_in_Difference_Flex(data_mNP, data_uNP, data_resten, Temp, price_area, start_date_before, end_date_before, start_date_after, end_date_after):

    # -------------- Norgespris gruppen -------------- #
    data_mNP['start_time_utc'] = pd.to_datetime(data_mNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)
    data_mNP['group_definition'] = "Med Norgespris"
    data_demand_NP = data_mNP[data_mNP['price_area'] == price_area].copy()

    #print(data_mNP)

    data_demand_NP['kWh/Metering_point'] = data_demand_NP['consumption_kwh'] / data_demand_NP['metering_point_count']


    total_demand_NP = data_demand_NP.groupby(['Date', 'Hour', 'norgespris_group', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()


    #print(total_demand_NP)

    total_demand_NP['Date'] = pd.to_datetime(total_demand_NP['Date'], errors='coerce')

    total_demand_NP['time'] = (
            total_demand_NP['Date'] +
            pd.to_timedelta(total_demand_NP['Hour'], unit='h')
    )

    total_demand_NP['time'] = total_demand_NP['time'].dt.tz_localize('UTC')

    # print(total_demand_NP)

    # -------------- Ikke Norgespris gruppen -------------- #
    data_uNP['start_time_utc'] = pd.to_datetime(data_uNP['start_time_utc'],
                                                format='%Y-%m-%d %H:%M:%S',
                                                errors='coerce',
                                                utc=True)

    data_uNP['Date'] = data_uNP['start_time_utc'].dt.date
    data_uNP['Hour'] = data_uNP['start_time_utc'].dt.hour.astype(int)
    data_uNP['group_definition'] = "Uten Norgespris"
    data_demand_uNP = data_uNP[data_uNP['price_area'] == price_area].copy()

    data_demand_uNP['kWh/Metering_point'] = data_demand_uNP['consumption_kwh'] / data_demand_uNP['metering_point_count']
    total_demand_uNP = data_demand_uNP.groupby(['Date', 'Hour', 'norgespris_group', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()

    total_demand_uNP['Date'] = pd.to_datetime(total_demand_uNP['Date'], errors='coerce')

    total_demand_uNP['time'] = (
            total_demand_uNP['Date'] +
            pd.to_timedelta(total_demand_uNP['Hour'], unit='h')
    )

    total_demand_uNP['time'] = total_demand_uNP['time'].dt.tz_localize('UTC')

    # print(total_demand_uNP)

    # -------------- Resten -------------- #
    data_resten['start_time_utc'] = pd.to_datetime(data_resten['start_time_utc'],
                                                   format='%Y-%m-%d %H:%M:%S',
                                                   errors='coerce',
                                                   utc=True)

    data_resten['Date'] = data_resten['start_time_utc'].dt.date
    data_resten['Hour'] = data_resten['start_time_utc'].dt.hour.astype(int)
    data_resten['group_definition'] = "Resten"
    data_demand_resten = data_resten[data_resten['price_area'] == price_area].copy()

    data_demand_resten['kWh/Metering_point'] = data_demand_resten['consumption_kwh'] / data_demand_resten[
        'metering_point_count']
    total_demand_resten = data_demand_resten.groupby(['Date', 'Hour', 'norgespris_group', 'group_definition'])[
        'kWh/Metering_point'].sum().reset_index()

    total_demand_resten['Date'] = pd.to_datetime(total_demand_resten['Date'], errors='coerce')

    total_demand_resten['time'] = (
            total_demand_resten['Date'] +
            pd.to_timedelta(total_demand_resten['Hour'], unit='h')
    )

    total_demand_resten['time'] = total_demand_resten['time'].dt.tz_localize('UTC')

    # print(total_demand_resten)

    # -------------- Temperatur -------------- #
    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(float)
    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(window=24, min_periods=1).mean()
    #Temp['Temp24^2'] = Temp['Temp24'] **2
    #Temp['Temp24^3'] = Temp['Temp24'] ** 3

    df_temp = Temp[['Date', 'Hour', 'Temp24']]
    #print(df_temp)

    # -------------- Dataframe -------------- #
    df_NP = pd.DataFrame(total_demand_NP)
    df_uNP = pd.DataFrame(total_demand_uNP)
    df_resten = pd.DataFrame(total_demand_resten)

    #print(df_uNP)

    df = pd.concat([df_NP, df_uNP, df_resten], ignore_index=True)
    df = pd.merge(df, df_temp, on = ['Date', 'Hour'], how = 'left')

    df = df[df['kWh/Metering_point'] > 0].copy()
    #print(df)

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

    # -------------- Model -------------- #
    df['entity'] = pd.Categorical(df['group_definition'],
                                  categories = ['Uten Norgespris','Med Norgespris', 'Resten'],
                                  # Referanse = Uten Norgespris
                                  ordered=True)
    df['period'] = pd.Categorical(df['Period'],
                                  categories=['Reference', 'Treatment', 'Rest'],  # Reference = Reference
                                  ordered=True)
    df['log_y'] = df['kWh/Metering_point']    # -------------- HER MÅ NP.LOG LEGGES TIL FOR Å FÅ PROSENT IGJEN -------------- #

    results = []
    results_temp = []
    all_fitted = []
    all_residuals = []

    all_fitted_temp = []
    all_residuals_temp = []
    for h in range(24):
        sub = df[df['Hour'] == h].copy()

        if sub.empty:
            results.append({
                'Hour': h,
                'DiD': np.nan,
                'CI_low': np.nan,
                'CI_high': np.nan
            })
            continue

        panel_df = sub.set_index(['entity', 'time'], drop = False)

        model = PanelOLS.from_formula(
        'np.log(log_y) ~ 1 + C(entity)*C(period) + TimeEffects',
            data = panel_df,
            drop_absorbed=True
            #check_rank=False

        )

        model_temp = PanelOLS.from_formula(
        'np.log(log_y) ~ 1 + C(entity)*C(period) '
                '+  Temp24 + I(Temp24**2) + I(Temp24**3)'
                '+ C(entity):Temp24 '
                '+ C(entity):I(Temp24**2)'
                '+ C(entity):I(Temp24**3)'
                '+ TimeEffects',
            data = panel_df,
            drop_absorbed=True
            #check_rank=False
        )

        res = model.fit(cov_type='clustered', cluster_time=True)
        #print(res)
        res_temp = model_temp.fit(cov_type='clustered', cluster_time=True)

        # ---- Residualplot ----

        # --- Uten temp ---

        fitted = res.fitted_values.squeeze()
        residuals = res.resids.squeeze()
        effects = res.estimated_effects.squeeze()

        fitted_full = fitted + effects
        idx = res.resids.index

        fitted_full = fitted_full.loc[idx].values
        residuals = residuals.loc[idx].values
        y_true = np.log(panel_df.loc[idx, 'log_y'].values)

        reconstructed = fitted_full + residuals

        print(f"Time {h}: Stemmer reconstructed y med log_y?")
        print(np.allclose(y_true, reconstructed, atol=1e-6))

        all_fitted.extend(fitted_full)
        all_residuals.extend(residuals)

        # --- Med temp ---

        fitted_t = res_temp.fitted_values.squeeze()
        residuals_t = res_temp.resids.squeeze()
        effects_t = res_temp.estimated_effects.squeeze()

        fitted_full_t = fitted_t + effects_t
        idx_t = res_temp.resids.index

        fitted_full_t = fitted_full_t.loc[idx_t].values
        residuals_t = residuals_t.loc[idx_t].values
        y_true_t = np.log(panel_df.loc[idx_t, 'log_y'].values)

        reconstructed_t = fitted_full_t + residuals_t

        print(f"Time {h} (temp): Stemmer reconstructed y med log_y?")
        print(np.allclose(y_true_t, reconstructed_t, atol=1e-6))

        all_fitted_temp.extend(fitted_full_t)
        all_residuals_temp.extend(residuals_t)

    # ---- Residualplot U/Temp ----

    plt.figure(figsize=(8, 5))
    plt.scatter(all_fitted, all_residuals, alpha=0.3)
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel("Predicted values", fontsize=25)
    plt.ylabel("Residuals", fontsize=25)
    plt.title("Residualplot without temp")
    plt.grid(True)
    plt.show()

    # ---- Residualplot M/Temp ----

    plt.figure(figsize=(8, 5))
    plt.scatter(all_fitted_temp, all_residuals_temp, alpha=0.3)
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel("Predicted values", fontsize=25)
    plt.ylabel("Residuals", fontsize=25)
    plt.title("Residualplot with temp)")
    plt.grid(True)
    plt.show()


# ------------------------------------ BESTEMMELSE AV HVILKE MND SOM ER MED OG UTEN NORGESPRIS ------------------------------------ #


#BACKUP N01: data_NO1_NPoct, data_NO1_NPnov, data_NO1_NPdec,data_NO1_NPjan,data_NO1_NPfeb,data_NO1_NPmars,data_NO1_NPapril
#BACKUP N02: data_NO2_NPoct, data_NO2_NPnov, data_NO2_NPdec,data_NO2_NPjan,data_NO2_NPfeb,data_NO2_NPmars,data_NO2_NPapril
#BACKUP N05: data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec,data_NO5_NPjan,data_NO5_NPfeb,data_NO5_NPmars,data_NO5_NPapril


# ------------------------------------ ENDRE PARAMETER MELLOM HER FOR Å ENDRE ANALYSEN ------------------------------------ #

start_date_before = '2025-01-01'
end_date_before = '2025-01-31'

start_date_after = '2026-01-01'
end_date_after = '2026-01-31'

data_NO2_mNP = pd.concat([data_NO2_NPoct, data_NO2_NPnov, data_NO2_NPdec, data_NO2_NPjan], ignore_index=True)

data_NO2_rest = pd.concat([data_NO2_NPfeb, data_NO2_NPmars, data_NO2_NPapril], ignore_index=True)

data_NO2_uNP_gr = pd.concat([data_NO2_uNP], ignore_index=True)

# ------------------------------------ STOPP AV ENDRING HER, DONT TOUCH ------------------------------------ #

Difference_in_Difference_Flex(data_NO2_mNP, data_NO2_uNP_gr, data_NO2_rest, Temp_Stavanger, 'NO2', start_date_before, end_date_before, start_date_after, end_date_after)
