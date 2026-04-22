
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



def Difference_in_Difference_temp_daily(
    data_mNP,
    data_uNP,
    data_resten,
    price_area,
    Temp,
    analysis_start,
    analysis_end,
    ref_start,
    ref_end
):
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from linearmodels.panel import PanelOLS
    from scipy.stats import linregress

    print("\n========== START DiD – DAGLIG EVENT STUDY ==========\n")

    # -----------------------------------------------------------
    # 1. KLARGJØR ETTERSPØRSEL – DAGLIG
    # -----------------------------------------------------------
    def prep_daily(df):
        df = df.copy()
        df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True)
        df['Date'] = df['start_time_utc'].dt.floor('D')
        df = df[df['price_area'] == price_area]

        df['kWh/Metering_point'] = (
            df['consumption_kwh'] / df['metering_point_count']
        )

        return (
            df.groupby(['Date', 'group_definition'])['kWh/Metering_point']
            .mean()
            .reset_index()
        )

    df = pd.concat(
        [
            prep_daily(data_mNP),
            prep_daily(data_uNP),
            prep_daily(data_resten),
        ],
        ignore_index=True,
    )

    # -----------------------------------------------------------
    # 2. TEMPERATUR – DAGLIG
    # -----------------------------------------------------------
    Temp = Temp.copy()
    Temp['Date'] = pd.to_datetime(Temp['Date'])

    Temp = Temp.sort_values(['Date', 'Hour'])
    Temp['Temp24'] = (
        Temp['Lufttemperatur']
        .rolling(window=24, min_periods=1)
        .mean()
    )

    Temp_daily = (
        Temp.groupby('Date')['Temp24']
        .mean()
        .reset_index()
        .rename(columns={'Temp24': 'Temp_d'})
    )

    df['Date'] = df['Date'].dt.tz_localize(None)
    Temp_daily['Date'] = Temp_daily['Date'].dt.tz_localize(None)

    df = df.merge(Temp_daily, on='Date', how='left')

    df = df[df['Temp_d'].notna()]
    df = df[df['kWh/Metering_point'] > 0]

    # -----------------------------------------------------------
    # 3. VELG ANALYSEPERIODE
    # -----------------------------------------------------------
    analysis_start = pd.Timestamp(analysis_start)
    analysis_end   = pd.Timestamp(analysis_end)

    df = df[
        (df['Date'] >= analysis_start) &
        (df['Date'] <= analysis_end)
    ].copy()

    # -----------------------------------------------------------
    # 4. DEFINER REFERANSEPERIODE OG EVENT‑TID
    # -----------------------------------------------------------
    ref_start = pd.Timestamp(ref_start)
    ref_end   = pd.Timestamp(ref_end)

    treat_start = ref_end + pd.Timedelta(days=1)

    '''df['treat_day'] = np.where(
        df['Date'] >= treat_start,
        (df['Date'] - treat_start).dt.days,
        -1
    )'''
    df['treat_day'] = (df['Date'] - treat_start).dt.days

    #nytt
    min_day = -30
    max_day = 60

    event_cols = []

    for d in range(min_day, max_day + 1):
        if d == -1:
            continue

        if d < 0:
            col = f"event_m{abs(d)}"
        else:
            col = f"event_p{d}"

        df[col] = (
                (df['treat_day'] == d)
                & (df['group_definition'] == 'Med Norgespris')
        ).astype(int)

        if df[col].sum() > 0:
            event_cols.append(col)


