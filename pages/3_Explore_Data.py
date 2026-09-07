import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from src import storage
from src.viz import CATEGORY_ORDER, INDUSTRY_ORDER, DEPARTMENT_ORDER, COMPANY_SIZE_ORDER, MATURITY_ORDER, ordered_with_extras

st.set_page_config(page_title="Explore Data", layout="wide")
st.title("Explore AI Tooling Use Cases")

df = storage.load_ai_tooling_use_cases()

if df.empty:
    st.warning("No data yet. Run `python -m scripts.seed_db` to load the curated seed dataset.")
    st.stop()

topics_joined = storage.load_ai_tooling_use_case_topics_joined()
links_joined = storage.load_ai_tooling_use_case_case_study_links_joined()
topics_by_use_case = topics_joined.groupby("ai_tooling_use_case_id")["topic_name"].apply(list) if not topics_joined.empty else pd.Series(dtype=object)

all_industries = ordered_with_extras(
    INDUSTRY_ORDER,
    set(df["target_industries"].dropna().str.split(";").explode().str.strip()) - {""},
)
all_departments = ordered_with_extras(
    DEPARTMENT_ORDER,
    set(df["target_departments"].dropna().str.split(";").explode().str.strip()) - {""},
)
all_company_sizes = ordered_with_extras(
    COMPANY_SIZE_ORDER,
    set(df["target_company_size"].dropna().str.split(";").explode().str.strip()) - {""},
)

with st.sidebar:
    st.header("Filters")
    categories = st.multiselect("Category", ordered_with_extras(CATEGORY_ORDER, df["category"].unique()))
    tools = st.multiselect("Tool", sorted(df["tool_name"].unique()))
    maturities = st.multiselect("Maturity", ordered_with_extras(MATURITY_ORDER, df["maturity"].unique()))
    industries = st.multiselect("Industry", all_industries)
    departments = st.multiselect("Department / business function", all_departments)
    company_sizes = st.multiselect("Company size", all_company_sizes)
    topics_filter = st.multiselect("Topic", sorted(topics_joined["topic_name"].unique()) if not topics_joined.empty else [])
    min_score = st.slider("Minimum business value score", 1, 5, 1)
    search_text = st.text_input("Search (title / ROI drivers)")

filtered = df.copy()
if categories:
    filtered = filtered[filtered["category"].isin(categories)]
if tools:
    filtered = filtered[filtered["tool_name"].isin(tools)]
if maturities:
    filtered = filtered[filtered["maturity"].isin(maturities)]
if industries:
    filtered = filtered[
        filtered["target_industries"].apply(
            lambda v: any(i in [p.strip() for p in str(v).split(";")] for i in industries)
        )
    ]
if departments:
    filtered = filtered[
        filtered["target_departments"].apply(
            lambda v: any(d in [p.strip() for p in str(v).split(";")] for d in departments)
        )
    ]
if company_sizes:
    filtered = filtered[
        filtered["target_company_size"].apply(
            lambda v: any(s in [p.strip() for p in str(v).split(";")] for s in company_sizes)
        )
    ]
if topics_filter:
    matching_ids = set(topics_joined[topics_joined["topic_name"].isin(topics_filter)]["ai_tooling_use_case_id"])
    filtered = filtered[filtered["id"].isin(matching_ids)]
filtered = filtered[filtered["business_value_score"] >= min_score]
if search_text:
    needle = search_text.lower()
    filtered = filtered[
        filtered["use_case_title"].str.lower().str.contains(needle, na=False)
        | filtered["roi_drivers"].str.lower().str.contains(needle, na=False)
    ]

st.caption(f"{len(filtered)} of {len(df)} AI tooling use cases match the current filters.")
if company_sizes and filtered.empty:
    st.info(
        "No AI tooling use cases are tagged for this company size yet — a real data gap in this "
        "dataset, not a bug. Most tools skew toward enterprise-scale evidence; try widening the "
        "company-size filter."
    )

display_df = filtered.copy()
display_df["topics"] = display_df["id"].map(lambda i: "; ".join(topics_by_use_case.get(i, [])))

st.dataframe(
    display_df[
        [
            "category",
            "tool_name",
            "use_case_title",
            "use_case_description",
            "maturity",
            "business_value_score",
            "topics",
            "roi_drivers",
            "target_industries",
            "target_departments",
            "target_company_size",
            "example_companies",
        ]
    ],
    width='stretch',
    hide_index=True,
    column_config={
        "use_case_description": st.column_config.TextColumn("Description", width="large"),
        "topics": st.column_config.TextColumn("Topics"),
        "target_industries": st.column_config.TextColumn("Industries"),
        "target_departments": st.column_config.TextColumn("Departments"),
        "target_company_size": st.column_config.TextColumn("Company size"),
        "example_companies": st.column_config.TextColumn("Example companies"),
    },
)

st.download_button(
    "Download filtered results as CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="ai_tooling_use_cases_filtered.csv",
    mime="text/csv",
)

st.divider()
st.subheader("AI tooling use case detail")

if not filtered.empty:
    options = filtered.apply(lambda r: f"[{r['id']}] {r['tool_name']} — {r['use_case_title']}", axis=1)
    choice = st.selectbox("Select an AI tooling use case", options)
    selected_id = int(choice.split("]")[0][1:])
    row = filtered[filtered["id"] == selected_id].iloc[0]

    st.markdown(f"### {row['use_case_title']}")
    st.markdown(f"**Category:** {row['category']} &nbsp;|&nbsp; **Tool:** {row['tool_name']} ({row['vendor']})")
    st.markdown(f"**Maturity:** {row['maturity']} &nbsp;|&nbsp; **Business value score:** {row['business_value_score']}/5")
    st.markdown(f"**Target users:** {row['target_users']}")
    st.markdown(f"**Target industries:** {row['target_industries']}")
    st.markdown(f"**Target departments:** {row['target_departments']}")
    st.markdown(f"**Company size:** {row['target_company_size']}")
    row_topics = topics_by_use_case.get(selected_id, [])
    if row_topics:
        st.markdown(f"**Topics:** {'; '.join(row_topics)}")
    st.write(row["use_case_description"])
    st.markdown(f"**ROI drivers:** {row['roi_drivers']}")
    st.markdown(f"**Example companies:** {row['example_companies']}")
    st.markdown(f"**Rationale:** {row['business_value_rationale']}")

    related_links = links_joined[links_joined["ai_tooling_use_case_id"] == selected_id] if not links_joined.empty else links_joined
    if not related_links.empty:
        st.markdown("**Related case studies:**")
        for _, link_row in related_links.iterrows():
            st.markdown(f"- {link_row['company_name']} ({link_row['tool_or_platform']}) — *{link_row['match_type']}*")

    urls = [u.strip() for u in str(row["source_url"]).split(";") if u.strip()]
    sources_md = " · ".join(f"[{u}]({u})" for u in urls)
    st.markdown(f"**Sources:** {sources_md} ({row['source_type']})")
    st.caption(
        f"First available: {pd.to_datetime(row['first_available']).strftime('%Y-%m')}  ·  "
        f"Collected: {pd.to_datetime(row['collected_at']).strftime('%Y-%m-%d')}  ·  "
        f"Last verified: {pd.to_datetime(row['last_verified']).strftime('%Y-%m-%d')}"
    )
    if row["notes"]:
        st.info(row["notes"])
