import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date

import pandas as pd
import streamlit as st

from src import storage, taxonomy

st.set_page_config(page_title="Data Collection", layout="wide")
st.title("Data Collection")

MATURITY_OPTIONS = ["experimental", "emerging", "mainstream", "enterprise-standard"]
SOURCE_TYPE_OPTIONS = ["vendor_docs", "case_study", "news_article", "community_report", "academic"]
CONFIDENCE_OPTIONS = ["high", "moderate", "directional"]
FINANCIAL_IMPACT_TYPE_OPTIONS = [
    "not quantified", "profit impact", "cost savings", "revenue impact", "cost avoidance", "headcount efficiency",
]
DEPLOYMENT_STATUS_OPTIONS = ["pilot", "scaled/production", "scaled then partially reversed", "discontinued"]


def _split(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in str(value).split(";") if v.strip()]


def _join(values: list[str]) -> str:
    return "; ".join(values)


tab_add, tab_edit, tab_cases, tab_admin = st.tabs(
    ["Add new use case", "Edit existing", "Company case studies", "Admin"]
)

with tab_add:
    st.subheader("Add a new use case")
    categories = taxonomy.category_names()
    category = st.selectbox("Category", categories, key="add_category")
    tools = [t["name"] for t in taxonomy.tools_for_category(category)]
    tool_name = st.selectbox("Tool", tools, key="add_tool") if tools else st.text_input("Tool name", key="add_tool_text")
    vendor_default = taxonomy.vendor_for_tool(category, tool_name) if tools else ""

    with st.form("add_use_case_form", clear_on_submit=True):
        vendor = st.text_input("Vendor", value=vendor_default)
        use_case_title = st.text_input("Use case title")
        use_case_description = st.text_area("Use case description")
        target_users = st.text_input("Target users")
        target_industries = st.multiselect(
            "Target industries", taxonomy.industry_names(), accept_new_options=True,
            help="Pick one or more; type to add an industry not in the list.",
        )
        target_departments = st.multiselect(
            "Target departments / business functions", taxonomy.department_names(), accept_new_options=True,
            help="Which company functions this use case serves (Sales, After-Sales/Service, IT, R&D/Engineering, ...).",
        )
        maturity = st.selectbox("Maturity", MATURITY_OPTIONS)
        first_available = st.date_input("First available (approximate)", value=date.today())
        business_value_score = st.slider("Business value score", 1, 5, 3)
        business_value_rationale = st.text_area("Business value rationale")
        roi_drivers = st.text_input("ROI drivers (semicolon-separated, e.g. 'time saved; cost reduction')")
        example_companies = st.text_input(
            "Example companies (semicolon-separated; use 'Not publicly disclosed' if unknown)",
            value="Not publicly disclosed",
        )
        source_url = st.text_input("Source URL(s) (semicolon-separated if more than one)")
        source_type = st.selectbox("Source type", SOURCE_TYPE_OPTIONS)
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add use case")
        if submitted:
            if not use_case_title:
                st.error("Use case title is required.")
            else:
                new_id = storage.insert_use_case(
                    dict(
                        category=category,
                        tool_name=tool_name,
                        vendor=vendor,
                        use_case_title=use_case_title,
                        use_case_description=use_case_description,
                        target_users=target_users,
                        target_industries=_join(target_industries),
                        target_departments=_join(target_departments),
                        maturity=maturity,
                        first_available=first_available,
                        business_value_score=business_value_score,
                        business_value_rationale=business_value_rationale,
                        roi_drivers=roi_drivers,
                        example_companies=example_companies,
                        source_url=source_url,
                        source_type=source_type,
                        notes=notes,
                    )
                )
                st.success(f"Added use case #{new_id}: {use_case_title}")

