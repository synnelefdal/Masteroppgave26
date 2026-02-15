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


def DifferenceinDifference(data_mNP, data_uNP, price_area,
                           make_plot = True, plot_adjusted = True, backtransform_log = False, savepath = None):
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

    df_NP['Norgespris'] = 'Med_NP'  #
    df_UtenNP['Norgespris'] = 'Uten_NP'  #


    df = pd.concat([df_NP, df_UtenNP], ignore_index=True)
    df = df[df['kWh/Metering_point'] > 0].copy()

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


    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.max_rows', None)
    #print(df[['Date', 'Norgespris','Group']])
    #print(df)

    formula = (
        'np.log(Q("kWh/Metering_point")) ~ '
        'C(Group, Treatment(reference="Before_ref")) '
        '* C(Norgespris, Treatment(reference="Uten_NP"))'
    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())


    # ----------------- Plotting ----------------- #
    fig, ax = (None, None)
    if make_plot:
        # Robuste rader: bruk samme posisjoner som i designmatrisen y
        df_model = df.iloc[y.index.to_numpy()].copy()

        # Prediksjoner fra modellen
        yhat = np.asarray(model.fittedvalues).reshape(-1)
        if backtransform_log:
            # Duan-smearing for nivåskala
            smear = np.exp(model.mse_resid / 2.0)
            df_model['_y_for_plot'] = np.exp(yhat) * smear
            y_label = 'Pred. kWh per målepunkt (nivå, smearing)'
            pct_from_log = False
        else:
            # Log-skala (matcher modellen)
            df_model['_y_for_plot'] = yhat
            y_label = 'Pred. log(kWh per målepunkt)'
            pct_from_log = True

        # Aggreger til pre/post × gruppe
        agg = (df_model
               .groupby(['Norgespris', 'Group'])['_y_for_plot']
               .mean()
               .unstack())

        # Sjekk at alle 4 celler finnes
        needed = [('Uten_NP', 'Before_ref'), ('Uten_NP', 'After_ref'),
                  ('Med_NP', 'Before_ref'), ('Med_NP', 'After_ref')]
        for g0, p0 in needed:
            if (g0 not in agg.index) or (p0 not in agg.columns) or pd.isna(agg.loc[g0, p0]):
                raise ValueError(f"Mangler ({g0}, {p0}) for plottet. Sjekk data/filtre.")

        # Punkter (A,B,C,D i teorien)
        # Her velger vi: A = Treatment Pre, B = Kontroll Pre, C = Treatment Post (obs), D = Kontroll Post
        A = float(agg.loc['Med_NP', 'Before_ref'])
        B = float(agg.loc['Uten_NP', 'Before_ref'])
        C = float(agg.loc['Med_NP', 'After_ref'])
        D = float(agg.loc['Uten_NP', 'After_ref'])

        # Kontrafaktisk behandling Post: A + (D - B)
        C_cf = A + (D - B)

        # DiD = (C - A) - (D - B)
        did_val = (C - A) - (D - B)
        did_pct_exact = (100 * (np.exp(did_val) - 1)) if pct_from_log else None

        # X-akse: 0=Pre, 1=Post
        x_pre, x_post = 0.0, 1.0

        # Start figur
        fig, ax = plt.subplots(figsize=(8.6, 5.2))

        # --- Kontroll: grønn heltrukket linje B -> D ---
        ax.plot([x_pre, x_post], [B, D],
                color='tab:green', lw=3.0, label='Kontroll (observasjon)', zorder=2)
        ax.scatter([x_pre, x_post], [B, D],
                   color='tab:green', s=50, zorder=3)

        # --- Behandling (observasjon): rød heltrukket linje A -> C ---
        ax.plot([x_pre, x_post], [A, C],
                color='tab:red', lw=3.0, label='Behandling (observasjon)', zorder=2)
        ax.scatter([x_pre, x_post], [A, C],
                   color='tab:red', s=50, zorder=3)

        # --- Behandling (kontrafaktisk): rød stiplet linje A -> C_cf ---
        ax.plot([x_pre, x_post], [A, C_cf],
                color='tab:red', lw=3.0, ls='--', label='Behandling (kontrafaktisk)', zorder=1)

        # Vertikal intervensjonslinje
        ax.axvline(0.5, color='gray', lw=1.2)
        ax.text(0.5, ax.get_ylim()[0], 'Intervensjon', ha='center', va='bottom', color='gray')

        # --- Annoter A, B, C, D (som i teorifiguren) ---
        ax.text(x_pre - 0.02, A, 'A', color='tab:red', va='center', ha='right', fontsize=11)
        ax.text(x_pre - 0.02, B, 'B', color='tab:green', va='center', ha='right', fontsize=11)
        ax.text(x_post + 0.02, C, 'C', color='tab:red', va='center', ha='left', fontsize=11)
        ax.text(x_post + 0.02, D, 'D', color='tab:green', va='center', ha='left', fontsize=11)

        # --- Intervensjonseffekt (vertikal brakett) ved Post ---
        y_top = max(C, C_cf)
        y_bot = min(C, C_cf)
        ax.annotate(
            '', xy=(x_post, y_top), xytext=(x_post, y_bot),
            arrowprops=dict(arrowstyle='<->', color='tab:red', lw=2.0)
        )
        label = f"Intervensjonseffekt"
        if pct_from_log:
            label += f" (log) = {did_val:.3f}"
            if did_pct_exact is not None:
                label += f"\n≈ {did_pct_exact:.1f}%"
        else:
            label += f" ≈ {did_val:.3f}"
        ax.text(x_post + 0.03, (y_top + y_bot) / 2, label, color='tab:red', va='center', ha='left')

        # --- Konstant forskjell i utfall (pre og post) som vertikale braketter ---
        # Pre: mellom A og B ved x_pre
        y_top_pre = max(A, B)
        y_bot_pre = min(A, B)
        ax.annotate('', xy=(x_pre, y_top_pre), xytext=(x_pre, y_bot_pre),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
        ax.text(x_pre - 0.03, (y_top_pre + y_bot_pre) / 2, 'Konstant forskjell\n(Pre)',
                ha='right', va='center', color='black')

        # Post: mellom C (obs) og D ved x_post
        y_top_post = max(C, D)
        y_bot_post = min(C, D)
        ax.annotate('', xy=(x_post, y_top_post), xytext=(x_post, y_bot_post),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
        ax.text(x_post + 0.03, (y_top_post + y_bot_post) / 2, 'Konstant forskjell\n(Post)',
                ha='left', va='center', color='black')

        # Akseoppsett
        ax.set_xticks([x_pre, x_post])
        ax.set_xticklabels(['Pre Intervention', 'Post Intervention'])

        # Litt luft på y-aksen for å få plass til tekst/markører
        y_vals = [A, B, C, D, C_cf]
        y_min, y_max = min(y_vals), max(y_vals)
        pad = 0.07 * (y_max - y_min if y_max > y_min else 1.0)
        ax.set_ylim(y_min - pad, y_max + pad)

        ax.set_title('Difference-in-Differences (teori-stil)')
        ax.set_ylabel(y_label)
        ax.legend(loc='upper left', frameon=False)
        ax.grid(True, axis='y', alpha=0.25)
        plt.tight_layout()
        plt.show()

        if savepath:
            plt.savefig(savepath, dpi=200, bbox_inches='tight')
            print(f"[Plot] Lagret figur til: {savepath}")

        # Sørg for at figuren vises i skript/terminal
        try:
            plt.show()
        except Exception as e:
            print(f"[Plot] Kunne ikke vise automatisk: {e}. Åpne filen du lagret, eller bruk riktig backend.")


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
        '+ Lufttemperatur'
        '+ Lufttemperatur * C(Norgespris, Treatment(reference="Uten_NP"))'
        '+ C(Hour)'
    )

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())


