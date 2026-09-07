import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px

from src import storage
from src.analysis import summaries
from src.viz import (
    CATEGORY_ORDER, CATEGORY_COLORS, DEPARTMENT_ORDER,
    MATURITY_ORDER, MATURITY_COLORS, SEQUENTIAL_BLUE,
)

st.set_page_config(page_title="Analysis", layout="wide")
st.title("Analysis")

df = storage.load_ai_tooling_use_cases()

if df.empty:
    st.warning("No data yet. Run `python -m scripts.seed_db` to load the curated seed dataset.")
    st.stop()

kcol1, kcol2, kcol3, kcol4 = st.columns(4)
named_companies = (df["example_companies"] != "Not publicly disclosed").sum()
kcol1.metric("AI tooling use cases with a named company", f"{named_companies} / {len(df)}")
mainstream_pct = df["maturity"].isin(["mainstream", "enterprise-standard"]).mean() * 100
kcol2.metric("Mainstream+ maturity", f"{mainstream_pct:.0f}%")
kcol3.metric("Median business value score", df["business_value_score"].median())
top_roi = summaries.roi_driver_counts(df).iloc[0]
kcol4.metric("Top ROI driver", top_roi["roi_driver"], f"{top_roi['count']} AI tooling use cases")

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

st.subheader("Category growth over time")
cat_by_year = summaries.grouped_counts_by_year(df, "category")
fig = px.area(
    cat_by_year, x="year", y="count", color="category",
    category_orders={"category": CATEGORY_ORDER}, color_discrete_map=CATEGORY_COLORS,
)
fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases")
fig.update_xaxes(type="category")
st.plotly_chart(fig, width="stretch")

st.subheader("Department growth over time")
dept_by_year = summaries.grouped_counts_by_year(df, "target_departments", explode=True)
fig = px.area(dept_by_year, x="year", y="count", color="target_departments")
fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases", legend_title="Department")
fig.update_xaxes(type="category")
st.plotly_chart(fig, width="stretch")

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("AI tooling use cases per category")
    counts = summaries.counts_by_category(df)
    fig = px.bar(
        counts, x="category", y="count", text="count", color="category",
        category_orders={"category": CATEGORY_ORDER}, color_discrete_map=CATEGORY_COLORS,
    )
    fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases", showlegend=False)
    st.plotly_chart(fig, width='stretch')

with col2:
    st.subheader("Business value score distribution per category")
    avg_scores = summaries.avg_score_by_category(df)
    fig = px.box(
        df, x="category", y="business_value_score", color="category",
        category_orders={"category": CATEGORY_ORDER}, color_discrete_map=CATEGORY_COLORS,
        points="outliers",
    )
    fig.update_layout(xaxis_title="", yaxis_title="Business value score (1-5)", showlegend=False)
    fig.update_yaxes(range=[0, 5])
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)

with col3:
    st.subheader("AI tooling use cases by maturity")
    maturity_counts = (
        summaries.counts_by_maturity(df)
        .set_index("maturity")
        .reindex(MATURITY_ORDER, fill_value=0)
        .reset_index()
    )
    fig = px.funnel(
        maturity_counts, x="count", y="maturity", color="maturity",
        category_orders={"maturity": MATURITY_ORDER}, color_discrete_map=MATURITY_COLORS,
    )
    fig.update_layout(yaxis_title="", showlegend=False)
    st.plotly_chart(fig, width='stretch')

with col4:
    st.subheader("ROI driver frequency")
    roi_counts = summaries.roi_driver_counts(df)
    fig = px.bar(roi_counts, x="roi_driver", y="count", text="count")
    fig.update_layout(xaxis_title="", yaxis_title="Mentions")
    st.plotly_chart(fig, width='stretch')

st.divider()
dcol1, dcol2 = st.columns(2)

with dcol1:
    st.subheader("AI tooling use cases per department")
    dept_counts = summaries.department_counts(df)
    fig = px.bar(
        dept_counts, x="department", y="count", text="count",
        category_orders={"department": DEPARTMENT_ORDER},
    )
    fig.update_layout(xaxis_title="", yaxis_title="AI tooling use cases")
    st.plotly_chart(fig, width='stretch')

with dcol2:
    st.subheader("Average business value score per department")
    dept_scores = summaries.avg_score_by_department(df)
    fig = px.bar(
        dept_scores, x="department", y="avg_business_value_score", text="avg_business_value_score",
        range_y=[0, 5], category_orders={"department": DEPARTMENT_ORDER},
    )
    fig.update_layout(xaxis_title="", yaxis_title="Avg. score (1-5)")
    st.plotly_chart(fig, width='stretch')

st.divider()
st.subheader("Category comparison")
comparison = counts.merge(avg_scores, on="category")
fig = px.scatter(
    comparison,
    x="count",
    y="avg_business_value_score",
    text="category",
    size="count",
    color="category",
)
fig.update_traces(textposition="top center")
fig.update_layout(xaxis_title="Number of AI tooling use cases", yaxis_title="Avg. business value score", showlegend=False)
st.plotly_chart(fig, width='stretch')

st.divider()
st.subheader("Category × maturity composition")
fig = px.sunburst(
    df, path=["category", "maturity"], color="business_value_score",
    color_continuous_scale=SEQUENTIAL_BLUE,
)
fig.update_layout(coloraxis_colorbar_title="Avg. score")
st.plotly_chart(fig, width='stretch')

st.divider()
st.subheader("AI tooling use cases by category (browse titles)")
for category in sorted(df["category"].unique()):
    sub = df[df["category"] == category].sort_values("business_value_score", ascending=False)
    with st.expander(f"{category} ({len(sub)} AI tooling use cases)"):
        for _, row in sub.iterrows():
            st.markdown(
                f"- **{row['tool_name']}** — {row['use_case_title']} (score {row['business_value_score']}/5, {row['maturity']})\n"
                f"  \n  {row['use_case_description']}\n"
                f"  \n  *Example companies: {row['example_companies']}*"
            )
