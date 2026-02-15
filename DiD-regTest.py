import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import patsy
import matplotlib.pyplot as plt

data_mNP_NO1 = pd.read_csv('All_Demand_Data/NO1_mNP.csv', sep= ';')
data_uNP_NO1 = pd.read_csv('All_Demand_Data/NO1_uNP.csv', sep= ';')

data_mNP_NO2 = pd.read_csv('All_Demand_Data/NO2_mNP.csv', sep= ';')
data_uNP_NO2 = pd.read_csv('All_Demand_Data/NO2_uNP.csv', sep= ';')

data_mNP_NO5 = pd.read_csv('All_Demand_Data/NO5_mNP.csv', sep= ';')
data_uNP_NO5 = pd.read_csv('All_Demand_Data/NO5_uNP.csv', sep= ';')


def DifferenceinDifference(data_mNP, data_uNP, price_area):
    # ---- 1) Dato‑grenser og parsing ----
    start_date_before = pd.Timestamp('2024-10-01')
    end_date_before   = pd.Timestamp('2025-01-31')
    start_date_after  = pd.Timestamp('2025-10-01')
    end_date_after    = pd.Timestamp('2026-01-31')

    for df in [data_mNP, data_uNP]:
        df['start_time_utc'] = pd.to_datetime(
            df['start_time_utc'],
            format='%Y-%m-%d %H:%M:%S',
            errors='coerce', utc=True
        )
        df['Date'] = df['start_time_utc'].dt.floor('h').dt.tz_convert('UTC').dt.tz_localize(None).dt.date
        # Alternativt dropp tz‑styring hvis du vet alt er UTC, f.eks.:
        # df['Date'] = df['start_time_utc'].dt.date
        df['Hour'] = df['start_time_utc'].dt.hour.astype(int)

    # ---- 2) Filter på prisområde ----
    m = data_mNP.loc[data_mNP['price_area'] == price_area].copy()
    u = data_uNP.loc[data_uNP['price_area'] == price_area].copy()

    # ---- 3) Filter på før/etter ----
    # Gjør Date til Timestamp for sammenligning
    m['Date'] = pd.to_datetime(m['Date'])
    u['Date'] = pd.to_datetime(u['Date'])

    m_before = m[(m['Date'] >= start_date_before) & (m['Date'] <= end_date_before)].copy()
    m_after  = m[(m['Date'] >= start_date_after)  & (m['Date'] <= end_date_after)].copy()
    u_before = u[(u['Date'] >= start_date_before) & (u['Date'] <= end_date_before)].copy()
    u_after  = u[(u['Date'] >= start_date_after)  & (u['Date'] <= end_date_after)].copy()

    # ---- 4) Aggreger til (Date, Hour, ev. group_definition): SUM kWh og SUM MP ----
    # NB: Behold group_definition hvis du vil bruke det som kontroll/FE.
    by_cols = ['Date', 'Hour', 'group_definition']  # evt. dropp 'group_definition' hvis ikke relevant

    def agg_blocks(df):
        out = (df
               .groupby(by_cols, dropna=False)
               .agg(total_kwh=('consumption_kwh', 'sum'),
                    total_mp=('metering_point_count', 'sum'))
               .reset_index())
        out['kwh_per_mp'] = out['total_kwh'] / out['total_mp']
        return out

    m_before_agg = agg_blocks(m_before)
    m_after_agg  = agg_blocks(m_after)
    u_before_agg = agg_blocks(u_before)
    u_after_agg  = agg_blocks(u_after)

    # ---- 5) Merk grupper (Treat) og perioder (Post) ----
    for df in [m_before_agg, m_after_agg]:
        df['Norgespris'] = 'Med_NP'
    for df in [u_before_agg, u_after_agg]:
        df['Norgespris'] = 'Uten_NP'

    for df in [m_before_agg, u_before_agg]:
        df['Group'] = 'Before_ref'
    for df in [m_after_agg, u_after_agg]:
        df['Group'] = 'After_ref'

    df = pd.concat([m_before_agg, m_after_agg, u_before_agg, u_after_agg], ignore_index=True)

    # ---- 6) Rydd variabler og lag DID‑indikatorer ----
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['kwh_per_mp', 'total_mp'])
    df = df[df['kwh_per_mp'] > 0].copy()

    # Konsistent kategorisering av Hour (0–23) og Month
    df['Hour'] = df['Hour'].astype(int)
    df['Month'] = df['Date'].dt.month_name()
    df['Hour'] = pd.Categorical(df['Hour'], categories=list(range(24)), ordered=True)
    df['Month'] = pd.Categorical(
        df['Month'],
        categories=['January','February','March','April','May','June',
                    'July','August','September','October','November','December'],
        ordered=True
    )

    # Bevar et ryddig navn uten "/" til formelbruk
    df = df.rename(columns={'kwh_per_mp': 'kwh_per_mp'})

    # DID‑dummies
    df['post']   = (df['Group'] == 'After_ref').astype(int)         # Time
    df['treat']  = (df['Norgespris'] == 'Med_NP').astype(int)       # Intervention

    # ---- 7) Modeller ----
    # Basismodell: Y ~ Post + Treat + Post*Treat + time‑FE (Hour, Month) + ev. group_definition‑FE
    # Cluster standardfeil på dato (gir robusthet for seriekorrelasjon innen samme dag)
    formula = 'np.log(kwh_per_mp) ~ post + treat + post:treat + C(group_definition)'

    y, X = patsy.dmatrices(
        formula,
        data=df,
        return_type="dataframe",
        NA_action="drop"
    )

    model = sm.OLS(y, X).fit()
    print(model.summary())

    ols_model = smf.ols(formula, data=df).fit(
        cov_type='cluster', cov_kwds={'groups': df['Date']}
    )

    # Vektet (WLS): vekter med antall målepunkter
    wls_model = smf.wls(formula, data=df, weights=df['total_mp']).fit(
        cov_type='cluster', cov_kwds={'groups': df['Date']}
    )

    # Eksempel: time‑spesifikk DID (hvis du vil se effekt per time gjennom døgnet)
    # kwh_per_mp ~ post*treat*C(Hour) + C(Month) + C(group_definition)
    # Merk: tolking blir et sett av post:treat‑koeffisienter for hver time.
    # model_by_hour = smf.ols(
    #     'kwh_per_mp ~ post*treat*C(Hour) + C(Month) + C(group_definition)',
    #     data=df
    # ).fit(cov_type='cluster', cov_kwds={'groups': df['Date']})

    results = {
        'data_for_regression': df,
        'ols_summary': ols_model.summary().as_text(),
        'wls_summary': wls_model.summary().as_text(),
        'ols_params': ols_model.params.to_dict(),
        'wls_params': wls_model.params.to_dict(),
        'did_effect_ols': ols_model.params.get('post:treat', np.nan),
        'did_effect_wls': wls_model.params.get('post:treat', np.nan),
        'did_ci_ols': ols_model.conf_int().loc[
            'post:treat'].tolist() if 'post:treat' in ols_model.params.index else None,
        'did_ci_wls': wls_model.conf_int().loc[
            'post:treat'].tolist() if 'post:treat' in wls_model.params.index else None
    }
    return results


