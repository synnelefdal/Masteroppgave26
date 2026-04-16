
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

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')
Temp_Stavanger = pd.read_csv('Temp_Stavanger.csv')


def Difference_in_Difference_temp_hourly(
    data_mNP, data_uNP, data_resten, price_area, Temp
):
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from linearmodels.panel import PanelOLS

    print("\n========== START DIFFERENCE-IN-DIFFERENCE (HOURLY) ==========\n")

    # -----------------------------------------------------------
    # 1. Klargjør etterspørselsdata (samme som hos deg)
    # -----------------------------------------------------------
    def prep(df):
        df = df.copy()
        df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True)
        df['Date'] = df['start_time_utc'].dt.date
        df['Hour'] = df['start_time_utc'].dt.hour
        df = df[df['price_area'] == price_area]
        df['kWh/Metering_point'] = (
            df['consumption_kwh'] / df['metering_point_count']
        )
        df = (
            df.groupby(['Date', 'Hour', 'group_definition'])
            ['kWh/Metering_point']
            .sum()
            .reset_index()
        )
        df['Date'] = pd.to_datetime(df['Date'])
        df['time'] = (
            df['Date'] + pd.to_timedelta(df['Hour'], unit='h')
        ).dt.tz_localize('UTC')
        return df

    df = pd.concat([
        prep(data_mNP),
        prep(data_uNP),
        prep(data_resten)
    ], ignore_index=True)

    # -----------------------------------------------------------
    # 2. Temperatur
    # -----------------------------------------------------------
    Temp = Temp.copy()
    Temp['Date'] = pd.to_datetime(Temp['Date'])

    Temp = Temp.sort_values(['Date', 'Hour'])

    Temp['time'] = (
            Temp['Date'] + pd.to_timedelta(Temp['Hour'], unit='h')
    ).dt.tz_localize('UTC')

    #Temp['Hour'] = Temp['Hour'].astype(int)
    Temp['Temp24'] = (
        Temp['Lufttemperatur']
        .rolling(window=24, min_periods=1)
        .mean()
    )




    '''df = df.merge(
        Temp[['Date', 'Hour', 'Temp24']],
        on=['Date', 'Hour'],
        how='left'
    )'''

    df = df.merge(
        Temp[['time', 'Temp24']],
        on='time',
        how='left'
    )

    #print(df[['time', 'Temp24']].head())
    #print(df['Temp24'].isna().mean())

    df = df[df['Temp24'].notna()].copy()

    df = df[df['kWh/Metering_point'] > 0].copy()

    # -----------------------------------------------------------
    # 3. Referanse + behandling
    # -----------------------------------------------------------
    ref_start = pd.Timestamp('2024-10-01')
    ref_end   = pd.Timestamp('2024-10-31 23:00')

    treat_start = pd.Timestamp('2024-11-01', tz='UTC')

    df['is_post'] = (df['time'] >= treat_start).astype(int)

    # Time siden behandling (kun post)
    df['treat_hour'] = np.where(
        df['is_post'] == 1,
        ((df['time'] - treat_start).dt.total_seconds() / 3600).astype(int),
        -1
    )

    # -----------------------------------------------------------
    # 4. Entity / panel
    # -----------------------------------------------------------
    df['entity'] = pd.Categorical(
        df['group_definition'],
        categories=['Uten Norgespris', 'Med Norgespris', 'Resten'],
        ordered=True
    )

    df['log_y'] = np.log(df['kWh/Metering_point'])

    panel_df = df.set_index(['entity', 'time'], drop=False).sort_index()

    # -----------------------------------------------------------
    # 5. MODELL – ca 8000 DiD-koeffisienter
    # -----------------------------------------------------------
    print(df['treat_hour'].value_counts().sort_index().head())

    '''print(
        df.loc[df['is_post'] == 1, 'time']
        .agg(['min', 'max', 'count'])
    )'''


    print("Estimerer panelmodell med timevise treatment-effekter ...\n")

    model = PanelOLS.from_formula(
        """
        log_y ~ 1
        + C(entity, Treatment(reference="Uten Norgespris"))
            : C(treat_hour, Treatment(reference=-1))
        + Temp24 + I(Temp24**2) + I(Temp24**3)
        + TimeEffects
        """,
        data=panel_df,
        drop_absorbed=True
    )

    res = model.fit(cov_type="clustered", cluster_time=True)

    print(res.summary)

    # -----------------------------------------------------------
    # 6. Hent ut ~8000 estimater
    # -----------------------------------------------------------
    coefs = res.params.reset_index()
    coefs.columns = ['term', 'beta']
    ci = res.conf_int().reset_index()
    ci.columns = ['term', 'ci_low', 'ci_high']

    out = coefs.merge(ci, on='term')

    out = out[
        out['term']
        .str.contains("Med Norgespris")
        &
        out['term']
        .str.contains("treat_hour")
    ].copy()

    out['hour'] = (
        out['term']
        .str.extract(r'treat_hour\)\[T\.(\d+)\]')
        .astype(int)
    )

    out['effect_pct'] = (np.exp(out['beta']) - 1) * 100
    out['ci_low_pct'] = (np.exp(out['ci_low']) - 1) * 100
    out['ci_high_pct'] = (np.exp(out['ci_high']) - 1) * 100

    print("\n---------- EKSEMPEL PÅ ESTIMATER ----------")
    print(out.head(10))

    # -----------------------------------------------------------
    # 7. FIGUR
    # -----------------------------------------------------------
    plt.figure(figsize=(11, 5))

    plt.plot(out['hour'], out['effect_pct'], color='black', lw=1)
    plt.fill_between(
        out['hour'],
        out['ci_low_pct'],
        out['ci_high_pct'],
        alpha=0.3
    )

    plt.axhline(0, ls='--', color='red')
    plt.xlabel("Timer siden Norgespris")
    plt.ylabel("Endring i forbruk [%]")
    plt.title(f"Timevis DiD – Norgespris ({price_area})")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------------
    # 8. Trend / strukturelt avvik
    # -----------------------------------------------------------
    from scipy.stats import linregress

    trend = linregress(out['hour'], out['effect_pct'])

    print("\n========== TRENDTEST ==========")
    print(f"Helling (% per time): {trend.slope:.4f}")
    print(f"P-verdi for trend:    {trend.pvalue:.4f}")

    if trend.pvalue < 0.05:
        print("→ Signifikant endring i trend etter Norgespris.")
    else:
        print("→ Ingen statistisk signifikant trend.")

    print("\n========== FERDIG ==========\n")

    return out


Difference_in_Difference_temp_hourly(data_mNP_NO1, data_uNP_NO1, data_rest_NO1,'NO1', Temp_Oslo)
