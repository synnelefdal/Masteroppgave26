# ===========================================
# Manuell Difference-in-Differences (2×2)
# - Treatment: Med_NP.csv
# - Control:   Uten_NP.csv (legg gjerne .csv i filnavn)
# - Ingen regresjoner; kun manuell gruppegjennomsnitt-DiD
# - Valgfri bootstrap for KI
# ===========================================

import pandas as pd
import numpy as np

# ---------- 1) Last inn og harmoniser ----------
def load_and_harmonize(
    path_treat: str,
    path_ctrl: str,
    column_map_treat: dict,
    column_map_ctrl: dict,
    time_as_period: str | None = "Y"  # "Y", "Q", "M" eller None hvis allerede numerisk
) -> pd.DataFrame:
    """
    Forventer at du mapper til felles navn:
      - unit_id : unik enhets-ID (person, skole, bedrift, region, osv.)
      - time    : tidskolonne (år/kvartal/måned)
      - outcome : utfallsvariabelen
    """
    df_t = pd.read_csv(path_treat)
    df_c = pd.read_csv(path_ctrl)

    df_t = df_t.rename(columns=column_map_treat)
    df_c = df_c.rename(columns=column_map_ctrl)

    needed = {"unit_id", "time", "outcome"}
    miss_t = needed - set(df_t.columns)
    miss_c = needed - set(df_c.columns)
    if miss_t:
        raise ValueError(f"Treatment-datasettet mangler kolonner etter rename: {miss_t}")
    if miss_c:
        raise ValueError(f"Control-datasettet mangler kolonner etter rename: {miss_c}")

    # Merk grupper
    df_t["treated"] = 1
    df_c["treated"] = 0

    # Håndter tid
    if time_as_period is not None:
        freq = {"Y": "Y", "Q": "Q", "M": "M"}[time_as_period]
        df_t["time"] = pd.PeriodIndex(df_t["time"].astype(str), freq=freq)
        df_c["time"] = pd.PeriodIndex(df_c["time"].astype(str), freq=freq)
    # ellers lar vi time være som den er (f.eks. heltallige år)

    df = pd.concat([df_t, df_c], ignore_index=True)
    df = df.sort_values(["unit_id", "time"]).reset_index(drop=True)
    return df


# ---------- 2) Manuelt 2×2 DiD ----------
def manual_2x2_did(df: pd.DataFrame, pre_mask: pd.Series, post_mask: pd.Series) -> dict:
    """
    tau = (Y_T_post - Y_T_pre) - (Y_C_post - Y_C_pre)
    pre_mask / post_mask er boolske masker som definerer pre- og post-vindu.
    """
    y_t_pre = df.loc[pre_mask & (df["treated"] == 1), "outcome"].mean()
    y_t_post = df.loc[post_mask & (df["treated"] == 1), "outcome"].mean()
    y_c_pre = df.loc[pre_mask & (df["treated"] == 0), "outcome"].mean()
    y_c_post = df.loc[post_mask & (df["treated"] == 0), "outcome"].mean()

    tau = (y_t_post - y_t_pre) - (y_c_post - y_c_pre)
    return {
        "Y_T_pre": y_t_pre,
        "Y_T_post": y_t_post,
        "Y_C_pre": y_c_pre,
        "Y_C_post": y_c_post,
        "DiD": tau
    }


