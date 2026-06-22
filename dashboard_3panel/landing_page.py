"""
dashboard_3panel/landing_page.py  —  Executive summary landing page
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from utils.data_loader import (
    load_waterfall,
    load_heatmap_payer,
    load_fingerprint,
)

st.set_page_config(
    page_title="Claims Leakage Audit — Executive View",
    page_icon="📊",
    layout="wide",
)

# ── Load data for KPI cards ──────────────────────────────────────────────────
waterfall_df = load_waterfall()
heatmap_df   = load_heatmap_payer()
fp_df        = load_fingerprint()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Claims Leakage Audit")
st.markdown(
    "**A strategic view of revenue integrity across three lenses: "
    "financial performance, operational failure, and clinical signal.** "
    "Each panel is designed for a different leadership conversation."
)
st.divider()

# ── KPI Cards ────────────────────────────────────────────────────────────────
ncr          = waterfall_df["ncr_overall_pct"].iloc[0]
denial_dol   = abs(waterfall_df.loc[waterfall_df["stage_label"] == "Denials", "amount"].iloc[0])
appeal_rec   = waterfall_df.loc[waterfall_df["stage_label"] == "Appeal Recovery", "amount"].iloc[0]
top_payer    = heatmap_df.groupby("payer_id")["dollars_at_risk"].sum().idxmax()
top_node     = heatmap_df.groupby("upstream_failure_node")["dollars_at_risk"].sum().idxmax()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Collection Rate",   f"{ncr:.1f}%")
col2.metric("Denial Leakage",        f"${denial_dol:,.0f}")
col3.metric("Appeal Recovery",       f"${appeal_rec:,.0f}")
col4.metric("Highest-Risk Payer",    top_payer.replace("_", " ").title())

st.divider()

# ── Dashboard Map ─────────────────────────────────────────────────────────────
st.subheader("Dashboard Map")
st.caption("Three lenses, three leadership conversations. Use the sidebar to navigate.")

st.markdown("""
| Panel | Primary Audience | The Question |
|---|---|---|
| **1 · Financial Intelligence** | Executive, CFO | Where does billed revenue go before it becomes cash? |
| **2 · Operational Investigation** | RCM, Contracting | Which payers and providers are driving leakage? |
| **3 · Clinical Intelligence** | Clinical Ops, ACO | What does the denial pattern mean clinically? |
""")

st.divider()
st.caption(
    "Data: Synthea synthetic claims, processed through DuckDB  ·  "
    "Built with pandas, Plotly, Streamlit  ·  "
    "github.com/3yes-0pen/claims-leakage-audit"
)