"""
dashboard_3panel/pages/1_Financial_Intelligence.py
Panel 1 — Financial Intelligence
Audience: Executive, CFO
Question: Where does billed revenue go before it becomes cash?
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from utils.data_loader import load_waterfall
from utils.chart_builders import build_waterfall

st.set_page_config(
    page_title="Financial Intelligence · Claims Leakage Audit",
    page_icon="💰",
    layout="wide",
)

# ── Load ─────────────────────────────────────────────────────────────────────
df = load_waterfall()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Financial Intelligence")
st.caption("Audience: Executive, CFO  ·  Question: Where does billed revenue go before it becomes cash?")
st.divider()

# ── KPI Cards ────────────────────────────────────────────────────────────────
ncr        = df["ncr_overall_pct"].iloc[0]
gross      = df.loc[df["stage_label"] == "Gross Billed",    "amount"].iloc[0]
denial_dol = abs(df.loc[df["stage_label"] == "Denials",     "amount"].iloc[0])
final_net  = df.loc[df["stage_label"] == "Final Net",       "amount"].iloc[0]
appeal_rec = df.loc[df["stage_label"] == "Appeal Recovery", "amount"].iloc[0]

leakage_pct = round(denial_dol / gross * 100, 1) if gross > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Collection Rate", f"{ncr:.1f}%",       help="Net cash collected / net revenue")
col2.metric("Gross Billed",        f"${gross:,.0f}")
col3.metric("Denial Leakage",      f"${denial_dol:,.0f}", delta=f"-{leakage_pct}% of gross", delta_color="inverse")
col4.metric("Appeal Recovery",     f"${appeal_rec:,.0f}", delta="recovered", delta_color="normal")

st.divider()

# ── Chart ────────────────────────────────────────────────────────────────────
fig = build_waterfall(df)
st.plotly_chart(fig, use_container_width=True)

# ── Context ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
**The executive read**

The gap between *Gross Billed* and *Final Net* is total revenue leakage.
The contractual adjustment is expected — it represents the difference between
billed charges and contracted rates, not a performance problem.

The denial bar is the performance problem. Every dollar there represents
a claim that should have been paid and wasn't — driven by authorization gaps,
coding errors, timely filing misses, and credentialing lapses.
Appeal recovery shows how much of that leakage was clawed back.
The spread between denials and appeal recovery is the permanent write-off exposure.
""")