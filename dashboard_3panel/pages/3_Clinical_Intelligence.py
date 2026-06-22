"""
dashboard_3panel/pages/3_Clinical_Intelligence.py
Panel 3 — Clinical Intelligence & Strategic Action
Audience: Clinical Ops, ACO
Question: What does the denial pattern mean clinically, and what gets fixed first?
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from utils.data_loader import load_fingerprint, load_specialty_interpretations
from utils.chart_builders import build_fingerprint

st.set_page_config(
    page_title="Clinical Intelligence · Claims Leakage Audit",
    page_icon="🧬",
    layout="wide",
)

# ── Load ─────────────────────────────────────────────────────────────────────
df    = load_fingerprint()
notes = load_specialty_interpretations()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Clinical Intelligence & Strategic Action")
st.caption("Audience: Clinical Ops, ACO  ·  Question: What does the denial pattern mean clinically?")
st.markdown(
    "The denial fingerprint shows CARC *composition* by specialty — not volume, but mix. "
    "A CARC spike in one specialty is a clinical process signal. "
    "The interpretation panel below translates each pattern into a strategic action."
)
st.divider()

# ── KPI Cards ────────────────────────────────────────────────────────────────
total_denials   = df["denial_count"].sum()
unique_carcs    = df["carc_code"].nunique()
unique_segs     = df["patient_segment"].nunique()
dominant_carc   = df.groupby("carc_code")["denial_count"].sum().idxmax()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Denial Lines",     f"{total_denials:,}")
col2.metric("Distinct CARC Codes",    str(unique_carcs))
col3.metric("Specialty Segments",     str(unique_segs))
col4.metric("Most Common CARC",       dominant_carc)

st.divider()

# ── Chart ────────────────────────────────────────────────────────────────────
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

# ── Clinical Interpretation + Strategic Action ────────────────────────────────
st.divider()
st.subheader("Clinical Interpretation & Strategic Action")
st.markdown(
    "Each specialty's denial fingerprint points to a specific upstream process gap. "
    "The fix belongs at the clinical workflow level, not the billing team."
)

for _, row in notes.iterrows():
    with st.expander(f"**{row['specialty']}**"):
        st.markdown(row["clinical_interpretation"])

# ── Context ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
**Why denial pattern composition matters more than denial volume**

High denial *volume* in a specialty could simply reflect high claim volume.
High denial *concentration* in one CARC code within a specialty is a signal —
it means a specific, repeatable failure is happening in that clinical workflow.

Standard RCM tools surface volume. This panel surfaces pattern.
That distinction is what separates a billing report from a clinical operations insight.
""")