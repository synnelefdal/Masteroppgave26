from cProfile import label
import numpy as np
import pandas as pd
import statsmodels.api as sm
import patsy
from linearmodels.panel import PanelOLS
import matplotlib.pyplot as plt
from matplotlib.pyplot import xticks
from matplotlib.lines import Line2D

# =====================================================
# =============== GLOBALT DATO-VALG ===================
# =====================================================

START_DATE_BEFORE = '2025-01-05'
END_DATE_BEFORE   = '2025-01-06'

START_DATE_AFTER  = '2026-01-07'
END_DATE_AFTER    = '2026-01-08'


# =====================================================
# ==================== DATA ===========================
# =====================================================

data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep=';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep=';')
data_rest_NO1 = pd.read_csv('All_Demand_Data/NO1_resten.csv', sep=';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep=';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep=';')
data_rest_NO2 = pd.read_csv('All_Demand_Data/NO2_resten.csv', sep=';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep=';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep=';')
data_rest_NO5 = pd.read_csv('All_Demand_Data/NO5_resten.csv', sep=';')

Temp_Bergen = pd.read_csv('../Temperature_Files/Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('../Temperature_Files/Temp_Oslo.csv')
Temp_Stavanger = pd.read_csv('../Temperature_Files/Temp_Stavanger.csv')


# =====================================================
# ==================== DiD ============================
# =====================================================

def Difference_in_Difference_Flex(data_mNP, data_uNP, data_resten, Temp, price_area):

    for d in [data_mNP, data_uNP, data_resten]:
        d['start_time_utc'] = pd.to_datetime(d['start_time_utc'], errors='coerce', utc=True)
        d['Date'] = d['start_time_utc'].dt.date
        d['Hour'] = d['start_time_utc'].dt.hour.astype(int)

    def aggregate(df):
        df = df[df['price_area'] == price_area].copy()
        df['kWh/Metering_point'] = df['consumption_kwh'] / df['metering_point_count']
        return (
            df.groupby(['Date', 'Hour', 'group_definition'])['kWh/Metering_point']
            .sum()
            .reset_index()
        )

    df = pd.concat(
        [aggregate(data_mNP), aggregate(data_uNP), aggregate(data_resten)],
        ignore_index=True
    )

    df['Date'] = pd.to_datetime(df['Date'])
    df['time'] = (
        df['Date'] + pd.to_timedelta(df['Hour'], unit='h')
    ).dt.tz_localize('UTC')

    df = df[df['kWh/Metering_point'] > 0].copy()

    Temp['Date'] = pd.to_datetime(Temp['Date'])
    Temp['Hour'] = Temp['Hour'].astype(int)
    Temp['Temp24'] = Temp['Lufttemperatur'].rolling(24, min_periods=1).mean()

    df = pd.merge(df, Temp[['Date', 'Hour', 'Temp24']], on=['Date', 'Hour'], how='left')

    before = (df['Date'] >= START_DATE_BEFORE) & (df['Date'] <= END_DATE_BEFORE)
    after  = (df['Date'] >= START_DATE_AFTER)  & (df['Date'] <= END_DATE_AFTER)

    df['Period'] = np.select(
        [before, after],
        ['Reference', 'Treatment'],
        default='Rest'
    )

    df['entity'] = pd.Categorical(
        df['group_definition'],
        categories=['Uten Norgespris', 'Med Norgespris', 'Resten'],
        ordered=True
    )

    df['period'] = pd.Categorical(
        df['Period'],
        categories=['Reference', 'Treatment', 'Rest'],
        ordered=True
    )

    df['log_y'] = df['kWh/Metering_point'] # her må np.log legges tilbake for prosent

    results = []

    for h in range(24):
        sub = df[df['Hour'] == h].copy()

        if sub.empty:
            results.append({
                'Hour': h,
                'DiD_temp': np.nan,
                'CI_low_temp': np.nan,
                'CI_high_temp': np.nan,
                'p_value': np.nan          # <<< NY
            })
            continue

        panel_df = sub.set_index(['entity', 'time'], drop=False)

        model = PanelOLS.from_formula(
            'log_y ~ 1 + C(entity)*C(period)'
            ' + Temp24 + I(Temp24**2) + I(Temp24**3)'
            ' + C(entity):Temp24'
            ' + C(entity):I(Temp24**2)'
            ' + C(entity):I(Temp24**3)'
            ' + TimeEffects',
            data=panel_df,
            drop_absorbed=True
        )

        res = model.fit(cov_type='clustered', cluster_time=True)


        key = "C(entity)[T.Med Norgespris]:C(period)[T.Treatment]"

        if key not in res.params.index:
            results.append({
                'Hour': h,
                'DiD_temp': np.nan,
                'CI_low_temp': np.nan,
                'CI_high_temp': np.nan,
                'p_value': np.nan          # <<< NY
            })
            continue

        beta = res.params[key]
        ci_low, ci_high = res.conf_int().loc[key]
        p_val = res.pvalues[key]          # <<< NY

        #DiD = (np.exp(beta) - 1) * 100
        #CI_low = (np.exp(ci_low) - 1) * 100
        #CI_high = (np.exp(ci_high) - 1) * 100      # DISSE MÅ TILBAKE FOR PROSENT

        results.append({
            'Hour': h,
            'DiD_temp': beta,
            'CI_low_temp': ci_low,
            'CI_high_temp': ci_high,
            'p_value': p_val               # <<< NY      DISSE MÅ TILBAKE FOR PROSENT
        })

    return pd.DataFrame(results)


def print_did_results(results_df, area_name, metering_point_count):
    """
    Printer DiD-resultater per time på en ryddig og lesbar måte.
    Bruker samme tall som punktene og båndene i figuren.
    """



    print("")
    print("=" * 65)
    print(f" Difference-in-Differences med temperatur – {area_name}")
    print("=" * 65)
    print(
        f"{'Time':>4} | {'DiD':>10} | {'Nedre KI':>10} | {'Øvre KI':>10} | {'Ganga med antall':>10}"
    )
    print("-" * 65)

    for _, row in results_df.iterrows():
        hour = int(row['Hour'])

        if pd.isna(row['DiD_temp']):
            print(f"{hour:02d}   |     NA     |     NA     |     NA")
        else:
            print(
                f"{hour:02d}   | "
                f"{row['DiD_temp']:>10.4f} | "
                f"{row['CI_low_temp']:>10.4f} | "
                f"{row['CI_high_temp']:>10.4f} | "
                f"{row['DiD_temp'] * metering_point_count :>10.4f} "
            )

    print("=" * 65)



# =====================================================
# ==================== PLOT ===========================
# =====================================================

def plot_dognprofil(results_NO1, results_NO2, results_NO5):

    plt.figure(figsize=(12, 6))


    for res, color, label_ in zip(
        [results_NO1, results_NO2, results_NO5],
        ['royalblue', 'red', 'green'],
        ['NO1', 'NO2', 'NO5']
    ):
        first_line = True  # <<< NY
        for h in range(23):   # <<< NY: plott time-for-time
            linestyle = '--' if res.loc[h, 'p_value'] > 0.05 else '-'
            plt.plot(
                res.loc[h:h+1, 'Hour'],
                res.loc[h:h+1, 'DiD_temp'],
                color=color,
                linestyle=linestyle,
                linewidth=2,
                label=f'DiD w/temp – {label_}' if first_line else None
            )

            first_line = False

        plt.fill_between(
            res['Hour'],
            res['CI_low_temp'],
            res['CI_high_temp'],
            color=color,
            alpha=0.1#,
            #label=f'DiD w/temp – {label_}'
            )

    plt.xticks(range(24))
    plt.xlabel("Hour", fontsize=20)
    plt.ylabel("Difference-in-Difference [%]", fontsize=20)
    plt.grid(alpha=0.3)
    #plt.legend(handles=legend_handles, fontsize=18)
    plt.legend(fontsize=18)
    plt.tight_layout()
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.show()


# =====================================================
# ==================== KJØR ===========================
# =====================================================

results_NO1 = Difference_in_Difference_Flex(
    data_mNP_NO1, data_uNP_NO1, data_rest_NO1, Temp_Oslo, 'NO1'
)

results_NO2 = Difference_in_Difference_Flex(
    data_mNP_NO2, data_uNP_NO2, data_rest_NO2, Temp_Stavanger, 'NO2'
)


results_NO5 = Difference_in_Difference_Flex(
    data_mNP_NO5, data_uNP_NO5, data_rest_NO5, Temp_Bergen, 'NO5'
)


print_did_results(results_NO1, "NO1", 307214)
print_did_results(results_NO2, "NO2", 331860)
print_did_results(results_NO5, "NO5", 73917)


plot_dognprofil(results_NO1, results_NO2, results_NO5)