#til hit



    # -----------------------------------------------------------
    # 5. PANELSTRUKTUR
    # -----------------------------------------------------------
    df['entity'] = pd.Categorical(
        df['group_definition'],
        categories=[
            'Uten Norgespris',
            'Med Norgespris',
            'Resten'
        ],
        ordered=True
    )

    df['log_y'] = np.log(df['kWh/Metering_point'])

    panel_df = (
        df.set_index(['entity', 'Date'], drop=False)
        .sort_index()
    )

    # -----------------------------------------------------------
    # 6. MODELL – DAGLIG EVENT STUDY
    # -----------------------------------------------------------
    print("\nEstimerer daglig event‑study DiD …\n")

    '''# Hvor mange observasjoner per kombinasjon?
    print(
        df.groupby(['entity', 'treat_day'])
        .size()
        .unstack(fill_value=0)
    )

    model = PanelOLS.from_formula(
        """
        log_y ~ 1
        + C(entity, Treatment(reference="Uten Norgespris"))
          : C(treat_day, Treatment(reference=-1))
        + Temp_d + I(Temp_d**2) + I(Temp_d**3)
        
        """,
        data=panel_df,
        drop_absorbed=True
    )'''

    event_terms = " + ".join(event_cols
        #[f"event_{d}" for d in range(-30, max_lead + 1) if d != -1]
    )

    '''formula = f"""
        log_y ~ 1
        + {event_terms}
        + Temp_d + I(Temp_d**2) + I(Temp_d**3)
        """'''

    formula = (
            "log_y ~ 1 "
            + (f"+ {event_terms} " if event_terms else "")
            + "+ Temp_d + I(Temp_d**2) + I(Temp_d**3)"
    )

    print("FORMULA som estimerer:")
    print(formula)

    model = PanelOLS.from_formula(
        formula,
        data=panel_df,
        drop_absorbed=True
    )


    res = model.fit(
        cov_type="clustered",
        cluster_time=True,
        #check_rank=False
    )


    #nytt
    #pre_terms = [f'event_{d}' for d in range(-30, 0) if d != -1]

    import numpy as np

    # Hent koeffisientnavn i riktig rekkefølge
    param_names = list(res.params.index)

    # Pre-treatment event-termer

    pre_terms = [col for col in event_cols if col.startswith("event_m")]

    print("Antall pre-termer:", len(pre_terms))

    # Bygg restriksjonsmatrise R * beta = 0
    R = np.zeros((len(pre_terms), len(param_names)))

    for i, term in enumerate(pre_terms):
        j = param_names.index(term)
        R[i, j] = 1

    # Wald-test
    wald = res.wald_test(R)

    print("\nPARALLELL TREND TEST")
    print(wald)

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    # -----------------------------
    # 1. Hent koeffisienter + CI
    # -----------------------------
    params = res.params
    ci = res.conf_int()

    pre_data = []

    for name in params.index:
        if name.startswith("event_m"):
            day = -int(name.replace("event_m", ""))
            beta = params[name]
            ci_low, ci_high = ci.loc[name]

            pre_data.append({
                "day": day,
                "beta": beta,
                "ci_low": ci_low,
                "ci_high": ci_high
            })

    pre_df = pd.DataFrame(pre_data).sort_values("day")

    # Log → prosent
    pre_df["effect_pct"] = (np.exp(pre_df["beta"]) - 1) * 100
    pre_df["ci_low_pct"] = (np.exp(pre_df["ci_low"]) - 1) * 100
    pre_df["ci_high_pct"] = (np.exp(pre_df["ci_high"]) - 1) * 100

    # -----------------------------
    # 2. Lag graf
    # -----------------------------
    plt.figure(figsize=(10, 5))

    plt.plot(
        pre_df["day"],
        pre_df["effect_pct"],
        marker="o",
        linestyle="-",
        label="Estimert effekt"
    )

    plt.fill_between(
        pre_df["day"],
        pre_df["ci_low_pct"],
        pre_df["ci_high_pct"],
        alpha=0.3,
        label="95 % KI"
    )

    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel("Dager før Norgespris")
    plt.ylabel("Endring i strømforbruk (%)")
    plt.title("Event‑study: Pre‑treatment (parallell trend)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

    #til hit

    plt.axvline(0, color='black', ls='--')
    plt.text(-10, 0, "Pre-period", alpha=0.6)
    plt.text(5, 0, "Post-period", alpha=0.6)

    print(res.summary)

    # -----------------------------------------------------------
    # 7. HENT UT DAGLIGE EFFEKTER
    # -----------------------------------------------------------
    params = res.params.reset_index()
    params.columns = ['term', 'beta']

    ci = res.conf_int().reset_index()
    ci.columns = ['term', 'ci_low', 'ci_high']

    out = params.merge(ci, on='term')

    out = out[
        out['term'].str.contains("Med Norgespris") &
        out['term'].str.contains("treat_day")
    ].copy()

    out['day'] = out['term'].str.extract(
        r'treat_day\)\[T\.(\d+)\]'
    ).astype(float)

    out = out[out['day'].notna()]
    out['day'] = out['day'].astype(int)

    out['effect_pct'] = (np.exp(out['beta']) - 1) * 100
    out['ci_low_pct'] = (np.exp(out['ci_low']) - 1) * 100
    out['ci_high_pct'] = (np.exp(out['ci_high']) - 1) * 100

    # -----------------------------------------------------------
    # 8. FIGUR
    # -----------------------------------------------------------
    plt.figure(figsize=(11, 5))
    plt.plot(out['day'], out['effect_pct'], lw=2)
    plt.fill_between(
        out['day'],
        out['ci_low_pct'],
        out['ci_high_pct'],
        alpha=0.3
    )
    plt.axhline(0, ls='--', color='red')
    plt.xlabel("Dager siden Norgespris")
    plt.ylabel("Endring i forbruk [%]")
    plt.title(f"Daglig event‑study – Norgespris ({price_area})")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------------
    # 9. TRENDTEST
    # -----------------------------------------------------------
    trend = linregress(out['day'], out['effect_pct'])

    print("\n========== TRENDTEST ==========")
    print(f"Helling (% per dag): {trend.slope:.4f}")
    print(f"P-verdi:            {trend.pvalue:.4f}")

    if trend.pvalue < 0.05:
        print("→ Signifikant trend etter Norgespris.")
    else:
        print("→ Ingen signifikant trend.")

    print("\n========== FERDIG ==========\n")

    return out


out = Difference_in_Difference_temp_daily(
    data_mNP_NO1,
    data_uNP_NO1,
    data_rest_NO1,
    price_area='NO1',
    Temp=Temp_Oslo,
    analysis_start='2024-10-01',
    analysis_end='2026-01-31',
    ref_start='2024-10-01',
    ref_end='2024-10-31'
)