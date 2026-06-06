PROVIDER_PERSONAS = {
    "internal_medicine_group": {
        "persona_type":             "slow_charge_capture",
        "specialty":                "Internal Medicine",
        "charge_entry_lag_mean":    14,    # avg days from DOS to claim submission
        "charge_entry_lag_std":     5,
        "timely_filing_miss_rate": 0.07,
        "credentialing_lapse_rate": 0.0,
        "eligibility_verify_rate":  0.85,  # 85% of encounters verify eligibility first
        "prior_auth_obtain_rate":   0.90,
        "coding_accuracy_rate":     0.92,
        "base_auth_required_rate":  0.0,
        "retroactive_auth_rate":    0.0,
    },
    "radiology_group": {
        "persona_type":             "prior_auth_miss",
        "specialty":                "Radiology",
        "charge_entry_lag_mean":    3,
        "charge_entry_lag_std":     1,
        "timely_filing_miss_rate":  0.0,
        "credentialing_lapse_rate": 0.0,
        "eligibility_verify_rate":  0.95,
        "prior_auth_obtain_rate":   0.68,  # scheduling staff misses auth frequently
        "coding_accuracy_rate":     0.95,
        "base_auth_required_rate":  0.65,
        "retroactive_auth_rate":    0.20,   # FIX: 20% of obtained auths come in after service
    },
    "emergency_group": {
        "persona_type":             "coding_errors",
        "specialty":                "Emergency Medicine",
        "charge_entry_lag_mean":    5,
        "charge_entry_lag_std":     2,
        "timely_filing_miss_rate":  0.0,
        "credentialing_lapse_rate": 0.0,
        "eligibility_verify_rate":  0.60,  # ER sees unverified patients constantly
        "prior_auth_obtain_rate":   0.85,
        "coding_accuracy_rate":     0.78,  # high coding error rate
        "base_auth_required_rate":  0.0,
        "retroactive_auth_rate":    0.0,
    },
    "behavioral_health_group": {
        "persona_type":             "credentialing_errors",
        "specialty":                "Behavioral Health",
        "charge_entry_lag_mean":    7,
        "charge_entry_lag_std":     3,
        "timely_filing_miss_rate":  0.0,
        "eligibility_verify_rate":  0.80,
        "prior_auth_obtain_rate":   0.88,
        "coding_accuracy_rate":     0.85,
        "credentialing_lapse_rate": 0.12,  # new field — % of providers with expired creds
        "base_auth_required_rate":  0.0,
        "retroactive_auth_rate":    0.0,
    },
    "oncology_group": {
        "persona_type":             "medical_necessity_denials",
        "specialty":                "Oncology",
        "charge_entry_lag_mean":    5,
        "charge_entry_lag_std":     2,
        "timely_filing_miss_rate":  0.0,
        "eligibility_verify_rate":  0.92,
        "prior_auth_obtain_rate":   0.75,  # chemo auth is complex, misses happen
        "coding_accuracy_rate":     0.90,
        "credentialing_lapse_rate": 0.0,
        "base_auth_required_rate":  0.70,   # FIX: most oncology procedures need auth
        "retroactive_auth_rate":    0.15,   # FIX: 15% of auths are retroactive
    },
}

PAYER_PERSONAS = {
    "medi_cal_managed_care": {
        "adjudication_lag_mean":        45,
        "timely_filing_limit_days":     90,
        "bundling_edit_rate":           0.25,
        "prior_auth_denial_rate":       0.35,
        "medical_necessity_denial_rate":0.08,
        "allowed_rate":                 0.72,  # pays 72% of billed
    },
    "commercial_ppo": {
        "adjudication_lag_mean":        20,
        "timely_filing_limit_days":     180,
        "bundling_edit_rate":           0.05,
        "prior_auth_denial_rate":       0.12,
        "medical_necessity_denial_rate":0.02,
        "allowed_rate":                 0.85,
    },
    "medicare_advantage": {
        "adjudication_lag_mean":        30,
        "timely_filing_limit_days":     365,
        "bundling_edit_rate":           0.15,
        "prior_auth_denial_rate":       0.20,
        "medical_necessity_denial_rate":0.06,
        "allowed_rate":                 0.80,
    },
    "dual_eligible_cobpayer": {
        "adjudication_lag_mean":        60,
        "timely_filing_limit_days":     90,
        "bundling_edit_rate":           0.10,
        "prior_auth_denial_rate":       0.15,
        "medical_necessity_denial_rate":0.04,
        "allowed_rate":                 0.70,
        "cob_denial_rate":              0.20,  # new field — COB sequencing failures
    },
}

PERSONA_TYPE_TO_KEY = {
    v["persona_type"]: k for k, v in PROVIDER_PERSONAS.items()
}