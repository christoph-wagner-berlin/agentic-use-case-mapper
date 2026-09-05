import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
import plotly.express as px

from src import storage
from src.analysis import summaries

st.set_page_config(page_title="Revenue & ROI+", layout="wide")
st.title("Revenue & ROI+")
st.warning(
    "This dataset is knowledge-based and **not independently re-verified**. Company figures are "
    "AI-recalled from general public knowledge; macro market-size and investment figures vary "
    "5–10x by analyst firm and should be read as directional, not precise. Check `confidence` and "
    "the source before citing anything here externally.",
    icon="⚠️",
)

cs = storage.load_case_studies()
mc = storage.load_market_context()

if cs.empty:
    st.warning("No case studies yet. Run `python -m scripts.seed_db` or add entries via the Data Collection page.")
    st.stop()

st.markdown(
    "**Two different flows get conflated under \"AI is the most invested topic in the world\":** money "
    "flowing *into* AI vendors and infrastructure (model training, chips, data centers, VC bets on "
    "agent startups), and money enterprises have actually *realized* from deploying agents "
    "day-to-day. The first is genuinely enormous and well-documented. The second is much smaller, "
    "much harder to find hard numbers for, and — per this dataset — reported qualitatively "
    "(a percentage, a headcount story) far more often than as an audited dollar figure. That gap is "
    "what this page tries to make visible rather than paper over."
)

st.divider()
qr = summaries.quantification_rate(cs)
kcol1, kcol2, kcol3, kcol4 = st.columns(4)
kcol1.metric("Case studies with a disclosed $ figure", f"{qr['quantified']} / {qr['total']}", f"{qr['rate']:.0%}")
total_impact = cs["financial_impact_usd"].sum()
kcol2.metric("Total disclosed annual $ impact", f"${total_impact:,.0f}" if total_impact else "$0")
discontinued_or_reversed = cs["deployment_status"].isin(["discontinued", "scaled then partially reversed"]).sum()
kcol3.metric("Discontinued / partially reversed", f"{discontinued_or_reversed} / {len(cs)}")
scaled = (cs["deployment_status"] == "scaled/production").sum()
kcol4.metric("Reached scaled/production", f"{scaled} / {len(cs)}")

st.caption(
    "The low quantification rate is itself the headline finding, not a data-quality problem: most "
    "public AI success stories are told in percentages or headcount terms, not as company-reported "
    "profit or savings figures — which makes precise ROI hard to compare across companies even when "
    "the underlying results are real."
)

st.divider()
st.header("Over time")
st.caption(
    "History only — deliberately **no forward projection** here, unlike the Trends & Industries "
    "forecast. With a handful of quantified case studies in the whole dataset, extrapolating a "
    "dollar trend would manufacture false precision rather than show a real pattern."
)
tcol1, tcol2 = st.columns(2)
with tcol1:
    st.subheader("Cumulative disclosed $ impact")
    cum_impact = summaries.cumulative_financial_impact_by_year(cs)
    if cum_impact.empty:
        st.info("No case study currently has a quantified $ figure.")
    else:
        fig = px.line(cum_impact, x="year", y="cumulative_disclosed_usd", markers=True)
        fig.update_layout(xaxis_title="", yaxis_title="Cumulative USD/year disclosed")
        fig.update_xaxes(type="category")
        st.plotly_chart(fig, width="stretch")
with tcol2:
    st.subheader("Quantification rate by year")
    qr_by_year = summaries.quantification_rate_by_year(cs)
    fig = px.bar(qr_by_year, x="year", y="rate", text=qr_by_year["rate"].map(lambda r: f"{r:.0%}"))
    fig.update_layout(xaxis_title="", yaxis_title="Share of case studies with a $ figure")
    fig.update_yaxes(range=[0, 1], tickformat=".0%")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")
st.caption("Small yearly totals (single digits to low teens) mean each year's rate swings a lot on just one or two case studies — read it as a rough signal, not a precise trend.")

