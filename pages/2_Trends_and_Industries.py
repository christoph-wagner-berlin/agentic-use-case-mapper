import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
import plotly.express as px

from src import storage
from src.analysis import summaries
from src.viz import (
    CATEGORY_ORDER, CATEGORY_COLORS, INDUSTRY_ORDER, DEPARTMENT_ORDER,
    CATEGORICAL_8, OTHER_COLOR, SEQUENTIAL_BLUE, ordered_with_extras,
)

st.set_page_config(page_title="Trends & Industries", layout="wide")
st.title("Trends & Industries")
st.caption(
    "`first_available` dates are month/year estimates from known public launch milestones, "
    "and `target_industries` is an editorial categorization — both treat as approximate."
)

df = storage.load_ai_tooling_use_cases()

if df.empty:
    st.warning("No data yet. Run `python -m scripts.seed_db` to load the curated seed dataset.")
    st.stop()

df["first_available"] = pd.to_datetime(df["first_available"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Industries covered", summaries.industry_counts(df)["industry"].nunique())
col2.metric("Earliest AI tooling use case", int(df["first_available"].dt.year.min()))
col3.metric("Newest AI tooling use case", int(df["first_available"].dt.year.max()))
avg_age_years = ((pd.Timestamp.today() - df["first_available"]).dt.days / 365.25).mean()
col4.metric("Avg. age (years)", round(avg_age_years, 1))

st.divider()
st.header("Over time")

tcol1, tcol2 = st.columns(2)
with tcol1:
    st.subheader("AI tooling use cases by emergence year")
    yearly = summaries.counts_by_year(df)
    fig = px.bar(yearly, x="year", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")

with tcol2:
    st.subheader("Cumulative growth")
    cumulative = summaries.cumulative_by_year(df)
    fig = px.line(cumulative, x="year", y="cumulative_count", markers=True)
    fig.update_layout(xaxis_title="", yaxis_title="Total tracked AI tooling use cases")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")

st.subheader("AI tooling use cases by emergence date and value")
fig = px.scatter(
    df,
    x="first_available",
    y="business_value_score",
    color="category",
    hover_data=["tool_name", "use_case_title"],
    labels={"first_available": "First available", "business_value_score": "Business value score"},
    category_orders={"category": CATEGORY_ORDER},
    color_discrete_map=CATEGORY_COLORS,
)
fig.update_yaxes(range=[0.5, 5.5])
st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Industries")

icol1, icol2 = st.columns(2)
with icol1:
    st.subheader("AI tooling use cases per industry")
    ind_counts = summaries.industry_counts(df)
    fig = px.bar(
        ind_counts, x="industry", y="count", text="count",
        category_orders={"industry": INDUSTRY_ORDER},
    )
    fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases")
    st.plotly_chart(fig, width="stretch")

with icol2:
    st.subheader("Average business value score per industry")
    ind_scores = summaries.avg_score_by_industry(df)
    fig = px.bar(
        ind_scores, x="industry", y="avg_business_value_score", text="avg_business_value_score",
        range_y=[0, 5], category_orders={"industry": INDUSTRY_ORDER},
    )
    fig.update_layout(xaxis_title="", yaxis_title="Avg. score (1-5)")
    st.plotly_chart(fig, width="stretch")

st.subheader("Industry growth over time")
top_industries = summaries.industry_counts(df).head(7)["industry"].tolist()
ind_by_year = summaries.grouped_counts_by_year(df, "target_industries", explode=True)
ind_by_year["target_industries"] = ind_by_year["target_industries"].where(
    ind_by_year["target_industries"].isin(top_industries), "Other"
)
ind_by_year = ind_by_year.groupby(["year", "target_industries"], as_index=False)["count"].sum()
industry_area_colors = dict(zip(top_industries, CATEGORICAL_8[:7]))
industry_area_colors["Other"] = OTHER_COLOR
fig = px.area(
    ind_by_year, x="year", y="count", color="target_industries",
    category_orders={"target_industries": top_industries + ["Other"]},
    color_discrete_map=industry_area_colors,
)
fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases", legend_title="Industry")
fig.update_xaxes(type="category")
st.plotly_chart(fig, width="stretch")

st.subheader("Category breakdown per industry")
exploded = df[["category", "target_industries"]].copy()
exploded["industry"] = exploded["target_industries"].str.split(";")
exploded = exploded.explode("industry")
exploded["industry"] = exploded["industry"].str.strip()
exploded = exploded[exploded["industry"] != ""]
pivot = exploded.groupby(["industry", "category"]).size().reset_index(name="count")
fig = px.bar(
    pivot, x="industry", y="count", color="category", barmode="stack",
    category_orders={"category": CATEGORY_ORDER, "industry": INDUSTRY_ORDER},
    color_discrete_map=CATEGORY_COLORS,
)
fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases")
st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Departments")
st.caption("`target_departments` is an editorial categorization of which business function(s) an AI tooling use case serves.")

dcol1, dcol2 = st.columns(2)
with dcol1:
    st.subheader("AI tooling use cases per department")
    dept_counts = summaries.department_counts(df)
    fig = px.bar(
        dept_counts, x="department", y="count", text="count",
        category_orders={"department": DEPARTMENT_ORDER},
    )
    fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases")
    st.plotly_chart(fig, width="stretch")

with dcol2:
    st.subheader("Average business value score per department")
    dept_scores = summaries.avg_score_by_department(df)
    fig = px.bar(
        dept_scores, x="department", y="avg_business_value_score", text="avg_business_value_score",
        range_y=[0, 5], category_orders={"department": DEPARTMENT_ORDER},
    )
    fig.update_layout(xaxis_title="", yaxis_title="Avg. score (1-5)")
    st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Industry × Department mapping")
st.caption(
    "Where agentic-AI use cases concentrate across industry and business function. "
    "A cell is the count of tracked AI tooling use cases relevant to that industry/department pair."
)

matrix = summaries.industry_department_matrix(df)
heatmap_data = matrix.pivot(index="department", columns="industry", values="count").fillna(0)
heatmap_data = heatmap_data.reindex(
    index=ordered_with_extras(DEPARTMENT_ORDER, heatmap_data.index),
    columns=ordered_with_extras(INDUSTRY_ORDER, heatmap_data.columns),
)
fig = px.imshow(
    heatmap_data,
    labels=dict(x="Industry", y="Department", color="AI tooling use cases"),
    color_continuous_scale=SEQUENTIAL_BLUE,
    text_auto=True,
    aspect="auto",
)
fig.update_layout(height=550)
st.plotly_chart(fig, width="stretch")

st.subheader("Browse by industry × department")
bcol1, bcol2 = st.columns(2)
with bcol1:
    present_industries = set(summaries.industry_counts(df)["industry"])
    pick_industry = st.selectbox("Industry", ordered_with_extras(INDUSTRY_ORDER, present_industries))
with bcol2:
    present_departments = set(summaries.department_counts(df)["department"])
    pick_department = st.selectbox("Department", ordered_with_extras(DEPARTMENT_ORDER, present_departments))

matched = df[
    df["target_industries"].apply(lambda v: pick_industry in [p.strip() for p in str(v).split(";")])
    & df["target_departments"].apply(lambda v: pick_department in [p.strip() for p in str(v).split(";")])
]
if matched.empty:
    st.info(f"No tracked AI tooling use cases yet for {pick_industry} × {pick_department}.")
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

if dimension == "Category":
    forecast_order = CATEGORY_ORDER
    forecast_colors = CATEGORY_COLORS
else:
    top_groups = summary_df.sort_values("total_count", ascending=False).head(7)[group_col].tolist()
    series_df = series_df.copy()
    series_df[group_col] = series_df[group_col].where(series_df[group_col].isin(top_groups), "Other")
    series_df = series_df.groupby(["year", group_col, "is_forecast"], as_index=False)["count"].sum()
    forecast_order = top_groups + ["Other"]
    forecast_colors = dict(zip(top_groups, CATEGORICAL_8[:7]))
    forecast_colors["Other"] = OTHER_COLOR

fig = px.line(
    series_df, x="year", y="count", color=group_col,
    line_dash="is_forecast", line_dash_map={False: "solid", True: "dash"}, markers=True,
    labels={group_col: dimension},
    category_orders={group_col: forecast_order},
    color_discrete_map=forecast_colors,
)
fig.update_xaxes(type="category")
fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases (solid = actual, dashed = projected)")
st.plotly_chart(fig, width="stretch")

rankable = summary_df[~summary_df["insufficient_history"]]
excluded = len(summary_df) - len(rankable)

lcol1, lcol2 = st.columns(2)
with lcol1:
    st.subheader("Fastest-growing")
    st.caption("Ranked by recent_share — the fraction of a group's tracked AI tooling use cases that first appeared in its latest observed year. Which AI tooling use cases will come more.")
    fastest = rankable.sort_values("recent_share", ascending=False).head(8)
    st.dataframe(
        fastest[[group_col, "recent_share", "total_count"]],
        hide_index=True, width="stretch",
        column_config={
            group_col: dimension,
            "recent_share": st.column_config.ProgressColumn("Recent share", min_value=0, max_value=1, format="%.0f%%"),
            "total_count": "Total AI tooling use cases",
        },
    )
with lcol2:
    st.subheader("Largest / most established")
    st.caption("Ranked by total tracked AI tooling use cases, with average business value score alongside. Which areas are most important today.")
    largest = rankable.sort_values("total_count", ascending=False).head(8)
    cols_to_show = [group_col, "total_count"] + (["avg_business_value_score"] if "avg_business_value_score" in largest.columns else [])
    st.dataframe(
        largest[cols_to_show],
        hide_index=True, width="stretch",
        column_config={group_col: dimension, "total_count": "Total AI tooling use cases", "avg_business_value_score": "Avg. score (1-5)"},
    )

if excluded:
    st.caption(f"{excluded} {dimension.lower()}(s) have fewer than 2 years of history and aren't ranked above yet — too new to call a trend.")
