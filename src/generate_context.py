import uuid
import numpy as np
import pandas as pd
from src.personas import PROVIDER_PERSONAS
from src.prior_auth_rules import auth_required  # replaces hardcoded CPT set


def build_encounter_context(claim_header_df, claim_line_df, providers_df):
    rows = []

    for _, claim in claim_header_df.iterrows():
        # ── Provider + persona lookup ─────────────────────────────────────
        provider = providers_df[
            providers_df["provider_id"] == claim["provider_id"]
        ].iloc[0]

        matched_key = next(
            (k for k in PROVIDER_PERSONAS
             if PROVIDER_PERSONAS[k]["persona_type"] == provider["persona_type"]),
            None
        )
        if matched_key is None:
            raise ValueError(
                f"No persona found for persona_type: '{provider['persona_type']}'. "
                f"Check that personas.py contains a matching persona_type value."
            )
        persona  = PROVIDER_PERSONAS[matched_key]
        payer_id = claim["payer_id"]

        # ── CPT codes for this claim ──────────────────────────────────────
        lines = claim_line_df[claim_line_df["claim_id"] == claim["claim_id"]]
        cpts  = set(lines["cpt_code"].tolist())

        # FIXED: payer-aware auth check — replaces hardcoded PRIOR_AUTH_REQUIRED_CPTS
        # any CPT on this claim that requires auth with this payer triggers the flag
        prior_auth_required = any(auth_required(cpt, payer_id) for cpt in cpts)
        if not prior_auth_required:
            prior_auth_required = (
                np.random.random() < persona.get("base_auth_required_rate", 0.0)
            )

        # ── Auth obtained logic ───────────────────────────────────────────
        if prior_auth_required:
            auth_obtained = np.random.random() < persona["prior_auth_obtain_rate"]

            # ADDED: auth_request_date — only exists when auth was required and obtained
            # models realistic behavior: auth requested a few days before DOS
            if auth_obtained:
                retro_rate = persona.get("retroactive_auth_rate", 0.0)
                if np.random.random() < retro_rate:
                    days_after = int(np.random.uniform(1, 14))
                    auth_request_date = (
                        pd.Timestamp(claim["date_of_service"]) + pd.Timedelta(days=days_after)
                        ).date()
                else:
                    days_before = int(np.random.uniform(1, 7))
                    auth_request_date = (
                        pd.Timestamp(claim["date_of_service"]) - pd.Timedelta(days=days_before)
                    ).date()
            else:
                auth_request_date = None  # auth required but never requested
        else:
            auth_obtained     = None
            auth_request_date = None

        # ── Charge entry lag ──────────────────────────────────────────────
        # Derive from actual submission_date — eliminates the dual independent-draw inconsistency
        lag = (
            pd.Timestamp(claim["submission_date"]) - pd.Timestamp(claim["date_of_service"])
            ).days

        # ADDED: credentialing_lapse — computed from persona, passed through to
        # generate_remittance so CO-B7 denials can fire without touching payer persona
        credentialing_lapsed = (
            np.random.random() < persona.get("credentialing_lapse_rate", 0.0)
        )

        rows.append({
            "encounter_id":              str(uuid.uuid4()),
            "claim_id":                  claim["claim_id"],
            "patient_id":                claim["patient_id"],
            "provider_id":               claim["provider_id"],
            "date_of_service":           claim["date_of_service"],
            "eligibility_verified_flag": np.random.random() < persona["eligibility_verify_rate"],
            "prior_auth_required":       prior_auth_required,
            "prior_auth_obtained":       auth_obtained,
            "auth_request_date":         auth_request_date,   # ADDED
            "charge_entry_lag_days":     lag,
            "coding_accuracy_flag":      np.random.random() < persona["coding_accuracy_rate"],
            "credentialing_lapsed":      credentialing_lapsed,  # ADDED — feeds CO-B7 logic
        })

    return pd.DataFrame(rows)