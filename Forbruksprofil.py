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


def plot_timer(data_mNP, data_uNP, data_resten, price_area):

    # -------- REFERENCE ---------- #

    def prep_ref(df):
        df = df.copy()

        start_dato = '2025-01-01'
        slutt_dato = '2025-01-31'

        df['start_time_utc'] = pd.to_datetime((df['start_time_utc']), utc=True)
        df = df[(df['start_time_utc'] >= start_dato) & (df['start_time_utc'] <= slutt_dato)]

        df['Hour'] = df['start_time_utc'].dt.hour
        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']

        #print('her er gjennonsmittet?;', df['kWh/metering_point'].mean(), df['price_area'])
        return df

    df_mNP_ref = prep_ref(data_mNP)
    df_uNP_ref = prep_ref(data_uNP)

    mNP_prof_ref = df_mNP_ref.groupby('Hour')['kWh/metering_point'].mean()
    uNP_prof_ref = df_uNP_ref.groupby('Hour')['kWh/metering_point'].mean()

    # --------- TREATMENT ---------- #
    def prep_tre(df):
        df = df.copy()

        start_dato = '2026-01-01'
        slutt_dato = '2026-01-31'

        df['start_time_utc'] = pd.to_datetime((df['start_time_utc']), utc=True)
        df = df[(df['start_time_utc'] >= start_dato) & (df['start_time_utc'] <= slutt_dato)]

        df['Hour'] = df['start_time_utc'].dt.hour
        df['kWh/metering_point'] = df['consumption_kwh'] / df['metering_point_count']
        return df

    df_mNP_tre = prep_tre(data_mNP)
    df_uNP_tre = prep_tre(data_uNP)

    mNP_prof_tre = df_mNP_tre.groupby('Hour')['kWh/metering_point'].mean()
    uNP_prof_tre = df_uNP_tre.groupby('Hour')['kWh/metering_point'].mean()

    # --------- PLOT ------------- #
    plt.figure(figsize=(10,5))
    plt.plot(mNP_prof_ref.index, mNP_prof_ref.values, marker = 'o', label = 'With Norgespris 24/25')
    plt.plot(uNP_prof_ref.index, uNP_prof_ref.values, marker = 'o', label = 'Without Norgespris 24/25')

    plt.plot(mNP_prof_tre.index, mNP_prof_tre.values, marker='o', label= 'With Norgespris 25/26')
    plt.plot(uNP_prof_tre.index, uNP_prof_tre.values, marker='o', label= 'Without Norgespris 25/26')

    plt.xlabel('Hour', fontsize=20)
    plt.ylabel('kWh/metering_point', fontsize=20)
    #plt.title(f'Consumption - kWh per metering point in {price_area}', fontsize=20)
    plt.xticks(range(24))
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.grid(True, alpha = 0.3)
    plt.legend(fontsize=20)
    plt.tight_layout()
    plt.show()

plot_timer(data_mNP_NO5, data_uNP_NO5, data_rest_NO5, 'NO5')
plot_timer(data_mNP_NO1, data_uNP_NO1, data_rest_NO1, 'NO1')
plot_timer(data_mNP_NO2, data_uNP_NO2, data_rest_NO2, 'NO2')


