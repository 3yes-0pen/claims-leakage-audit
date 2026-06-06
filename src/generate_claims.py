import uuid
import numpy as np
import pandas as pd
from src.personas import PROVIDER_PERSONAS, PERSONA_TYPE_TO_KEY
from src.cpt_lookup import get_cpt
from src.icd_lookup import get_icd10

SPECIALTY_BILLED_RANGE = {
    "Internal Medicine":  (120, 450),
    "Radiology":          (300, 1800),
    "Emergency Medicine": (500, 3500),
    "Oncology":           (1500, 12000),
    "Behavioral Health":  (100, 350),
}

PAYER_IDS      = ["medi_cal_managed_care", "commercial_ppo", "medicare_advantage", "dual_eligible_cobpayer"]
PAYER_WEIGHTS  = [0.45, 0.30, 0.20, 0.05]

def build_providers(n_providers=3):
    """Creates the provider table rows from persona definitions."""
    rows = []
    for i, (key, persona) in enumerate(PROVIDER_PERSONAS.items()):
        rows.append({
            "provider_id":    f"PROV_{i+1:03d}",
            "npi":            f"1{np.random.randint(100000000, 999999999)}",
            "specialty":      persona["specialty"],
            "practice_name":  key.replace("_", " ").title(),
            "network_status": "in-network",
            "persona_type":   persona["persona_type"],
        })
    return pd.DataFrame(rows)

def build_claim_header(encounters_df, providers_df):
    """
    Input:  Synthea encounters CSV as DataFrame, your providers DataFrame
    Output: claim_header DataFrame
    """
    rows = []

    for _, enc in encounters_df.iterrows():
        # Assign a provider and get their persona
        provider = providers_df.sample(1).iloc[0]
        persona_key = PERSONA_TYPE_TO_KEY[provider["persona_type"]]
        persona     = PROVIDER_PERSONAS[persona_key]

        # ── Charge entry lag ──────────────────────────────────────────────
        # FIX: bimodal distribution for slow_charge_capture persona.
        # A tail population (timely_filing_miss_rate) gets a lag that breaches
        # the 90-day Medi-Cal/Dual window. Commercial (180d) and MA (365d) stay clean.
        miss_rate = persona.get("timely_filing_miss_rate", 0.0)
        if np.random.random() < miss_rate:
            lag = int(np.random.uniform(92, 110))
        else:
            lag = max(1, int(np.random.normal(
                persona["charge_entry_lag_mean"],
                persona["charge_entry_lag_std"]
            )))

        dos = pd.to_datetime(enc["DATE"]).date()
        specialty    = provider["specialty"]
        bill_range   = SPECIALTY_BILLED_RANGE.get(specialty, (150, 2500))
        billed       = round(np.random.uniform(*bill_range), 2)

        rows.append({
            "claim_id":         str(uuid.uuid4()),
            "patient_id":       enc["PATIENT"],
            "provider_id":      provider["provider_id"],
            "payer_id":         np.random.choice(PAYER_IDS, p=PAYER_WEIGHTS),
            "date_of_service":  dos,
            "submission_date":  dos + pd.Timedelta(days=lag),
            "claim_type":       "837P",
            "place_of_service": "11",
            "billed_amount":    billed,
            "claim_status":     "submitted",
        })

    return pd.DataFrame(rows)

def build_claim_line(claim_header_df, procedures_df):
    """
    Input:  claim_header DataFrame, Synthea procedures CSV as DataFrame
    Output: claim_line DataFrame
    """
    rows = []
    for _, claim in claim_header_df.iterrows():
        # Find procedures matching this patient
        pt_procs = procedures_df[procedures_df["PATIENT"] == claim["patient_id"]]
        if pt_procs.empty:
            pt_procs = procedures_df.sample(1)  # fallback

        for line_num, (_, proc) in enumerate(pt_procs.head(3).iterrows(), start=1):
            rows.append({
                "claim_line_id": str(uuid.uuid4()),
                "claim_id":      claim["claim_id"],
                "line_number":   line_num,
                "cpt_code":      get_cpt(proc.get("CODE", "")),
                "icd10_primary": get_icd10(proc.get("REASONCODE", "")),
                "units":         1,
                "billed_amount": round(claim["billed_amount"] / line_num, 2),
                "line_status":   "submitted",
            })

    return pd.DataFrame(rows)