# src/appeal_outcomes.py
import uuid
import numpy as np
import pandas as pd

# Appeal success rates by CARC code
# These are informed by industry benchmarks:
# - Coding errors (CO-4, CO-97): high success when corrected and resubmitted
# - Prior auth (CO-57): moderate — requires clinical documentation
# - Timely filing (CO-29): very low — hard deadline, rarely overturned
# - Medical necessity (CO-50): low — payer has clinical criteria
# - COB (CO-22): moderate — sequencing error is correctable
# - Credentialing (CO-B7): very low — retroactive credentialing rarely approved
APPEAL_SUCCESS_RATES = {
    "CO-4":   0.68,   # coding error — correct and resubmit, high win rate
    "CO-97":  0.62,   # bundling — unbundle with documentation, moderate-high
    "CO-57":  0.48,   # prior auth — clinical appeal, coin flip
    "CO-50":  0.32,   # medical necessity — hardest to overturn
    "CO-29":  0.08,   # timely filing — near-impossible after window closes
    "CO-22":  0.55,   # COB sequencing — fixable if primary remit is obtained
    "CO-16":  0.72,   # missing info — easiest: just supply what was missing
    "CO-B7":  0.15,   # credentialing — retroactive approval rarely granted
}

# Days to resolution by appeal type
# Reflects realistic payer turnaround times
APPEAL_RESOLUTION_DAYS = {
    "CO-4":   (15, 30),    # correct/resubmit: fastest
    "CO-97":  (20, 45),
    "CO-57":  (30, 90),    # clinical review takes time
    "CO-50":  (45, 120),   # peer-to-peer review, long process
    "CO-29":  (14, 30),    # quick denial, little back-and-forth
    "CO-22":  (20, 45),
    "CO-16":  (10, 20),    # fastest — just missing a field
    "CO-B7":  (30, 60),
}

FALLBACK_SUCCESS_RATE       = 0.25
FALLBACK_RESOLUTION_DAYS    = (30, 60)


def simulate_appeal_outcomes(denial_forensics_df, remittance_df):
    """
    Input:  denial_forensics DataFrame, remittance_835 DataFrame
    Output: appeal_outcomes DataFrame — one row per appealed denial

    Only models appeals for claims where recommended_action is 'appeal'
    or 'correct_resubmit'. Write-offs and patient_collect are excluded
    because those aren't worked through appeal.
    """
    # Only simulate appeals on actionable denials
    appealable = denial_forensics_df[
        denial_forensics_df["recommended_action"].isin(["appeal", "correct_resubmit"])
    ].copy()

    rows = []

    for _, denial in appealable.iterrows():
        carc = denial["carc_code"]

        # Get success rate and resolution window for this CARC
        success_rate     = APPEAL_SUCCESS_RATES.get(carc, FALLBACK_SUCCESS_RATE)
        resolution_range = APPEAL_RESOLUTION_DAYS.get(carc, FALLBACK_RESOLUTION_DAYS)

        # Simulate outcome
        appeal_successful = np.random.random() < success_rate

        # Days to resolution — draws from realistic range
        days_to_resolve = int(np.random.uniform(*resolution_range))

        # If successful, how much was recovered?
        # Partial recoveries happen — payer may pay less than full denied amount
        if appeal_successful:
            recovery_rate   = np.random.uniform(0.80, 1.0)   # 80–100% of denied dollars
            dollars_recovered = round(denial["dollars_at_risk"] * recovery_rate, 2)
            outcome_status  = "paid"
        else:
            dollars_recovered = 0.0
            outcome_status  = "denied_final"

        rows.append({
            "appeal_id":          str(uuid.uuid4()),
            "denial_id":          denial["denial_id"],
            "claim_line_id":      denial["claim_line_id"],
            "carc_code":          carc,
            "appeal_successful":  appeal_successful,
            "outcome_status":     outcome_status,
            "dollars_at_risk":    denial["dollars_at_risk"],
            "dollars_recovered":  dollars_recovered,
            "days_to_resolve":    days_to_resolve,
            "recovery_rate_est":  denial["recovery_probability"],   # what you predicted
            "recovery_rate_act":  round(dollars_recovered / denial["dollars_at_risk"], 4)
                                  if denial["dollars_at_risk"] > 0 else 0.0,  # what happened
        })

    return pd.DataFrame(rows)


def calibration_summary(appeal_outcomes_df):
    """
    Compares estimated recovery probability against actual appeal success rate
    by CARC code. This is the validation query — it shows your model is calibrated.

    Returns a summary DataFrame suitable for display in the forensics notebook.
    """
    summary = (
        appeal_outcomes_df
        .groupby("carc_code")
        .agg(
            total_appeals       = ("appeal_id",        "count"),
            successful_appeals  = ("appeal_successful", "sum"),
            total_at_risk       = ("dollars_at_risk",   "sum"),
            total_recovered     = ("dollars_recovered",  "sum"),
            avg_estimated_prob  = ("recovery_rate_est", "mean"),
            avg_actual_rate     = ("recovery_rate_act", "mean"),
            avg_days_to_resolve = ("days_to_resolve",   "mean"),
        )
        .reset_index()
    )

    summary["appeal_success_rate"] = (
        summary["successful_appeals"] / summary["total_appeals"]
    ).round(3)

    summary["calibration_error"] = (
        summary["avg_actual_rate"] - summary["avg_estimated_prob"]
    ).round(3)

    # Positive calibration_error = model underestimated recovery (conservative)
    # Negative calibration_error = model overestimated recovery (optimistic)

    return summary[[
        "carc_code",
        "total_appeals",
        "appeal_success_rate",
        "avg_estimated_prob",
        "calibration_error",
        "total_at_risk",
        "total_recovered",
        "avg_days_to_resolve",
    ]]