def DifferenceinDifferenceTemp2(data_mNP, data_uNP, price_area, Temp, use_log=False, verbose=True):
    """
    Estimerer DiD med temperatur og interaksjon (Temperatur_t x Treatment_i),
    faste effekter for enhet (group_definition) og tid (Hour, Month),
    cluster-robuste SE på enhetsnivå.

    Parametre
    ---------
    data_mNP : pd.DataFrame    # data for Med_NP
    data_uNP : pd.DataFrame    # data for Uten_NP
    price_area : str           # prisområdefilter (må finnes i begge datasett)
    Temp : pd.DataFrame        # temperaturdata med kolonner: Date, Hour, Lufttemperatur
    use_log : bool             # True => log-spesifikasjon av Y
    verbose : bool             # True => print modelloppsummering

    Returnerer
    ----------
    dict med:
      - 'model'  : statsmodels-resultatobjekt
      - 'n_obs'  : antall observasjoner
      - 'coef'   : nøkkelkoeffisienter (β for DiD, θ for temp×treated, γ for temp)
      - 'data'   : analysematrise (df) som ble brukt (nyttig for diagnose)
    """

    # ------------------- Dato-vinduer (bruk Timestamp) ------------------- #
    start_date_before = pd.Timestamp('2024-10-01')
    end_date_before   = pd.Timestamp('2025-01-31')

    start_date_after  = pd.Timestamp('2025-10-01')
    end_date_after    = pd.Timestamp('2026-01-31')

    cutoff = pd.Timestamp('2025-10-01')  # Post-periode starter

    # ------------------- Tidsfelter ------------------- #
    def prep_time(df):
        df = df.copy()
        df['start_time_utc'] = pd.to_datetime(
            df['start_time_utc'],
            format='%Y-%m-%d %H:%M:%S',
            errors='coerce',
            utc=True
        )
        # Fjern tz for enkel sammenligning og lag Date/Hour
        st = df['start_time_utc'].dt.tz_convert('UTC').dt.tz_localize(None)
        df['Date'] = pd.to_datetime(st.dt.date)  # midnatt samme dag
        df['Hour'] = st.dt.hour.astype(int)
        return df

    data_mNP = prep_time(data_mNP)
    data_uNP = prep_time(data_uNP)

    # ----------------- Filter prisområde ------------------ #
    data_demand_NP     = data_mNP.loc[data_mNP['price_area'] == price_area].copy()
    data_demand_UtenNP = data_uNP.loc[data_uNP['price_area'] == price_area].copy()

    # ----------------- Filtrer perioder ------------------- #
    def window(df):
        m_before = (df['Date'] >= start_date_before) & (df['Date'] <= end_date_before)
        m_after  = (df['Date'] >= start_date_after)  & (df['Date'] <= end_date_after)
        return df.loc[m_before | m_after].copy()

    data_demand_NP     = window(data_demand_NP)
    data_demand_UtenNP = window(data_demand_UtenNP)

    # ------------- KPI: kWh per målepunkt ------------- #
    for df0 in [data_demand_NP, data_demand_UtenNP]:
        df0['kWh/Metering_point'] = df0['consumption_kwh'] / df0['metering_point_count']

    # ----------- Aggreger per (Date, Hour, group_definition) ----------- #
    # NB: bruker mean (ikke sum) for et konsistent "per målepunkt"-mål per enhet og time.
    group_keys = ['Date', 'Hour', 'group_definition']
    np_g   = data_demand_NP.groupby(group_keys, as_index=False)['kWh/Metering_point'].mean()
    uten_g = data_demand_UtenNP.groupby(group_keys, as_index=False)['kWh/Metering_point'].mean()

    # ----------------- Temperatur ------------------ #
    Temp = Temp.copy()
    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(int)

    # Restriktér til samme perioder
    mTb = (Temp['Date'] >= start_date_before) & (Temp['Date'] <= end_date_before)
    mTa = (Temp['Date'] >= start_date_after)  & (Temp['Date'] <= end_date_after)
    Temp = Temp.loc[mTb | mTa].copy()

    # Én observasjon per (Date, Hour): gj.snitt hvis flere stasjoner
    temp_agg = (Temp
                .groupby(['Date', 'Hour'], as_index=False)
                .agg(Lufttemperatur=('Lufttemperatur', 'mean')))

    # -------- Merge datasett -------- #
    np_g['Norgespris']   = 'Med_NP'
    uten_g['Norgespris'] = 'Uten_NP'
    df = pd.concat([np_g, uten_g], ignore_index=True)

    # Merge inn temperatur
    df = df.merge(temp_agg, on=['Date', 'Hour'], how='left')

    # Fjern ikke-positive utfall
    df = df[df['kWh/Metering_point'] > 0].copy()

    # ----------------- DiD-variabler ------------------ #
    df['treated'] = (df['Norgespris'] == 'Med_NP').astype(int)          # Treatment_i
    df['post']    = (df['Date'] >= cutoff).astype(int)                  # Post_t
    df['Month']   = df['Date'].dt.month                                 # 1..12 (for C(Month))

    # ----------------- Formelen som matcher ønsket modell ------------------ #
    # Y_it = α + β*(treated*post) + γ*Temp + θ*(Temp*treated) + δ_i + τ_t + ε
    # δ_i: C(group_definition)  |  τ_t: C(Hour) + C(Month)
    fe_terms = 'C(Hour) + C(Month)'
    use_group_fe = ('group_definition' in df.columns) and (df['group_definition'].nunique() > 1)
    if use_group_fe:
        fe_terms = f'C(group_definition) + {fe_terms}'

    y_var = 'Q("kWh/Metering_point")'
    if use_log:
        df = df.copy()
        df['ln_kwh_mp'] = np.log(df['kWh/Metering_point'])
        y_var = 'ln_kwh_mp'

    formula = f'{y_var} ~ treated:post + Lufttemperatur + Lufttemperatur:treated + {fe_terms}'

    # ----------------- Estimering: cluster-robuste SE ------------------ #
    cov_type = 'cluster'
    if use_group_fe:
        cov_kwds = {'groups': df['group_definition']}
    else:
        # Fallback hvis group_definition mangler/konstant
        cov_kwds = {'groups': df['Date']}

    model = smf.ols(formula=formula, data=df).fit(cov_type=cov_type, cov_kwds=cov_kwds)

    # ----------------- Hent nøkkelkoeffisienter ------------------ #
    def ci_get(name):
        if name in model.params.index:
            lo, hi = model.conf_int().loc[name].tolist()
            return model.params[name], lo, hi
        return np.nan, np.nan, np.nan

    beta,  beta_lo,  beta_hi  = ci_get('treated:post')                 # DiD-effekt
    theta, theta_lo, theta_hi = ci_get('Lufttemperatur:treated')       # diff. temp-respons
    gamma, gamma_lo, gamma_hi = ci_get('Lufttemperatur')               # temp-effekt i kontroll

    if verbose:
        print(model.summary())

    return {
        'model': model,
        'n_obs': int(model.nobs),
        'coef': {
            'DiD_beta_treated_post': {
                'coef': beta,  'ci_low': beta_lo,  'ci_high': beta_hi
            },
            'theta_temp_x_treated': {
                'coef': theta, 'ci_low': theta_lo, 'ci_high': theta_hi
            },
            'gamma_temp_level': {
                'coef': gamma, 'ci_low': gamma_lo, 'ci_high': gamma_hi
            }
        },
        'data': df
    }