st.divider()
fcol1, fcol2, fcol3 = st.columns(3)
with fcol1:
    st.subheader("Disclosed $ impact by industry")
    fi_industry = summaries.financial_impact_by_industry(cs)
    if fi_industry.empty:
        st.info("No case study currently has a quantified $ figure for this filter.")
    else:
        fig = px.bar(fi_industry, x="industry", y="total_financial_impact_usd", text="total_financial_impact_usd")
        fig.update_layout(xaxis_title="", yaxis_title="USD / year")
        st.plotly_chart(fig, width="stretch")
with fcol2:
    st.subheader("Disclosed $ impact by department")
    fi_dept = summaries.financial_impact_by_department(cs)
    if fi_dept.empty:
        st.info("No case study currently has a quantified $ figure for this filter.")
    else:
        fig = px.bar(fi_dept, x="department", y="total_financial_impact_usd", text="total_financial_impact_usd")
        fig.update_layout(xaxis_title="", yaxis_title="USD / year")
        st.plotly_chart(fig, width="stretch")
with fcol3:
    st.subheader("Deployment status")
    dep_counts = summaries.deployment_status_counts(cs)
    fig = px.bar(dep_counts, x="deployment_status", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="Case studies")
    st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Why the investment/ROI gap looks the way it does")
st.caption(
    "Independent survey and analyst evidence for the pattern above — grouped by what kind of claim "
    "each figure is making. None of these are marked `high` confidence: they're contested, "
    "fast-moving macro figures, not audited financials."
)

CATEGORY_LABELS = {
    "investment/market size": "How much money is flowing in",
    "pilot-to-production funnel": "How much of it reaches production",
    "realized ROI evidence": "How much realized ROI gets reported",
    "risk/failure signal": "How much gets walked back",
}
CATEGORY_ORDER = ["investment/market size", "pilot-to-production funnel", "realized ROI evidence", "risk/failure signal"]
conf_badge = {"high": "🟢", "moderate": "🟡", "directional": "🟠"}

grouped = summaries.market_context_by_category(mc)
for category in CATEGORY_ORDER:
    group = grouped.get(category)
    if group is None or group.empty:
        continue
    st.subheader(CATEGORY_LABELS.get(category, category))
    for _, row in group.iterrows():
        badge = conf_badge.get(row["confidence"], "")
        with st.expander(f"{badge} {row['metric']}"):
            st.markdown(row["value_display"])
            meta_bits = [f"**Scope:** {row['scope']}", f"**Period:** {row['time_period']}", f"**Confidence:** {row['confidence']}"]
            st.caption(" · ".join(meta_bits))
            if pd.notna(row.get("source_url")):
                st.markdown(f"**Source:** [{row['source_url']}]({row['source_url']}) ({row['source_type']})")
            if row.get("notes"):
                st.info(row["notes"])

st.divider()
st.header("Case studies with a disclosed $ figure")
quantified_cs = cs[cs["financial_impact_usd"].notna()].sort_values("financial_impact_usd", ascending=False)
if quantified_cs.empty:
    st.info("None of the current case studies include a hard, company-reported dollar figure.")
else:
    for _, row in quantified_cs.iterrows():
        with st.expander(f"{row['company_name']} — ${row['financial_impact_usd']:,.0f}/yr ({row['financial_impact_type']})"):
            st.markdown(f"**Industry:** {row['industry']} &nbsp;|&nbsp; **Departments:** {row['target_departments']}")
            st.markdown(f"**Deployment status:** {row['deployment_status']}")
            st.markdown(f"**Reported gain:** {row['reported_efficiency_gain']}")
            st.caption(f"Confidence: {row['confidence']}")

st.download_button(
    "Download market context as CSV",
    mc.to_csv(index=False).encode("utf-8"),
    file_name="market_context.csv",
    mime="text/csv",
)
