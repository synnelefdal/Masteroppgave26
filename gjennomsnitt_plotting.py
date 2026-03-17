import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')
data_rest_NO1 = pd.read_csv('All_Demand_Data/NO1_resten.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')
data_rest_NO2 = pd.read_csv('All_Demand_Data/NO2_resten.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')
data_rest_NO5 = pd.read_csv('All_Demand_Data/NO5_resten.csv', sep= ';')



def plot_daglig_gjennomsnitt(data_mNP, data_uNP, data_resten, price_area):

    # --- Helper: Forbered data ---
    def prep(df):
        df = df.copy()
        df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True)

        # kWh per målepunkt
        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']

        # Lag dato-kolonne
        df['Date'] = df['start_time_utc'].dt.date

        # Daglig gjennomsnitt
        dag = df.groupby('Date')['kWh/metering_point'].mean()

        # Liten smoothing: 3-dagers glidende gjennomsnitt
        dag_smooth = dag.rolling(window=3, center=True, min_periods=1).mean()

        return dag_smooth

    # --- Beregn profiler ---
    dag_mNP = prep(data_mNP)
    dag_uNP = prep(data_uNP)
    dag_rest = prep(data_resten)

    # --- Plot ---
    plt.figure(figsize=(12,6))

    plt.plot(dag_mNP.index, dag_mNP.values, label='With Norgespris', linewidth=2.5)
    plt.plot(dag_uNP.index, dag_uNP.values, label='Without Norgespris', linewidth=2.5)
    plt.plot(dag_rest.index, dag_rest.values, label='Remaining', linewidth=2.5)

    #plt.title(f'Daily Average Consumption – {price_area}', fontsize=18)
    plt.xlabel('Date', fontsize=20)
    plt.ylabel('kWh per household', fontsize=20)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.show()



#plot_daglig_gjennomsnitt(data_mNP_NO5, data_uNP_NO5, data_rest_NO5, "NO5")


def plot_daglig_gjennomsnitt_prissone(
    data_NO1_mNP, data_NO1_uNP, data_NO1_rest,
    data_NO2_mNP, data_NO2_uNP, data_NO2_rest,
    data_NO5_mNP, data_NO5_uNP, data_NO5_rest,
):

    def prep_total(df_mNP, df_uNP, df_rest):
        # Kombiner alle tre datasettene
        df = pd.concat([df_mNP, df_uNP, df_rest]).copy()

        # Konverter tid
        df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True)

        # kWh per målepunkt
        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']

        # Lag datokolonne
        df['Date'] = df['start_time_utc'].dt.date

        # Daglig gjennomsnitt for hele prissonen
        dag = df.groupby('Date')['kWh/metering_point'].mean()

        # Smoothing (samme som forrige funksjon)
        dag_smooth = dag.rolling(window=3, center=True, min_periods=1).mean()

        return dag_smooth


    # ---- Beregn for NO1, NO2, NO5 ----
    dag_NO1 = prep_total(data_NO1_mNP, data_NO1_uNP, data_NO1_rest)
    dag_NO2 = prep_total(data_NO2_mNP, data_NO2_uNP, data_NO2_rest)
    dag_NO5 = prep_total(data_NO5_mNP, data_NO5_uNP, data_NO5_rest)

    # ---- Plot ----
    plt.figure(figsize=(12,6))

    plt.plot(dag_NO1.index, dag_NO1.values, linewidth=1.5, label='NO1')
    plt.plot(dag_NO2.index, dag_NO2.values, linewidth=1.5, label='NO2')
    plt.plot(dag_NO5.index, dag_NO5.values, linewidth=1.5, label='NO5')

    #plt.title('Daily Average Consumption per Price Zone', fontsize=18)
    plt.xlabel('Date', fontsize=20)
    plt.ylabel('kWh per household', fontsize=20)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.show()