def DifferenceinDifferenceTemp3(data_mNP, data_uNP, price_area, Temp, verbose=True):
    """
    DiD med log-utfall og Temp24 (24t rullende snitt):
      ln(Y_it) = α + β*(treated*post) + γ*Temp24_t + θ*(Temp24_t*treated) + δ_i + τ_t + ε_it
    - Enhets-FE: C(group_definition)
    - Tids-FE:   C(Hour) + C(Month)
    - Cluster-robuste SE på group_definition

    Parametre
    ---------
    data_mNP : pd.DataFrame    # Med_NP
    data_uNP : pd.DataFrame    # Uten_NP
    price_area : str
    Temp : pd.DataFrame        # kolonner: Date, Hour, Lufttemperatur
    verbose : bool             # print summary

    Returnerer
    ----------
    dict med 'model', 'n_obs', 'coef' (β, θ, γ) og 'data' (analysematrise).
    """

    # ------------------- Dato-vinduer ------------------- #
    start_date_before = pd.Timestamp('2024-10-01')
    end_date_before   = pd.Timestamp('2025-01-31')

    start_date_after  = pd.Timestamp('2025-10-01')
    end_date_after    = pd.Timestamp('2026-01-31')

    cutoff = pd.Timestamp('2025-10-01')  # Post-periode starter

    # ------------------- Tidsfelter ------------------- #
    def prep_time(df):
        df = df.copy()
        df['start_time_utc'] = pd.to_datetime(
            df['start_time_utc'],
            format='%Y-%m-%d %H:%M:%S',
            errors='coerce',
            utc=True
        )
        # Normaliser til "naiv" UTC for enkel Date/Hour
        st = df['start_time_utc'].dt.tz_convert('UTC').dt.tz_localize(None)
        df['Date'] = pd.to_datetime(st.dt.date)
        df['Hour'] = st.dt.hour.astype(int)
        return df

    data_mNP = prep_time(data_mNP)
    data_uNP = prep_time(data_uNP)

    # ----------------- Filter prisområde ------------------ #
    data_demand_NP     = data_mNP.loc[data_mNP['price_area'] == price_area].copy()
    data_demand_UtenNP = data_uNP.loc[data_uNP['price_area'] == price_area].copy()

    # ----------------- Filtrer perioder ------------------- #
    def window(df):
        m_before = (df['Date'] >= start_date_before) & (df['Date'] <= end_date_before)
        m_after  = (df['Date'] >= start_date_after)  & (df['Date'] <= end_date_after)
        return df.loc[m_before | m_after].copy()

    data_demand_NP     = window(data_demand_NP)
    data_demand_UtenNP = window(data_demand_UtenNP)

    # ------------- KPI: kWh per målepunkt ------------- #
    for df0 in [data_demand_NP, data_demand_UtenNP]:
        df0['kWh/Metering_point'] = df0['consumption_kwh'] / df0['metering_point_count']

    # ----------- Aggreger per (Date, Hour, group_definition) ----------- #
    group_keys = ['Date', 'Hour', 'group_definition']
    np_g   = data_demand_NP.groupby(group_keys, as_index=False)['kWh/Metering_point'].mean()
    uten_g = data_demand_UtenNP.groupby(group_keys, as_index=False)['kWh/Metering_point'].mean()

    # ----------------- Temperatur ------------------ #
    # 1) Aggreger til én rad per (Date, Hour)
    T = Temp.copy()
    T['Date'] = pd.to_datetime(T['Date'])
    T['Hour'] = T['Hour'].astype(int)

    mTb = (T['Date'] >= start_date_before) & (T['Date'] <= end_date_before)
    mTa = (T['Date'] >= start_date_after)  & (T['Date'] <= end_date_after)
    T = T.loc[mTb | mTa].copy()

    temp_hourly = (T.groupby(['Date', 'Hour'], as_index=False)
                     .agg(Lufttemperatur=('Lufttemperatur', 'mean')))

    # 2) Lag tidsstempel for ryddig rullende vindu (24 timer)
    temp_hourly['ts'] = temp_hourly['Date'] + pd.to_timedelta(temp_hourly['Hour'], unit='h')
    temp_hourly = temp_hourly.sort_values('ts')

    # Obs: Dette forutsetter (omtrent) komplett time-serie. Hvis det er hull,
    # vurder tidbasert rolling med resampling til H-frekvens først.
    temp_hourly['Temp24'] = temp_hourly['Lufttemperatur'].rolling(window=24, min_periods=1).mean()

    # Behold bare nødvendige felter til merge
    temp_hourly = temp_hourly[['Date', 'Hour', 'Lufttemperatur', 'Temp24']]

    # -------- Merge datasett -------- #
    np_g['Norgespris']   = 'Med_NP'
    uten_g['Norgespris'] = 'Uten_NP'
    df = pd.concat([np_g, uten_g], ignore_index=True)

    df = df.merge(temp_hourly, on=['Date', 'Hour'], how='left')

    # Fjern ikke-positive utfall (for log)
    df = df[df['kWh/Metering_point'] > 0].copy()
    # Lag log-utfall
    df['ln_kwh_mp'] = np.log(df['kWh/Metering_point'])

    # ----------------- DiD-variabler ------------------ #
    df['treated'] = (df['Norgespris'] == 'Med_NP').astype(int)  # Treatment_i
    df['post']    = (df['Date'] >= cutoff).astype(int)          # Post_t
    df['Month']   = df['Date'].dt.month                         # 1..12

    # ----------------- Modell (log + Temp24) ------------------ #
    # ln(Y) = β*(treated*post) + γ*Temp24 + θ*(Temp24*treated) + FE + ε
    fe_terms = 'C(Hour) + C(Month)'
    use_group_fe = ('group_definition' in df.columns) and (df['group_definition'].nunique() > 1)
    if use_group_fe:
        fe_terms = f'C(group_definition) + {fe_terms}'

    formula = f'ln_kwh_mp ~ treated:post + Temp24 + Temp24:treated + {fe_terms}'

    # Cluster-robuste SE
    cov_type = 'cluster'
    if use_group_fe:
        cov_kwds = {'groups': df['group_definition']}
    else:
        cov_kwds = {'groups': df['Date']}  # fallback: svakere, men bedre enn ingenting

    model = smf.ols(formula=formula, data=df).fit(cov_type=cov_type, cov_kwds=cov_kwds)

    # ----------------- Nøkkelkoeffisienter ------------------ #
    def ci_get(name):
        if name in model.params.index:
            lo, hi = model.conf_int().loc[name].tolist()
            return model.params[name], lo, hi
        return np.nan, np.nan, np.nan

    beta,  beta_lo,  beta_hi  = ci_get('treated:post')      # DiD-effekt (log-skala)
    theta, theta_lo, theta_hi = ci_get('Temp24:treated')    # diff. temperaturrespons
    gamma, gamma_lo, gamma_hi = ci_get('Temp24')            # temp-effekt i kontroll

    if verbose:
        print(model.summary())

    return {
        'model': model,
        'n_obs': int(model.nobs),
        'coef': {
            'DiD_beta_treated_post (log)': {
                'coef': beta, 'ci_low': beta_lo, 'ci_high': beta_hi,
                'pct_effect_approx': 100 * beta,  # liten beta
                'pct_effect_exact': 100 * (np.exp(beta) - 1)  # eksakt
            },
            'theta_Temp24_x_treated': {
                'coef': theta, 'ci_low': theta_lo, 'ci_high': theta_hi
            },
            'gamma_Temp24_level': {
                'coef': gamma, 'ci_low': gamma_lo, 'ci_high': gamma_hi
            }
        },
        'data': df
    }

#DifferenceinDifference(data_mNP_NO1, data_uNP_NO1, 'NO1',
                           #make_plot = True, plot_adjusted = True, backtransform_log = False, savepath = None)  # Ved NO1 bruk Temp_Oslo, og ved NO5 bruk Temp_Bergen
#DifferenceinDifferenceTemp(data_mNP_NO1, data_uNP_NO1, 'NO1', Temp_Oslo)
#DifferenceinDifferenceTemp2(data_mNP_NO1, data_uNP_NO1, 'NO1', Temp_Oslo, use_log=True, verbose=True)
#DifferenceinDifferenceTemp3(data_mNP_NO1, data_uNP_NO1, 'NO1', Temp_Oslo, verbose=True)


model, df_used, fig, ax = DifferenceinDifference(
    data_mNP_NO1, data_uNP_NO1, price_area='NO1',
    make_plot=True,           # slå plott på
    plot_adjusted=True,       # bruk modellens prediksjoner i figuren
    backtransform_log=True,  # sett True hvis du vil ha nivå-akse via smearing
    savepath=None             # evt. 'did_plot.png'
)




