import pandas as pd
import matplotlib.pyplot as plt


# -------------------------------- ALLE CSV FILER MED FORBRUKSDATA -------------------------------- #

data_NO1_uNP = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO1_uNP.csv', sep= ';')
data_NO1_NPoct = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO1_NP_oct.csv', sep= ';')
data_NO1_NPnov = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO1_NP_nov.csv', sep= ';')
data_NO1_NPdec = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO1_NP_dec.csv', sep= ';')
data_NO1_NPjan = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO1_NP_jan.csv', sep= ';')
data_NO1_NPfeb = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO1_NP_feb.csv', sep= ';')
data_NO1_NPmars = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO1_NP_mars.csv', sep= ';')
data_NO1_NPapril = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO1_NP_april.csv', sep= ';')


data_NO2_uNP = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO2_uNP.csv', sep= ';')
data_NO2_NPoct = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO2_NP_oct.csv', sep= ';')
data_NO2_NPnov = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO2_NP_nov.csv', sep= ';')
data_NO2_NPdec = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO2_NP_dec.csv', sep= ';')
data_NO2_NPjan = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO2_NP_jan.csv', sep= ';')
data_NO2_NPfeb = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO2_NP_feb.csv', sep= ';')
data_NO2_NPmars = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO2_NP_mars.csv', sep= ';')
data_NO2_NPapril = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO2_NP_april.csv', sep= ';')


data_NO5_uNP = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO5_uNP.csv', sep= ';')
data_NO5_NPoct = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO5_NP_oct.csv', sep= ';')
data_NO5_NPnov = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO5_NP_nov.csv', sep= ';')
data_NO5_NPdec = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO5_NP_dec.csv', sep= ';')
data_NO5_NPjan = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO5_NP_jan.csv', sep= ';')
data_NO5_NPfeb = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO5_NP_feb.csv', sep= ';')
data_NO5_NPmars = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO5_NP_mars.csv', sep= ';')
data_NO5_NPapril = pd.read_csv('/Users/synnelefdal/Desktop/<3/5.klasse/Master/NY_All_Demand_Data/NO5_NP_april.csv', sep= ';')


def plot_daglig_gjennomsnitt(data_mNP, data_uNP, data_resten, price_area):

    # --- Forbered data --- #
    def prep(df):
        df = df.copy()
        df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True)

        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']            # kWh per målepunkt

        df['Date'] = df['start_time_utc'].dt.date                                                # Lag dato-kolonne

        dag = df.groupby('Date')['kWh/metering_point'].mean()                                    # Daglig gjennomsnitt

        dag_smooth = dag.rolling(window=3, center=True, min_periods=1).mean()

        return dag_smooth

    # --- Beregn profiler --- #
    dag_mNP = prep(data_mNP)
    dag_uNP = prep(data_uNP)
    dag_rest = prep(data_resten)

    # --- Plot --- #
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
        df = pd.concat([df_mNP, df_uNP, df_rest]).copy()                               # Kombiner alle tre datasettene

        df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True)          # Konverter tid

        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']  # kWh per målepunkt

        df['Date'] = df['start_time_utc'].dt.date                                      # Lag datokolonne

        dag = df.groupby('Date')['kWh/metering_point'].mean()                          # Daglig gjennomsnitt for hele prissonen

        dag_smooth = dag.rolling(window=3, center=True, min_periods=1).mean()

        return dag_smooth


    # ---- Beregn for NO1, NO2, NO5 ---- #
    dag_NO1 = prep_total(data_NO1_mNP, data_NO1_uNP, data_NO1_rest)
    dag_NO2 = prep_total(data_NO2_mNP, data_NO2_uNP, data_NO2_rest)
    dag_NO5 = prep_total(data_NO5_mNP, data_NO5_uNP, data_NO5_rest)

    # ---- Plot ---- #
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



