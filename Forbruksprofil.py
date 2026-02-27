import pandas as pd
import matplotlib.pyplot as plt

data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')


timestamp_col = "timestamp"
consumption_col = "consumption"

data_mNP_NO1[timestamp_col] = pd.to_datetime(data_mNP_NO1[timestamp_col])
data_uNP_NO1[timestamp_col] = pd.to_datetime(data_uNP_NO1[timestamp_col])

data_mNP_NO2[timestamp_col] = pd.to_datetime(data_mNP_NO2[timestamp_col])
data_uNP_NO2[timestamp_col] = pd.to_datetime(data_uNP_NO2[timestamp_col])

data_mNP_NO5[timestamp_col] = pd.to_datetime(data_mNP_NO5[timestamp_col])
data_uNP_NO5[timestamp_col] = pd.to_datetime(data_uNP_NO5[timestamp_col])


norgespris_vinter_start = "2025-11-01"
norgespris_vinter_slutt = "2026-01-31"

forrige_vinter_start = "2024-11-01"
forrige_vinter_slutt = "2025-01-31"

# -------- NO1 --------- #
data_mNP_NO1 = data_mNP_NO1[(data_mNP_NO1[timestamp_col] >= norgespris_vinter_start) &
                            (data_mNP_NO1[timestamp_col] <= norgespris_vinter_slutt)]
data_uNP_NO1 = data_uNP_NO1[(data_uNP_NO1[timestamp_col] >= norgespris_vinter_start) &
                            (data_uNP_NO1[timestamp_col] <= norgespris_vinter_slutt)]

data_mNP_NO1 = data_mNP_NO1[(data_mNP_NO1[timestamp_col] >= forrige_vinter_start) &
                            (data_mNP_NO1[timestamp_col] <= forrige_vinter_slutt)]
data_uNP_NO1 = data_uNP_NO1[(data_uNP_NO1[timestamp_col] >= forrige_vinter_start) &
                            (data_uNP_NO1[timestamp_col] <= forrige_vinter_slutt)]

data_mNP_NO1 = data_mNP_NO1[(data_mNP_NO1[timestamp_col] >= norgespris_vinter_start) &
                            (data_mNP_NO1[timestamp_col] <= norgespris_vinter_slutt)]
data_uNP_NO1 = data_uNP_NO1[(data_uNP_NO1[timestamp_col] >= norgespris_vinter_start) &
                            (data_uNP_NO1[timestamp_col] <= norgespris_vinter_slutt)]

data_mNP_NO1 = data_mNP_NO1[(data_mNP_NO1[timestamp_col] >= forrige_vinter_start) &
                            (data_mNP_NO1[timestamp_col] <= forrige_vinter_slutt)]
data_uNP_NO1 = data_uNP_NO1[(data_uNP_NO1[timestamp_col] >= forrige_vinter_start) &
                            (data_uNP_NO1[timestamp_col] <= forrige_vinter_slutt)]

# -------- NO2 --------- #
data_mNP_NO2 = data_mNP_NO2[(data_mNP_NO2[timestamp_col] >= norgespris_vinter_start) &
                            (data_mNP_NO2[timestamp_col] <= norgespris_vinter_slutt)]
data_uNP_NO2 = data_uNP_NO2[(data_uNP_NO2[timestamp_col] >= norgespris_vinter_start) &
                            (data_uNP_NO2[timestamp_col] <= norgespris_vinter_slutt)]

data_mNP_NO2 = data_mNP_NO2[(data_mNP_NO2[timestamp_col] >= forrige_vinter_start) &
                            (data_mNP_NO2[timestamp_col] <= forrige_vinter_slutt)]
data_uNP_NO2 = data_uNP_NO2[(data_uNP_NO2[timestamp_col] >= forrige_vinter_start) &
                            (data_uNP_NO2[timestamp_col] <= forrige_vinter_slutt)]

