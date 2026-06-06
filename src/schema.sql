CREATE TABLE IF NOT EXISTS provider (
    provider_id          VARCHAR PRIMARY KEY,
    npi                  VARCHAR,
    specialty            VARCHAR,
    practice_name        VARCHAR,
    network_status       VARCHAR,
    persona_type         VARCHAR
);

CREATE TABLE IF NOT EXISTS member_eligibility (
    member_id            VARCHAR NOT NULL,
    payer_id             VARCHAR NOT NULL,
    plan_type            VARCHAR,
    coverage_start_date  DATE,
    coverage_end_date    DATE,
    is_active            BOOLEAN,
    copay_amount         DECIMAL(6,2),
    deductible_annual    DECIMAL(8,2)
);

CREATE TABLE IF NOT EXISTS claim_header (
    claim_id             VARCHAR PRIMARY KEY,
    patient_id           VARCHAR NOT NULL,
    provider_id          VARCHAR NOT NULL,
    payer_id             VARCHAR NOT NULL,
    date_of_service      DATE NOT NULL,
    submission_date      DATE NOT NULL,
    claim_type           VARCHAR,
    place_of_service     VARCHAR,
    billed_amount        DECIMAL(10,2),
    claim_status         VARCHAR
);

CREATE TABLE IF NOT EXISTS claim_line (
    claim_line_id        VARCHAR PRIMARY KEY,
    claim_id             VARCHAR NOT NULL,
    line_number          INTEGER NOT NULL,
    cpt_code             VARCHAR NOT NULL,
    icd10_primary        VARCHAR NOT NULL,
    units                INTEGER DEFAULT 1,
    billed_amount        DECIMAL(10,2),
    line_status          VARCHAR
);

CREATE TABLE IF NOT EXISTS remittance_835 (
    remittance_id            VARCHAR PRIMARY KEY,
    claim_id                 VARCHAR NOT NULL,
    claim_line_id            VARCHAR NOT NULL,
    adjudication_date        DATE NOT NULL,
    allowed_amount           DECIMAL(10,2),
    paid_amount              DECIMAL(10,2),
    patient_responsibility   DECIMAL(10,2),
    adjustment_amount        DECIMAL(10,2),
    carc_code                VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS encounter_context (
    encounter_id                VARCHAR PRIMARY KEY,
    claim_id                    VARCHAR NOT NULL,
    patient_id                  VARCHAR NOT NULL,
    provider_id                 VARCHAR NOT NULL,
    date_of_service             DATE NOT NULL,
    eligibility_verified_flag   BOOLEAN,
    credentialing_lapsed        BOOLEAN, 
    prior_auth_required         BOOLEAN,
    prior_auth_obtained         BOOLEAN,
    auth_request_date           DATE,
    charge_entry_lag_days       INTEGER,
    coding_accuracy_flag        BOOLEAN
);

CREATE TABLE IF NOT EXISTS denial_forensics (
    denial_id                VARCHAR PRIMARY KEY,
    claim_line_id            VARCHAR NOT NULL,
    carc_code                VARCHAR NOT NULL,
    denial_category          VARCHAR,
    upstream_failure_node    VARCHAR,
    preventability_flag      BOOLEAN,
    recovery_probability     DECIMAL(3,2),
    days_remaining_window    INTEGER,
    dollars_at_risk          DECIMAL(10,2),
    recommended_action       VARCHAR,
    priority_score           DECIMAL(10,4)
);

CREATE TABLE IF NOT EXISTS appeal_outcomes (
    appeal_id            VARCHAR PRIMARY KEY,
    denial_id            VARCHAR NOT NULL,
    claim_line_id        VARCHAR NOT NULL,
    carc_code            VARCHAR NOT NULL,
    appeal_successful    BOOLEAN,
    outcome_status       VARCHAR,
    dollars_at_risk      DECIMAL(10,2),
    dollars_recovered    DECIMAL(10,2),
    days_to_resolve      INTEGER,
    recovery_rate_est    DECIMAL(5,4),
    recovery_rate_act    DECIMAL(5,4)
);