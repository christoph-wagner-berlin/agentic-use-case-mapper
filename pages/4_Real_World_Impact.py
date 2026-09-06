import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
import plotly.express as px

from src import storage
from src.analysis import summaries

st.set_page_config(page_title="Real-World Impact", layout="wide")
st.title("Real-World Impact: What Companies Are Doing")
st.warning(
    "This dataset is knowledge-based and **not independently re-verified**. Figures are AI-recalled "
    "from general public knowledge and may be stale, imprecise, or wrong — check `confidence` and "
    "the source before citing anything here externally. See REQUIREMENTS.md section 5a.",
    icon="⚠️",
)
st.caption("Looking for the money angle specifically? See the **Revenue & ROI+** page for disclosed $ figures and market context.")

df = storage.load_case_studies()

if df.empty:
    st.warning("No case studies yet. Run `python -m scripts.seed_db` to load the curated seed dataset.")
    st.stop()

all_industries = sorted(df["industry"].dropna().unique())
all_departments = sorted(
    set(df["target_departments"].dropna().str.split(";").explode().str.strip()) - {""}
)
all_gain_types = sorted(
    set(df["gain_type"].dropna().str.split(";").explode().str.strip()) - {""}
)
all_company_sizes = sorted(df["company_size_band"].dropna().unique())

with st.sidebar:
    st.header("Filters")
    industries = st.multiselect("Industry", all_industries)
    departments = st.multiselect("Department / business function", all_departments)
    gain_types = st.multiselect("Gain type", all_gain_types)
    confidences = st.multiselect("Confidence", ["high", "moderate", "directional"])
    deployment_statuses = st.multiselect(
        "Deployment status", ["pilot", "scaled/production", "scaled then partially reversed", "discontinued"]
    )
    company_sizes = st.multiselect("Company size", all_company_sizes)

filtered = df.copy()
if industries:
    filtered = filtered[filtered["industry"].isin(industries)]
if departments:
    filtered = filtered[
        filtered["target_departments"].apply(
            lambda v: any(d in [p.strip() for p in str(v).split(";")] for d in departments)
        )
    ]
if gain_types:
    filtered = filtered[
        filtered["gain_type"].apply(
            lambda v: any(g in [p.strip() for p in str(v).split(";")] for g in gain_types)
        )
    ]
if confidences:
    filtered = filtered[filtered["confidence"].isin(confidences)]
if deployment_statuses:
    filtered = filtered[filtered["deployment_status"].isin(deployment_statuses)]
if company_sizes:
    filtered = filtered[filtered["company_size_band"].isin(company_sizes)]

st.caption(f"{len(filtered)} of {len(df)} company case studies match the current filters.")
if company_sizes and filtered.empty:
    st.info(
        "No case studies at this company-size scale yet — a real data gap, not a bug. Most of "
        "this dataset skews enterprise; the handful of mid-market/SMB rows are concentrated in "
        "finance/back-office automation, B2B sales, and B2B customer support."
    )

kcol1, kcol2, kcol3 = st.columns(3)
kcol1.metric("Companies", filtered["company_name"].nunique())
kcol2.metric("Industries covered", filtered["industry"].nunique())
kcol3.metric("High-confidence reports", int((filtered["confidence"] == "high").sum()))

st.divider()
st.header("Over time")
tcol1, tcol2 = st.columns(2)
with tcol1:
    st.subheader("Case studies by year reported")
    yearly = summaries.counts_by_year(filtered, date_column="date_reported")
    fig = px.bar(yearly, x="year", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="Case studies")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")
with tcol2:
    st.subheader("Cumulative case studies")
    cumulative = summaries.cumulative_by_year(filtered, date_column="date_reported")
    fig = px.line(cumulative, x="year", y="cumulative_count", markers=True)
    fig.update_layout(xaxis_title="", yaxis_title="Total tracked case studies")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")
st.caption(
    "The 2025 dip is very likely reporting lag (companies take time to publicize results), not "
    "a real drop-off — treat the most recent year as undercounted, here and everywhere in this app."
)