with tab_edit:
    st.subheader("Edit an existing use case")
    df = storage.load_use_cases()
    if df.empty:
        st.info("No use cases yet.")
    else:
        options = df.apply(lambda r: f"[{r['id']}] {r['tool_name']} — {r['use_case_title']}", axis=1)
        choice = st.selectbox("Select a use case to edit", options)
        selected_id = int(choice.split("]")[0][1:])
        row = df[df["id"] == selected_id].iloc[0]

        with st.form("edit_use_case_form"):
            category = st.text_input("Category", value=row["category"])
            tool_name = st.text_input("Tool", value=row["tool_name"])
            vendor = st.text_input("Vendor", value=row["vendor"])
            use_case_title = st.text_input("Use case title", value=row["use_case_title"])
            use_case_description = st.text_area("Use case description", value=row["use_case_description"])
            target_users = st.text_input("Target users", value=row["target_users"])
            target_industries = st.multiselect(
                "Target industries",
                sorted(set(taxonomy.industry_names()) | set(_split(row["target_industries"]))),
                default=_split(row["target_industries"]),
                accept_new_options=True,
            )
            target_departments = st.multiselect(
                "Target departments / business functions",
                sorted(set(taxonomy.department_names()) | set(_split(row.get("target_departments")))),
                default=_split(row.get("target_departments")),
                accept_new_options=True,
            )
            maturity = st.selectbox("Maturity", MATURITY_OPTIONS, index=MATURITY_OPTIONS.index(row["maturity"]) if row["maturity"] in MATURITY_OPTIONS else 0)
            first_available_value = pd.to_datetime(row["first_available"]).date() if pd.notna(row["first_available"]) else date.today()
            first_available = st.date_input("First available (approximate)", value=first_available_value)
            business_value_score = st.slider("Business value score", 1, 5, int(row["business_value_score"]))
            business_value_rationale = st.text_area("Business value rationale", value=row["business_value_rationale"])
            roi_drivers = st.text_input("ROI drivers", value=row["roi_drivers"])
            example_companies = st.text_input(
                "Example companies (semicolon-separated; use 'Not publicly disclosed' if unknown)",
                value=row["example_companies"] or "Not publicly disclosed",
            )
            source_url = st.text_input("Source URL(s) (semicolon-separated if more than one)", value=row["source_url"])
            source_type = st.selectbox("Source type", SOURCE_TYPE_OPTIONS, index=SOURCE_TYPE_OPTIONS.index(row["source_type"]) if row["source_type"] in SOURCE_TYPE_OPTIONS else 0)
            notes = st.text_area("Notes", value=row["notes"] or "")

            if st.form_submit_button("Save changes"):
                storage.update_use_case(
                    selected_id,
                    dict(
                        category=category,
                        tool_name=tool_name,
                        vendor=vendor,
                        use_case_title=use_case_title,
                        use_case_description=use_case_description,
                        target_users=target_users,
                        target_industries=_join(target_industries),
                        target_departments=_join(target_departments),
                        maturity=maturity,
                        first_available=first_available,
                        business_value_score=business_value_score,
                        business_value_rationale=business_value_rationale,
                        roi_drivers=roi_drivers,
                        example_companies=example_companies,
                        source_url=source_url,
                        source_type=source_type,
                        notes=notes,
                    ),
                )
                st.success(f"Updated use case #{selected_id}. `last_verified` set to today.")

