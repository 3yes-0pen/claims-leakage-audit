"""
dashboard_5panel/pages/4_Denial_Fingerprint.py
Panel 4 — Denial Pattern Fingerprint by Specialty
Audience: Clinical Ops, ACO
Question: What does it mean clinically?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from utils.data_loader import load_fingerprint, load_specialty_interpretations
from utils.chart_builders import build_fingerprint

st.set_page_config(
    page_title="Denial Fingerprint · Claims Leakage Audit",
    page_icon="🧬",
    layout="wide",
)

df    = load_fingerprint()
notes = load_specialty_interpretations()

st.title("Denial Pattern Fingerprint by Specialty")
st.caption("Audience: Clinical Ops, ACO  ·  Question: What does it mean clinically?")
st.markdown(
    "Each bar shows the CARC composition of denials for that specialty — "
    "not volume, but *mix*. A spike in one CARC code within a specialty "
    "is a clinical process signal, not just a billing problem."
)
st.divider()

fig = build_fingerprint(df)
st.plotly_chart(fig, use_container_width=True)

# ── CARC Code Reference ───────────────────────────────────────────────────────
st.divider()
st.subheader("CARC Code Reference")
st.caption("Click any code to see its definition.")

carc_definitions = {
    "CO-4":  ("Inconsistent Modifier",
               "The service or procedure code is inconsistent with the modifier submitted — "
               "typically a mismatch between what was billed and how the service was coded. "
               "Usually a coding or documentation accuracy issue."),
    "CO-16": ("Missing Information",
               "The claim lacks information needed for adjudication — incomplete documentation "
               "or missing required fields. Often resolved by resubmitting with the correct "
               "supporting data."),
    "CO-22": ("COB — Other Payer Responsible",
               "This care may be covered by another payer per coordination of benefits. "
               "A secondary insurer issue — requires correct primary/secondary payer sequencing "
               "on the claim."),
    "CO-29": ("Timely Filing Expired",
               "The time limit for filing has expired — the charge was submitted outside the "
               "payer's filing window. Once the window closes, recovery probability is near zero. "
               "Prevention is the only viable intervention."),
    "CO-50": ("Not Medically Necessary",
               "These services are non-covered because they were not deemed medically necessary "
               "by the payer. Often requires clinical documentation, a letter of medical necessity, "
               "or an appeal with supporting clinical evidence."),
    "CO-57": ("Prior Authorization Missing",
               "Prior authorization or precertification was absent — the service was delivered "
               "without required advance approval from the payer. The intervention belongs at "
               "the point of order entry, not the billing team."),
    "CO-97": ("Bundled Into Another Service",
               "The benefit for this service is included in the payment for another service "
               "already adjudicated. A coding bundling issue — the procedure was billed separately "
               "when it should have been included in a global code."),
    "CO-B7": ("Provider Not Credentialed",
               "This provider was not certified or eligible to be paid for this procedure on "
               "this date of service. A network stability and credentialing maintenance issue — "
               "common in high-turnover specialties."),
}

for code, (short_name, definition) in carc_definitions.items():
    with st.expander(f"**{code}** — {short_name}"):
        st.markdown(definition)

# ── Clinical Interpretation ───────────────────────────────────────────────────
st.divider()
st.subheader("Clinical Interpretation by Specialty")
st.markdown(
    "The denial pattern fingerprint becomes actionable when each specialty's "
    "CARC concentration is interpreted through a clinical lens — not a billing lens."
)

for _, row in notes.iterrows():
    with st.expander(f"**{row['specialty']}**"):
        st.markdown(row["clinical_interpretation"])

st.divider()
st.markdown("""
**Why this chart matters**

Standard RCM dashboards show denial *volume* — total counts or dollars by CARC.
This chart shows denial *composition* — what share of each specialty's denials
come from each failure type. That distinction separates billing intelligence from
clinical intelligence.

A CO-57 spike in Oncology isn't a billing team failure — it's an order-entry workflow
that doesn't flag authorization requirements at the point the imaging order is placed.
The intervention belongs upstream of the billing team entirely.
""")