def plot_did_figure(results,
                    weighted=True,
                    title='Difference-in-Differences (kWh per målepunkt)',
                    savepath=None):
    """
    Lager et DiD-plott i samme stil som eksempelet (A, B, C, D + beta1, beta2, beta3).

    Parametre
    ---------
    results : dict
        Output fra DifferenceinDifference(...). Må inneholde 'data_for_regression'.
    weighted : bool
        True: bruk vektet gjennomsnitt (vekter = total_mp).
        False: bruk uvektet gjennomsnitt.
    title : str
        Figur-tittel.
    savepath : str or None
        Hvis gitt, lagres figuren til denne filstien (f.eks. 'did_plot.png').
    """

    df = results['data_for_regression'].copy()

    # Sikre at vi har nødvendige felt
    required_cols = {'Date','Hour','Norgespris','Group','kwh_per_mp','total_mp'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Mangler kolonner i data_for_regression: {missing}")

    # For aggregering: Pre = Before_ref, Post = After_ref
    # Vi aggregerer over alle observasjoner i hver (Post/Pre x Treat/Control)
    # og bruker enten uvektet eller vektet snitt.
    def agg_mean(sub):
        if weighted:
            w = sub['total_mp'].astype(float)
            x = sub['kwh_per_mp'].astype(float)
            return np.average(x, weights=w)
        else:
            return sub['kwh_per_mp'].mean()

    # Build tabell: nivåer for (Group x Norgespris)
    # Treat = Med_NP, Control = Uten_NP
    A = agg_mean(df[(df['Group']=='Before_ref') & (df['Norgespris']=='Med_NP')])   # Treat-Pre
    B = agg_mean(df[(df['Group']=='Before_ref') & (df['Norgespris']=='Uten_NP')]) # Control-Pre
    C = agg_mean(df[(df['Group']=='After_ref')  & (df['Norgespris']=='Med_NP')])  # Treat-Post
    D = agg_mean(df[(df['Group']=='After_ref')  & (df['Norgespris']=='Uten_NP')]) # Control-Post

    # DID-komponenter:
    beta1 = D - B                    # Kontrollgruppens endring (post - pre)
    beta2 = A - B                    # Forskjell mellom grupper før (treat - control pre)
    beta3 = (C - A) - (D - B)        # DiD-effekten

    # For plotting (x-aksen: 0=Pre, 1=Post)
    x_pre, x_post = 0, 1

    # Kontrafaktisk for behandlingsgruppen etter intervensjonen: A + beta1
    counterfactual_treat_post = A + beta1

    fig, ax = plt.subplots(figsize=(8, 5))

    # Heltrukne linjer: observerte snitt
    # Control (grønn)
    ax.plot([x_pre, x_post], [B, D], color='green', linewidth=2, label='Uten NP (observed)')
    # Treat (rød)
    ax.plot([x_pre, x_post], [A, C], color='red', linewidth=2, label='Med NP (observed)')

    # Stiplet: kontrafaktisk (grønn trend anvendt på treat)
    ax.plot([x_post-0.2, x_post], [counterfactual_treat_post, counterfactual_treat_post],
            color='red', linestyle=':', linewidth=2, label='Kontrafaktisk (Med NP)')

    # Punkter A, B, C, D
    ax.scatter([x_pre], [A], color='red', s=60, zorder=3)
    ax.scatter([x_pre], [B], color='green', s=60, zorder=3)
    ax.scatter([x_post], [C], color='red', s=60, zorder=3)
    ax.scatter([x_post], [D], color='green', s=60, zorder=3)

    # Annoter A,B,C,D
    ax.text(x_pre-0.04, A, 'A', fontsize=11, color='red', va='bottom', ha='right')
    ax.text(x_pre-0.04, B, 'B', fontsize=11, color='green', va='top', ha='right')
    ax.text(x_post+0.02, C, 'C', fontsize=11, color='red', va='bottom', ha='left')
    ax.text(x_post+0.02, D, 'D', fontsize=11, color='green', va='bottom', ha='left')

    # Vertikal linje ved intervensjon (mellom pre og post)
    ax.axvline(x=0.5, color='#395b8b', linewidth=2)

    # Stiplede “brackets” for å vise beta1 og beta3
    # beta1: vertikalt avvik D - B i Post-feltet (tegn det på x=1.05)
    x_beta1 = x_post + 0.05
    y_beta1_low, y_beta1_high = min(B, D), max(B, D)
    ax.vlines(x=x_beta1, ymin=B, ymax=D, color='black', linestyle='--', linewidth=1.5)
    ax.text(x_beta1+0.02, (B+D)/2, r'$\beta_1$', rotation=90, va='center', ha='left', fontsize=11)

    # beta3: forskjellen mellom C og kontrafaktisk (A + beta1) ved Post
    x_beta3 = x_post + 0.18
    ax.vlines(x=x_beta3, ymin=counterfactual_treat_post, ymax=C, color='black', linestyle='--', linewidth=1.5)
    ax.text(x_beta3+0.02, (counterfactual_treat_post + C)/2, r'$\beta_3$', rotation=90, va='center', ha='left', fontsize=11)

    # Valgfritt: beta2 bracket ved Pre (A - B)
    x_beta2 = x_pre - 0.10
    ax.vlines(x=x_beta2, ymin=min(A,B), ymax=max(A,B), color='black', linestyle='--', linewidth=1.5)
    ax.text(x_beta2-0.02, (A+B)/2, r'$\beta_2$', rotation=90, va='center', ha='right', fontsize=11)

    # Akser og etiketter
    ax.set_xticks([x_pre, x_post])
    ax.set_xticklabels(['Pre-intervensjon', 'Post-intervensjon'])
    ax.set_xlim(-0.25, 1.35)

    ax.set_ylabel('kWh per målepunkt')
    ttl = title + (' (vektet med antall målepunkter)' if weighted else ' (uvektet)')
    ax.set_title(ttl)

    # Forklaring: vis små hjelpetekster
    ax.legend(loc='upper left', frameon=False)

    # Grid/rammer
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle=':', alpha=0.4)

    # Skriv ut tall i konsoll + legg til tekst i figuren (nederst)
    txt = f"A={A:.4f}, B={B:.4f}, C={C:.4f}, D={D:.4f} | " \
          f"β1(D-B)={beta1:.4f}, β2(A-B)={beta2:.4f}, β3(DID)={beta3:.4f}"
    print(txt)
    ax.text(0.0, 0.02, txt, transform=ax.transAxes, fontsize=9, ha='left', va='bottom')

    plt.tight_layout()
    if savepath:
        plt.savefig(savepath, dpi=200, bbox_inches='tight')
    plt.show()