# ---------- 3) (Valgfritt) Bootstrap-KI for manuell DiD ----------
def bootstrap_did_ci(df, pre_mask, post_mask, n_boot=1000, alpha=0.05, random_state=42):
    """
    En enkel blokk-bootstrap på enhetsnivå (resample av unit_id) for KI rundt manuell DiD.
    """
    rng = np.random.default_rng(random_state)
    units = df["unit_id"].unique()
    estimates = []

    # For å holde pre/post-kriteriet konsistent når vi resampler,
    # bygger vi maskene på nytt pr. bootstrap-sample etter join.
    for _ in range(n_boot):
        sampled = rng.choice(units, size=len(units), replace=True)
        df_b = pd.concat([df[df["unit_id"] == u] for u in sampled], ignore_index=True)

        # Re-beregn masker ved å matche på tid i bootstrap-samplet
        # Antar at pre_mask/post_mask i originalen er basert på tid, ikke på indeks
        # Derfor lager vi dem på nytt fra grenseverdier:
        if isinstance(df["time"].iloc[0], pd.Period):
            # Finn pre-/post-grenser fra originalmaskene via min/max tid
            pre_times = df.loc[pre_mask, "time"].unique()
            post_times = df.loc[post_mask, "time"].unique()
            pre_cond = df_b["time"].isin(pre_times)
            post_cond = df_b["time"].isin(post_times)
        else:
            pre_vals = df.loc[pre_mask, "time"].unique()
            post_vals = df.loc[post_mask, "time"].unique()
            pre_cond = df_b["time"].isin(pre_vals)
            post_cond = df_b["time"].isin(post_vals)

        est = manual_2x2_did(df_b, pre_mask=pre_cond, post_mask=post_cond)["DiD"]
        estimates.append(est)

    low = np.quantile(estimates, alpha/2)
    high = np.quantile(estimates, 1 - alpha/2)
    return {"low": low, "high": high, "alpha": alpha, "n_boot": n_boot}


# ---------- 4) EKSEMPEL: tilpass og kjør ----------
if __name__ == "__main__":
    # Filstier
    path_treat = 'All_Demand_Data/NO1_mNP.csv'    #"Med_NP.csv"
    path_ctrl = 'All_Demand_Data/NO1_uNP.csv'   #"Uten_NP.csv"  # legg til .csv hvis filen heter f.eks. Uten_NP.csv

    # Tilpass disse mappingene til dine faktiske kolonner i hver fil
    # Eksempel: Med_NP.csv har kolonner: id, år, y
    #           Uten_NP.csv har kolonner: unit, year, outcome
    column_map_treat = {
        "usage_date_id": "unit_id",
        "start_time_utc": "time",        # hvis kolonnen heter 'year', skriv "year": "time"
        "consumption_kwh": "outcome",
    }
    column_map_ctrl = {
        "usage_date_id": "unit_id",
        "start_time_utc": "time",
        "consumption_kwh": "outcome",
    }

    # 1) Last inn
    # Sett time_as_period til "Y"/"Q"/"M" hvis tid er år/kvartal/måned som streng/tall og du vil bruke Period.
    # Sett til None hvis 'time' allerede er numerisk år (int) og du vil bruke tall direkte.
    df = load_and_harmonize(
        path_treat,
        path_ctrl,
        column_map_treat,
        column_map_ctrl,
        time_as_period="Y"   # endre til "Q" eller "M" ved behov, eller None
    )

    # 2) Definer pre- og post-vindu (VELG SELV)
    # Alternativ A: hvis time er Period[Y]
    if isinstance(df["time"].iloc[0], pd.Period):
        # EKSEMPEL: pre = t <= 2019, post = t >= 2021 (hopper over 2020 som overgang)
        pre_mask = (df["time"] <= pd.Period("2019", freq="Y"))
        post_mask = (df["time"] >= pd.Period("2021", freq="Y"))
    else:
        # Alternativ B: hvis time er numerisk (int)
        pre_mask = (df["time"] <= 2019)
        post_mask = (df["time"] >= 2021)

    # 3) Beregn manuell DiD
    res = manual_2x2_did(df, pre_mask=pre_mask, post_mask=post_mask)
    print("\n--- Manuell 2×2 DiD ---")
    for k, v in res.items():
        if isinstance(v, (int, float, np.floating)):
            print(f"{k}: {v:.6f}")
        else:
            print(f"{k}: {v}")

    # 4) (Valgfritt) Bootstrap KI
    ci = bootstrap_did_ci(df, pre_mask=pre_mask, post_mask=post_mask, n_boot=500, alpha=0.05)
    print(f"95% KI (bootstrap): [{ci['low']:.6f}, {ci['high']:.6f}]")
``