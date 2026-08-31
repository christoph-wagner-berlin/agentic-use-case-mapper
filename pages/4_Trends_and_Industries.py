import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
import plotly.express as px

from src import storage
from src.analysis import summaries

st.set_page_config(page_title="Trends & Industries", layout="wide")
st.title("Trends & Industries")
st.caption(
    "`first_available` dates are month/year estimates from known public launch milestones, "
    "and `target_industries` is an editorial categorization — both treat as approximate."
)

df = storage.load_use_cases()

if df.empty:
    st.warning("No data yet. Run `python -m scripts.seed_db` or add entries via the Data Collection page.")
    st.stop()

df["first_available"] = pd.to_datetime(df["first_available"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Industries covered", summaries.industry_counts(df)["industry"].nunique())
col2.metric("Earliest use case", int(df["first_available"].dt.year.min()))
col3.metric("Newest use case", int(df["first_available"].dt.year.max()))
avg_age_years = ((pd.Timestamp.today() - df["first_available"]).dt.days / 365.25).mean()
col4.metric("Avg. age (years)", round(avg_age_years, 1))

st.divider()
st.header("Over time")

tcol1, tcol2 = st.columns(2)
with tcol1:
    st.subheader("Use cases by emergence year")
    yearly = summaries.counts_by_year(df)
    fig = px.bar(yearly, x="year", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="Use cases")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")

with tcol2:
    st.subheader("Cumulative growth")
    cumulative = summaries.cumulative_by_year(df)
    fig = px.line(cumulative, x="year", y="cumulative_count", markers=True)
    fig.update_layout(xaxis_title="", yaxis_title="Total tracked use cases")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")

st.subheader("Use cases by emergence date and value")
fig = px.scatter(
    df,
    x="first_available",
    y="business_value_score",
    color="category",
    hover_data=["tool_name", "use_case_title"],
    labels={"first_available": "First available", "business_value_score": "Business value score"},
)
fig.update_yaxes(range=[0.5, 5.5])
st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Industries")

icol1, icol2 = st.columns(2)
with icol1:
    st.subheader("Use cases per industry")
    ind_counts = summaries.industry_counts(df)
    fig = px.bar(ind_counts, x="industry", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="Use cases")
    st.plotly_chart(fig, width="stretch")

with icol2:
    st.subheader("Average business value score per industry")
    ind_scores = summaries.avg_score_by_industry(df)
    fig = px.bar(ind_scores, x="industry", y="avg_business_value_score", text="avg_business_value_score", range_y=[0, 5])
    fig.update_layout(xaxis_title="", yaxis_title="Avg. score (1-5)")
    st.plotly_chart(fig, width="stretch")

st.subheader("Industry growth over time")
ind_by_year = summaries.grouped_counts_by_year(df, "target_industries", explode=True)
fig = px.area(ind_by_year, x="year", y="count", color="target_industries")
fig.update_layout(xaxis_title="", yaxis_title="Use cases", legend_title="Industry")
fig.update_xaxes(type="category")
st.plotly_chart(fig, width="stretch")

st.subheader("Category breakdown per industry")
exploded = df[["category", "target_industries"]].copy()
exploded["industry"] = exploded["target_industries"].str.split(";")
exploded = exploded.explode("industry")
exploded["industry"] = exploded["industry"].str.strip()
exploded = exploded[exploded["industry"] != ""]
pivot = exploded.groupby(["industry", "category"]).size().reset_index(name="count")
fig = px.bar(pivot, x="industry", y="count", color="category", barmode="stack")
fig.update_layout(xaxis_title="", yaxis_title="Use cases")
st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Departments")
st.caption("`target_departments` is an editorial categorization of which business function(s) a use case serves.")

dcol1, dcol2 = st.columns(2)
with dcol1:
    st.subheader("Use cases per department")
    dept_counts = summaries.department_counts(df)
    fig = px.bar(dept_counts, x="department", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="Use cases")
    st.plotly_chart(fig, width="stretch")

with dcol2:
    st.subheader("Average business value score per department")
    dept_scores = summaries.avg_score_by_department(df)
    fig = px.bar(dept_scores, x="department", y="avg_business_value_score", text="avg_business_value_score", range_y=[0, 5])
    fig.update_layout(xaxis_title="", yaxis_title="Avg. score (1-5)")
    st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Industry × Department mapping")
st.caption(
    "Where agentic-AI use cases concentrate across industry and business function. "
    "A cell is the count of tracked use cases relevant to that industry/department pair."
)

matrix = summaries.industry_department_matrix(df)
heatmap_data = matrix.pivot(index="department", columns="industry", values="count").fillna(0)
fig = px.imshow(
    heatmap_data,
    labels=dict(x="Industry", y="Department", color="Use cases"),
    color_continuous_scale="Blues",
    text_auto=True,
    aspect="auto",
)
fig.update_layout(height=550)
st.plotly_chart(fig, width="stretch")

st.subheader("Browse by industry × department")
bcol1, bcol2 = st.columns(2)
with bcol1:
    pick_industry = st.selectbox("Industry", sorted(summaries.industry_counts(df)["industry"]))
with bcol2:
    pick_department = st.selectbox("Department", sorted(summaries.department_counts(df)["department"]))

matched = df[
    df["target_industries"].apply(lambda v: pick_industry in [p.strip() for p in str(v).split(";")])
    & df["target_departments"].apply(lambda v: pick_department in [p.strip() for p in str(v).split(";")])
]
if matched.empty:
    st.info(f"No tracked use cases yet for {pick_industry} × {pick_department}.")
else:
    for _, row in matched.sort_values("business_value_score", ascending=False).iterrows():
        st.markdown(
            f"- **{row['tool_name']}** — {row['use_case_title']} (score {row['business_value_score']}/5, {row['maturity']})\n"
            f"  \n  {row['use_case_description']}"
        )

st.divider()
st.header("Forecast & Momentum")
st.warning(
    "This is a **naive linear trend extrapolation** over a small, curated dataset (a handful of years, "
    "tens of rows per group) — not a statistical forecast. Read the direction, not the exact numbers: "
    "a dashed line means 'if the recent pace continued,' not a prediction anyone should plan a budget "
    "around.",
    icon="⚠️",
)

DIMENSION_CONFIG = {
    "Category": dict(column="category", explode=False),
    "Industry": dict(column="target_industries", explode=True),
    "Department": dict(column="target_departments", explode=True),
}
dimension = st.radio("View by", list(DIMENSION_CONFIG.keys()), horizontal=True)
cfg = DIMENSION_CONFIG[dimension]
group_col = cfg["column"]

series_df, summary_df = summaries.growth_forecast(df, group_col, explode=cfg["explode"])

fig = px.line(
    series_df, x="year", y="count", color=group_col,
    line_dash="is_forecast", markers=True,
    labels={group_col: dimension},
)
fig.update_xaxes(type="category")
fig.update_layout(xaxis_title="", yaxis_title="Use cases (solid = actual, dashed = projected)")
st.plotly_chart(fig, width="stretch")

rankable = summary_df[~summary_df["insufficient_history"]]
excluded = len(summary_df) - len(rankable)

lcol1, lcol2 = st.columns(2)
with lcol1:
    st.subheader("Fastest-growing")
    st.caption("Ranked by recent_share — the fraction of a group's tracked use cases that first appeared in its latest observed year. Which use cases will come more.")
    fastest = rankable.sort_values("recent_share", ascending=False).head(8)
    st.dataframe(
        fastest[[group_col, "recent_share", "total_count"]],
        hide_index=True, width="stretch",
        column_config={
            group_col: dimension,
            "recent_share": st.column_config.ProgressColumn("Recent share", min_value=0, max_value=1, format="%.0f%%"),
            "total_count": "Total use cases",
        },
    )
with lcol2:
    st.subheader("Largest / most established")
    st.caption("Ranked by total tracked use cases, with average business value score alongside. Which areas are most important today.")
    largest = rankable.sort_values("total_count", ascending=False).head(8)
    cols_to_show = [group_col, "total_count"] + (["avg_business_value_score"] if "avg_business_value_score" in largest.columns else [])
    st.dataframe(
        largest[cols_to_show],
        hide_index=True, width="stretch",
        column_config={group_col: dimension, "total_count": "Total use cases", "avg_business_value_score": "Avg. score (1-5)"},
    )

if excluded:
    st.caption(f"{excluded} {dimension.lower()}(s) have fewer than 2 years of history and aren't ranked above yet — too new to call a trend.")
