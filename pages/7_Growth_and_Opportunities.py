import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
import plotly.express as px

from src import storage
from src.analysis import summaries

st.set_page_config(page_title="Growth & Opportunities", layout="wide")
st.title("Growth & Opportunities")
st.warning(
    "Two heuristics live on this page, neither of them a rigorous model: growth is a **naive linear "
    "trend** over a small, curated dataset (read direction, not precision — see the Trends & "
    "Industries forecast for the same caveat), and the opportunity finder is a **simple scoring "
    "heuristic** (a department that scores well elsewhere and is barely represented in an industry "
    "today), not a market-sizing study. Use both to prioritize where to look next, not as a plan to "
    "commit budget against.",
    icon="⚠️",
)

df = storage.load_use_cases()
cs = storage.load_case_studies()

if df.empty:
    st.warning("No data yet. Run `python -m scripts.seed_db` or add entries via the Data Collection page.")
    st.stop()

DIMENSION_CONFIG = {
    "Category": dict(column="category", explode=False),
    "Industry": dict(column="target_industries", explode=True),
    "Department": dict(column="target_departments", explode=True),
}
dimension = st.radio("View by", list(DIMENSION_CONFIG.keys()), index=1, horizontal=True)
cfg = DIMENSION_CONFIG[dimension]
group_col = cfg["column"]

_, growth_summary = summaries.growth_forecast(df, group_col, explode=cfg["explode"])
maturity_df = summaries.maturity_readiness(df, group_col, explode=cfg["explode"])
merged = growth_summary.merge(maturity_df[[group_col, "maturity_readiness_pct"]], on=group_col, how="left")
merged["history_status"] = merged["insufficient_history"].map({True: "New / insufficient history", False: "Established trend"})

st.divider()
st.header("Value vs. growth vs. maturity")
st.caption(
    "Every point is one " + dimension.lower() + ". X = growth momentum (share of its use cases that "
    "are brand new), Y = average business value score, bubble size = how many use cases exist today, "
    "color = how much of it has reached mainstream/enterprise-standard maturity. Dotted lines mark the "
    "median across established trends (new/thin-history points are shown but excluded from the median "
    "so a couple of noisy debutants can't drag it around)."
)

fig = px.scatter(
    merged, x="recent_share", y="avg_business_value_score",
    size="total_count", color="maturity_readiness_pct",
    symbol="history_status",
    color_continuous_scale="Viridis",
    hover_name=group_col,
    hover_data={
        "total_count": True, "years_of_history": True,
        "recent_share": ":.0%", "maturity_readiness_pct": ":.0%",
        "history_status": False,
    },
    labels={
        "recent_share": "Growth (recent share)",
        "avg_business_value_score": "Business value (avg score, 1-5)",
        "maturity_readiness_pct": "Maturity readiness",
        "history_status": "",
    },
)
stable = merged[~merged["insufficient_history"]]
if len(stable):
    fig.add_vline(x=stable["recent_share"].median(), line_dash="dot", line_color="gray")
    fig.add_hline(y=stable["avg_business_value_score"].median(), line_dash="dot", line_color="gray")
annotation_style = dict(showarrow=False, font=dict(size=10, color="gray"))
fig.add_annotation(xref="paper", yref="paper", x=0.02, y=0.98, xanchor="left", text="Proven, steady value", **annotation_style)
fig.add_annotation(xref="paper", yref="paper", x=0.98, y=0.98, xanchor="right", text="Emerging priority", **annotation_style)
fig.add_annotation(xref="paper", yref="paper", x=0.02, y=0.04, xanchor="left", text="Early-stage / niche", **annotation_style)
fig.add_annotation(xref="paper", yref="paper", x=0.98, y=0.04, xanchor="right", text="Watch — growing, unproven", **annotation_style)
fig.update_xaxes(tickformat=".0%", title="")
fig.update_yaxes(range=[0.5, 5.5], title="Avg. business value score")
st.plotly_chart(fig, width="stretch")

st.divider()
st.header(f"Full breakdown — every {dimension.lower()}")
st.caption("Nothing truncated to a top-N here — sort any column to explore the complete picture.")
st.dataframe(
    merged[[group_col, "total_count", "avg_business_value_score", "recent_share", "maturity_readiness_pct", "years_of_history", "insufficient_history"]]
    .sort_values("total_count", ascending=False),
    hide_index=True, width="stretch",
    column_config={
        group_col: dimension,
        "total_count": "Use cases",
        "avg_business_value_score": st.column_config.NumberColumn("Avg. value (1-5)", format="%.2f"),
        "recent_share": st.column_config.ProgressColumn("Growth (recent share)", min_value=0, max_value=1, format="%.0f%%"),
        "maturity_readiness_pct": st.column_config.ProgressColumn("Maturity readiness", min_value=0, max_value=1, format="%.0f%%"),
        "years_of_history": "Years of history",
        "insufficient_history": "Too new to trend?",
    },
)

st.divider()
st.header("Where's the untapped value?")
st.caption(
    "Every (industry, department) pair where that department scores well across the dataset as a "
    "whole but this industry has 0-1 use cases of it today — a proven pattern this industry hasn't "
    "applied yet. Sorted by how proven the department pattern is elsewhere."
)
opportunities = summaries.opportunity_finder(df)
opp_industry_filter = st.multiselect("Filter by industry", sorted(opportunities["industry"].unique()))
opp_display = opportunities[opportunities["industry"].isin(opp_industry_filter)] if opp_industry_filter else opportunities
st.caption(f"{len(opp_display)} of {len(opportunities)} opportunity pairs shown.")
st.dataframe(
    opp_display, hide_index=True, width="stretch",
    column_config={
        "industry": "Industry", "department": "Department",
        "current_count": "Use cases today",
        "department_global_avg_score": st.column_config.NumberColumn("Department's proven value elsewhere", format="%.2f"),
    },
)

st.divider()
st.header("What's mature and ready to build on")
st.caption(
    "Ranked by share of use cases already at mainstream/enterprise-standard maturity — the "
    f"strongest foundations to extend with adjacent {dimension.lower()}-specific use cases, "
    "rather than starting from zero."
)
if dimension == "Industry":
    scaled_df = summaries.scaled_production_counts_by_industry(cs).rename(columns={"industry": group_col})
    maturity_display = maturity_df.merge(scaled_df, on=group_col, how="left")
    maturity_display["scaled_case_studies"] = maturity_display["scaled_case_studies"].fillna(0).astype(int)
    st.caption("`scaled_case_studies` cross-checks the curated maturity field against real company deployments reported at `scaled/production` on the Real-World Impact page.")
else:
    maturity_display = maturity_df

display_cols = [group_col, "total_count", "mature_count", "maturity_readiness_pct"]
col_config = {
    group_col: dimension, "total_count": "Use cases", "mature_count": "Mainstream+ use cases",
    "maturity_readiness_pct": st.column_config.ProgressColumn("Maturity readiness", min_value=0, max_value=1, format="%.0f%%"),
}
if "scaled_case_studies" in maturity_display.columns:
    display_cols.append("scaled_case_studies")
    col_config["scaled_case_studies"] = "Scaled company deployments"

st.dataframe(
    maturity_display[display_cols], hide_index=True, width="stretch", column_config=col_config,
)
