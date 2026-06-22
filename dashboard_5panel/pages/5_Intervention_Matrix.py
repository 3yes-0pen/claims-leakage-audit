"""
dashboard_5panel/pages/5_Intervention_Matrix.py
Panel 5 — Intervention Prioritization Matrix
Audience: QI, Clinical Ops, Executive
Question: What do I fix first?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
from utils.data_loader import load_intervention_matrix
from utils.chart_builders import build_intervention_matrix

st.set_page_config(
    page_title="Intervention Matrix · Claims Leakage Audit",
    page_icon="🎯",
    layout="wide",
)

df = load_intervention_matrix()

st.title("Intervention Prioritization Matrix")
st.caption("Audience: QI, Clinical Ops, Executive  ·  Question: What do I fix first?")
st.markdown(
    "Upper-left quadrant = fund immediately. "
    "Use the sliders to adjust implementation complexity for your organization — "
    "the matrix updates in real time."
)
st.divider()

st.sidebar.header("Adjust Complexity")
st.sidebar.caption(
    "Default scores reflect typical implementation difficulty. "
    "Adjust based on your organization's capacity and existing infrastructure."
)

complexity_overrides = {}
for _, row in df.iterrows():
    name    = row["intervention"]
    default = int(row["complexity"])
    val = st.sidebar.slider(
        label=name, min_value=1, max_value=5, value=default,
        help=f"Default: {default}  ·  1 = Low effort, 5 = High effort",
    )
    complexity_overrides[name] = val

total_dollars    = df["dollars_recovered"].sum()
total_denials    = df["denials_avoided"].sum()
recovery_count   = (df["value_type"] == "Recovery").sum()
prevention_count = (df["value_type"] == "Prevention").sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Portfolio Impact",   f"${total_dollars:,.0f}")
col2.metric("Total Denials Avoided",    f"{total_denials:,}")
col3.metric("Recovery Interventions",   str(recovery_count),
            help="Reclaim dollars already denied")
col4.metric("Prevention Interventions", str(prevention_count),
            help="Avoid future denials before they occur")

st.divider()

fig = build_intervention_matrix(df, complexity_overrides=complexity_overrides)
st.plotly_chart(fig, use_container_width=True)

# ── How this matrix was built ─────────────────────────────────────────────────
st.divider()
st.subheader("How this matrix was built")
st.markdown("""
**This is a simulation model, not a machine learning prediction.**

Each intervention is evaluated on two dimensions:

**Dollar impact (Y-axis)** — computed by estimating what would happen if the denial rate
for each failure type dropped from its current observed rate to a realistic target rate.
The formula is: `(current_rate − target_rate) × denial_volume × avg_claim_value`.
Target rates are achievable benchmarks drawn from the denial pattern analysis in the
preceding notebooks — not best-case scenarios.

**Implementation complexity (X-axis)** — expert-assigned scores (1–5) reflecting how
difficult each intervention typically is to execute:

| Score | What it means | Timeline |
|---|---|---|
| 1–2 | Calendar alert, checklist change, or policy memo | Days to weeks |
| 3 | EMR workflow change or staff education program | Weeks to months |
| 4–5 | Contracting renegotiation, CDI program buildout, or IT integration | Quarters |

Use the sidebar sliders to override these scores for your organization's specific context.
The quadrant placement and sort order update in real time.

**Recovery vs. Prevention** — Recovery interventions reclaim dollars already denied.
Prevention interventions stop denials before they occur. CO-29 (timely filing) has
near-zero recovery probability once the window closes — its entire value is preventive.
The bubble shape (circle vs. triangle) reflects this distinction.
""")

# ── Summary Table ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Intervention Summary")

summary_display = df[[
    "intervention", "provider", "failure_node",
    "denials_avoided", "dollars_recovered", "value_type"
]].copy()
summary_display["complexity"]        = summary_display["intervention"].map(complexity_overrides)
summary_display["dollars_recovered"] = summary_display["dollars_recovered"].apply(lambda v: f"${v:,.0f}")
summary_display["denials_avoided"]   = summary_display["denials_avoided"].apply(lambda v: f"{v:,}")

summary_display = summary_display.rename(columns={
    "intervention":     "Intervention",
    "provider":         "Provider",
    "failure_node":     "Failure Node",
    "denials_avoided":  "Denials Avoided",
    "dollars_recovered":"$ Impact",
    "value_type":       "Type",
    "complexity":       "Complexity (adjusted)",
})

st.dataframe(summary_display, use_container_width=True, hide_index=True)