st.subheader("Deployment status mix by year")
status_by_year = summaries.grouped_counts_by_year(filtered, "deployment_status", date_column="date_reported")
fig = px.bar(status_by_year, x="year", y="count", color="deployment_status", barmode="stack")
fig.update_layout(xaxis_title="", yaxis_title="Case studies", legend_title="Deployment status")
fig.update_xaxes(type="category")
st.plotly_chart(fig, width="stretch")

st.divider()
ccol1, ccol2, ccol3 = st.columns(3)
with ccol1:
    st.subheader("By industry")
    fig = px.bar(summaries.case_studies_by_industry(filtered), x="industry", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="Case studies")
    st.plotly_chart(fig, width="stretch")
with ccol2:
    st.subheader("By gain type")
    fig = px.bar(summaries.case_studies_by_gain_type(filtered), x="gain_type", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="Mentions")
    st.plotly_chart(fig, width="stretch")
with ccol3:
    st.subheader("By confidence")
    fig = px.pie(summaries.case_studies_by_confidence(filtered), names="confidence", values="count")
    st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Industry × Department: who's doing what")
st.caption(
    "Counts of real-world company case studies per industry/department pair — "
    "the evidence layer behind the taxonomy-level mapping on the Trends & Industries page."
)
matrix = summaries.case_studies_industry_department_matrix(filtered)
if matrix.empty:
    st.info("No case studies match the current filters.")
else:
    heatmap_data = matrix.pivot(index="department", columns="industry", values="count").fillna(0)
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Industry", y="Department", color="Case studies"),
        color_continuous_scale="Greens",
        text_auto=True,
        aspect="auto",
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Case studies")
status_icon = {
    "pilot": "🧪", "scaled/production": "✅",
    "scaled then partially reversed": "↩️", "discontinued": "🛑",
}
for _, row in filtered.sort_values("date_reported", ascending=False).iterrows():
    conf_badge = {"high": "🟢", "moderate": "🟡", "directional": "🟠"}.get(row["confidence"], "")
    status = row.get("deployment_status") or ""
    status_badge = status_icon.get(status, "")
    with st.expander(f"{conf_badge} {status_badge} {row['company_name']} — {row['tool_or_platform']} ({row['industry']})"):
        st.markdown(f"**Departments involved:** {row['target_departments'] or 'Not specified'}")
        st.markdown(f"**Company size:** {row.get('company_size_band') or 'Not specified'}")
        if row["related_category"]:
            st.markdown(f"**Related category:** {row['related_category']}")
        st.markdown(f"**Deployment status:** {status or 'Not specified'}")
        st.markdown(f"**What they did:** {row['what_they_did']}")
        st.markdown(f"**Reported gain:** {row['reported_efficiency_gain']}")
        if pd.notna(row.get("financial_impact_usd")):
            st.markdown(f"**Disclosed $ impact:** ${row['financial_impact_usd']:,.0f}/yr ({row.get('financial_impact_type') or 'unspecified type'})")
        if pd.notna(row.get("implementation_cost_usd")):
            st.markdown(f"**Disclosed implementation cost:** ${row['implementation_cost_usd']:,.0f}")
        st.markdown(f"**Gain type:** {row['gain_type']} &nbsp;|&nbsp; **Confidence:** {row['confidence']}")
        urls = [u.strip() for u in str(row["source_url"]).split(";") if u.strip()]
        sources_md = " · ".join(f"[{u}]({u})" for u in urls)
        st.markdown(f"**Sources:** {sources_md} ({row['source_type']})")
        date_reported = pd.to_datetime(row["date_reported"]) if pd.notna(row["date_reported"]) else None
        if date_reported is not None:
            st.caption(f"Reported: {date_reported.strftime('%Y-%m')}")
        if row["notes"]:
            st.info(row["notes"])

st.download_button(
    "Download filtered case studies as CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="company_case_studies_filtered.csv",
    mime="text/csv",
)
