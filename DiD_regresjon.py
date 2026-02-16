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


    # ------- Plotting ----------- #

    '''fig, ax = plt.subplots(figsize=(10, 6))

    # --- A, B, C, D punkter ---
    A = (0, 2.0)  # Kontroll pre
    D = (1, 4.0)  # Kontroll post
    B = (0, 3.5)  # Behandling pre

    # Kontrafaktisk post (parallell med kontroll)
    Cprime_y = B[1] + (D[1] - A[1])
    Cprime = (1, Cprime_y)

    # Faktisk post med DiD-effekt
    beta3 = 2.0
    C = (1, Cprime_y + beta3)

    # --- Plot kontrollgruppen ---
    ax.plot([A[0], D[0]], [A[1], D[1]], color='green', lw=3, label='Kontrollgruppe')
    ax.scatter(A[0], A[1], s=80, color='green')
    ax.scatter(D[0], D[1], s=80, color='green')
    ax.text(A[0] - 0.05, A[1] - 0.25, "A", fontsize=12, fontweight="bold", color="green")
    ax.text(D[0] + 0.03, D[1] + 0.2, "D", fontsize=12, fontweight="bold", color="green")

    # --- Plot behandlingsgruppen før intervensjon ---
    ax.plot([B[0], 0.5], [B[1], Cprime_y - (0.5 * (D[1] - A[1]))],
            color='firebrick', lw=3)
    ax.scatter(B[0], B[1], s=80, color='firebrick')
    ax.text(B[0] - 0.05, B[1] - 0.25, "B", fontsize=12, fontweight="bold", color="firebrick")

    # --- Punktet der linjen skal "knekke" ---
    kink_x = 0.5
    kink_y = B[1] + (0.5 * (D[1] - A[1]))  # høyden der første linje slutter

    # --- Ny linje etter intervensjon ---
    ax.plot([kink_x, C[0]], [kink_y, C[1]], color='firebrick', lw=3, label='Behandlingsgruppe')
    ax.scatter(C[0], C[1], s=80, color='firebrick')
    ax.text(C[0] + 0.03, C[1] + 0.2, "C", fontsize=12, fontweight="bold", color="firebrick")

    # --- Kontrafaktisk stiplet linje ---
    ax.plot([kink_x, Cprime[0]], [kink_y, Cprime[1]],
            linestyle=':', color='firebrick', lw=2)

    # --- β3 marker ---
    arrow = FancyArrowPatch((1.05, Cprime[1]), (1.05, C[1]),
                            arrowstyle='<->', linewidth=1.5, color='black')
    ax.add_patch(arrow)
    ax.text(1.08, (Cprime[1] + C[1]) / 2, r'$\beta_3$', fontsize=14)

    # --- Blå vertikal intervensjonslinje ---
    ax.axvline(x=0.5, color='steelblue', linewidth=2)

    # --- Layout ---
    ax.set_xlim(-0.1, 1.2)
    ax.set_ylim(0, 10)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Pre-intervention', 'Post-intervention'])
    ax.set_ylabel("Outcome")
    ax.set_title("Difference-in-Differences")
    ax.legend()

    plt.tight_layout()
    plt.show()'''

    def plot_did_simple(df,
                        y='kWh/Metering_point',
                        time='Group',  # Before_ref / After_ref
                        treat='Norgespris',  # Uten_NP / Med_NP
                        pre='Before_ref',
                        post='After_ref',
                        ctrl='Uten_NP',
                        trt='Med_NP'):
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.patches import FancyArrowPatch

        # --- Beregn A B C D direkte fra data ---
        A = df[(df[time] == pre) & (df[treat] == ctrl)][y].mean()
        D = df[(df[time] == post) & (df[treat] == ctrl)][y].mean()
        B = df[(df[time] == pre) & (df[treat] == trt)][y].mean()
        C = df[(df[time] == post) & (df[treat] == trt)][y].mean()

        # kontrafaktisk C'
        Cprime = B + (D - A)

        # --- Figur ---
        fig, ax = plt.subplots(figsize=(10, 6))

        # blå intervensjonslinje
        ax.axvline(0.5, color='steelblue', lw=2)

        # kontrollgruppe (A -> D)
        ax.plot([0, 1], [A, D], color='green', lw=3, label='Kontrollgruppe')
        ax.scatter([0, 1], [A, D], color='green')

        # behandlingsgruppe før knekk (B -> kink)
        kink_y = B + 0.5 * (D - A)
        ax.plot([0, 0.5], [B, kink_y], color='firebrick', lw=3)

        # behandlingsgruppe etter knekk (kink -> C)
        ax.plot([0.5, 1], [kink_y, C], color='firebrick', lw=3, label='Behandlingsgruppe')
        ax.scatter([0, 1], [B, C], color='firebrick')

        # kontrafaktisk stiplet
        ax.plot([0.5, 1], [kink_y, Cprime], color='firebrick', linestyle=':', lw=2)

        # β3-markering
        arrow = FancyArrowPatch((1.05, Cprime), (1.05, C),
                                arrowstyle='<->', color='black', lw=1.5)
        ax.add_patch(arrow)
        ax.text(1.08, (C + Cprime) / 2, r'$\beta_3$', fontsize=14)

        # labels
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Pre-intervention', 'Post-intervention'])
        ax.set_ylabel("kWh per målepunkt")
        ax.set_title("Difference-in-Differences (basert på data)")

        ax.set_xlim(-0.1, 1.2)
        ax.set_ylim(0, max(A, B, C, D, Cprime) * 1.1)

        ax.legend()
        plt.tight_layout()
        plt.show()

        return {'A': A, 'B': B, 'C': C, 'D': D, 'Cprime': Cprime}

    print(plot_did_simple(df, y='kWh/Metering_point',
                        time='Group',  # Before_ref / After_ref
                        treat='Norgespris',  # Uten_NP / Med_NP
                        pre='Before_ref',
                        post='After_ref',
                        ctrl='Uten_NP',
                        trt='Med_NP'))



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



model = DifferenceinDifference(data_mNP_NO1, data_uNP_NO1, 'NO1')
#DifferenceinDifferenceTemp(data_mNP_NO1, data_uNP_NO1, 'NO1', Temp_Oslo)     #Ved NO1 bruk Temp_Oslo, og ved NO5 bruk Temp_Bergen