# Eksempelbruk etter at du har kjørt DifferenceinDifference(...):
# results = DifferenceinDifference(data_mNP, data_uNP, price_area='NO3')
# plot_did_figure(results, weighted=True, title='DID – NO3', savepath='did_no3.png')
# plot_did_figure(results, weighted=False, title='DID (uvektet) – NO3')

from matplotlib.ticker import PercentFormatter

def plot_did_figure_percent(results,
                            relative_to='own_pre',
                            did_as='diff_in_pct_change',
                            weighted=True,
                            title='Difference-in-Differences (prosent)',
                            savepath=None):
    """
    Lager et DiD-plott i prosent i stedet for nivåer.

    Parametre
    ---------
    results : dict
        Output fra DifferenceinDifference(...). Må inneholde 'data_for_regression'.
    relative_to : {'own_pre', 'control_pre'}
        - 'own_pre': hver gruppes pre settes som 100 %. Post vises som % av egen pre.
        - 'control_pre': kontrollgruppens pre (B) settes som 100 % for begge grupper.
    did_as : {'diff_in_pct_change', 'percent_of_control_pre'}
        - 'diff_in_pct_change': β3 rapporteres som forskjell i %-endring (log-approksimasjon).
        - 'percent_of_control_pre': β3 (nivå-DiD) rapporteres som % av kontroll-pre (B).
    weighted : bool
        True: bruk vektet gjennomsnitt (vekter = total_mp). False: uvektet.
    title : str
        Figur-tittel.
    savepath : str or None
        Hvis gitt, lagres figuren til denne filstien.
    """

    df = results['data_for_regression'].copy()

    # Sikre at vi har nødvendige felt
    required_cols = {'Date','Hour','Norgespris','Group','kwh_per_mp','total_mp'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Mangler kolonner i data_for_regression: {missing}")

    # Aggregér til A, B, C, D (vektet eller uvektet)
    def agg_mean(sub):
        if weighted:
            w = sub['total_mp'].astype(float)
            x = sub['kwh_per_mp'].astype(float)
            return np.average(x, weights=w)
        else:
            return sub['kwh_per_mp'].mean()

    A = agg_mean(df[(df['Group']=='Before_ref') & (df['Norgespris']=='Med_NP')])   # Treat-Pre
    B = agg_mean(df[(df['Group']=='Before_ref') & (df['Norgespris']=='Uten_NP')]) # Control-Pre
    C = agg_mean(df[(df['Group']=='After_ref')  & (df['Norgespris']=='Med_NP')])  # Treat-Post
    D = agg_mean(df[(df['Group']=='After_ref')  & (df['Norgespris']=='Uten_NP')]) # Control-Post

    # Sikkerhet: ingen null/NaN baseliner
    for name, val in [('A',A), ('B',B), ('C',C), ('D',D)]:
        if pd.isna(val) or np.isinf(val):
            raise ValueError(f"{name} er NaN/inf. Sjekk filtrene og data.")

    if relative_to not in ('own_pre','control_pre'):
        raise ValueError("relative_to må være 'own_pre' eller 'control_pre'")
    if did_as not in ('diff_in_pct_change', 'percent_of_control_pre'):
        raise ValueError("did_as må være 'diff_in_pct_change' eller 'percent_of_control_pre'")

    # --- Prosent‑transformasjoner ---
    if relative_to == 'own_pre':
        # Sett hver gruppes pre som 100 %
        A_pct = 100.0
        B_pct = 100.0
        C_pct = (C / A) * 100.0
        D_pct = (D / B) * 100.0

        # Kontrafaktisk post for treat gitt kontrollens %-endring:
        # Kontrollens %-endring = (D/B); anvendt på A => A * (D/B), i prosent av A = (D/B)*100
        counterfactual_treat_post_pct = (D / B) * 100.0

        # β1, β2 (i prosent-plot) som “brackets”:
        beta1_pct = D_pct - B_pct            # kontrollens %-endring
        beta2_pct = A_pct - B_pct            # forskjell i pre (blir 0 i dette moduset)
        # β3: valg
        if did_as == 'percent_of_control_pre':
            # nivå-DiD i kWh som % av B (kontroll-pre)
            beta3_raw = ( (C - A) - (D - B) )
            beta3_pct = (beta3_raw / B) * 100.0
        else:
            # diff i prosentendringer: (C/A - 1) - (D/B - 1) = C/A - D/B
            beta3_pct = (C / A - D / B) * 100.0

    else:  # relative_to == 'control_pre'
        # Sett kontrollens pre som 100 % for begge
        A_pct = (A / B) * 100.0
        B_pct = 100.0
        C_pct = (C / B) * 100.0
        D_pct = (D / B) * 100.0

        # Kontrafaktisk post for treat:
        # A-konvertert baseline er A/B*100, og kontrollens vekstfaktor er D/B.
        # Kontrafaktisk (i % av B) = (A/B * D/B) * 100 = (A*D/B^2) * 100
        counterfactual_treat_post_pct = (A * D / (B * B)) * 100.0

        # β1, β2 i prosent-skala
        beta1_pct = D_pct - B_pct                     # kontrollens %-økning fra 100
        beta2_pct = A_pct - B_pct                     # pre-forskjell (treat vs control) i %
        if did_as == 'percent_of_control_pre':
            # nivå-DiD i kWh som % av B
            beta3_raw = ( (C - A) - (D - B) )
            beta3_pct = (beta3_raw / B) * 100.0
        else:
            # “prosent-DiD”: forskjell i %-endringer relativt til B
            # %-endring treat = (C/B - A/B) = (C-A)/B
            # %-endring control = (D/B - B/B) = (D-B)/B
            # diff = (C-A - (D-B))/B * 100
            beta3_pct = (( (C - A) - (D - B) ) / B) * 100.0

    # --- Plot ---
    x_pre, x_post = 0, 1
    fig, ax = plt.subplots(figsize=(8, 5))

    # Heltrukne linjer (i prosent)
    ax.plot([x_pre, x_post], [B_pct, D_pct], color='green', linewidth=2, label='Uten NP (observasjon)')
    ax.plot([x_pre, x_post], [A_pct, C_pct], color='red', linewidth=2, label='Med NP (observasjon)')

    # Stiplet: kontrafaktisk for behandlingsgruppen i post
    ax.plot([x_post-0.2, x_post], [counterfactual_treat_post_pct, counterfactual_treat_post_pct],
            color='red', linestyle=':', linewidth=2, label='Kontrafaktisk (Med NP)')

    # Punkter A, B, C, D i prosent
    ax.scatter([x_pre], [A_pct], color='red', s=60, zorder=3)
    ax.scatter([x_pre], [B_pct], color='green', s=60, zorder=3)
    ax.scatter([x_post], [C_pct], color='red', s=60, zorder=3)
    ax.scatter([x_post], [D_pct], color='green', s=60, zorder=3)

    # Annoter A,B,C,D
    ax.text(x_pre-0.04, A_pct, 'A', fontsize=11, color='red', va='bottom', ha='right')
    ax.text(x_pre-0.04, B_pct, 'B', fontsize=11, color='green', va='top', ha='right')
    ax.text(x_post+0.02, C_pct, 'C', fontsize=11, color='red', va='bottom', ha='left')
    ax.text(x_post+0.02, D_pct, 'D', fontsize=11, color='green', va='bottom', ha='left')

    # Vertikal linje ved intervensjon
    ax.axvline(x=0.5, color='#395b8b', linewidth=2)

    # Brackets for β1 og β3 (i prosent)
    x_beta1 = x_post + 0.05
    ax.vlines(x=x_beta1, ymin=B_pct, ymax=D_pct, color='black', linestyle='--', linewidth=1.5)
    ax.text(x_beta1+0.02, (B_pct + D_pct)/2, r'$\beta_1$', rotation=90, va='center', ha='left', fontsize=11)

    x_beta3 = x_post + 0.18
    ax.vlines(x=x_beta3, ymin=counterfactual_treat_post_pct, ymax=C_pct, color='black', linestyle='--', linewidth=1.5)
    ax.text(x_beta3+0.02, (counterfactual_treat_post_pct + C_pct)/2, r'$\beta_3$', rotation=90, va='center', ha='left', fontsize=11)

    # Valgfri β2-bracket ved pre
    x_beta2 = x_pre - 0.10
    low2, high2 = (A_pct, B_pct) if A_pct <= B_pct else (B_pct, A_pct)
    ax.vlines(x=x_beta2, ymin=low2, ymax=high2, color='black', linestyle='--', linewidth=1.5)
    ax.text(x_beta2-0.02, (A_pct+B_pct)/2, r'$\beta_2$', rotation=90, va='center', ha='right', fontsize=11)

    # Akseoppsett
    ax.set_xticks([x_pre, x_post])
    ax.set_xticklabels(['Pre-intervensjon', 'Post-intervensjon'])
    ax.set_xlim(-0.25, 1.35)

    ax.set_ylabel('Prosent')
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))

    ttl = title + (' – vektet' if weighted else ' – uvektet')
    if relative_to == 'own_pre':
        ttl += ' (egen pre = 100%)'
    else:
        ttl += ' (kontroll pre = 100%)'
    ax.set_title(ttl)

    ax.legend(loc='upper left', frameon=False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle=':', alpha=0.4)

    # Tekst med summering
    # NB: Vi skriver ut både nivå‑DID (kWh) og valgt prosent‑DID for transparens
    did_level = ( (C - A) - (D - B) )
    if did_as == 'percent_of_control_pre':
        did_pct = (did_level / B) * 100.0
        did_desc = 'β3 (nivå‑DID som % av kontroll‑pre)'
    else:
        did_pct = (C / A - D / B) * 100.0
        did_desc = 'β3 (forskjell i %-endring)'
    txt = (f"A={A_pct:.1f}%, B={B_pct:.1f}%, C={C_pct:.1f}%, D={D_pct:.1f}% | "
           f"β1={beta1_pct:.1f}pp, β2={beta2_pct:.1f}pp, "
           f"β3={did_pct:.1f}% ({did_desc}); "
           f"β3 nivå={did_level:.4f} (kWh/MP)")
    print(txt)
    ax.text(0.0, 0.02, txt, transform=ax.transAxes, fontsize=9, ha='left', va='bottom')

    plt.tight_layout()
    if savepath:
        plt.savefig(savepath, dpi=200, bbox_inches='tight')
    plt.show()

results = DifferenceinDifference(data_mNP_NO1, data_uNP_NO1, 'NO1')
plot_did_figure(results,
                    weighted=True,
                    title='Difference-in-Differences (kWh per målepunkt)',
                    savepath=None)

plot_did_figure_percent(results,
                            relative_to='own_pre',
                            did_as='diff_in_pct_change',
                            weighted=True,
                            title='Difference-in-Differences (prosent)',
                            savepath=None)