import uuid
import numpy as np
import pandas as pd

# Maps CARC codes to analytical classifications
CARC_CLASSIFICATION = {
    "CO-29": {
        "denial_category":       "timely_filing",
        "upstream_failure_node": "charge_capture",
        "preventability_flag":   True,
        "recovery_probability":  0.10,  # hard to recover after window closes
        "recommended_action":    "write_off",
    },
    "CO-57": {
        "denial_category":       "authorization",
        "upstream_failure_node": "prior_authorization",
        "preventability_flag":   True,
        "recovery_probability":  0.55,
        "recommended_action":    "appeal",
    },
    "CO-97": {
        "denial_category":       "bundling",
        "upstream_failure_node": "coding",
        "preventability_flag":   True,
        "recovery_probability":  0.65,
        "recommended_action":    "correct_resubmit",
    },
    "CO-4": {
        "denial_category":       "coding_error",
        "upstream_failure_node": "coding",
        "preventability_flag":   True,
        "recovery_probability":  0.70,
        "recommended_action":    "correct_resubmit",
    },
    "CO-50": {
        "denial_category":       "medical_necessity",
        "upstream_failure_node": "prior_authorization",
        "preventability_flag":   False,
        "recovery_probability":  0.35,
        "recommended_action":    "appeal",
    },
    "CO-22": {
        "denial_category":       "coordination_of_benefits",
        "upstream_failure_node": "remittance_posting",
        "preventability_flag":   True,
        "recovery_probability":  0.55,
        "recommended_action":    "correct_resubmit",
    },
    "CO-16": {
        "denial_category":       "missing_information",
        "upstream_failure_node": "billing",
        "preventability_flag":   True,
        "recovery_probability":  0.72,
        "recommended_action":    "correct_resubmit",
    },
    "CO-B7": {
        "denial_category":       "provider_credentialing",
        "upstream_failure_node": "credentialing",
        "preventability_flag":   True,
        "recovery_probability":  0.15,
        "recommended_action":    "appeal",
    },
}

def build_denial_forensics(remittance_df, claim_header_df):
    denied = remittance_df[remittance_df["paid_amount"] == 0].copy()
    # Exclude expected adjustments — CO-45 and PR-1 are not failures
    denied = denied[~denied["carc_code"].isin(["CO-45", "PR-1"])]

    rows = []
    # Anchor reference date to data — use max adjudication date + 30 days
    # instead of real today, since Synthea data is historical
    
    reference_date = pd.Timestamp(remittance_df["adjudication_date"].max()) + pd.Timedelta(days=30)

    for _, rem in denied.iterrows():
        header = claim_header_df[claim_header_df["claim_id"] == rem["claim_id"]]
        if header.empty:
            continue
        header = header.iloc[0]

        classification = CARC_CLASSIFICATION.get(rem["carc_code"], {
            "denial_category":       "other",
            "upstream_failure_node": "unknown",
            "preventability_flag":   False,
            "recovery_probability":  0.20,
            "recommended_action":    "review",
        })

        adj_date = pd.Timestamp(rem["adjudication_date"])
        days_remaining = max(0, 180 - (reference_date - adj_date).days)
        dollars_at_risk = rem["adjustment_amount"]
        recovery_prob   = classification["recovery_probability"]

        urgency_weight = 1 + (1 - days_remaining / 180)  # higher as window closes
        priority_score = dollars_at_risk * recovery_prob * urgency_weight

        rows.append({
            "denial_id":              str(uuid.uuid4()),
            "claim_line_id":          rem["claim_line_id"],
            "carc_code":              rem["carc_code"],
            "denial_category":        classification["denial_category"],
            "upstream_failure_node":  classification["upstream_failure_node"],
            "preventability_flag":    classification["preventability_flag"],
            "recovery_probability":   recovery_prob,
            "days_remaining_window":  days_remaining,
            "dollars_at_risk":        round(dollars_at_risk, 2),
            "recommended_action":     classification["recommended_action"],
            "priority_score":         round(priority_score, 4),
        })

    return pd.DataFrame(rows)