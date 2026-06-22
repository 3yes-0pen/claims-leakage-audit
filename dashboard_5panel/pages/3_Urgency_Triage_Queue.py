"""
dashboard_5panel/pages/3_Urgency_Triage_Queue.py
Panel 3 — Urgency Triage Queue
Audience: Billing Ops, RCM
Question: What do I work today?
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from utils.data_loader import load_triage_queue
from utils.chart_builders import filter_triage

st.set_page_config(
    page_title="Urgency Triage Queue · Claims Leakage Audit",
    page_icon="🚨",
    layout="wide",
)

# ── Load ─────────────────────────────────────────────────────────────────────
df = load_triage_queue()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Urgency Triage Queue")
st.caption("Audience: Billing Ops, RCM  ·  Question: What do I work today?")
st.markdown(
    "Active denials sorted by priority score — a composite of dollars at risk, "
    "recovery probability, and days remaining in the appeal window. "
    "Work the top of this list first."
)
st.divider()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filter Queue")

payer_options    = ["All"] + sorted(df["payer_id"].unique().tolist())
provider_options = ["All"] + sorted(df["practice_name"].unique().tolist())
carc_options     = sorted(df["carc_code"].unique().tolist())

selected_payer    = st.sidebar.selectbox("Payer",     payer_options)
selected_provider = st.sidebar.selectbox("Provider",  provider_options)
selected_carcs    = st.sidebar.multiselect("CARC Code", carc_options)

# ── Apply Filters ────────────────────────────────────────────────────────────
display_df = filter_triage(
    df,
    payer=selected_payer,
    carc_codes=selected_carcs if selected_carcs else None,
    provider=selected_provider,
)

# ── KPI Cards (update with filter) ───────────────────────────────────────────
# Re-filter on raw df for numeric metrics before display formatting
raw_filtered = df.copy()
if selected_payer != "All":
    raw_filtered = raw_filtered[raw_filtered["payer_id"] == selected_payer]
if selected_carcs:
    raw_filtered = raw_filtered[raw_filtered["carc_code"].isin(selected_carcs)]
if selected_provider != "All":
    raw_filtered = raw_filtered[raw_filtered["practice_name"] == selected_provider]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Claims in View",        f"{len(raw_filtered):,}")
col2.metric("Total $ at Risk",       f"${raw_filtered['dollars_at_risk'].sum():,.0f}")
col3.metric("Avg Days Remaining",    f"{raw_filtered['days_remaining_window'].mean():.0f}")
col4.metric("Avg Priority Score",    f"{raw_filtered['priority_score'].mean():.1f}")

st.divider()

# ── Triage Table ─────────────────────────────────────────────────────────────
st.subheader(f"Work Queue — {len(display_df):,} claims")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Priority Score": st.column_config.NumberColumn(format="%.1f"),
        "Days Left":      st.column_config.NumberColumn(help="Days remaining in appeal window"),
        "Action":         st.column_config.TextColumn(help="Recommended next action"),
    },
)

# ── Context ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
**Priority Score formula**

`priority_score = dollars_at_risk × recovery_probability × urgency_multiplier`

where `urgency_multiplier` increases as the appeal window closes — 
claims with fewer days remaining are weighted higher than equivalent-dollar claims with more time.
A claim with 10 days left scores higher than the same claim with 90 days left.

Claims with `days_remaining_window = 0` are excluded — their appeal window has closed.
""")