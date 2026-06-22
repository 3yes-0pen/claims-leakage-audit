"""
dashboard_5panel/app.py  —  Landing page / narrative overview
"""

import sys
from pathlib import Path

# Add repo root to path so utils/ and data/ are reachable
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from utils.data_loader import (
    load_waterfall,
    load_triage_queue,
    load_intervention_matrix,
)

st.set_page_config(
    page_title="Claims Leakage Audit Engine",
    page_icon="🏥",
    layout="wide",
)

# ── Load data for KPI cards ──────────────────────────────────────────────────
waterfall_df = load_waterfall()
triage_df    = load_triage_queue()
matrix_df    = load_intervention_matrix()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Claims Leakage Audit")
st.markdown(
    "**Every denied dollar has a birth certificate.** "
    "This dashboard traces it -- and answers specific questions related "
    "to what this data means."
)
st.divider()

# ── KPI Cards ────────────────────────────────────────────────────────────────
ncr            = waterfall_df["ncr_overall_pct"].iloc[0]
denial_dollars = abs(
    waterfall_df.loc[waterfall_df["stage_label"] == "Denials", "amount"].iloc[0]
)
active_claims      = len(triage_df)
total_recoverable  = matrix_df["dollars_recovered"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Collection Rate",          f"{ncr:.1f}%")
col2.metric("Denial Leakage",               f"${denial_dollars:,.0f}")
col3.metric("Active Claims in Window",      f"{active_claims:,}")
col4.metric("Recoverable via Intervention", f"${total_recoverable:,.0f}")

st.divider()

# ── Dashboard Map ─────────────────────────────────────────────────────────────
st.subheader("Dashboard Map")
st.caption("Each panel answers a distinct question for a distinct audience. Use the sidebar to navigate.")

st.markdown("""
| Panel | Primary Audience | The Question |
|---|---|---|
| **1 · Revenue Waterfall** | Executive, CFO | How much leaked? |
| **2 · Failure Node Heatmap** | RCM, Contracting | Who caused it? |
| **3 · Urgency Triage Queue** | Billing Ops, RCM | What do I work on today? |
| **4 · Denial Fingerprint** | Clinical Ops, ACO | What does this mean clinically? |
| **5 · Intervention Matrix** | QI, Clinical Ops, Executive | What to fix first? |
""")

st.divider()
st.caption(
    "Data: Synthea synthetic claims, processed through DuckDB  ·  "
    "Built with pandas, Plotly, Streamlit  ·  "
    "github.com/3yes-0pen/claims-leakage-audit"
)