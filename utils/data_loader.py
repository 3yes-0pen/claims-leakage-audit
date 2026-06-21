"""
utils/data_loader.py

Cached data loading functions for both dashboards.
Each function reads one parquet file and caches it with @st.cache_data —
the file loads once per session, then every subsequent call returns
the cached copy without touching disk again.

Usage in any dashboard page:
    from utils.data_loader import load_waterfall, load_triage_queue
    df = load_waterfall()
"""

from pathlib import Path
import pandas as pd
import streamlit as st

# Resolve data/ directory relative to this file's location.
# utils/data_loader.py → parent = utils/ → parent = repo root → / "data"
# This works whether the app is run locally or on Streamlit Community Cloud.
DATA_DIR = Path(__file__).parent.parent / "data"


# ── Panel 1 ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_waterfall() -> pd.DataFrame:
    """
    Revenue Leakage Waterfall — 8 rows, one per waterfall stage.
    Columns: stage_label, stage_order, amount, measure_type, ncr_overall_pct

    Pull KPI card value with: df["ncr_overall_pct"].iloc[0]
    """
    return pd.read_parquet(DATA_DIR / "waterfall_summary.parquet")


# ── Panel 2 ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_heatmap_payer() -> pd.DataFrame:
    """
    Failure Node × Payer Heatmap.
    Columns: payer_id, upstream_failure_node, denial_count, dollars_at_risk
    """
    return pd.read_parquet(DATA_DIR / "failure_node_payer_heatmap.parquet")


@st.cache_data
def load_heatmap_provider() -> pd.DataFrame:
    """
    Failure Node × Provider Heatmap.
    Columns: practice_name, persona_type, upstream_failure_node, denial_count, dollars_at_risk
    """
    return pd.read_parquet(DATA_DIR / "failure_node_provider_heatmap.parquet")


# ── Panel 3 ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_triage_queue() -> pd.DataFrame:
    """
    Urgency Triage Queue — claim-line grain, active appeal window only.
    Columns: denial_id, claim_id, practice_name, payer_id, date_of_service,
             carc_code, denial_category, upstream_failure_node,
             days_remaining_window, dollars_at_risk, recovery_probability,
             priority_score, recommended_action
    Pre-sorted by priority_score DESC.
    """
    return pd.read_parquet(DATA_DIR / "urgency_triage_queue.parquet")


# ── Panel 4 ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_fingerprint() -> pd.DataFrame:
    """
    Denial Pattern Fingerprint — CARC composition by specialty.
    Columns: patient_segment, carc_code, denial_count
    """
    return pd.read_parquet(DATA_DIR / "denial_fingerprint.parquet")


@st.cache_data
def load_specialty_interpretations() -> pd.DataFrame:
    """
    Authored clinical interpretation text per specialty.
    Columns: specialty, clinical_interpretation
    Merge with fingerprint df on specialty == patient_segment for the annotation panel.
    """
    return pd.read_parquet(DATA_DIR / "specialty_interpretations.parquet")


# ── Panel 5 ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_intervention_matrix() -> pd.DataFrame:
    """
    Intervention Prioritization Matrix — one row per intervention.
    Columns: intervention, provider, failure_node,
             denials_avoided, dollars_recovered, complexity, value_type

    complexity stores the DEFAULT value only.
    Dashboard sliders override it at runtime via build_intervention_matrix(df, overrides).
    """
    return pd.read_parquet(DATA_DIR / "intervention_matrix.parquet")