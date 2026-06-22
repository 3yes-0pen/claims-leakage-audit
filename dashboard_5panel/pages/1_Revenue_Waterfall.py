"""
dashboard_5panel/pages/1_Revenue_Waterfall.py
Panel 1 — Revenue Leakage Waterfall
Audience: Executive, CFO
Question: How much leaked?
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from utils.data_loader import load_waterfall
from utils.chart_builders import build_waterfall

st.set_page_config(
    page_title="Revenue Waterfall · Claims Leakage Audit",
    page_icon="💧",
    layout="wide",
)

# ── Load ─────────────────────────────────────────────────────────────────────
df = load_waterfall()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Revenue Leakage Waterfall")
st.caption("Audience: Executive, CFO  ·  Question: How much leaked?")
st.divider()

# ── KPI Card ─────────────────────────────────────────────────────────────────
ncr          = df["ncr_overall_pct"].iloc[0]
gross        = df.loc[df["stage_label"] == "Gross Billed",    "amount"].iloc[0]
denial_dol   = abs(df.loc[df["stage_label"] == "Denials",     "amount"].iloc[0])
final_net    = df.loc[df["stage_label"] == "Final Net",       "amount"].iloc[0]
appeal_rec   = df.loc[df["stage_label"] == "Appeal Recovery", "amount"].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Collection Rate",    f"{ncr:.1f}%",          help="Net cash collected / net revenue")
col2.metric("Gross Billed",           f"${gross:,.0f}")
col3.metric("Denial Leakage",         f"${denial_dol:,.0f}",  help="Unexpected — excludes CO-45 contractual adjustments")
col4.metric("Appeal Recovery",        f"${appeal_rec:,.0f}",  help="Dollars recaptured through successful appeals")

st.divider()

# ── Chart ────────────────────────────────────────────────────────────────────
fig = build_waterfall(df)
st.plotly_chart(fig, use_container_width=True)

# ── Context ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
**How to read this chart**

- **Green bars** (Gross Billed, Final Net) — positive totals.
- **Red bars** (Contractual Adj., Denials, Patient Resp.) — reductions from the prior total.
- **Blue bars** (Net Revenue, Net Collected) — running subtotals.
- The gap between *Gross Billed* and *Final Net* is the total revenue leakage. 
  The gap between *Net Revenue* and *Net Collected* isolates denial and patient responsibility leakage — 
  the portion that is operationally addressable.

**Contractual Adjustment vs. Denials**  
Contractual adjustments (CO-45) are expected write-downs to contracted rates — not leakage.  
Denials are unexpected losses from billing, authorization, coding, and credentialing failures — 
this is where the audit engine focuses.
""")