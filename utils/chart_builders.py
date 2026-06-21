"""
utils/chart_builders.py

Shared Plotly figure builders for both dashboards.
Every function takes a pre-loaded DataFrame and returns a go.Figure
(or a filtered DataFrame for the triage panel).

Dashboard pages stay thin:
    from utils.chart_builders import build_waterfall
    fig = build_waterfall(df)
    st.plotly_chart(fig, use_container_width=True)
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── Shared Color Palettes ────────────────────────────────────────────────────
# Single source of truth — imported by both dashboard apps.
# Pulled from notebooks: PAYER_COLORS from NB07, SEGMENT_COLORS + carc_colors from NB06.

PAYER_COLORS = {
    "medi_cal_managed_care":  "#e63946",
    "commercial_ppo":         "#2a9d8f",
    "medicare_advantage":     "#457b9d",
    "dual_eligible_cobpayer": "#f4a261",
}

SEGMENT_COLORS = {
    "Oncology":           "#e63946",
    "Emergency Medicine": "#f4a261",
    "Behavioral Health":  "#8338ec",
    "Radiology":          "#457b9d",
    "Internal Medicine":  "#2a9d8f",
}

CARC_COLORS = {
    "CO-29": "#e63946",
    "CO-57": "#f4a261",
    "CO-97": "#2a9d8f",
    "CO-4":  "#457b9d",
    "CO-50": "#8338ec",
    "CO-22": "#e9c46a",
    "CO-16": "#06d6a0",
    "CO-B7": "#adb5bd",
}

INTERVENTION_COLORS = {
    "Auth Workflow (CO-57)":          "#e63946",
    "Charge Lag Process (CO-29)":     "#457b9d",
    "Coding Accuracy (CO-4)":         "#2a9d8f",
    "Credentialing Renewal (CO-B7)":  "#e9c46a",
}

# Quadrant thresholds for Intervention Matrix — match NB05 Cell 2 parameters
COMPLEXITY_THRESHOLD = 2.5
RECOVERY_THRESHOLD   = 150_000


# ── Panel 1: Revenue Leakage Waterfall ──────────────────────────────────────

def build_waterfall(df: pd.DataFrame) -> go.Figure:
    """
    Build the revenue leakage waterfall chart.

    Data: waterfall_summary.parquet
    Columns used: stage_label, stage_order, amount, measure_type

    The ncr_overall_pct column is a KPI value, not a bar —
    pull it in the dashboard page with df["ncr_overall_pct"].iloc[0].
    """
    df = df.sort_values("stage_order")

    fig = go.Figure(go.Waterfall(
        name="Revenue",
        orientation="v",
        measure=df["measure_type"].tolist(),
        x=df["stage_label"].tolist(),
        y=df["amount"].tolist(),
        text=[f"${abs(v):,.0f}" for v in df["amount"]],
        textposition="outside",
        connector={"line": {"color": "#6b7280", "dash": "dot", "width": 1}},
        increasing={"marker": {"color": "#06d6a0"}},   # appeal recovery
        decreasing={"marker": {"color": "#e63946"}},   # contractual adj, denials
        totals={"marker": {"color": "#457b9d"}},        # subtotal bars
    ))

    fig.update_layout(
        title=dict(
            text="Revenue Leakage Waterfall — Gross Billed to Final Net Position",
            font=dict(size=15, color="#1f2937"),
        ),
        yaxis=dict(tickformat="$,.0f", gridcolor="#f3f4f6"),
        xaxis=dict(tickfont=dict(size=11)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=520,
        showlegend=False,
        margin=dict(t=60, b=40, l=80, r=40),
    )

    return fig


# ── Panel 2: Failure Node × Payer / Provider Heatmap ────────────────────────

def build_heatmap(
    df: pd.DataFrame,
    index_col: str,
    title: str,
    colorscale: str = "YlOrRd",
) -> go.Figure:
    """
    Build a failure-node heatmap for either payer or provider dimension.

    Data: failure_node_payer_heatmap.parquet   → index_col="payer_id"
          failure_node_provider_heatmap.parquet → index_col="practice_name"
    """
    pivot = df.pivot_table(
        index=index_col,
        columns="upstream_failure_node",
        values="dollars_at_risk",
        aggfunc="sum",
    ).fillna(0)

    # Format column labels: prior_authorization → Prior Authorization
    col_labels = [c.replace("_", " ").title() for c in pivot.columns]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=col_labels,
        y=pivot.index.tolist(),
        colorscale=colorscale,
        text=[[f"${v:,.0f}" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont={"size": 9, "color": "white"},
        colorbar=dict(title="Denial $", tickformat="$,.0f"),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Failure Node: %{x}<br>"
            "Denial Dollars: %{text}<extra></extra>"
        ),
    ))

    # Auto-darken cell text for low values (light cells)
    # Plotly doesn't support conditional text color natively,
    # so white text + dark colorscale reads cleanly for most cells.

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1f2937")),
        xaxis=dict(tickangle=-30, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        margin=dict(t=60, b=80, l=160, r=40),
    )

    return fig


# ── Panel 3: Urgency Triage Queue ───────────────────────────────────────────

def filter_triage(
    df: pd.DataFrame,
    payer: str | None = None,
    carc_codes: list[str] | None = None,
    provider: str | None = None,
) -> pd.DataFrame:
    """
    Apply sidebar filters to the triage queue and return a display-ready DataFrame.

    The returned df is passed directly to st.dataframe().
    Sorting (priority_score DESC) is preserved from the parquet file.

    Dashboard page handles st.selectbox / st.multiselect widgets;
    this function just applies the filter logic in one place.
    """
    filtered = df.copy()

    if payer and payer != "All":
        filtered = filtered[filtered["payer_id"] == payer]

    if carc_codes:
        filtered = filtered[filtered["carc_code"].isin(carc_codes)]

    if provider and provider != "All":
        filtered = filtered[filtered["practice_name"] == provider]

    # Format columns for display
    display_cols = [
        "priority_score", "dollars_at_risk", "days_remaining_window",
        "practice_name", "payer_id", "carc_code",
        "upstream_failure_node", "recommended_action",
    ]
    out = filtered[display_cols].copy()

    out["priority_score"]     = out["priority_score"].round(1)
    out["dollars_at_risk"]    = out["dollars_at_risk"].apply(lambda v: f"${v:,.0f}")

    out = out.rename(columns={
        "priority_score":        "Priority Score",
        "dollars_at_risk":       "$ at Risk",
        "days_remaining_window": "Days Left",
        "practice_name":         "Provider",
        "payer_id":              "Payer",
        "carc_code":             "CARC",
        "upstream_failure_node": "Failure Node",
        "recommended_action":    "Action",
    })

    return out


# ── Panel 4: Denial Pattern Fingerprint by Specialty ────────────────────────

def build_fingerprint(df: pd.DataFrame) -> go.Figure:
    """
    Build the 100% stacked horizontal bar showing CARC composition by specialty.

    Data: denial_fingerprint.parquet
    Columns: patient_segment, carc_code, denial_count
    """
    pivot = df.pivot_table(
        index="patient_segment",
        columns="carc_code",
        values="denial_count",
        aggfunc="sum",
    ).fillna(0)

    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig = go.Figure()

    for carc in pivot_pct.columns:
        vals  = pivot_pct[carc].values
        color = CARC_COLORS.get(carc, "#cccccc")

        fig.add_trace(go.Bar(
            name=carc,
            y=pivot_pct.index.tolist(),
            x=vals,
            orientation="h",
            marker_color=color,
            text=[f"{v:.0f}%" if v > 8 else "" for v in vals],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=9),
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"CARC: {carc}<br>"
                "Share: %{x:.1f}%<extra></extra>"
            ),
        ))

    fig.update_layout(
        barmode="stack",
        title=dict(
            text="Denial Pattern Fingerprint by Specialty",
            font=dict(size=14, color="#1f2937"),
        ),
        xaxis=dict(
            title="% of Denials by CARC Code",
            ticksuffix="%",
            range=[0, 100],
            gridcolor="#f3f4f6",
        ),
        yaxis=dict(tickfont=dict(size=11)),
        legend=dict(title="CARC Code", orientation="v"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        margin=dict(t=60, b=60, l=140, r=40),
    )

    return fig


# ── Panel 5: Intervention Prioritization Matrix ──────────────────────────────

def build_intervention_matrix(
    df: pd.DataFrame,
    complexity_overrides: dict | None = None,
) -> go.Figure:
    """
    Build the effort-vs-return scatter plot (Intervention Matrix).

    Data: intervention_matrix.parquet
    Columns: intervention, provider, failure_node,
             denials_avoided, dollars_recovered, complexity, value_type

    complexity_overrides: dict of {intervention_name: slider_value}
        Passed from the dashboard page's st.slider widgets.
        Overrides the default complexity score from the parquet file.
        If None, uses stored default values.
    """
    plot_df = df.copy()

    if complexity_overrides:
        for name, val in complexity_overrides.items():
            plot_df.loc[plot_df["intervention"] == name, "complexity"] = val

    marker_symbols = {"Recovery": "circle", "Prevention": "triangle-up"}

    fig = go.Figure()

    for _, row in plot_df.iterrows():
        name   = row["intervention"]
        color  = INTERVENTION_COLORS.get(name, "#6b7280")
        symbol = marker_symbols.get(row.get("value_type", "Recovery"), "circle")
        size   = max(18, row["denials_avoided"] * 0.35)

        fig.add_trace(go.Scatter(
            x=[row["complexity"]],
            y=[row["dollars_recovered"]],
            mode="markers+text",
            marker=dict(
                size=size,
                color=color,
                symbol=symbol,
                line=dict(color="white", width=2),
                opacity=0.88,
            ),
            text=[f"  {name}<br>  ${row['dollars_recovered']:,.0f}"],
            textposition="middle right",
            textfont=dict(size=9, color="#374151"),
            name=name,
            showlegend=True,
            hovertemplate=(
                f"<b>{name}</b><br>"
                f"Provider: {row['provider']}<br>"
                "Complexity: %{x}<br>"
                "$ Impact: %{y:$,.0f}<br>"
                f"Denials avoided: {row['denials_avoided']:,}<extra></extra>"
            ),
        ))

    # Quadrant dividers
    fig.add_vline(
        x=COMPLEXITY_THRESHOLD,
        line_dash="dash", line_color="#9ca3af", opacity=0.6,
    )
    fig.add_hline(
        y=RECOVERY_THRESHOLD,
        line_dash="dash", line_color="#9ca3af", opacity=0.6,
    )

    # Quadrant labels (fixed to corners via paper coordinates)
    quadrant_labels = [
        dict(x=0.02, y=0.97, text="FUND FIRST",      xanchor="left",  yanchor="top"),
        dict(x=0.98, y=0.97, text="PLAN CAREFULLY",  xanchor="right", yanchor="top"),
        dict(x=0.02, y=0.03, text="QUICK WINS",      xanchor="left",  yanchor="bottom"),
        dict(x=0.98, y=0.03, text="DEPRIORITIZE",    xanchor="right", yanchor="bottom"),
    ]
    annotations = [
        dict(
            xref="paper", yref="paper", showarrow=False,
            font=dict(color="#9ca3af", size=9),
            **lbl,
        )
        for lbl in quadrant_labels
    ]

    fig.update_layout(
        title=dict(
            text="Intervention Prioritization Matrix",
            font=dict(size=14, color="#1f2937"),
        ),
        xaxis=dict(
            title="Implementation Complexity (1 = Low → 5 = High)",
            range=[0.5, 5.5],
            gridcolor="#f3f4f6",
            dtick=1,
        ),
        yaxis=dict(
            title="Expected Dollar Impact — Recovery or Prevention ($)",
            tickformat="$,.0f",
            gridcolor="#f3f4f6",
        ),
        annotations=annotations,
        legend=dict(title="Intervention"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=560,
        margin=dict(t=60, b=60, l=100, r=200),
    )

    return fig