data_mNP_NO2 = data_mNP_NO2[(data_mNP_NO2[timestamp_col] >= norgespris_vinter_start) &
                            (data_mNP_NO2[timestamp_col] <= norgespris_vinter_slutt)]
data_uNP_NO2 = data_uNP_NO2[(data_uNP_NO2[timestamp_col] >= norgespris_vinter_start) &
                            (data_uNP_NO2[timestamp_col] <= norgespris_vinter_slutt)]

data_mNP_NO2 = data_mNP_NO2[(data_mNP_NO2[timestamp_col] >= forrige_vinter_start) &
                            (data_mNP_NO2[timestamp_col] <= forrige_vinter_slutt)]
data_uNP_NO2 = data_uNP_NO2[(data_uNP_NO2[timestamp_col] >= forrige_vinter_start) &
                            (data_uNP_NO2[timestamp_col] <= forrige_vinter_slutt)]

# -------- NO5 --------- #
data_mNP_NO5 = data_mNP_NO5[(data_mNP_NO5[timestamp_col] >= norgespris_vinter_start) &
                            (data_mNP_NO5[timestamp_col] <= norgespris_vinter_slutt)]
data_uNP_NO5 = data_uNP_NO5[(data_uNP_NO5[timestamp_col] >= norgespris_vinter_start) &
                            (data_uNP_NO5[timestamp_col] <= norgespris_vinter_slutt)]

data_mNP_NO5 = data_mNP_NO5[(data_mNP_NO5[timestamp_col] >= forrige_vinter_start) &
                            (data_mNP_NO5[timestamp_col] <= forrige_vinter_slutt)]
data_uNP_NO5 = data_uNP_NO5[(data_uNP_NO5[timestamp_col] >= forrige_vinter_start) &
                            (data_uNP_NO5[timestamp_col] <= forrige_vinter_slutt)]

data_mNP_NO5 = data_mNP_NO5[(data_mNP_NO5[timestamp_col] >= norgespris_vinter_start) &
                            (data_mNP_NO5[timestamp_col] <= norgespris_vinter_slutt)]
data_uNP_NO5 = data_uNP_NO5[(data_uNP_NO5[timestamp_col] >= norgespris_vinter_start) &
                            (data_uNP_NO5[timestamp_col] <= norgespris_vinter_slutt)]

data_mNP_NO5 = data_mNP_NO5[(data_mNP_NO5[timestamp_col] >= forrige_vinter_start) &
                            (data_mNP_NO5[timestamp_col] <= forrige_vinter_slutt)]
data_uNP_NO5 = data_uNP_NO5[(data_uNP_NO5[timestamp_col] >= forrige_vinter_start) &
                            (data_uNP_NO5[timestamp_col] <= forrige_vinter_slutt)]



def plot_profil(df_med, df_uten, title):
    # Legg til time-of-day
    df_med = df_med.copy()
    df_uten = df_uten.copy()

    df_med["hour"] = df_med[timestamp_col].dt.hour
    df_uten["hour"] = df_uten[timestamp_col].dt.hour

    # Beregn gjennomsnitt pr time
    profil_med = df_med.groupby("hour")[consumption_col].mean()
    profil_uten = df_uten.groupby("hour")[consumption_col].mean()

    plt.figure(figsize=(10, 5))
    plt.plot(profil_med.index, profil_med.values, label="Med Norgespris")
    plt.plot(profil_uten.index, profil_uten.values, label="Uten Norgespris")

    plt.title(title)
    plt.xlabel("Time på døgnet")
    plt.ylabel("Gjennomsnittlig forbruk (kWh)")
    plt.grid(True)
    plt.legend()
    plt.show()


plot_profil(data_mNP_NO1, data_uNP_NO1, "Forbruksprofil – Norgespris-vinter")
plot_profil(data_mNP_NO1, data_uNP_NO1, "Forbruksprofil – Forrige vinter")
