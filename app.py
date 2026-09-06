import pandas as pd
import streamlit as st

from src import storage

st.set_page_config(page_title="App Overview", layout="wide")
st.title("App Overview")
st.write("Where agentic AI is already creating real business value — before you dive into the mapping tools in the sidebar.")

df = storage.load_ai_tooling_use_cases()
case_studies = storage.load_case_studies()
achievements = storage.load_achievements()
topics = storage.load_topics()

if df.empty:
    st.warning("No data yet. Run `python -m scripts.seed_db` from the project root to load the curated seed dataset.")
else:
    total_impact = case_studies["financial_impact_usd"].sum() if not case_studies.empty else 0
    scaled = int((case_studies["deployment_status"] == "scaled/production").sum()) if not case_studies.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AI tooling use cases tracked", len(df))
    col2.metric("Avg. business value score", round(df["business_value_score"].mean(), 2))
    col3.metric("Total disclosed $ impact", f"${total_impact:,.0f}" if total_impact else "$0")
    col4.metric("Companies at scaled/production", scaled)

    st.divider()
    st.header("🏆 Top business-value AI tooling use cases")
    st.caption("Highest-scored AI tooling use cases in the dataset, with the advantages and ROI behind each score.")
    top_use_cases = df.sort_values(
        ["business_value_score", "first_available"], ascending=[False, False]
    ).head(6)
    for _, row in top_use_cases.iterrows():
        with st.expander(f"⭐ {row['business_value_score']}/5 — {row['use_case_title']} ({row['tool_name']})"):
            st.markdown(f"**Category:** {row['category']} &nbsp;|&nbsp; **Maturity:** {row['maturity']}")
            st.write(row["use_case_description"])
            st.markdown(f"**Why it's valuable:** {row['business_value_rationale']}")
            st.markdown(f"**Advantages (ROI drivers):** {row['roi_drivers']}")
            if row["example_companies"]:
                st.markdown(f"**Example companies:** {row['example_companies']}")

    st.divider()
    st.header("💰 Real-world achievements")
    st.caption("Company case studies ranked by the biggest disclosed dollar impact.")
    if case_studies.empty:
        st.info("No case studies yet. Run `python -m scripts.seed_db` to load the curated seed dataset.")
    else:
        quantified = case_studies[case_studies["financial_impact_usd"].notna()]
        top_achievements = (quantified if not quantified.empty else case_studies).sort_values(
            "financial_impact_usd", ascending=False, na_position="last"
        ).head(6)
        conf_badge = {"high": "🟢", "moderate": "🟡", "directional": "🟠"}
        for _, row in top_achievements.iterrows():
            badge = conf_badge.get(row["confidence"], "")
            impact = f" — ${row['financial_impact_usd']:,.0f}/yr" if pd.notna(row.get("financial_impact_usd")) else ""
            with st.expander(f"{badge} {row['company_name']} ({row['industry']}){impact}"):
                st.markdown(f"**What they did:** {row['what_they_did']}")
                st.markdown(f"**Reported gain:** {row['reported_efficiency_gain']}")
                if pd.notna(row.get("financial_impact_usd")):
                    st.markdown(
                        f"**Disclosed $ impact:** ${row['financial_impact_usd']:,.0f}/yr "
                        f"({row.get('financial_impact_type') or 'unspecified type'})"
                    )
                st.markdown(f"**Deployment status:** {row['deployment_status']} &nbsp;|&nbsp; **Confidence:** {row['confidence']}")
                urls = [u.strip() for u in str(row["source_url"]).split(";") if u.strip()]
                if urls:
                    sources_md = " · ".join(f"[{u}]({u})" for u in urls)
                    st.markdown(f"**Sources:** {sources_md}")

    st.divider()
    st.header("🏅 Notable achievements")
    st.caption("Vendor- and tool-side milestones — funding, benchmarks, and adoption — distinct from the customer $ case studies above.")
    if achievements.empty:
        st.info("No achievements yet. Run `python -m scripts.seed_db` to load the curated seed dataset.")
    else:
        conf_badge = {"high": "🟢", "moderate": "🟡", "directional": "🟠"}
        top_achievements_list = achievements.sort_values("date_achieved", ascending=False).head(6)
        for _, row in top_achievements_list.iterrows():
            badge = conf_badge.get(row["confidence"], "")
            with st.expander(f"{badge} {row['title']}"):
                st.markdown(f"**Tool/company:** {row['tool_name']} ({row['company_name']}) &nbsp;|&nbsp; **Type:** {row['achievement_type']}")
                st.markdown(f"**{row['metric_display']}**")
                st.write(row["description"])
                st.markdown(f"**Confidence:** {row['confidence']}")
                if row["notes"]:
                    st.caption(row["notes"])

    st.divider()
    st.header("🗂️ Topics we cover")
    industries = df["target_industries"].dropna().str.split(";").explode().str.strip()
    industries = industries[industries != ""]
    departments = df["target_departments"].dropna().str.split(";").explode().str.strip()
    departments = departments[departments != ""]

    tcol1, tcol2, tcol3 = st.columns(3)
    tcol1.metric("Categories", df["category"].nunique())
    tcol2.metric("Industries covered", industries.nunique())
    tcol3.metric("Departments covered", departments.nunique())

    st.markdown("**Categories:** " + " · ".join(sorted(df["category"].unique())))
    if not topics.empty:
        st.markdown("**Cross-cutting topics:** " + " · ".join(sorted(topics["name"].unique())))
    st.markdown("**Industries:** " + " · ".join(sorted(industries.unique())))
    st.markdown("**Departments:** " + " · ".join(sorted(departments.unique())))

    st.divider()
    st.header("Dig deeper")
    lcol1, lcol2, lcol3, lcol4, lcol5, lcol6, lcol7 = st.columns(7)
    lcol1.page_link("pages/3_Explore_Data.py", label="Explore all AI tooling use cases", icon="🔎")
    lcol2.page_link("pages/2_Trends_and_Industries.py", label="Trends & Industries map", icon="🗺️")
    lcol3.page_link("pages/4_Real_World_Impact.py", label="Real-World Impact", icon="🏢")
    lcol4.page_link("pages/5_Revenue_and_ROI+.py", label="Revenue & ROI+", icon="💵")
    lcol5.page_link("pages/6_Growth_and_Opportunities.py", label="Growth & Opportunities", icon="📈")
    lcol6.page_link("pages/7_Agent_Catalog_and_Patterns.py", label="Agent Catalog & Patterns", icon="🤖")
    lcol7.page_link("pages/8_Startup_Vendors.py", label="Startup Vendors", icon="🚀")

    st.divider()
    st.subheader("AI tooling use cases per category")
    st.bar_chart(df.groupby("category").size())
