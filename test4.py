import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt


import pandas as pd

data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO1 = pd.read_csv('All_Demand_Data/NO1_resten.csv', skiprows= [1, 2, 3], sep =';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO2 = pd.read_csv('All_Demand_Data/NO2_resten.csv', skiprows= [1, 2, 3], sep =';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', skiprows= [1, 2, 3], sep=';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', skiprows= [1, 2, 3], sep=';')
data_rest_NO5 = pd.read_csv('All_Demand_Data/NO5_resten.csv', skiprows= [1, 2, 3], sep =';')

Temp_Bergen = pd.read_csv('Temperature_Files/Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temperature_Files/Temp_Oslo.csv')
Temp_Stavanger = pd.read_csv('Temperature_Files/Temp_Stavanger.csv')

# ------------------------------- DAGLIG DiD (LOG) MED TEMP ------------------------------- #

def Difference_in_Difference_temp_daily(
        data_mNP, data_uNP, data_resten, price_area, Temp
):
    import numpy as np
    import pandas as pd
    import statsmodels.formula.api as smf
    import matplotlib.pyplot as plt

    # ---------- Klargjør data ---------- #
    def prepare_demand(df):
        df['start_time_utc'] = pd.to_datetime(
            df['start_time_utc'],
            errors='coerce',
            utc=True
        )
        df['Date'] = df['start_time_utc'].dt.date
        df['Hour'] = df['start_time_utc'].dt.hour
        df = df[df['price_area'] == price_area].copy()
        df['kWh/Metering_point'] = df['consumption_kwh'] / df['metering_point_count']
        return df

    df = pd.concat([
        prepare_demand(data_mNP),
        prepare_demand(data_uNP),
        prepare_demand(data_resten)
    ])

    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['kWh/Metering_point'] > 0]
    df['log_kWh'] = np.log(df['kWh/Metering_point'])

    # VIKTIG: juster denne hvis group_definition har annen struktur
    df['group'] = np.where(
        df['group_definition'].astype(str).str.contains('mNP', case=False),
        'NP',
        'Control'
    )

    # ---------- Temperatur ---------- #
    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(24, min_periods=1).mean()

    df = pd.merge(df, Temp[['Date', 'Hour', 'Temp24']], on=['Date', 'Hour'], how='left')

    # ---------- Perioder ---------- #
    df_ref = df[(df['Date'] >= '2024-10-01') & (df['Date'] <= '2024-10-31')].copy()
    df_ref['Post'] = 0

    all_days = pd.date_range('2024-11-01', '2025-09-30', freq='D')
    results = []

    for day in all_days:
        df_day = df[df['Date'] == day].copy()
        df_day['Post'] = 1

        df_did = pd.concat([df_ref, df_day])

        # hopp over dager uten to grupper
        if df_did['group'].nunique() < 2:
            continue

        model = smf.ols(
            "log_kWh ~ Post * C(group) + Temp24",
            data=df_did
        ).fit()

        coef = 'Post:C(group)[T.NP]'
        if coef in model.params:
            beta3 = model.params[coef]
            did_percent = (np.exp(beta3) - 1) * 100

            results.append({
                'Date': day,
                'beta_3': beta3,
                'DiD_percent': did_percent
            })

    # ---------- Resultater ---------- #
    if len(results) == 0:
        print("❌ Ingen dager med identifiserbar DiD-effekt.")
        #return pd.DataFrame()

    results_df = pd.DataFrame(results)

    ''''# ---------- Plot ---------- #
    plt.figure(figsize=(12, 5))
    plt.plot(results_df['Date'], results_df['DiD_percent'])
    plt.axhline(0, linestyle='--', alpha=0.6)
    plt.ylabel('DiD (%) = (exp(beta₃) − 1) × 100')
    plt.xlabel('Dato')
    plt.title(f'Daglig DiD – {price_area}')
    plt.tight_layout()
    plt.show()'''

    #nyplotting
    # ---------- Resultater & plot ---------- #
    all_days = pd.date_range('2024-11-01', '2025-09-30', freq='D')
    results_df = pd.DataFrame({'Date': all_days})

    if len(results) > 0:
        temp_df = pd.DataFrame(results)
        results_df = results_df.merge(temp_df, on='Date', how='left')
    else:
        results_df['DiD_percent'] = np.nan

    plt.figure(figsize=(12, 5))
    plt.plot(
        results_df['Date'],
        results_df['DiD_percent'],
        marker='o',
        linestyle='-'
    )
    plt.axhline(0, linestyle='--', alpha=0.6)
    plt.ylabel('DiD (%) = (exp(beta₃) − 1) × 100')
    plt.xlabel('Dato')
    plt.title(f'Daglig DiD – {price_area}')
    plt.tight_layout()
    plt.show()

    return results_df



# ------------------ EKSEMPEL: NO1 ------------------ #
did_NO1 = Difference_in_Difference_temp_daily(
    data_mNP_NO1,
    data_uNP_NO1,
    data_rest_NO1,
    'NO1',
    Temp_Oslo
)
