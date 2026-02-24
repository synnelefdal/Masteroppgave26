import numpy as np
import pandas as pd
import statsmodels.api as sm
import patsy
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')
Temp_Stavanger = pd.read_csv('Temp_Stavanger.csv')


def Placebo_DiD(data_mNP, data_uNP, price_area):
    """
    Ren placebo Difference-in-Differences for 'kWh/Metering_point'
    basert på strukturen du allerede bruker i DifferenceinDifference().
    """

    import numpy as np
    import pandas as pd

    # ------------------- Placebo-vindu (ett år tidligere) ------------------- #
    start_before = '2023-10-01'
    end_before   = '2024-01-31'

    start_after  = '2024-10-01'
    end_after    = '2025-01-31'

    # ------------------- Konverter dato ------------------- #
    for df in [data_mNP, data_uNP]:
        df['start_time_utc'] = pd.to_datetime(
            df['start_time_utc'],
            format='%Y-%m-%d %H:%M:%S',
            errors='coerce',
            utc=True
        )
        df['Date'] = df['start_time_utc'].dt.date
        df['Date'] = pd.to_datetime(df['Date'])
        df['Hour'] = df['start_time_utc'].dt.hour.astype(int)

    # ------------------- Filter: PRICE AREA ------------------- #
    dNP = data_mNP[data_mNP['price_area'] == price_area].copy()
    dUP = data_uNP[data_uNP['price_area'] == price_area].copy()

    # ------------------- Perioder ------------------- #
    dNP_before = dNP[(dNP['Date'] >= start_before) & (dNP['Date'] <= end_before)].copy()
    dNP_after  = dNP[(dNP['Date'] >= start_after)  & (dNP['Date'] <= end_after)].copy()

    dUP_before = dUP[(dUP['Date'] >= start_before) & (dUP['Date'] <= end_before)].copy()
    dUP_after  = dUP[(dUP['Date'] >= start_after)  & (dUP['Date'] <= end_after)].copy()

    # ------------------- kWh per metering point ------------------- #
    for df in [dNP_before, dNP_after, dUP_before, dUP_after]:
        df['kWh/Metering_point'] = (
            df['consumption_kwh'] / df['metering_point_count']
        )

    # ------------------- Aggregering per Date × Hour × group_definition ------------------- #
    agg_NP_before = dNP_before.groupby(['Date','Hour','group_definition'])['kWh/Metering_point'].sum().reset_index()
    agg_NP_after  = dNP_after.groupby(['Date','Hour','group_definition'])['kWh/Metering_point'].sum().reset_index()

    agg_UP_before = dUP_before.groupby(['Date','Hour','group_definition'])['kWh/Metering_point'].sum().reset_index()
    agg_UP_after  = dUP_after.groupby(['Date','Hour','group_definition'])['kWh/Metering_point'].sum().reset_index()

    # ------------------- Kombiner ------------------- #
    df_NP = pd.concat([agg_NP_before, agg_NP_after], ignore_index=True)
    df_UP = pd.concat([agg_UP_before, agg_UP_after], ignore_index=True)

    df_NP['Norgespris'] = 'Med_NP'
    df_UP['Norgespris'] = 'Uten_NP'

    df = pd.concat([df_NP, df_UP], ignore_index=True)

    # ------------------- Gi hver observasjon periode ------------------- #
    df['Period'] = np.where(df['Date'] < start_after, 'Before', 'After')

    # ------------------- Beregn gjennomsnitt per gruppe ------------------- #
    mean_NP_before = df[(df['Norgespris']=='Med_NP') & (df['Period']=='Before')]['kWh/Metering_point'].mean()
    mean_NP_after  = df[(df['Norgespris']=='Med_NP') & (df['Period']=='After') ]['kWh/Metering_point'].mean()

    mean_UP_before = df[(df['Norgespris']=='Uten_NP') & (df['Period']=='Before')]['kWh/Metering_point'].mean()
    mean_UP_after  = df[(df['Norgespris']=='Uten_NP') & (df['Period']=='After') ]['kWh/Metering_point'].mean()

    # ------------------- ΔT, ΔC, DiD ------------------- #
    delta_T = mean_NP_after - mean_NP_before
    delta_C = mean_UP_after - mean_UP_before
    did_est = delta_T - delta_C

    # ------------------- Prosent endring ------------------- #
    pct_T = (mean_NP_after / mean_NP_before - 1) * 100
    pct_C = (mean_UP_after / mean_UP_before - 1) * 100
    did_pct = pct_T - pct_C

    # ------------------- Print ------------------- #
    print("\n===== PLACEBO DiD =====")
    print(f"Treatment før: {mean_NP_before:.4f}")
    print(f"Treatment etter: {mean_NP_after:.4f}")
    print(f"Control før: {mean_UP_before:.4f}")
    print(f"Control etter: {mean_UP_after:.4f}")
    print(f"ΔT = {delta_T:.4f}, ΔC = {delta_C:.4f}")
    print(f"DiD = {did_est:.4f}")
    print(f"Prosent-DiD = {did_pct:.4f} p.p.")

    return {
        "treatment_before": mean_NP_before,
        "treatment_after": mean_NP_after,
        "control_before": mean_UP_before,
        "control_after": mean_UP_after,
        "delta_treatment": delta_T,
        "delta_control": delta_C,
        "did": did_est,
        "treatment_pct_change": pct_T,
        "control_pct_change": pct_C,
        "did_pct": did_pct
    }

