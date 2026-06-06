# src/generate_remittance.py
import uuid
import numpy as np
import pandas as pd
from src.personas import PAYER_PERSONAS
from src.prior_auth_rules import auth_required

# CARC code assignment based on denial type
CARC_MAP = {
    "timely_filing":           "CO-29",
    "prior_auth":              "CO-57",
    "bundling":                "CO-97",
    "coding_error":            "CO-4",
    "not_medically_necessary": "CO-50",
    "contractual":             "CO-45",  # not a denial — expected adjustment
    "deductible":              "PR-1",   # patient responsibility
    "cob_sequencing":          "CO-22",  # dual eligible COB failure
    "missing_information":     "CO-16",  # incomplete claim
    "credentialing":           "CO-B7",  # expired provider credentials
}

# CPT codes where bundling edits are clinically realistic
BUNDLING_RISK_CPTS = {"74177", "71250", "72148", "45378", "76164", "93654"}


def generate_remittance(claim_line_df, claim_header_df, encounter_context_df):
    rows = []

    for _, line in claim_line_df.iterrows():
        header = claim_header_df[
            claim_header_df["claim_id"] == line["claim_id"]
        ].iloc[0]

        payer_persona = PAYER_PERSONAS[header["payer_id"]]

        context = encounter_context_df[
            encounter_context_df["claim_id"] == line["claim_id"]
        ]

        billed = line["billed_amount"]
        carc, outcome = _determine_outcome(line, header, context, payer_persona)

        if outcome == "denied":
            allowed      = 0.0
            paid         = 0.0
            patient_resp = 0.0
            adjustment   = billed
        else:
            allowed      = round(billed * payer_persona["allowed_rate"], 2)
            patient_resp = round(min(allowed, np.random.uniform(0, 50)), 2)
            paid         = round(allowed - patient_resp, 2)
            adjustment   = round(billed - allowed, 2)

        # Enforce financial constraint
        if abs(billed - (paid + patient_resp + adjustment)) >= 0.01:
            raise ValueError(
                f"Financial constraint violated on claim_line {line['claim_line_id']}: "
                f"allowed={allowed}, paid={paid}, "
                f"patient_resp={patient_resp}, adjustment={adjustment}"
            )

        adjudication_date = pd.Timestamp(header["submission_date"]) + pd.Timedelta(
            days=max(1, int(np.random.normal(
                payer_persona["adjudication_lag_mean"], 5
            )))
        )

        rows.append({
            "remittance_id":          str(uuid.uuid4()),
            "claim_id":               line["claim_id"],
            "claim_line_id":          line["claim_line_id"],
            "adjudication_date":      adjudication_date,
            "allowed_amount":         allowed,
            "paid_amount":            paid,
            "patient_responsibility": patient_resp,
            "adjustment_amount":      adjustment,
            "carc_code":              carc,
        })

    return pd.DataFrame(rows)


def _determine_outcome(line, header, context, payer):
    """
    Evaluates each claim line against payer rules and provider behavior.
    Returns (carc_code, 'denied' or 'paid').
    Checks run in priority order — first match wins.
    """
    cpt      = line["cpt_code"]
    payer_id = header["payer_id"]

    # 1. Timely filing — date math only, no randomness
    dos = pd.Timestamp(header["date_of_service"])
    sub = pd.Timestamp(header["submission_date"])
    if (sub - dos).days > payer["timely_filing_limit_days"]:
        return CARC_MAP["timely_filing"], "denied"
    
    # 2. Prior auth miss → CO-57
    # FIX: use prior_auth_required from encounter_context as single source of truth.
    # Previously called auth_required(cpt, payer_id) here independently, which rarely
    # returned True for Synthea CPT codes — producing only 2 CO-57 denials.
    # encounter_context.prior_auth_required now includes the persona-level base rate
    # override (base_auth_required_rate) set in generate_context.py.
    if not context.empty and context.iloc[0]["prior_auth_required"]:
        if not context.iloc[0]["prior_auth_obtained"]:
            if np.random.random() < payer["prior_auth_denial_rate"]:
                return CARC_MAP["prior_auth"], "denied"

    # # 2.5 Medical necessity → CO-50
    # FIX: fires when auth was required AND obtained, but payer still denies on
    # medical necessity grounds. Primary driver is oncology (complex chemo auth),
    # but any auth-required procedure can trigger it at the payer's denial rate.
    if not context.empty and context.iloc[0]["prior_auth_required"]:
        if context.iloc[0]["prior_auth_obtained"]:                            # auth WAS obtained
            if np.random.random() < payer.get("medical_necessity_denial_rate", 0.0):
                return CARC_MAP["not_medically_necessary"], "denied"


    # 3. Coding error — driven by provider coding accuracy flag
    if not context.empty and not context.iloc[0]["coding_accuracy_flag"]:
        if np.random.random() < 0.40:
            return CARC_MAP["coding_error"], "denied"
    
    # 3.5 Credentialing lapse — reads from encounter_context, not payer persona
    if not context.empty and context.iloc[0]["credentialing_lapsed"]:
        return CARC_MAP["credentialing"], "denied"
    

    # 4. Bundling — only triggered on clinically realistic CPT codes
    if cpt in BUNDLING_RISK_CPTS:
        if np.random.random() < payer["bundling_edit_rate"]:
            return CARC_MAP["bundling"], "denied"
        
    # 4.5 Missing information → CO-16
    # FIX: fires when eligibility was not verified before service.
    # ER group (60% verify rate) is the primary driver — 40% of ER encounters
    # have eligibility_verified_flag=False, triggering CO-16 at 15% rate.
    if not context.empty and not context.iloc[0]["eligibility_verified_flag"]:
        if np.random.random() < 0.15:
            return CARC_MAP["missing_information"], "denied"

    # 5. COB sequencing — only for dual eligible payer
    if payer_id == "dual_eligible_cobpayer":
        if np.random.random() < payer.get("cob_denial_rate", 0.0):
            return CARC_MAP["cob_sequencing"], "denied"

    # 6. Default: paid with contractual adjustment
    return CARC_MAP["contractual"], "paid"