with tab_cases:
    st.subheader("Company case studies")
    st.caption(
        "The other half of the picture: specific companies reporting concrete efficiency gains, "
        "and what they actually did — see the **Real-World Impact** page to browse this data."
    )
    cs_add, cs_edit = st.tabs(["Add new case study", "Edit existing"])

    with cs_add:
        with st.form("add_case_study_form", clear_on_submit=True):
            company_name = st.text_input("Company name")
            industry = st.selectbox("Industry", taxonomy.industry_names(), key="cs_add_industry")
            target_departments_cs = st.multiselect(
                "Departments / business functions involved",
                taxonomy.department_names(), accept_new_options=True, key="cs_add_depts",
            )
            tool_or_platform = st.text_input("Tool or platform (tracked name, or free text for proprietary/internal tools)")
            related_category = st.selectbox("Related category (if it maps cleanly)", [""] + taxonomy.category_names())
            what_they_did = st.text_area("What they did (2-4 sentences)")
            reported_efficiency_gain = st.text_area("Reported efficiency gain (as reported — % , $, or qualitative)")
            gain_type = st.text_input("Gain type (semicolon-separated, e.g. 'time saved; cost reduction; headcount efficiency')")
            confidence = st.selectbox("Confidence", CONFIDENCE_OPTIONS)
            fin_col1, fin_col2 = st.columns(2)
            with fin_col1:
                financial_impact_usd = st.number_input(
                    "Disclosed $ impact (USD/year, leave empty if not quantified)",
                    value=None, min_value=0.0, step=1000.0, key="cs_add_financial_usd",
                    help="Only fill this in when a specific dollar figure was actually reported — leave empty rather than estimating.",
                )
            with fin_col2:
                financial_impact_type = st.selectbox("Financial impact type", FINANCIAL_IMPACT_TYPE_OPTIONS, key="cs_add_financial_type")
            deployment_status = st.selectbox("Deployment status", DEPLOYMENT_STATUS_OPTIONS, key="cs_add_deployment_status")
            source_url = st.text_input("Source URL(s) (semicolon-separated if more than one)")
            source_type = st.selectbox("Source type", SOURCE_TYPE_OPTIONS, key="cs_add_source_type")
            date_reported = st.date_input("Date reported (approximate)", value=date.today())
            notes = st.text_area("Notes", key="cs_add_notes")

            if st.form_submit_button("Add case study"):
                if not company_name:
                    st.error("Company name is required.")
                else:
                    new_id = storage.insert_case_study(
                        dict(
                            company_name=company_name,
                            industry=industry,
                            target_departments=_join(target_departments_cs),
                            tool_or_platform=tool_or_platform,
                            related_category=related_category or None,
                            what_they_did=what_they_did,
                            reported_efficiency_gain=reported_efficiency_gain,
                            gain_type=gain_type,
                            confidence=confidence,
                            financial_impact_usd=financial_impact_usd,
                            financial_impact_type=financial_impact_type,
                            deployment_status=deployment_status,
                            source_url=source_url,
                            source_type=source_type,
                            date_reported=date_reported,
                            notes=notes,
                        )
                    )
                    st.success(f"Added case study #{new_id}: {company_name}")

    with cs_edit:
        cs_df = storage.load_case_studies()
        if cs_df.empty:
            st.info("No case studies yet.")
        else:
            cs_options = cs_df.apply(lambda r: f"[{r['id']}] {r['company_name']} — {r['tool_or_platform']}", axis=1)
            cs_choice = st.selectbox("Select a case study to edit", cs_options)
            cs_selected_id = int(cs_choice.split("]")[0][1:])
            cs_row = cs_df[cs_df["id"] == cs_selected_id].iloc[0]

            with st.form("edit_case_study_form"):
                company_name = st.text_input("Company name", value=cs_row["company_name"])
                industry_options = sorted(set(taxonomy.industry_names()) | {cs_row["industry"]})
                industry = st.selectbox("Industry", industry_options, index=industry_options.index(cs_row["industry"]))
                target_departments_cs = st.multiselect(
                    "Departments / business functions involved",
                    sorted(set(taxonomy.department_names()) | set(_split(cs_row.get("target_departments")))),
                    default=_split(cs_row.get("target_departments")),
                    accept_new_options=True,
                )
                tool_or_platform = st.text_input("Tool or platform", value=cs_row["tool_or_platform"])
                cat_options = [""] + taxonomy.category_names()
                related_category = st.selectbox(
                    "Related category (if it maps cleanly)", cat_options,
                    index=cat_options.index(cs_row["related_category"]) if cs_row["related_category"] in cat_options else 0,
                )
                what_they_did = st.text_area("What they did", value=cs_row["what_they_did"])
                reported_efficiency_gain = st.text_area("Reported efficiency gain", value=cs_row["reported_efficiency_gain"])
                gain_type = st.text_input("Gain type", value=cs_row["gain_type"])
                confidence = st.selectbox(
                    "Confidence", CONFIDENCE_OPTIONS,
                    index=CONFIDENCE_OPTIONS.index(cs_row["confidence"]) if cs_row["confidence"] in CONFIDENCE_OPTIONS else 0,
                )
                fin_col1, fin_col2 = st.columns(2)
                with fin_col1:
                    existing_financial_usd = cs_row.get("financial_impact_usd")
                    financial_impact_usd = st.number_input(
                        "Disclosed $ impact (USD/year, leave empty if not quantified)",
                        value=float(existing_financial_usd) if pd.notna(existing_financial_usd) else None,
                        min_value=0.0, step=1000.0,
                        help="Only fill this in when a specific dollar figure was actually reported — leave empty rather than estimating.",
                    )
                with fin_col2:
                    existing_financial_type = cs_row.get("financial_impact_type")
                    financial_impact_type = st.selectbox(
                        "Financial impact type", FINANCIAL_IMPACT_TYPE_OPTIONS,
                        index=FINANCIAL_IMPACT_TYPE_OPTIONS.index(existing_financial_type) if existing_financial_type in FINANCIAL_IMPACT_TYPE_OPTIONS else 0,
                    )
                existing_deployment_status = cs_row.get("deployment_status")
                deployment_status = st.selectbox(
                    "Deployment status", DEPLOYMENT_STATUS_OPTIONS,
                    index=DEPLOYMENT_STATUS_OPTIONS.index(existing_deployment_status) if existing_deployment_status in DEPLOYMENT_STATUS_OPTIONS else 0,
                )
                source_url = st.text_input("Source URL(s)", value=cs_row["source_url"])
                source_type = st.selectbox(
                    "Source type", SOURCE_TYPE_OPTIONS,
                    index=SOURCE_TYPE_OPTIONS.index(cs_row["source_type"]) if cs_row["source_type"] in SOURCE_TYPE_OPTIONS else 0,
                )
                date_reported_value = pd.to_datetime(cs_row["date_reported"]).date() if pd.notna(cs_row["date_reported"]) else date.today()
                date_reported = st.date_input("Date reported (approximate)", value=date_reported_value)
                notes = st.text_area("Notes", value=cs_row["notes"] or "")

                if st.form_submit_button("Save changes"):
                    storage.update_case_study(
                        cs_selected_id,
                        dict(
                            company_name=company_name,
                            industry=industry,
                            target_departments=_join(target_departments_cs),
                            tool_or_platform=tool_or_platform,
                            related_category=related_category or None,
                            what_they_did=what_they_did,
                            reported_efficiency_gain=reported_efficiency_gain,
                            gain_type=gain_type,
                            confidence=confidence,
                            financial_impact_usd=financial_impact_usd,
                            financial_impact_type=financial_impact_type,
                            deployment_status=deployment_status,
                            source_url=source_url,
                            source_type=source_type,
                            date_reported=date_reported,
                            notes=notes,
                        ),
                    )
                    st.success(f"Updated case study #{cs_selected_id}.")