def DifferenceinDifference(data_mNP, data_uNP, price_area):
    # ------------------- Filterer for dato ---------- #
    start_date_before = '2025-01-01'
    end_date_before = '2025-01-31'

    start_date_after = '2026-01-01'
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

    df_NP["price_area"] = price_area
    df_UtenNP["price_area"] = price_area

    df = pd.concat([df_NP, df_UtenNP], ignore_index=True)
    df = df[df['kWh/Metering_point'] > 0].copy()

    cutoff = pd.Timestamp('2025-10-01')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Periode'] = np.where(df['Date'] < cutoff, 'Before_ref', 'After_ref')   #Post

    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month'] = pd.Categorical(df['Month'],
                                  categories=['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'],
                                  ordered=True)

    df['Hour'] = pd.Categorical(df['Hour'].astype(str),
                                 categories=[str(i) for i in range(0, 23+1)], ordered=True)

    print(df.head(30))


    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.max_rows', None)
    #print(df[['Date', 'Norgespris','Group']])
    #print(df)

    formula = (
        'np.log(Q("kWh/Metering_point")) ~ '
        'C(Periode, Treatment(reference="Before_ref")) '
        '* C(Norgespris, Treatment(reference="Uten_NP")) '
        '+ C(Hour, Treatment(reference="1") ) + C(Month, Treatment(reference = "November"))'
    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())

    '''beta3 = model.params['C(Group, Treatment(reference="Before_ref"))[T.After_ref]:C(Norgespris, Treatment(reference="Uten_NP"))[T.Med_NP]']
    DiD = (np.exp(beta3) - 1)*100

    ci_low, ci_high = model.conf_int().loc['C(Group, Treatment(reference="Before_ref"))[T.After_ref]:C(Norgespris, Treatment(reference="Uten_NP"))[T.Med_NP]']
    DiD_low = (np.exp(ci_low) - 1)*100
    DiD_high = (np.exp(ci_high) - 1)*100

    print(f'DiD prosent for {price_area}: {DiD:.2f}%')
    print(f'KI: [{DiD_low:.2f}%, {DiD_high:.2f}%]')'''

    # ------------- F-Test ----------- #
    '''print('------------------- F TEST -------------------')
    param_names = model.params.index.tolist()
    did_term_candidates = [
        name for name in param_names
        if ("C(Group" in name and "T.After_ref" in name
            and "C(Norgespris" in name and "T.Med_NP" in name)
    ]
    if len(did_term_candidates) == 0:
        raise RuntimeError("Fant ikke DID-interaksjon i modellen. Sjekk formel og nivånavn.")
    did_term = did_term_candidates[0]

    # F-test (Wald-test) for at DID-koeffisienten = 0
    f_test_res = model.f_test(f"{did_term} = 0")
    print("F-test for DID-effekt = 0")
    print(f_test_res)  # viser F-stat, df og p-verdi

    # (Valgfritt) hent t-verdi/p-verdi direkte:
    print("\nDirekte fra koeffisienten:")
    print(model.t_test(f"{did_term} = 0"))'''

    # -------------- Event study ----------- #
    '''print('-------- Event study ------------')

    def run_event_study(df, cutoff="2025-10-01", min_k=-6, max_k=6, baseline=-1):
        dfe = df.copy()
        cutoff = pd.to_datetime(cutoff)

        # Relativ måned (k)
        dfe["Date"] = pd.to_datetime(dfe["Date"])
        rel = (dfe["Date"].dt.to_period("M") - cutoff.to_period("M")).apply(lambda x: x.n)
        dfe["rel_month"] = rel.astype(int)

        # Klipp vindu
        dfe = dfe[(dfe["rel_month"] >= min_k) & (dfe["rel_month"] <= max_k)].copy()

        # Kategoriske nivåer (viktig for stabile dummier)
        kept_levels = list(range(min_k, max_k + 1))
        # Bruk baseline = -1 (vanlig i litteraturen), men fallback hvis den ikke finnes i data
        if baseline not in dfe["rel_month"].unique():
            # velg en annen baseline som finnes og er <0 hvis mulig, ellers 0
            negs = sorted([k for k in kept_levels if k in dfe["rel_month"].unique() and k < 0])
            baseline = negs[-1] if len(negs) else 0

        dfe["rel_month"] = pd.Categorical(dfe["rel_month"], categories=kept_levels, ordered=True)
        dfe["Norgespris"] = pd.Categorical(dfe["Norgespris"], categories=["Uten_NP", "Med_NP"])

        # Bygg formel: Interaksjoner for alle k != baseline
        # Baselineleddet utelates automatisk i C(rel_month)
        formula_es = (
            'np.log(Q("kWh/Metering_point")) ~ '
            'C(Norgespris, Treatment(reference="Uten_NP")) '
            '+ C(rel_month) * C(Norgespris, Treatment(reference="Uten_NP")) '
            '+ C(Hour) + C(Month)'
        )

        es_mod = smf.ols(formula_es, data=dfe).fit(cov_type="HC1")
        print(es_mod.summary())

        # Trekk ut koeffisienter for (rel_month=k) × Med_NP
        coef_rows = []
        for k in kept_levels:
            if k == baseline:
                continue
            term = f"C(rel_month)[T.{k}]:C(Norgespris, Treatment(reference='Uten_NP'))[T.Med_NP]"
            # I praksis genererer patsy navn uten Treatment(...) i strengen;
            # finn matchende navn robust:
            cand = [p for p in es_mod.params.index if
                    f"C(rel_month)[T.{k}]:" in p and "C(Norgespris)" in p and "T.Med_NP" in p]
            if len(cand) == 0:
                # Noen ganger kommer interaksjonsnavnet i motsatt rekkefølge
                cand = [p for p in es_mod.params.index if
                        "C(rel_month)" in p and f"[T.{k}]" in p and "C(Norgespris)" in p and "T.Med_NP" in p]
            if len(cand) == 0:
                continue

            pname = cand[0]
            beta = es_mod.params[pname]
            se = es_mod.bse[pname]
            ci_l, ci_u = es_mod.conf_int().loc[pname].tolist()
            coef_rows.append({"k": k, "beta": beta, "se": se, "ci_l": ci_l, "ci_u": ci_u, "param": pname})

        es_df = pd.DataFrame(coef_rows).sort_values("k")
        print("\nEvent-study (interaksjonskoeffisienter for Med_NP, baseline k = {}):".format(baseline))
        print(es_df)

        # F-test av pretrender: alle leads (k < 0, k != baseline) = 0
        lead_params = [r["param"] for _, r in es_df.iterrows() if r["k"] < 0]
        if len(lead_params) >= 1:
            hyp = " , ".join([f"{p} = 0" for p in lead_params])  # kommaseparert = multippel restriksjon
            print("\nF-test: Alle pretrender (leads) = 0")
            print(es_mod.f_test(hyp))
        else:
            print("\nIngen leads i vinduet – kan ikke gjennomføre pretrend F-test.")

        return es_mod, es_df

    # Kjør:
    es_mod, es_df = run_event_study(df, cutoff="2025-10-01", min_k=-6, max_k=6, baseline=-1)
    print(es_mod,es_df)'''

    # -------------------- Placebo test ------------ #
    '''print('--------------- Placebo test ------------------')

    def run_placebo_did(
            treatment_file="All_Demand_Data/NO1_mNP.csv",
            control_file="All_Demand_Data/NO1_uNP.csv",
            placebo_before_start="2023-10-01",
            placebo_before_end="2024-01-31",
            placebo_after_start="2024-10-01",
            placebo_after_end="2025-01-31",
            n_boot=2000,
    ):
        """
        Kjør en komplett PLACEBO Difference-in-Differences med:
          - Nivå-DiD
          - Prosent-DiD
          - Bootstrap-KI
          - OLS (log)
        Returnerer et dictionary med alle resultater.
        """

        import pandas as pd
        import numpy as np
        import statsmodels.formula.api as smf

        # --------------------------
        # Konverter datoer
        # --------------------------
        PBS = pd.Timestamp(placebo_before_start)
        PBE = pd.Timestamp(placebo_before_end)
        PAS = pd.Timestamp(placebo_after_start)
        PAE = pd.Timestamp(placebo_after_end)

        DATE_COL = "start_time_utc"
        CONS_COL = "consumption_kwh"
        MP_COL = "metering_point_count"

        # --------------------------
        # Leser + aggregerer daglig
        # --------------------------
        def load_and_prepare(path, group):
            df = pd.read_csv(path, sep=";", encoding="utf-8")
            dt = pd.to_datetime(df[DATE_COL], errors="coerce", utc=True).dt.tz_convert(None)
            date = dt.dt.floor("D")

            df[CONS_COL] = pd.to_numeric(df[CONS_COL], errors="coerce")
            df[MP_COL] = pd.to_numeric(df[MP_COL], errors="coerce")

            daily = (
                pd.DataFrame({"date": date, CONS_COL: df[CONS_COL], MP_COL: df[MP_COL]})
                .groupby("date", as_index=False)
                .sum()
            )
            daily["per_mp"] = daily[CONS_COL] / daily[MP_COL]
            daily["group"] = group
            return daily

        treatment = load_and_prepare(treatment_file, "treatment")
        control = load_and_prepare(control_file, "control")
        daily = pd.concat([treatment, control], ignore_index=True)

        # --------------------------
        # Før/Efter-vindu
        # --------------------------
        def label_periods(date):
            out = pd.Series(index=date.index, dtype="object")
            out[(date >= PBS) & (date <= PBE)] = "before_ref"
            out[(date >= PAS) & (date <= PAE)] = "after_ref"
            return out

        daily["period"] = label_periods(daily["date"])

        # --------------------------
        # Aggreger nivå per periode
        # --------------------------
        def summarize(df):
            ag = (
                df.groupby(["group", "period"], as_index=False)
                .agg(sum_c=(CONS_COL, "sum"), sum_mp=(MP_COL, "sum"))
            )
            ag["avg_per_mp"] = ag["sum_c"] / ag["sum_mp"]
            return ag

        agg = summarize(daily.dropna(subset=["period"]))

        # --------------------------
        # DiD (nivå)
        # --------------------------
        def get_avg(g, p):
            row = agg[(agg["group"] == g) & (agg["period"] == p)]
            return float(row["avg_per_mp"].values[0]) if not row.empty else np.nan

        tb, ta = get_avg("treatment", "before_ref"), get_avg("treatment", "after_ref")
        cb, ca = get_avg("control", "before_ref"), get_avg("control", "after_ref")

        dt = ta - tb
        dc = ca - cb
        did = dt - dc

        # --------------------------
        # DiD (prosent)
        # --------------------------
        pct_t = (ta / tb - 1) * 100
        pct_c = (ca / cb - 1) * 100
        did_pct = pct_t - pct_c

        # --------------------------
        # Bootstrap
        # --------------------------
        dfb = daily.dropna(subset=["period"]).copy()
        rng = np.random.default_rng(42)

        strata = {
            (g, p): np.array(sorted(df_part["date"].unique()))
            for (g, p), df_part in dfb.groupby(["group", "period"])
        }

        def boot_once():
            rows = []
            for (g, p), days in strata.items():
                boot_days = days[rng.integers(0, len(days), len(days))]
                sub = dfb[(dfb["group"] == g) &
                          (dfb["period"] == p) &
                          (dfb["date"].isin(boot_days))]
                avg = sub[CONS_COL].sum() / sub[MP_COL].sum()
                rows.append({"group": g, "period": p, "avg_per_mp": avg})
            ag_b = pd.DataFrame(rows)

            tb = ag_b[(ag_b["group"] == "treatment") & (ag_b["period"] == "before_ref")]["avg_per_mp"].values[0]
            ta = ag_b[(ag_b["group"] == "treatment") & (ag_b["period"] == "after_ref")]["avg_per_mp"].values[0]
            cb = ag_b[(ag_b["group"] == "control") & (ag_b["period"] == "before_ref")]["avg_per_mp"].values[0]
            ca = ag_b[(ag_b["group"] == "control") & (ag_b["period"] == "after_ref")]["avg_per_mp"].values[0]
            return (ta - tb) - (ca - cb)

        boots = np.array([boot_once() for _ in range(n_boot)])
        ci_low, ci_high = np.percentile(boots, [2.5, 97.5])

        # --------------------------
        # OLS-DiD (log)
        # --------------------------
        df_ols = daily.dropna(subset=["period", "per_mp"]).copy()
        df_ols = df_ols[df_ols["per_mp"] > 0].copy()

        df_ols["post"] = (df_ols["period"] == "after_ref").astype(int)
        df_ols["treat"] = (df_ols["group"] == "treatment").astype(int)
        df_ols["log_per_mp"] = np.log(df_ols["per_mp"])

        model = smf.ols("log_per_mp ~ treat:post", data=df_ols).fit(cov_type="HC1")

        b = float(model.params["treat:post"])
        ci_b_low, ci_b_high = model.conf_int().loc["treat:post"].tolist()
        pct_eff = (np.exp(b) - 1) * 100

        # --------------------------
        # Print
        # --------------------------
        print("\n===== PLACEBO-DID RESULTATER =====")
        print(f"Treatment før   = {tb:.4f}")
        print(f"Treatment etter = {ta:.4f}")
        print(f"Control før     = {cb:.4f}")
        print(f"Control etter   = {ca:.4f}")
        print(f"ΔT = {dt:.4f}, ΔC = {dc:.4f}")
        print(f"DiD = {did:.4f}")
        print(f"Prosent-DiD = {did_pct:.4f} p.p.")
        print(f"Bootstrap 95% KI: [{ci_low:.4f}, {ci_high:.4f}]")

        print("\n===== OLS LOG-DiD =====")
        print(f"β = {b:.6f}, 95% KI = [{ci_b_low:.6f}, {ci_b_high:.6f}]")
        print(f"EFFEKT I % = {pct_eff:.3f}%")

        # --------------------------
        # Returner alt
        # --------------------------
        return {
            "treatment_before": tb,
            "treatment_after": ta,
            "control_before": cb,
            "control_after": ca,
            "delta_treatment": dt,
            "delta_control": dc,
            "did": did,
            "treatment_pct_change": pct_t,
            "control_pct_change": pct_c,
            "did_pct": did_pct,
            "bootstrap_ci_low": ci_low,
            "bootstrap_ci_high": ci_high,
            "ols_coef": b,
            "ols_ci_low": ci_b_low,
            "ols_ci_high": ci_b_high,
            "ols_pct_effect": pct_eff,
            "ols_model": model,
        }

    run_placebo_did()'''


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

