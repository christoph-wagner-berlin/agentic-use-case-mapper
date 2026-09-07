import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px

from src import storage
from src.analysis import summaries
from src.viz import DEPARTMENT_ORDER, COMPANY_SIZE_ORDER, BRAND_BLUE, ordered_with_extras

st.set_page_config(page_title="Startup Vendors", layout="wide")
st.title("Enterprise Workflow AI Startups")
st.warning(
    "Engagement model and pricing details are sourced from vendor sites and third-party estimates "
    "as of research date (2026-09) -- several pricing/funding figures are third-party estimates, not "
    "vendor-confirmed. Check `confidence` and the source before citing anything here externally.",
    icon="⚠️",
)
st.caption(
    "Distinct from Real-World Impact: that page tracks companies that **use** AI tools. This page "
    "tracks the AI **vendors/startups** themselves -- who they're really built for, and what actually "
    "happens if you try to engage them."
)

startups = storage.load_enterprise_ai_startups()
case_studies = storage.load_case_studies()

if startups.empty:
    st.warning("No startup vendors yet. Run `python -m scripts.seed_db` to load the curated seed dataset.")
    st.stop()

all_departments = ordered_with_extras(
    DEPARTMENT_ORDER, set(startups["target_departments"].dropna().str.split(";").explode().str.strip()) - {""}
)
all_company_sizes = ordered_with_extras(
    COMPANY_SIZE_ORDER, set(startups["target_company_size"].dropna().str.split(";").explode().str.strip()) - {""}
)

with st.sidebar:
    st.header("Filters")
    departments = st.multiselect("Department / workflow", all_departments)
    company_sizes = st.multiselect("Company size", all_company_sizes)

filtered = startups.copy()
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

st.caption(f"{len(filtered)} of {len(startups)} startups match the current filters.")
if (departments or company_sizes) and filtered.empty:
    st.info(
        "No startup vendors tagged for this combination yet -- a real gap in this dataset, not a bug. "
        "Try widening the department or company-size filter."
    )

st.divider()
st.header("Vendors by department / workflow")
dept_counts = summaries.department_counts(filtered)
if dept_counts.empty:
    st.info("No startup vendors match the current filters.")
else:
    fig = px.bar(
        dept_counts, x="department", y="count", text="count",
        category_orders={"department": DEPARTMENT_ORDER}, color_discrete_sequence=[BRAND_BLUE],
    )
    fig.update_layout(xaxis_title="", yaxis_title="Startup vendors")
    st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Startup catalog")
st.dataframe(
    filtered[
        [
            "company_name",
            "product_name",
            "target_departments",
            "target_company_size",
            "engagement_model",
            "funding_stage",
            "confidence",
        ]
    ],
    width="stretch",
    hide_index=True,
    column_config={
        "company_name": st.column_config.TextColumn("Company"),
        "product_name": st.column_config.TextColumn("Product"),
        "target_departments": st.column_config.TextColumn("Department"),
        "target_company_size": st.column_config.TextColumn("Company size"),
        "engagement_model": st.column_config.TextColumn("Engagement model", width="large"),
        "funding_stage": st.column_config.TextColumn("Funding", width="medium"),
    },
)

st.download_button(
    "Download startup vendors as CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="enterprise_ai_startups_filtered.csv",
    mime="text/csv",
)

st.divider()
st.header("Vendor detail")
for _, row in filtered.sort_values("company_name").iterrows():
    with st.expander(f"{row['company_name']} — {row['product_name']} ({row['target_departments']})"):
        st.markdown(f"### 📞 What they want you to do")
        st.markdown(row["engagement_model"])
        st.markdown(f"**What they do:** {row['what_they_do']}")
        st.markdown(f"**Built for:** {row['target_company_size']}")
        st.markdown(f"**Pricing signal:** {row['pricing_signal']}")
        st.markdown(f"**Funding stage:** {row['funding_stage']}")
        if row.get("notable_customers"):
            st.markdown(f"**Notable customers:** {row['notable_customers']}")

        if not case_studies.empty:
            related = case_studies[
                case_studies["tool_or_platform"].str.contains(row["company_name"], case=False, na=False, regex=False)
                | case_studies["tool_or_platform"].str.contains(row["product_name"], case=False, na=False, regex=False)
            ]
            if not related.empty:
                st.markdown("**Already in this dataset's Real-World Impact case studies:**")
                for _, cs_row in related.iterrows():
                    st.markdown(f"- {cs_row['company_name']} ({cs_row['industry']}) — *{cs_row['reported_efficiency_gain']}*")

        urls = [u.strip() for u in str(row["source_url"]).split(";") if u.strip()]
        sources_md = " · ".join(f"[{u}]({u})" for u in urls)
        st.markdown(f"**Sources:** {sources_md} ({row['source_type']})")
        st.caption(f"Confidence: {row['confidence']}  ·  Last verified: {row['last_verified']}")
        if row["notes"]:
            st.info(row["notes"])