def print_gjennomsnitt(data_mNP, data_uNP, data_resten, price_area):


    df_mNP = data_mNP.copy()
    df_uNP = data_uNP.copy()
    df_resten = data_resten.copy()

    start_dato = '2026-01-07'
    slutt_dato = '2026-01-08'

    df_mNP['start_time_utc'] = pd.to_datetime((df_mNP['start_time_utc']), utc=True)
    df_mNP = df_mNP[(df_mNP['start_time_utc'] >= start_dato) & (df_mNP['start_time_utc'] <= slutt_dato)]

    df_uNP['start_time_utc'] = pd.to_datetime((df_uNP['start_time_utc']), utc=True)
    df_uNP = df_uNP[(df_uNP['start_time_utc'] >= start_dato) & (df_uNP['start_time_utc'] <= slutt_dato)]

    df_resten['start_time_utc'] = pd.to_datetime((df_resten['start_time_utc']), utc=True)
    df_resten = df_resten[(df_resten['start_time_utc'] >= start_dato) & (df_resten['start_time_utc'] <= slutt_dato)]

    df_mNP['Hour'] = df_mNP['start_time_utc'].dt.hour
    df_mNP['kWh/metering_point'] = df_mNP['consumption_kwh'] / df_mNP['metering_point_count']
    print('Gjennomsnittsforbruk med NP for area:', price_area, df_mNP['kWh/metering_point'].mean())

    df_uNP['Hour'] = df_uNP['start_time_utc'].dt.hour
    df_uNP['kWh/metering_point'] = df_uNP['consumption_kwh'] / df_uNP['metering_point_count']
    print('Gjennomsnittsforbruk uten NP for area:', price_area, df_uNP['kWh/metering_point'].mean())

    df_resten['Hour'] = df_resten['start_time_utc'].dt.hour
    df_resten['kWh/metering_point'] = df_resten['consumption_kwh'] / df_resten['metering_point_count']
    print('Gjennomsnittsforbruk for resten for area:', price_area, df_resten['kWh/metering_point'].mean())

#print_gjennomsnitt(data_mNP_NO1, data_uNP_NO1, data_rest_NO1, 'NO1')




import pandas as pd
import matplotlib.pyplot as plt

# --- FUNKSJON: leser en fil og gjør den klar ---
def load_and_prepare(path):
    df = pd.read_csv(path, sep=';')

    # konverter tid til datetime
    df['start_time_utc'] = pd.to_datetime(df['start_time_utc'])

    # beregn forbruk per husholdning
    df['cons_per_house'] = df['consumption_kwh'] / df['metering_point_count']

    # beregn gjennomsnitt per dag
    df_daily = df.groupby(df['start_time_utc'].dt.date)['cons_per_house'].mean()
    return df_daily


# --- LES INN DATA ---

# NO1
NO1_m = load_and_prepare('All_Demand_Data/NO1_mNP.csv')
NO1_u = load_and_prepare('All_Demand_Data/NO1_uNP.csv')
NO1_r = load_and_prepare('All_Demand_Data/NO1_resten.csv')

# NO2
NO2_m = load_and_prepare('All_Demand_Data/NO2_mNP.csv')
NO2_u = load_and_prepare('All_Demand_Data/NO2_uNP.csv')
NO2_r = load_and_prepare('All_Demand_Data/NO2_resten.csv')

# NO5
NO5_m = load_and_prepare('All_Demand_Data/NO5_mNP.csv')
NO5_u = load_and_prepare('All_Demand_Data/NO5_uNP.csv')
NO5_r = load_and_prepare('All_Demand_Data/NO5_resten.csv')