def NorgesprisTemp(data_mNP, price_area, Temp):
    # ------------------- Filterer for dato ---------- #
    start_date_before = '2024-11-01'
    end_date_before = '2025-01-31'

    start_date_after = '2025-11-01'
    end_date_after = '2026-01-31'

    # ----------- Endring til Date og Hour ------------ #
    data_mNP['start_time_utc'] = pd.to_datetime(data_mNP['start_time_utc'],
                                                format = '%Y-%m-%d %H:%M:%S',
                                                errors = 'coerce',
                                                utc = True)

    data_mNP['Date'] = data_mNP['start_time_utc'].dt.date
    data_mNP['Hour'] = data_mNP['start_time_utc'].dt.hour.astype(int)
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

    # ----------------- Beregninger; NP-Gruppen ------------------- #
    '''df_NP['Date'] = pd.to_datetime(df_NP['Date'])
    df_NP['Month'] = df_NP['Date'].dt.strftime('%B')

    df_NP['Hour'] = pd.Categorical(df_NP['Hour'].astype(str),
                                 categories=[str(i) for i in range(1, 25)], ordered=True)
    df_NP['Month'] = pd.Categorical(df_NP['Month'],
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
        'C(Group, Treatment(reference="Before_ref"))'
        '+ Temp24'
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

    beta3 = model.params[
        'C(Group, Treatment(reference="Before_ref"))[T.After_ref]']
    DiD = (np.exp(beta3) - 1) * 100

    ci_low, ci_high = model.conf_int().loc[
        'C(Group, Treatment(reference="Before_ref"))[T.After_ref]']
    DiD_low = (np.exp(ci_low) - 1) * 100
    DiD_high = (np.exp(ci_high) - 1) * 100

    gamma2 = model.params['Temp24']
    effect_temp = (np.exp(gamma2) - 1) * 100

    ci_low_temp, ci_high_temp = model.conf_int().loc[
        'Temp24']
    DiD_low_temp = (np.exp(ci_low_temp) - 1) * 100
    DiD_high_temp = (np.exp(ci_high_temp) - 1) * 100

    print(f'DiD prosent for {price_area}: {DiD:.2f}%')
    print(f'KI: [{DiD_low:.2f}%, {DiD_high:.2f}%]')
    print(f'Effekt prosent for temp i {price_area}: {effect_temp:.2f}%')
    print(f'KI for temperatur effekt: [{DiD_low_temp:.2f}%, {DiD_high_temp:.2f}%]')


def UtenNorgesprisTemp(data_uNP, price_area, Temp):
    # ------------------- Filterer for dato ---------- #
    start_date_before = '2024-11-01'
    end_date_before = '2025-01-31'

    start_date_after = '2025-11-01'
    end_date_after = '2026-01-31'

    # ----------- Endring til Date og Hour ------------ #
    data_uNP['start_time_utc'] = pd.to_datetime(data_uNP['start_time_utc'],
                                                format = '%Y-%m-%d %H:%M:%S',
                                                errors = 'coerce',
                                                utc = True)

    data_uNP['Date'] = data_uNP['start_time_utc'].dt.date
    data_uNP['Hour'] = data_uNP['start_time_utc'].dt.hour.astype(int)
    # ----------------- Demand; NP-Gruppen ------------------ #

    data_demand_UtenNP = data_uNP[data_uNP['price_area'] == price_area].copy()
    data_demand_UtenNP['Date'] = pd.to_datetime(data_demand_UtenNP['Date'])
    data_demand_UtenNP['Hour'] = data_demand_UtenNP['Hour'].astype(int)

    data_demand_UtenNP_filtered_before = data_demand_UtenNP[(data_demand_UtenNP['Date'] >= start_date_before) &
                                        (data_demand_UtenNP['Date'] <= end_date_before)].copy()

    data_demand_UtenNP_filtered_after = data_demand_UtenNP[(data_demand_UtenNP['Date'] >= start_date_after) &
                                        (data_demand_UtenNP['Date'] <= end_date_after)].copy()
    #print(data_demand_NP_filtered_before)
    #print(data_demand_NP_filtered_after)

    data_demand_UtenNP_filtered_before['kWh/Metering_point'] = data_demand_UtenNP_filtered_before['consumption_kwh'] / data_demand_UtenNP_filtered_before['metering_point_count']
    #print(data_demand_NP_filtered_before.head(3))

    data_demand_UtenNP_filtered_after['kWh/Metering_point'] = data_demand_UtenNP_filtered_after['consumption_kwh'] / data_demand_UtenNP_filtered_after['metering_point_count']
    #print(data_demand_NP_filtered_after.head(3))

    total_demand_hour_UtenNP_before = data_demand_UtenNP_filtered_before.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    total_demand_hour_UtenNP_after = data_demand_UtenNP_filtered_after.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point'].sum().reset_index()
    #print(total_demand_hour_NP_before)
    #print(total_demand_hour_NP_after)

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
    df_UtenNP_before = pd.DataFrame(total_demand_hour_UtenNP_before)
    df_UtenNP_after = pd.DataFrame(total_demand_hour_UtenNP_after)

    df_UtenNP = pd.concat([df_UtenNP_before, df_UtenNP_after], ignore_index=True)

    pd.set_option('display.max_columns', None)

    # pd.set_option('display.max_columns', None)
    # print(df_NP.head(3))
    # --------------- Regresjonsanalyse ------------- #
    df_Temp_before = pd.DataFrame(total_temp_hour_before)
    df_Temp_after = pd.DataFrame(total_temp_hour_after)
    df_Temp = pd.concat([df_Temp_before, df_Temp_after], ignore_index=True)

    #df_NP['Group'] = 'Norgespris'  # 2024-periode
    #df_UtenNP['Group'] = 'Uten Norgespris'  # 2025-periode

    df_UtenNP['Norgespris'] = 'Uten_NP'  #

    df = pd.merge(df_UtenNP, df_Temp, on = ['Date', 'Hour'], how = 'left')
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
        'C(Group, Treatment(reference="Before_ref"))'
        '+ Temp24'
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

    beta3 = model.params[
        'C(Group, Treatment(reference="Before_ref"))[T.After_ref]']
    DiD = (np.exp(beta3) - 1) * 100

    ci_low, ci_high = model.conf_int().loc[
        'C(Group, Treatment(reference="Before_ref"))[T.After_ref]']
    DiD_low = (np.exp(ci_low) - 1) * 100
    DiD_high = (np.exp(ci_high) - 1) * 100

    gamma2 = model.params['Temp24']
    effect_temp = (np.exp(gamma2) - 1) * 100

    ci_low_temp, ci_high_temp = model.conf_int().loc['Temp24']
    DiD_low_temp = (np.exp(ci_low_temp) - 1) * 100
    DiD_high_temp = (np.exp(ci_high_temp) - 1) * 100

    print(f'DiD prosent for {price_area}: {DiD:.2f}%')
    print(f'KI: [{DiD_low:.2f}%, {DiD_high:.2f}%]')
    print(f'Effekt prosent for temp i {price_area}: {effect_temp:.2f}%')
    print(f'KI for temperatur effekt: [{DiD_low_temp:.2f}%, {DiD_high_temp:.2f}%]')

#Placebo_DiD(data_mNP_NO1, data_uNP_NO1, "NO1")
#Placebo_DiD(data_mNP_NO2, data_uNP_NO2, "NO2")
#Placebo_DiD(data_mNP_NO5, data_uNP_NO5, "NO5")



DifferenceinDifference(data_mNP_NO1, data_uNP_NO1, 'NO1')
#DifferenceinDifference(data_mNP_NO2, data_uNP_NO2, 'NO2')
#DifferenceinDifference(data_mNP_NO5, data_uNP_NO5, 'NO5')
#DifferenceinDifferenceTemp(data_mNP_NO1, data_uNP_NO1, 'NO1', Temp_Oslo)     #Ved NO1 bruk Temp_Oslo, og ved NO5 bruk Temp_Bergen

'''print(' ------------ NO1 --------------- ')

NorgesprisTemp(data_mNP_NO1, 'NO1', Temp_Oslo)
NorgesprisTemp(data_uNP_NO1, 'NO1', Temp_Oslo)

print(' ------------ NO2 --------------- ')

NorgesprisTemp(data_mNP_NO2, 'NO2', Temp_Stavanger)
NorgesprisTemp(data_uNP_NO2, 'NO2', Temp_Stavanger)

print(' ------------ NO5 --------------- ')

NorgesprisTemp(data_mNP_NO5, 'NO5', Temp_Bergen)
NorgesprisTemp(data_uNP_NO5, 'NO5', Temp_Bergen)'''






