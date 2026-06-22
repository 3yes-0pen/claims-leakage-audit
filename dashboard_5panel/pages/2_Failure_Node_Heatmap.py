"""
dashboard_5panel/pages/2_Failure_Node_Heatmap.py
Panel 2 — Failure Node × Payer / Provider Heatmap
Audience: RCM, Contracting
Question: Who caused it?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from utils.data_loader import load_heatmap_payer, load_heatmap_provider
from utils.chart_builders import build_heatmap

st.set_page_config(
    page_title="Failure Node Heatmap · Claims Leakage Audit",
    page_icon="🔥",
    layout="wide",
)

payer_df    = load_heatmap_payer()
provider_df = load_heatmap_provider()

st.title("Failure Node Heatmap")
st.caption("Audience: RCM, Contracting  ·  Question: Who caused it?")
st.markdown(
    "Each cell shows total denial dollars at the intersection of a failure type "
    "and a payer or provider. Darker = more leakage. The hot cell tells you where to focus."
)
st.divider()

total_at_risk    = payer_df["dollars_at_risk"].sum()
top_payer        = payer_df.groupby("payer_id")["dollars_at_risk"].sum().idxmax()
top_provider     = provider_df.groupby("practice_name")["dollars_at_risk"].sum().idxmax()
top_node         = payer_df.groupby("upstream_failure_node")["dollars_at_risk"].sum().idxmax()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Denial Dollars",  f"${total_at_risk:,.0f}")
col2.metric("Highest-Risk Payer",    top_payer.replace("_", " ").title())
col3.metric("Highest-Risk Provider", top_provider)
col4.metric("Highest-Risk Node",     top_node.replace("_", " ").title())

st.divider()

tab_payer, tab_provider = st.tabs(["Payer × Failure Node", "Provider × Failure Node"])

with tab_payer:
    st.markdown(
        "**Is this a payer problem?** "
        "A single payer concentrated across multiple failure nodes signals "
        "a contracting or appeals strategy conversation, not a process fix."
    )
    fig_payer = build_heatmap(
        payer_df, index_col="payer_id",
        title="Failure Node × Payer — Denial Dollars at Risk",
        colorscale="Blues",
    )
    st.plotly_chart(fig_payer, use_container_width=True)

with tab_provider:
    st.markdown(
        "**Or a provider problem?** "
        "A provider concentrated in one failure node points to a specific "
        "process gap — one intervention, one conversation, one fix."
    )
    fig_provider = build_heatmap(
        provider_df, index_col="practice_name",
        title="Failure Node × Provider — Denial Dollars at Risk",
        colorscale="YlOrRd",
    )
    st.plotly_chart(fig_provider, use_container_width=True)

st.divider()
st.markdown("""
**Failure node definitions**

| Node | What it represents |
|---|---|
| Prior Authorization | Auth not obtained or obtained retroactively before service |
| Charge Capture | Charge entry lag exceeding the payer's timely filing window |
| Coding | Diagnosis or procedure coding errors generating CO-4 denials |
| Credentialing | Provider credential lapses generating CO-B7 denials |
""")