def plot_full_analysis(data_mNP, data_uNP, data_resten, price_area):

    def prep(df):
        df = df.copy()
        df['start_time_utc'] = pd.to_datetime(df['start_time_utc'], utc=True)

        #---- KUTT DATA ETTER SEPTEMBER 2025 ---- #
        #cutoff = pd.Timestamp("2025-10-01", tz="UTC")
        #df = df[df['start_time_utc'] <= cutoff]

        # ---- KUTT DATA TIL ØNSKET PERIODE ---- #
        start_cutoff = pd.Timestamp("2023-09-30", tz="UTC")
        end_cutoff = pd.Timestamp("2026-03-31", tz="UTC")

        df = df[
            (df['start_time_utc'] >= start_cutoff) &
            (df['start_time_utc'] <= end_cutoff)
            ]

        df['kWh/mp'] = df['consumption_kwh'] / df['metering_point_count']
        df['Date'] = df['start_time_utc'].dt.date
        df['Weekday'] = df['start_time_utc'].dt.dayofweek
        df['Month'] = df['start_time_utc'].dt.to_period("M")
        return df

    mNP = prep(data_mNP)
    uNP = prep(data_uNP)
    #rest = prep(data_resten)

    groups = {
        "Med NP": mNP["kWh/mp"],
        "Uten NP": uNP["kWh/mp"]#,
        #"Resten": rest["kWh/mp"]
    }

    colors = {
        "Med NP": "#4e79a7",
        "Uten NP": "#f28e2b"#,
        #"Resten": "#59a14f"
    }

    def monthly(df):
        m = df.groupby("Month")["kWh/mp"].mean()
        m.index = m.index.to_timestamp()  # pent i plot
        return m.rolling(2, center=True, min_periods=1).mean()


    TRANSLATIONS = {
        "Med NP": "With Norway Price ",
        "Uten NP": "Without Norway Price",
        "Månedlig gjennomsnitt": "Monthly average",
        "Daglig gjennomsnitt": "Daily average",
        "Ukedagssnitt": "Weekday average",
        "kWh per målepunkt": "kWh per metering point",
        "Statistisk profil": "Statistical profile",
        "Fordeling (KDE)": "Distribution (KDE)",
        "Boksplot": "Box plot",
        "Load Duration Curve": "Load duration curve",
    }

    def _(text):
        return TRANSLATIONS.get(text, text)

    # --- Månedlig --- #
    plt.figure(figsize=(12,5))
    #plt.title(f"Monthly Average – {price_area}", fontsize=18)
    for label, df in zip(groups.keys(), [mNP, uNP]):
        plt.plot(monthly(df).index, monthly(df).values, linewidth=2.5, label=_(label), color=colors[label])
        plt.legend(fontsize = 20)
    plt.grid(alpha=0.3)
    plt.ylabel("Average kWh per household", size = 25 )
    plt.xlabel('Month', size = 25)
    plt.xticks(fontsize = 20)
    plt.yticks(fontsize = 20)
    plt.tight_layout()
    plt.show()

def plot_normalisert_abs(data_mNP, data_uNP):
    def prep(df):
        df = df.copy()
        df["start_time_utc"] = pd.to_datetime(df["start_time_utc"], utc=True)

        start_cutoff = pd.Timestamp("2023-09-30", tz="UTC")
        end_cutoff = pd.Timestamp("2026-03-31", tz="UTC")

        df = df[
            (df["start_time_utc"] >= start_cutoff) &
            (df["start_time_utc"] <= end_cutoff)
            ]

        df["kWh/mp"] = df["consumption_kwh"] / df["metering_point_count"]
        df["Month"] = df["start_time_utc"].dt.to_period("M")

        return df

    mNP = prep(data_mNP)
    uNP = prep(data_uNP)

    def monthly(df):
        m = df.groupby("Month")["kWh/mp"].mean()
        m.index = m.index.to_timestamp()
        return m.rolling(2, center=True, min_periods=1).mean()

    def normalize(series):
        return series / series.mean()

    # ------- PLOT ------- #

    colors = {
        "With Norway Price": "#4e79a7",
        "Without Norway Price": "#f28e2b"
    }

    plt.figure(figsize=(12, 5))

    series_mNP = normalize(monthly(mNP))
    series_uNP = normalize(monthly(uNP))

    plt.plot(
        series_mNP.index,
        series_mNP.values,
        linewidth=2.5,
        label="With Norway Price",
        color=colors["With Norway Price"]
    )

    plt.plot(
        series_uNP.index,
        series_uNP.values,
        linewidth=2.5,
        label="Without Norway Price",
        color=colors["Without Norway Price"]
    )

    # ------- Referanselinje ------- #
    plt.axhline(1.0, color="black", linestyle="--", linewidth=1, alpha=0.6)

    plt.grid(alpha=0.3)
    plt.ylabel("Normalized kWh per household", fontsize=25)
    plt.xlabel("Month", fontsize=25)

    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)

    plt.tight_layout()
    plt.show()


data_NO1_mNP = pd.concat( [data_NO1_NPoct, data_NO1_NPnov, data_NO1_NPdec,data_NO1_NPjan,data_NO1_NPfeb,data_NO1_NPmars], ignore_index=True)
data_NO2_mNP = pd.concat([data_NO2_NPoct, data_NO2_NPnov, data_NO2_NPdec,data_NO2_NPjan,data_NO2_NPfeb,data_NO2_NPmars], ignore_index=True)
data_NO5_mNP = pd.concat( [data_NO5_NPoct, data_NO5_NPnov, data_NO5_NPdec,data_NO5_NPjan,data_NO5_NPfeb,data_NO5_NPmars], ignore_index=True)

data_NO1_rest = pd.concat([data_NO1_NPapril], ignore_index=True)
data_NO2_rest = pd.concat([data_NO2_NPapril] , ignore_index=True)
data_NO5_rest = pd.concat([data_NO5_NPapril], ignore_index=True)


plot_full_analysis(data_NO1_mNP, data_NO1_uNP, data_NO1_rest,'NO1')
plot_full_analysis(data_NO2_mNP, data_NO2_uNP, data_NO2_rest, 'NO2')
plot_full_analysis(data_NO5_mNP, data_NO5_uNP, data_NO5_rest, 'NO5')

plot_normalisert_abs(data_NO1_mNP, data_NO1_uNP)
plot_normalisert_abs(data_NO2_mNP, data_NO2_uNP)
plot_normalisert_abs(data_NO5_mNP, data_NO5_uNP)
