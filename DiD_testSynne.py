# -*- coding: utf-8 -*-
"""
Difference-in-Differences (nivå + prosent) + Placebo + Pre-trends (Event-Study, log-OLS) + F-tester

Datasett:
- Treatment: NO1_mNP.csv
- Control:  NO1_uNP.csv

Output (i tillegg til tidligere):
- event_pretrends_f_test.csv        (H0: pre-leads = 0)
- event_post_zero_f_test.csv        (H0: post = 0)
- event_post_flat_f_test.csv        (H0: alle post-lag er like)
- main_interaction_f_test.csv       (H0: β_interaksjon = 0 i hoved log-OLS)
- placebo_interaction_f_test.csv    (H0: β_interaksjon = 0 i placebo log-OLS)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Parametere for innlesing
# -----------------------------
TREATMENT_FILE = "All_Demand_Data/NO1_mNP.csv"
CONTROL_FILE   = "All_Demand_Data/NO1_uNP.csv"

DATE_COL = "start_time_utc"
CONSUMPTION_COL = "consumption_kwh"
MP_COL = "metering_point_count"

READ_KW = dict(sep=';', encoding='utf-8')   # evt. encoding='latin1'

# -----------------------------
# Vinduer
# -----------------------------
# Hoved DiD
BEFORE_START = pd.Timestamp("2024-10-01")
BEFORE_END   = pd.Timestamp("2025-01-31")
AFTER_START  = pd.Timestamp("2025-10-01")
AFTER_END    = pd.Timestamp("2026-01-31")

# Placebo DiD (ett år tidligere)
PLACEBO_BEFORE_START = pd.Timestamp("2023-10-01")
PLACEBO_BEFORE_END   = pd.Timestamp("2024-01-31")
PLACEBO_AFTER_START  = pd.Timestamp("2024-10-01")
PLACEBO_AFTER_END    = pd.Timestamp("2025-01-31")

# Event-study: ekte treatment-dato
TREATMENT_DATE = pd.Timestamp("2025-10-01")

# Bootstrap
N_BOOT = 2000
RANDOM_SEED = 42

# Event-study innstillinger
EVENT_AGG_FREQ = "M"     # 'M' = månedsnivå (brukes i aggregering)
K_PRE  = 12              # antall leads (måneder) før
K_POST = 4               # antall lags etter

# -----------------------------
# Hjelpefunksjoner
# -----------------------------
def load_and_prepare(path: str, group_name: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Finner ikke fil: {path}")
    df = pd.read_csv(path, **READ_KW)

    for c in [DATE_COL, CONSUMPTION_COL, MP_COL]:
        if c not in df.columns:
            raise KeyError(f"Kolonnen '{c}' mangler i {path}. Kolonner: {list(df.columns)}")

    dt = pd.to_datetime(df[DATE_COL], errors="coerce", utc=True)
    if dt.isna().all():
        raise ValueError(f"Kunne ikke parse dato i '{DATE_COL}' i {path}. Eksempler: {df[DATE_COL].head(3).tolist()}")
    dt = dt.dt.tz_convert(None) if hasattr(dt.dt, "tz") else dt
    date = dt.dt.floor("D")

    df[CONSUMPTION_COL] = pd.to_numeric(df[CONSUMPTION_COL], errors="coerce")
    df[MP_COL] = pd.to_numeric(df[MP_COL], errors="coerce")

    daily = (pd.DataFrame({"date": date, CONSUMPTION_COL: df[CONSUMPTION_COL], MP_COL: df[MP_COL]})
             .groupby("date", as_index=False)
             .sum(numeric_only=True))
    daily[MP_COL] = daily[MP_COL].replace(0, np.nan)

    daily["per_mp"] = daily[CONSUMPTION_COL] / daily[MP_COL]
    daily["group"] = group_name
    return daily

def label_periods(d: pd.Series, before_start, before_end, after_start, after_end) -> pd.Series:
    cond_before = (d >= before_start) & (d <= before_end)
    cond_after  = (d >= after_start)  & (d <= after_end)
    out = pd.Series(index=d.index, dtype="object")
    out.loc[cond_before] = "before_ref"
    out.loc[cond_after]  = "after_ref"
    return out

def summarize_by_period(df: pd.DataFrame) -> pd.DataFrame:
    ag = (df
          .groupby(["group", "period"], as_index=False)
          .agg(sum_consumption=(CONSUMPTION_COL, "sum"),
               sum_mp=(MP_COL, "sum"),
               n_days=("date", "nunique")))
    ag["avg_per_mp"] = ag["sum_consumption"] / ag["sum_mp"]
    return ag

def compute_did_from_agg(agg: pd.DataFrame) -> dict:
    def get_avg(g, p):
        row = agg[(agg["group"] == g) & (agg["period"] == p)]
        if row.empty or pd.isna(row["avg_per_mp"].values[0]):
            return np.nan
        return float(row["avg_per_mp"].values[0])
    t_b = get_avg("treatment", "before_ref")
    t_a = get_avg("treatment", "after_ref")
    c_b = get_avg("control", "before_ref")
    c_a = get_avg("control", "after_ref")
    dt = t_a - t_b if pd.notna(t_a) and pd.notna(t_b) else np.nan
    dc = c_a - c_b if pd.notna(c_a) and pd.notna(c_b) else np.nan
    did = dt - dc if pd.notna(dt) and pd.notna(dc) else np.nan
    return {
        "treatment_before_avg_per_mp": t_b,
        "treatment_after_avg_per_mp":  t_a,
        "control_before_avg_per_mp":   c_b,
        "control_after_avg_per_mp":    c_a,
        "delta_treatment": dt,
        "delta_control":   dc,
        "did_estimate":    did
    }

def compute_percent_changes_from_agg(agg: pd.DataFrame) -> dict:
    def get_avg(g, p):
        row = agg[(agg["group"] == g) & (agg["period"] == p)]
        if row.empty or pd.isna(row["avg_per_mp"].values[0]):
            return np.nan
        return float(row["avg_per_mp"].values[0])
    t_b = get_avg("treatment", "before_ref")
    t_a = get_avg("treatment", "after_ref")
    c_b = get_avg("control", "before_ref")
    c_a = get_avg("control", "after_ref")
    def pct(aft, bef):
        if pd.isna(aft) or pd.isna(bef) or bef == 0:
            return np.nan
        return (aft / bef - 1.0) * 100.0
    pct_t = pct(t_a, t_b)
    pct_c = pct(c_a, c_b)
    did_pct = (pct_t - pct_c) if (pd.notna(pct_t) and pd.notna(pct_c)) else np.nan
    return {
        "treatment_pct_change": pct_t,
        "control_pct_change":   pct_c,
        "did_pct":              did_pct,
        "treatment_before_avg_per_mp": t_b,
        "treatment_after_avg_per_mp":  t_a,
        "control_before_avg_per_mp":   c_b,
        "control_after_avg_per_mp":    c_a
    }

def bootstrap_did(daily_df: pd.DataFrame, n_boot=2000, seed=42, use_percent=False) -> dict:
    rng = np.random.default_rng(seed)
    df = daily_df.dropna(subset=["period"]).copy()

    strata = {}
    for (g, p), sub in df.groupby(["group", "period"]):
        strata[(g, p)] = np.array(sorted(sub["date"].unique()))

    def agg_from_sampled_days():
        parts = []
        for (g, p), days in strata.items():
            if len(days) == 0:
                continue
            boot_days = days[rng.integers(0, len(days), size=len(days))]
            sub = df[(df["group"] == g) & (df["period"] == p) & (df["date"].isin(boot_days))]
            sum_c = sub[CONSUMPTION_COL].sum()
            sum_m = sub[MP_COL].sum()
            avg_pm = sum_c / sum_m if sum_m > 0 else np.nan
            parts.append({"group": g, "period": p, "avg_per_mp": avg_pm})
        return pd.DataFrame(parts)

    did_vals = []
    for _ in range(n_boot):
        agg = agg_from_sampled_days()
        for g in ["treatment", "control"]:
            for p in ["before_ref", "after_ref"]:
                if ((agg["group"] == g) & (agg["period"] == p)).sum() == 0:
                    agg.loc[len(agg)] = {"group": g, "period": p, "avg_per_mp": np.nan}
        if not use_percent:
            d = compute_did_from_agg(agg)
            did_vals.append(d["did_estimate"])
        else:
            p = compute_percent_changes_from_agg(agg)
            did_vals.append(p["did_pct"])

    did_vals = np.array(did_vals, dtype=float)
    did_vals = did_vals[~np.isnan(did_vals)]
    if did_vals.size == 0:
        return {"se": np.nan, "ci_low": np.nan, "ci_high": np.nan, "dist": np.array([])}
    se = did_vals.std(ddof=1)
    ci_low, ci_high = np.percentile(did_vals, [2.5, 97.5])
    return {"se": se, "ci_low": ci_low, "ci_high": ci_high, "dist": did_vals}

def try_ols_log_did(daily_df: pd.DataFrame):
    try:
        import statsmodels.formula.api as smf
    except Exception:
        return None, None
    df = daily_df.dropna(subset=["period", "per_mp"]).copy()
    df = df[df["per_mp"] > 0].copy()
    if df.empty:
        return None, None
    df["post"] = (df["period"] == "after_ref").astype(int)
    df["group_treatment"] = (df["group"] == "treatment").astype(int)
    df["log_per_mp"] = np.log(df["per_mp"])
    model = smf.ols("log_per_mp ~ group_treatment + post + group_treatment:post", data=df).fit(cov_type="HC1")
    if "group_treatment:post" in model.params.index:
        b = float(model.params["group_treatment:post"])
        ci_low, ci_high = model.conf_int().loc["group_treatment:post"].tolist()
        pct_effect = 100.0 * (np.exp(b) - 1.0)
        pct_ci_low = 100.0 * (np.exp(ci_low) - 1.0)
        pct_ci_high = 100.0 * (np.exp(ci_high) - 1.0)
        derived = {
            "log_DiD_coef": b,
            "log_DiD_ci_low": ci_low,
            "log_DiD_ci_high": ci_high,
            "pct_effect": pct_effect,
            "pct_ci_low": pct_ci_low,
            "pct_ci_high": pct_ci_high,
        }
    else:
        derived = None
    return model, derived

# ---------- Event-Study (Pre-trends) ----------
def month_id_from_date(d: pd.Series) -> pd.Series:
    return (d.dt.year * 12 + d.dt.month).astype(int)

def build_monthly_panel(daily: pd.DataFrame) -> pd.DataFrame:
    daily = daily.copy()
    daily["month_start"] = daily["date"].values.astype('datetime64[M]')
    ag = (daily
          .groupby(["group", "month_start"], as_index=False)
          .agg(sum_consumption=(CONSUMPTION_COL, "sum"),
               sum_mp=(MP_COL, "sum")))
    ag["avg_per_mp"] = ag["sum_consumption"] / ag["sum_mp"]
    ag["log_per_mp"] = np.where(ag["avg_per_mp"] > 0, np.log(ag["avg_per_mp"]), np.nan)
    ag["group_treatment"] = (ag["group"] == "treatment").astype(int)
    ag["month_id"] = month_id_from_date(pd.to_datetime(ag["month_start"]))
    return ag
'''
def run_event_study(monthly_df: pd.DataFrame, treatment_date: pd.Timestamp, k_pre=12, k_post=4):
    try:
        import statsmodels.formula.api as smf
    except Exception:
        return None, None
    df = monthly_df.copy()
    df = df.dropna(subset=["log_per_mp"]).copy()
    treat_month_id = month_id_from_date(pd.Series([treatment_date]))[0]
    df["event_k"] = df["month_id"] - treat_month_id
    df["event_k_clip"] = df["event_k"].clip(lower=-k_pre, upper=k_post)

    # Base = -1
    base_k = -1
    cats = sorted(df["event_k_clip"].unique())
    cats_no_base = [k for k in cats if k != base_k]

    # Interaksjonsdummier D_k
    for k in cats_no_base:
        df[f"D_{k}"] = ((df["group_treatment"] == 1) & (df["event_k_clip"] == k)).astype(int)

    # FE for group og måned
    rhs = ["C(group)", "C(month_id)"] + [f"D_{k}" for k in cats_no_base]
    formula = "log_per_mp ~ " + " + ".join(rhs)

    model = smf.ols(formula, data=df).fit(cov_type="HC1")

    # Koef-tabell
    rows = []
    for k in sorted(cats_no_base):
        pname = f"D_{k}"
        if pname in model.params.index:
            b = float(model.params[pname])
            se = float(model.bse[pname])
            ci_l, ci_h = model.conf_int().loc[pname].tolist()
            pct = 100.0 * (np.exp(b) - 1.0)
            pct_l = 100.0 * (np.exp(ci_l) - 1.0)
            pct_h = 100.0 * (np.exp(ci_h) - 1.0)
            rows.append({"k": k, "beta": b, "se": se, "ci_low": ci_l, "ci_high": ci_h,
                         "pct_effect": pct, "pct_ci_low": pct_l, "pct_ci_high": pct_h})
        else:
            rows.append({"k": k, "beta": np.nan, "se": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                         "pct_effect": np.nan, "pct_ci_low": np.nan, "pct_ci_high": np.nan})

    coeff_table = pd.DataFrame(rows).sort_values("k").reset_index(drop=True)
    base_row = {"k": base_k, "beta": 0.0, "se": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                "pct_effect": 0.0, "pct_ci_low": np.nan, "pct_ci_high": np.nan}
    coeff_table = pd.concat([coeff_table, pd.DataFrame([base_row])], ignore_index=True).sort_values("k").reset_index(drop=True)
    return coeff_table, model
'''
#ny versjon som funker med minustegnene
def run_event_study(monthly_df: pd.DataFrame, treatment_date: pd.Timestamp, k_pre=12, k_post=4):
    try:
        import statsmodels.formula.api as smf
    except Exception:
        return None, None

    df = monthly_df.copy()
    df = df.dropna(subset=["log_per_mp"]).copy()

    # month_id for treatment
    treat_month_id = month_id_from_date(pd.Series([treatment_date]))[0]
    df["event_k"] = df["month_id"] - treat_month_id
    df["event_k_clip"] = df["event_k"].clip(lower=-k_pre, upper=k_post)

    base_k = -1  # referansekategori

    # gyldige dummy-navn uten minus-tegn
    def dummy_name(k: int) -> str:
        if k < 0:
            return f"D_m{abs(k)}"
        else:
            return f"D_p{k}"

    cats = sorted(df["event_k_clip"].unique())
    cats_no_base = [k for k in cats if k != base_k]

    # lag dummies kun for treatment*event_k (interaksjoner)
    for k in cats_no_base:
        col = dummy_name(k)
        df[col] = ((df["group_treatment"] == 1) & (df["event_k_clip"] == k)).astype(int)

    # FE for group og måned + alle D_* ledd
    rhs = ["C(group)", "C(month_id)"] + [dummy_name(k) for k in cats_no_base]
    formula = "log_per_mp ~ " + " + ".join(rhs)

    model = smf.ols(formula, data=df).fit(cov_type="HC1")

    # Koef-tabell
    rows = []
    for k in sorted(cats_no_base):
        pname = dummy_name(k)
        if pname in model.params.index:
            b = float(model.params[pname])
            se = float(model.bse[pname])
            ci_l, ci_h = model.conf_int().loc[pname].tolist()
            rows.append({
                "k": k,
                "beta": b,
                "se": se,
                "ci_low": ci_l,
                "ci_high": ci_h,
                "pct_effect": 100.0 * (np.exp(b) - 1.0),
                "pct_ci_low": 100.0 * (np.exp(ci_l) - 1.0),
                "pct_ci_high": 100.0 * (np.exp(ci_h) - 1.0),
            })
        else:
            rows.append({
                "k": k, "beta": np.nan, "se": np.nan,
                "ci_low": np.nan, "ci_high": np.nan,
                "pct_effect": np.nan, "pct_ci_low": np.nan, "pct_ci_high": np.nan
            })

    base_row = {
        "k": base_k, "beta": 0.0, "se": np.nan,
        "ci_low": np.nan, "ci_high": np.nan,
        "pct_effect": 0.0, "pct_ci_low": np.nan, "pct_ci_high": np.nan
    }

    coeff_table = pd.concat(
        [pd.DataFrame(rows), pd.DataFrame([base_row])],
        ignore_index=True
    ).sort_values("k").reset_index(drop=True)

    return coeff_table, model


# ---------- F-TESTER (Wald) ----------
def wald_f_test_zero_coefs(model, param_names):
    """
    F-test for H0: angitte parametere = 0 (joint).
    Returnerer dict med F, df, p.
    """
    import numpy as np
    all_params = list(model.params.index)
    idx = [all_params.index(p) for p in param_names if p in all_params]
    if len(idx) == 0:
        return None
    R = np.zeros((len(idx), len(all_params)))
    for i, j in enumerate(idx):
        R[i, j] = 1.0
    ft = model.f_test(R)
    # håndter numpy-skalar vs array
    fval = float(np.squeeze(ft.fvalue))
    pval = float(np.squeeze(ft.pvalue))
    return {"F": fval, "df_num": int(ft.df_num), "df_denom": int(ft.df_denom), "p_value": pval,
            "tested_params": param_names}

def wald_f_test_equal_coefs(model, param_names):
    """
    F-test for H0: alle oppgitte parametere er like hverandre (D_k = D_ref for alle k).
    Implementasjon: test (D_k - D_ref) = 0 for alle k != ref.
    """
    import numpy as np
    all_params = list(model.params.index)
    param_names = [p for p in param_names if p in all_params]
    if len(param_names) <= 1:
        return None
    ref = param_names[0]
    idx_map = {p: all_params.index(p) for p in param_names}
    R = np.zeros((len(param_names) - 1, len(all_params)))
    for r, p in enumerate(param_names[1:]):
        R[r, idx_map[p]] = 1.0
        R[r, idx_map[ref]] = -1.0
    ft = model.f_test(R)
    fval = float(np.squeeze(ft.fvalue))
    pval = float(np.squeeze(ft.pvalue))
    return {"F": fval, "df_num": int(ft.df_num), "df_denom": int(ft.df_denom), "p_value": pval,
            "tested_params": param_names, "ref_param": ref}

def f_test_single_term_zero(model, term):
    """
    F-test for én restriksjon (lik t-test^2).
    """
    return wald_f_test_zero_coefs(model, [term])

# -----------------------------
# HOVEDKJØRING
# -----------------------------
pd.set_option("display.float_format", lambda x: f"{x:,.6f}")

# 1) Les inn og lag daglig panel
treatment_daily = load_and_prepare(TREATMENT_FILE, "treatment")
control_daily   = load_and_prepare(CONTROL_FILE,   "control")
daily = pd.concat([treatment_daily, control_daily], ignore_index=True)

# 2) Hoved-DiD
daily_main = daily.copy()
daily_main["period"] = label_periods(daily_main["date"], BEFORE_START, BEFORE_END, AFTER_START, AFTER_END)
agg_main = summarize_by_period(daily_main.dropna(subset=["period"]))
did_main = compute_did_from_agg(agg_main)
did_pct_main = compute_percent_changes_from_agg(agg_main)
boot_main = bootstrap_did(daily_main, n_boot=N_BOOT, seed=RANDOM_SEED, use_percent=False) if N_BOOT > 0 else {"se": np.nan, "ci_low": np.nan, "ci_high": np.nan}
boot_pct_main = bootstrap_did(daily_main, n_boot=N_BOOT, seed=RANDOM_SEED, use_percent=True) if N_BOOT > 0 else {"se": np.nan, "ci_low": np.nan, "ci_high": np.nan}
ols_model_main, ols_log_main = try_ols_log_did(daily_main)

# 3) PLACEBO-DiD
daily_placebo = daily.copy()
daily_placebo["period"] = label_periods(
    daily_placebo["date"],
    PLACEBO_BEFORE_START, PLACEBO_BEFORE_END,
    PLACEBO_AFTER_START,  PLACEBO_AFTER_END
)
agg_pl = summarize_by_period(daily_placebo.dropna(subset=["period"]))
did_pl = compute_did_from_agg(agg_pl)
did_pct_pl = compute_percent_changes_from_agg(agg_pl)
boot_pl = bootstrap_did(daily_placebo, n_boot=N_BOOT, seed=RANDOM_SEED, use_percent=False) if N_BOOT > 0 else {"se": np.nan, "ci_low": np.nan, "ci_high": np.nan}
boot_pct_pl = bootstrap_did(daily_placebo, n_boot=N_BOOT, seed=RANDOM_SEED, use_percent=True) if N_BOOT > 0 else {"se": np.nan, "ci_low": np.nan, "ci_high": np.nan}
ols_model_pl, ols_log_pl = try_ols_log_did(daily_placebo)

# 4) PRE-TRENDS / EVENT-STUDY
monthly = build_monthly_panel(daily)
es_table, es_model = run_event_study(monthly, TREATMENT_DATE, k_pre=K_PRE, k_post=K_POST)

# -----------------------------
# F-TESTER
# -----------------------------
'''
# (A) F-test: H0 pre-trends (alle pre-leads = 0)
pre_ft = post_zero_ft = post_flat_ft = None
if es_model is not None:
    es_param_names = list(es_model.params.index)
    pre_names = [p for p in es_param_names if p.startswith("D_") and int(p.split("_")[1]) <= -2]
    post_names = [p for p in es_param_names if p.startswith("D_") and int(p.split("_")[1]) >= 0]

    pre_ft = wald_f_test_zero_coefs(es_model, pre_names)
    post_zero_ft = wald_f_test_zero_coefs(es_model, post_names)
    post_flat_ft = wald_f_test_equal_coefs(es_model, post_names)

# (B) F-test: interaksjon = 0 i hoved og placebo (log-OLS)
main_interaction_ft = placebo_interaction_ft = None
if ols_model_main is not None:
    main_interaction_ft = f_test_single_term_zero(ols_model_main, "group_treatment:post")
if ols_model_pl is not None:
    placebo_interaction_ft = f_test_single_term_zero(ols_model_pl, "group_treatment:post")
'''
#nye a tester

# (A) F-test: H0 pre-trends (alle pre-leads = 0)
pre_ft = post_zero_ft = post_flat_ft = None
if es_model is not None:
    es_param_names = list(es_model.params.index)

    def parse_event_param_k(p: str):
        """
        Returnerer heltall k for event-study-parameter p.
        Støtter begge navneskjema:
        - Gammelt: D_-12, D_-2, D_0, D_3
        - Nytt:   D_m12 (k=-12), D_m2 (k=-2), D_p0 (k=0), D_p3 (k=3)
        Returnerer None hvis ikke gjenkjennelig.
        """
        try:
            if p.startswith("D_m"):   # nytt schema, negative k
                return -int(p[3:])
            if p.startswith("D_p"):   # nytt schema, k >= 0
                return int(p[3:])
            if p.startswith("D_"):    # gammelt schema, f.eks. D_-12 eller D_3
                return int(p.split("_", 1)[1])
        except Exception:
            return None
        return None

    # bygg lister over parametere vi skal teste
    pre_names = []
    post_names = []
    for p in es_param_names:
        k = parse_event_param_k(p)
        if k is None:
            continue
        if k <= -2:
            pre_names.append(p)
        if k >= 0:
            post_names.append(p)

    pre_ft = wald_f_test_zero_coefs(es_model, pre_names) if len(pre_names) > 0 else None
    post_zero_ft = wald_f_test_zero_coefs(es_model, post_names) if len(post_names) > 0 else None
    post_flat_ft = wald_f_test_equal_coefs(es_model, post_names) if len(post_names) > 1 else None

# (B) F-test: interaksjon = 0 i hoved og placebo (log-OLS)
main_interaction_ft = placebo_interaction_ft = None

# HOVED
if ols_model_main is not None:
    main_interaction_ft = f_test_single_term_zero(ols_model_main, "group_treatment:post")

# PLACEBO
if ols_model_pl is not None:
    placebo_interaction_ft = f_test_single_term_zero(ols_model_pl, "group_treatment:post")



'''
#igjen, ny versjon av f-tester som funker med de minus tegnene

pre_ft = post_zero_ft = post_flat_ft = None
if es_model is not None:
    es_param_names = list(es_model.params.index)

    def parse_k_from_name(p: str):
        # D_m12 -> k = -12, D_p3 -> k = 3, D_p0 -> k = 0
        if p.startswith("D_m"):
            try:
                return -int(p.replace("D_m", ""))
            except Exception:
                return None
        if p.startswith("D_p"):
            try:
                return int(p.replace("D_p", ""))
            except Exception:
                return None
        return None

    # Finn alle D_* parametere med tilhørende k
    k_map = {p: parse_k_from_name(p) for p in es_param_names if p.startswith(("D_m", "D_p"))}

    # Pre-leads: k <= -2 (base er -1 og inngår ikke som parameter)
    pre_names = [p for p, k in k_map.items() if k is not None and k <= -2]

    # Post: k >= 0
    post_names = [p for p, k in k_map.items() if k is not None and k >= 0]

    pre_ft = wald_f_test_zero_coefs(es_model, pre_names) if len(pre_names) > 0 else None
    post_zero_ft = wald_f_test_zero_coefs(es_model, post_names) if len(post_names) > 0 else None
    post_flat_ft = wald_f_test_equal_coefs(es_model, post_names) if len(post_names) > 1 else None
'''


# -----------------------------
# PRINT
# -----------------------------
print("\n===== [HOVED] Aggregater per gruppe og periode =====")
print(agg_main.sort_values(["group", "period"]))

print("\n===== [HOVED] DiD (nivå) =====")
print(pd.Series(did_main))

print("\n===== [HOVED] DiD (prosent) =====")
print(pd.Series({
    "Treatment % endring": did_pct_main["treatment_pct_change"],
    "Control   % endring": did_pct_main["control_pct_change"],
    "DiD i prosentpoeng": did_pct_main["did_pct"],
}))
print("\n===== [HOVED] Bootstrap-KI =====")
print("Nivå-DiD 95% KI:", boot_main.get("ci_low"), boot_main.get("ci_high"))
print("Prosent-DiD 95% KI:", boot_pct_main.get("ci_low"), boot_pct_main.get("ci_high"))

if ols_model_main is not None:
    print("\n===== [HOVED] OLS-DiD (LOG, robuste SE) =====")
    try:
        print(ols_model_main.summary())
    except Exception:
        print("Parametere:", ols_model_main.params)
        print("Robuste SE:", ols_model_main.bse)
    if ols_log_main is not None:
        print("\n— Tolkning (prosent):")
        print(pd.Series({
            "β_DiD (log)": ols_log_main["log_DiD_coef"],
            "95% KI β": f"[{ols_log_main['log_DiD_ci_low']}, {ols_log_main['log_DiD_ci_high']}]",
            "Effekt i %": ols_log_main["pct_effect"],
            "95% KI %": f"[{ols_log_main['pct_ci_low']}, {ols_log_main['pct_ci_high']}]"
        }))

print("\n===== [PLACEBO] DiD (nivå og prosent) =====")
print(pd.Series(did_pl))
print(pd.Series({
    "Treatment % endring": did_pct_pl["treatment_pct_change"],
    "Control   % endring": did_pct_pl["control_pct_change"],
    "DiD i prosentpoeng": did_pct_pl["did_pct"],
}))

if es_table is not None:
    print("\n===== [EVENT-STUDY] Første rader =====")
    print(es_table.head(10))

# F-test resultater
def _print_ft(name, res):
    if res is None:
        print(f"{name}: (ikke tilgjengelig)")
    else:
        print(f"{name}: F({res['df_num']}, {res['df_denom']}) = {res['F']:.3f}, p = {res['p_value']:.4f}")

print("\n===== F-TESTER =====")
_print_ft("Pre-trends H0: alle pre-leads = 0", pre_ft)
_print_ft("Post H0: alle post-lag = 0", post_zero_ft)
_print_ft("Post H0: alle post-lag er like", post_flat_ft)
_print_ft("HOVED log-OLS H0: interaksjon = 0", main_interaction_ft)
_print_ft("PLACEBO log-OLS H0: interaksjon = 0", placebo_interaction_ft)

# -----------------------------
# Lagring: tabeller og tester
# -----------------------------
''' # ta vekk skrivingen til filer fordi filene e tatt vekk 
# Hoved
agg_main.to_csv("did_aggregates.csv", index=False)
pd.DataFrame([{
    **did_main,
    "boot_se":      boot_main.get("se"),
    "boot_ci_low":  boot_main.get("ci_low"),
    "boot_ci_high": boot_main.get("ci_high"),
    "treatment_pct_change": did_pct_main["treatment_pct_change"],
    "control_pct_change":   did_pct_main["control_pct_change"],
    "did_pct":              did_pct_main["did_pct"],
    "boot_pct_se":          boot_pct_main.get("se"),
    "boot_pct_ci_low":      boot_pct_main.get("ci_low"),
    "boot_pct_ci_high":     boot_pct_main.get("ci_high"),
    "ols_log_did_coef":   (ols_log_main or {}).get("log_DiD_coef"),
    "ols_log_did_ci_low": (ols_log_main or {}).get("log_DiD_ci_low"),
    "ols_log_did_ci_high":(ols_log_main or {}).get("log_DiD_ci_high"),
    "ols_pct_effect":     (ols_log_main or {}).get("pct_effect"),
    "ols_pct_ci_low":     (ols_log_main or {}).get("pct_ci_low"),
    "ols_pct_ci_high":    (ols_log_main or {}).get("pct_ci_high"),
}]).to_csv("did_summary.csv", index=False)

# Placebo
pd.DataFrame([{
    **did_pl,
    "boot_se":      boot_pl.get("se"),
    "boot_ci_low":  boot_pl.get("ci_low"),
    "boot_ci_high": boot_pl.get("ci_high"),
    "treatment_pct_change": did_pct_pl["treatment_pct_change"],
    "control_pct_change":   did_pct_pl["control_pct_change"],
    "did_pct":              did_pct_pl["did_pct"],
    "boot_pct_se":          boot_pct_pl.get("se"),
    "boot_pct_ci_low":      boot_pct_pl.get("ci_low"),
    "boot_pct_ci_high":     boot_pct_pl.get("ci_high"),
    "ols_log_did_coef":   (ols_log_pl or {}).get("log_DiD_coef"),
    "ols_log_did_ci_low": (ols_log_pl or {}).get("log_DiD_ci_low"),
    "ols_log_did_ci_high":(ols_log_pl or {}).get("log_DiD_ci_high"),
    "ols_pct_effect":     (ols_log_pl or {}).get("pct_effect"),
    "ols_pct_ci_low":     (ols_log_pl or {}).get("pct_ci_low"),
    "ols_pct_ci_high":    (ols_log_pl or {}).get("pct_ci_high"),
}]).to_csv("placebo_did_summary.csv", index=False)

# Event-study koeffisienter
if es_table is not None:
    es_table.to_csv("event_study_coeffs.csv", index=False)

# F-test filer
if pre_ft is not None:
    pd.DataFrame([pre_ft]).to_csv("event_pretrends_f_test.csv", index=False)
if post_zero_ft is not None:
    pd.DataFrame([post_zero_ft]).to_csv("event_post_zero_f_test.csv", index=False)
if post_flat_ft is not None:
    pd.DataFrame([post_flat_ft]).to_csv("event_post_flat_f_test.csv", index=False)
if main_interaction_ft is not None:
    pd.DataFrame([main_interaction_ft]).to_csv("main_interaction_f_test.csv", index=False)
if placebo_interaction_ft is not None:
    pd.DataFrame([placebo_interaction_ft]).to_csv("placebo_interaction_f_test.csv", index=False)

# -----------------------------
# Plot: hoved/ placeb o + event-study (samme som tidligere, kortet litt)
# -----------------------------
# Hoved plot (nivå)
fig, ax = plt.subplots(figsize=(11, 6))
plot_df = daily_main.sort_values("date").copy()
plot_df["per_mp_roll7"] = (plot_df.groupby("group")["per_mp"].transform(lambda s: s.rolling(7, min_periods=1).mean()))
for grp, sub in plot_df.groupby("group"):
    ax.plot(sub["date"], sub["per_mp_roll7"], label=f"{grp} (7-d gj.sn.)", linewidth=1.8)
ax.axvspan(BEFORE_START, BEFORE_END, color="tab:blue", alpha=0.10, label="before_ref")
ax.axvspan(AFTER_START,  AFTER_END,  color="tab:orange", alpha=0.10, label="after_ref")
ax.set_title("Forbruk per målepunkt (kWh per MP per dag) – HOVED", fontsize=13)
ax.set_xlabel("Dato"); ax.set_ylabel("kWh per målepunkt per dag"); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("did_plot.png", dpi=150); plt.close()

# Hoved prosent-plot
base_vals = agg_main.pivot(index="group", columns="period", values="avg_per_mp")
base_t = base_vals.loc["treatment", "before_ref"] if ("treatment" in base_vals.index and "before_ref" in base_vals.columns) else np.nan
base_c = base_vals.loc["control", "before_ref"]   if ("control"   in base_vals.index and "before_ref" in base_vals.columns) else np.nan
plot_df2 = daily_main.sort_values("date").copy()
plot_df2["baseline"] = plot_df2["group"].map({"treatment": base_t, "control": base_c})
plot_df2["pct_from_baseline"] = np.where(plot_df2["baseline"] > 0, (plot_df2["per_mp"] / plot_df2["baseline"] - 1) * 100.0, np.nan)
plot_df2["pct_roll7"] = (plot_df2.groupby("group")["pct_from_baseline"].transform(lambda s: s.rolling(7, min_periods=1).mean()))
fig, ax = plt.subplots(figsize=(11, 6))
for grp, sub in plot_df2.groupby("group"):
    ax.plot(sub["date"], sub["pct_roll7"], label=f"{grp} (% fra baseline, 7-d)", linewidth=1.8)
ax.axvspan(BEFORE_START, BEFORE_END, color="tab:blue", alpha=0.10, label="before_ref")
ax.axvspan(AFTER_START,  AFTER_END,  color="tab:orange", alpha=0.10, label="after_ref")
ax.axhline(0, color="k", linewidth=0.8, alpha=0.6)
ax.set_title("Prosent avvik fra egen baseline – HOVED", fontsize=13)
ax.set_xlabel("Dato"); ax.set_ylabel("Avvik fra baseline (%)"); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("did_pct_plot.png", dpi=150); plt.close()

# Placebo nivå
fig, ax = plt.subplots(figsize=(11, 6))
plot_df = daily_placebo.sort_values("date").copy()
plot_df["per_mp_roll7"] = (plot_df.groupby("group")["per_mp"].transform(lambda s: s.rolling(7, min_periods=1).mean()))
for grp, sub in plot_df.groupby("group"):
    ax.plot(sub["date"], sub["per_mp_roll7"], label=f"{grp} (7-d gj.sn.)", linewidth=1.8)
ax.axvspan(PLACEBO_BEFORE_START, PLACEBO_BEFORE_END, color="tab:blue", alpha=0.10, label="placebo_before")
ax.axvspan(PLACEBO_AFTER_START,  PLACEBO_AFTER_END,  color="tab:orange", alpha=0.10, label="placebo_after")
ax.set_title("Forbruk per målepunkt – PLACEBO", fontsize=13)
ax.set_xlabel("Dato"); ax.set_ylabel("kWh per målepunkt per dag"); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("placebo_did_plot.png", dpi=150); plt.close()

# Placebo prosent
base_vals_pl = agg_pl.pivot(index="group", columns="period", values="avg_per_mp")
base_t_pl = base_vals_pl.loc["treatment", "before_ref"] if ("treatment" in base_vals_pl.index and "before_ref" in base_vals_pl.columns) else np.nan
base_c_pl = base_vals_pl.loc["control", "before_ref"]   if ("control"   in base_vals_pl.index and "before_ref" in base_vals_pl.columns) else np.nan
plot_df2 = daily_placebo.sort_values("date").copy()
plot_df2["baseline"] = plot_df2["group"].map({"treatment": base_t_pl, "control": base_c_pl})
plot_df2["pct_from_baseline"] = np.where(plot_df2["baseline"] > 0, (plot_df2["per_mp"] / plot_df2["baseline"] - 1) * 100.0, np.nan)
plot_df2["pct_roll7"] = (plot_df2.groupby("group")["pct_from_baseline"].transform(lambda s: s.rolling(7, min_periods=1).mean()))
fig, ax = plt.subplots(figsize=(11, 6))
for grp, sub in plot_df2.groupby("group"):
    ax.plot(sub["date"], sub["pct_roll7"], label=f"{grp} (% fra placebo-baseline, 7-d)", linewidth=1.8)
ax.axvspan(PLACEBO_BEFORE_START, PLACEBO_BEFORE_END, color="tab:blue", alpha=0.10, label="placebo_before")
ax.axvspan(PLACEBO_AFTER_START,  PLACEBO_AFTER_END,  color="tab:orange", alpha=0.10, label="placebo_after")
ax.axhline(0, color="k", linewidth=0.8, alpha=0.6)
ax.set_title("Prosent avvik fra placebo-baseline – PLACEBO", fontsize=13)
ax.set_xlabel("Dato"); ax.set_ylabel("Avvik fra baseline (%)"); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("placebo_did_pct_plot.png", dpi=150); plt.close()

print("\nFerdig! Filer skrevet:")
print(" - did_aggregates.csv")
print(" - did_summary.csv")
print(" - did_plot.png")
print(" - did_pct_plot.png")
print(" - placebo_did_summary.csv")
print(" - placebo_did_plot.png")
print(" - placebo_did_pct_plot.png")
print(" - event_study_coeffs.csv")
print(" - event_pretrends_f_test.csv")
print(" - event_post_zero_f_test.csv")
print(" - event_post_flat_f_test.csv")
print(" - main_interaction_f_test.csv")
print(" - placebo_interaction_f_test.csv")'''