# --- FIGUR FOR NO1 ---
plt.figure(figsize=(14, 7))
plt.plot(NO1_m.index, NO1_m.values, label='mNP')
plt.plot(NO1_u.index, NO1_u.values, label='uNP')
plt.plot(NO1_r.index, NO1_r.values, label='resten')
plt.title("Daglig gjennomsnittsforbruk per husholdning – NO1")
plt.xlabel("Dato")
plt.ylabel("Forbruk per husholdning (kWh)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# --- FIGUR FOR NO2 ---
plt.figure(figsize=(14, 7))
plt.plot(NO2_m.index, NO2_m.values, label='mNP')
plt.plot(NO2_u.index, NO2_u.values, label='uNP')
plt.plot(NO2_r.index, NO2_r.values, label='resten')
plt.title("Daglig gjennomsnittsforbruk per husholdning – NO2")
plt.xlabel("Dato")
plt.ylabel("Forbruk per husholdning (kWh)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# --- FIGUR FOR NO5 ---
plt.figure(figsize=(14, 7))
plt.plot(NO5_m.index, NO5_m.values, label='mNP')
plt.plot(NO5_u.index, NO5_u.values, label='uNP')
plt.plot(NO5_r.index, NO5_r.values, label='resten')
plt.title("Daglig gjennomsnittsforbruk per husholdning – NO5")
plt.xlabel("Dato")
plt.ylabel("Forbruk per husholdning (kWh)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


import pandas as pd
import matplotlib.pyplot as plt

# --- FUNKSJON: leser en fil og gjør den klar ---
def load_and_prepare(path):
    df = pd.read_csv(path, sep=';')

    # konverter tid til datetime
    df['start_time_utc'] = pd.to_datetime(df['start_time_utc'])

    # beregn forbruk per husholdning
    df['cons_per_house'] = df['consumption_kwh'] / df['metering_point_count']

    # dagsgjennomsnitt
    df_daily = df.groupby(df['start_time_utc'].dt.date)['cons_per_house'].mean()
    return df_daily


# --- LES INN DATA ---

# NO1
NO1_m = load_and_prepare('All_Demand_Data/NO1_mNP.csv')
NO1_u = load_and_prepare('All_Demand_Data/NO1_uNP.csv')
NO1_r = load_and_prepare('All_Demand_Data/NO1_resten.csv')

# NO2
NO2_m = load_and_prepare('All_Demand_Data/NO2_mNP.csv')
NO2_u = load_and_prepare('All_Demand_Data/NO2_uNP.csv')
NO2_r = load_and_prepare('All_Demand_Data/NO2_resten.csv')

# NO5
NO5_m = load_and_prepare('All_Demand_Data/NO5_mNP.csv')
NO5_u = load_and_prepare('All_Demand_Data/NO5_uNP.csv')
NO5_r = load_and_prepare('All_Demand_Data/NO5_resten.csv')


# --- FUNKSJON: plotter ett område ---
def plot_area(area_name, m, u, r):
    plt.figure(figsize=(14, 7))

    # hovedlinjer
    plt.plot(m.index, m.values, label='mNP')
    plt.plot(u.index, u.values, label='uNP')
    plt.plot(r.index, r.values, label='resten')

    # differanse mNP - uNP (aligner datoene)
    diff = m.subtract(u, fill_value=float('nan'))
    plt.plot(diff.index, diff.values, label='mNP - uNP', linewidth=3, linestyle='--')

    plt.title(f"Daglig gjennomsnittsforbruk per husholdning – {area_name}")
    plt.xlabel("Dato")
    plt.ylabel("Forbruk per husholdning (kWh)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# --- GENERER PLOTT ---

#plot_area("NO1", NO1_m, NO1_u, NO1_r)
#plot_area("NO2", NO2_m, NO2_u, NO2_r)
#plot_area("NO5", NO5_m, NO5_u, NO5_r)


import pandas as pd
import matplotlib.pyplot as plt

# --- FUNKSJON: leser fil og beregner forbruk per husholdning ---
def load_and_prepare_monthly(path):
    df = pd.read_csv(path, sep=';')

    # konverter tid til datetime
    df['start_time_utc'] = pd.to_datetime(df['start_time_utc'])

    # forbruk per husholdning
    df['cons_per_house'] = df['consumption_kwh'] / df['metering_point_count']

    # månedlig gjennomsnitt
    df_monthly = df.groupby(df['start_time_utc'].dt.to_period('M'))['cons_per_house'].mean()

    # konverter PeriodIndex → datetime for plotting
    df_monthly.index = df_monthly.index.to_timestamp()

    return df_monthly


# --- LAST INN DATA FOR ALLE OMRÅDER ---

# NO1
NO1_m = load_and_prepare_monthly('All_Demand_Data/NO1_mNP.csv')
NO1_u = load_and_prepare_monthly('All_Demand_Data/NO1_uNP.csv')
NO1_r = load_and_prepare_monthly('All_Demand_Data/NO1_resten.csv')

# NO2
NO2_m = load_and_prepare_monthly('All_Demand_Data/NO2_mNP.csv')
NO2_u = load_and_prepare_monthly('All_Demand_Data/NO2_uNP.csv')
NO2_r = load_and_prepare_monthly('All_Demand_Data/NO2_resten.csv')

# NO5
NO5_m = load_and_prepare_monthly('All_Demand_Data/NO5_mNP.csv')
NO5_u = load_and_prepare_monthly('All_Demand_Data/NO5_uNP.csv')
NO5_r = load_and_prepare_monthly('All_Demand_Data/NO5_resten.csv')


# --- FUNKSJON: plotter ett område også med differanse ---
def plot_area_monthly(area_name, m, u, r):
    plt.figure(figsize=(14, 7))

    # hovedkurver
    plt.plot(m.index, m.values, label='mNP')
    plt.plot(u.index, u.values, label='uNP')
    plt.plot(r.index, r.values, label='resten')

    # differanse mNP - uNP
    diff = m.subtract(u, fill_value=float('nan'))

    # prosentdifferanse
    pct_diff = (diff / u) * 100

    # plot differanse
    plt.plot(diff.index, diff.values,
             label='mNP - uNP (absolutt)', linewidth=2.5, linestyle='--')

    # plot prosent-differanse
    #plt.plot(pct_diff.index, pct_diff.values,
             #label='mNP - uNP (%)', linewidth=2.5, linestyle=':', color='black')

    plt.title(f"Månedlig forbruk per husholdning – {area_name}")
    plt.xlabel("Måned")
    plt.ylabel("kWh per husholdning / differanser")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# --- GENERER 3 FIGURER (NO1 / NO2 / NO5) ---

#plot_area_monthly("NO1", NO1_m, NO1_u, NO1_r)
#plot_area_monthly("NO2", NO2_m, NO2_u, NO2_r)
#plot_area_monthly("NO5", NO5_m, NO5_u, NO5_r)



import pandas as pd
import matplotlib.pyplot as plt

# --- FUNKSJON: leser fil og beregner ÅRLIG forbruk per husholdning ---
def load_and_prepare_yearly(path):
    df = pd.read_csv(path, sep=';')

    # konverter tid til datetime
    df['start_time_utc'] = pd.to_datetime(df['start_time_utc'])

    # forbruk per husholdning
    df['cons_per_house'] = df['consumption_kwh'] / df['metering_point_count']

    # yearly aggregation
    df_yearly = df.groupby(df['start_time_utc'].dt.to_period('Y'))['cons_per_house'].mean()

    # konverter PeriodIndex → datetime (1. januar hvert år) for plotting
    df_yearly.index = df_yearly.index.to_timestamp()

    return df_yearly


# --- LAST INN DATA FOR ALLE OMRÅDER ---

# NO1
NO1_m = load_and_prepare_yearly('All_Demand_Data/NO1_mNP.csv')
NO1_u = load_and_prepare_yearly('All_Demand_Data/NO1_uNP.csv')
NO1_r = load_and_prepare_yearly('All_Demand_Data/NO1_resten.csv')

# NO2
NO2_m = load_and_prepare_yearly('All_Demand_Data/NO2_mNP.csv')
NO2_u = load_and_prepare_yearly('All_Demand_Data/NO2_uNP.csv')
NO2_r = load_and_prepare_yearly('All_Demand_Data/NO2_resten.csv')

# NO5
NO5_m = load_and_prepare_yearly('All_Demand_Data/NO5_mNP.csv')
NO5_u = load_and_prepare_yearly('All_Demand_Data/NO5_uNP.csv')
NO5_r = load_and_prepare_yearly('All_Demand_Data/NO5_resten.csv')


# --- FUNKSJON: plotter ett område med differanser ---
def plot_area_yearly(area_name, m, u, r):
    plt.figure(figsize=(14, 7))

    # hovedkurver
    plt.plot(m.index, m.values, label='mNP')
    plt.plot(u.index, u.values, label='uNP')
    plt.plot(r.index, r.values, label='resten')

    # absolutt differanse mNP - uNP
    diff = m.subtract(u, fill_value=float('nan'))

    # prosentdifferanse
    pct_diff = (diff / u) * 100

    # legg på differanse
    plt.plot(diff.index, diff.values,
             label='mNP - uNP (absolutt)', linewidth=2.5, linestyle='--')

    # legg på prosentdiff
    #plt.plot(pct_diff.index, pct_diff.values,
             #label='mNP - uNP (%)', linewidth=2.5, linestyle=':', color='black')

    plt.title(f"Årlig forbruk per husholdning – {area_name}")
    plt.xlabel("År")
    plt.ylabel("kWh per husholdning / differanser")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# --- GENERER 3 FIGURER (NO1 / NO2 / NO5) ---

#plot_area_yearly("NO1", NO1_m, NO1_u, NO1_r)
#plot_area_yearly("NO2", NO2_m, NO2_u, NO2_r)
#plot_area_yearly("NO5", NO5_m, NO5_u, NO5_r)