'''plot_daglig_gjennomsnitt_prissone(
    data_mNP_NO1, data_uNP_NO1, data_rest_NO1,
    data_mNP_NO2, data_uNP_NO2, data_rest_NO2,
    data_mNP_NO5, data_uNP_NO5, data_rest_NO5
)'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_full_analysis(data_mNP, data_uNP, data_resten, price_area):

    def prep(df):
        df = df.copy()
        df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True)
        df['kWh/mp'] = df['consumption_kwh'] / df['metering_point_count']
        df['Date'] = df['start_time_utc'].dt.date
        df['Weekday'] = df['start_time_utc'].dt.dayofweek
        df['Month'] = df['start_time_utc'].dt.to_period("M")
        return df

    mNP = prep(data_mNP)
    uNP = prep(data_uNP)
    rest = prep(data_resten)

    groups = {
        "Med NP": mNP["kWh/mp"],
        "Uten NP": uNP["kWh/mp"],
        "Resten": rest["kWh/mp"]
    }

    colors = {
        "Med NP": "#4e79a7",
        "Uten NP": "#f28e2b",
        "Resten": "#59a14f"
    }

    # -----------------------
    # 1) Boksplot + Histogram + ECDF + Load Duration Curve
    # -----------------------

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Statistisk profil – {price_area}", fontsize=18)

    # --- A) Boxplot ---
    axs[0, 0].boxplot([g.dropna() for g in groups.values()],
                      labels=groups.keys(),
                      patch_artist=True)
    axs[0, 0].set_title("Boksplot")
    axs[0, 0].set_ylabel("kWh per målepunkt")
    axs[0, 0].grid(alpha=0.3)

    # --- B) Histogram/KDE ---
    for label, s in groups.items():
        s.dropna().plot(kind="kde", linewidth=2,
                        color=colors[label], ax=axs[0, 1])
    axs[0, 1].set_title("Fordeling (KDE)")
    axs[0, 1].grid(alpha=0.3)

    # --- C) ECDF ---
    for label, s in groups.items():
        x = np.sort(s.dropna())
        y = np.linspace(0, 1, len(x))
        axs[1, 0].plot(x, y, label=label, linewidth=2, color=colors[label])
    axs[1, 0].set_title("ECDF (kumulativ fordeling)")
    axs[1, 0].set_xlabel("kWh per målepunkt")
    axs[1, 0].grid(alpha=0.3)
    axs[1, 0].legend()

    # --- D) Load Duration Curve ---
    for label, s in groups.items():
        sorted_vals = np.sort(s.dropna())[::-1]
        axs[1, 1].plot(sorted_vals, linewidth=2, label=label, color=colors[label])
    axs[1, 1].set_title("Load Duration Curve")
    axs[1, 1].set_ylabel("kWh per målepunkt")
    axs[1, 1].grid(alpha=0.3)
    axs[1, 1].legend()

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    # -----------------------
    # 2) Daglig, ukedags- og månedlig profil (smooth)
    # -----------------------

    # Daglig snitt
    def daily(df):
        return df.groupby("Date")["kWh/mp"].mean().rolling(3, center=True, min_periods=1).mean()

    # Ukedagssnitt
    def weekday(df):
        return df.groupby("Weekday")["kWh/mp"].mean()

    # Månedssnitt
    def monthly(df):
        m = df.groupby("Month")["kWh/mp"].mean()
        m.index = m.index.to_timestamp()  # pent i plot
        return m.rolling(2, center=True, min_periods=1).mean()

    # --- Daglig ---
    plt.figure(figsize=(12,5))
    plt.title(f"Daglig gjennomsnitt – {price_area}", fontsize=18)
    for label, df in zip(groups.keys(), [mNP, uNP, rest]):
        plt.plot(daily(df).index, daily(df).values, linewidth=2.5, label=label, color=colors[label])
    plt.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.ylabel("kWh per målepunkt")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --- Ukedag ---
    plt.figure(figsize=(10,4))
    plt.title(f"Ukedagssnitt – {price_area}", fontsize=18)
    weekday_names = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
    for label, df in zip(groups.keys(), [mNP, uNP, rest]):
        plt.plot(weekday_names, weekday(df).values, linewidth=2.5, label=label, color=colors[label])
    plt.grid(alpha=0.3)
    plt.ylabel("kWh per målepunkt")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --- Månedlig ---
    plt.figure(figsize=(12,5))
    plt.title(f"Månedlig gjennomsnitt – {price_area}", fontsize=18)
    for label, df in zip(groups.keys(), [mNP, uNP, rest]):
        plt.plot(monthly(df).index, monthly(df).values, linewidth=2.5, label=label, color=colors[label])
    plt.grid(alpha=0.3)
    plt.ylabel("kWh per målepunkt")
    plt.legend()
    plt.tight_layout()
    plt.show()


res_NO1 = plot_full_analysis(
    data_mNP_NO1, data_uNP_NO1, data_rest_NO1,
    price_area='NO1',
    )
#denne er veldig overkill tror eg