with tab_admin:
    st.subheader("Admin")
    st.caption("Reloading wipes any manually added/edited entries and restores the curated seed dataset.")
    admin_col1, admin_col2, admin_col3 = st.columns(3)
    with admin_col1:
        if st.button("Reload use case seed data", type="secondary"):
            seed_path = Path(__file__).resolve().parent.parent / "data" / "seed" / "use_cases_seed.csv"
            count = storage.seed_from_csv(seed_path)
            st.success(f"Reloaded {count} use cases from the seed dataset.")
    with admin_col2:
        if st.button("Reload case study seed data", type="secondary"):
            cs_seed_path = Path(__file__).resolve().parent.parent / "data" / "seed" / "company_case_studies_seed.csv"
            count = storage.seed_case_studies_from_csv(cs_seed_path)
            st.success(f"Reloaded {count} company case studies from the seed dataset.")
    with admin_col3:
        if st.button("Reload market context seed data", type="secondary"):
            mc_seed_path = Path(__file__).resolve().parent.parent / "data" / "seed" / "market_context_seed.csv"
            count = storage.seed_market_context_from_csv(mc_seed_path)
            st.success(f"Reloaded {count} market context rows from the seed dataset.")

    admin_col4, admin_col5, admin_col6, admin_col7 = st.columns(4)
    seed_dir = Path(__file__).resolve().parent.parent / "data" / "seed"
    with admin_col4:
        if st.button("Reload topics & tagging", type="secondary"):
            storage.seed_topics_from_csv(seed_dir / "topics_seed.csv")
            count = storage.seed_use_case_topics_from_csv(seed_dir / "use_case_topics_seed.csv")
            st.success(f"Reloaded topics and {count} use-case tags from the seed dataset.")
    with admin_col5:
        if st.button("Reload achievements seed data", type="secondary"):
            count = storage.seed_achievements_from_csv(seed_dir / "achievements_seed.csv")
            st.success(f"Reloaded {count} achievements from the seed dataset.")
    with admin_col6:
        if st.button("Reload use case ↔ case study links", type="secondary"):
            count = storage.seed_links_from_csv(seed_dir / "use_case_case_study_links_seed.csv")
            st.success(f"Reloaded {count} links from the seed dataset.")
    with admin_col7:
        if st.button("Rebuild sources from existing data", type="secondary"):
            count = storage.backfill_sources_from_existing()
            st.success(f"Derived {count} source rows from use_cases/company_case_studies/market_context.")

    admin_col8, admin_col9 = st.columns(2)
    with admin_col8:
        if st.button("Reload agent catalog", type="secondary"):
            count = storage.seed_agents_from_csv(seed_dir / "agents_seed.csv")
            st.success(f"Reloaded {count} agents from the seed dataset.")
    with admin_col9:
        if st.button("Reload agent patterns & links", type="secondary"):
            storage.seed_agent_patterns_from_csv(seed_dir / "agent_patterns_seed.csv")
            count = storage.seed_agent_pattern_links_from_csv(seed_dir / "agent_pattern_links_seed.csv")
            st.success(f"Reloaded agent patterns and {count} agent/pattern links from the seed dataset.")

    st.divider()
    st.caption("Export the current datasets.")
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        df = storage.load_use_cases()
        st.download_button(
            "Export all use cases as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="use_cases_export.csv",
            mime="text/csv",
        )
    with exp_col2:
        cs_df = storage.load_case_studies()
        st.download_button(
            "Export all company case studies as CSV",
            cs_df.to_csv(index=False).encode("utf-8"),
            file_name="company_case_studies_export.csv",
            mime="text/csv",
        )
    with exp_col3:
        mc_df = storage.load_market_context()
        st.download_button(
            "Export market context as CSV",
            mc_df.to_csv(index=False).encode("utf-8"),
            file_name="market_context_export.csv",
            mime="text/csv",
        )

    exp_col4, exp_col5, exp_col6 = st.columns(3)
    with exp_col4:
        topics_joined_df = storage.load_use_case_topics_joined()
        st.download_button(
            "Export use-case topic tags as CSV",
            topics_joined_df.to_csv(index=False).encode("utf-8"),
            file_name="use_case_topics_export.csv",
            mime="text/csv",
        )
    with exp_col5:
        achievements_df = storage.load_achievements()
        st.download_button(
            "Export achievements as CSV",
            achievements_df.to_csv(index=False).encode("utf-8"),
            file_name="achievements_export.csv",
            mime="text/csv",
        )
    with exp_col6:
        sources_df = storage.load_sources()
        st.download_button(
            "Export sources as CSV",
            sources_df.to_csv(index=False).encode("utf-8"),
            file_name="sources_export.csv",
            mime="text/csv",
        )

    exp_col7, exp_col8 = st.columns(2)
    with exp_col7:
        agents_df = storage.load_agents()
        st.download_button(
            "Export agent catalog as CSV",
            agents_df.to_csv(index=False).encode("utf-8"),
            file_name="agents_export.csv",
            mime="text/csv",
        )
    with exp_col8:
        agent_links_df = storage.load_agent_pattern_links_joined()
        st.download_button(
            "Export agent/pattern links as CSV",
            agent_links_df.to_csv(index=False).encode("utf-8"),
            file_name="agent_pattern_links_export.csv",
            mime="text/csv",
        )
