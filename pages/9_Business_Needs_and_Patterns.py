import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src import storage
from src.viz import (
    CATEGORY_ORDER, INDUSTRY_ORDER, DEPARTMENT_ORDER, COMPANY_SIZE_ORDER, MATURITY_ORDER,
    CATEGORY_COLORS, OTHER_COLOR, SEQUENTIAL_BLUE, ordered_with_extras,
)

st.set_page_config(page_title="Business Needs & Patterns", layout="wide")
st.title("Business Needs & Patterns")
st.caption(
    "The **Explore Data** page maps use cases to a specific tool. This page steps back from that: "
    "a **business need** is a raw problem that may not have any tool yet, a **tool-agnostic use case "
    "pattern** is a proven generic shape of solution (e.g. 'AI-assisted code review') independent of "
    "any vendor, and a tool-mapped use case (Explore Data) is one specific product's implementation "
    "of that pattern. A need can link straight to a tool-mapped use case, or via a pattern in between."
)

business_needs = storage.load_business_needs()
patterns = storage.load_tool_agnostic_use_cases()
need_pattern_links = storage.load_business_need_pattern_links_joined()
need_use_case_links = storage.load_business_need_use_case_links_joined()
pattern_use_case_links = storage.load_pattern_use_case_links_joined()

STATUS_ORDER = ["unmet", "partially addressed", "addressed"]
STATUS_COLORS = {"unmet": "#d03b3b", "partially addressed": "#fab219", "addressed": "#0ca30c"}
TOOL_NODE_COLOR = SEQUENTIAL_BLUE[2]

st.divider()
st.header("🗺️ Need → pattern → tool map")
st.caption(
    "Every business need's path toward a solution: straight to a specific tool-mapped use case, "
    "via a tool-agnostic pattern, or not yet linked to either. Ribbon color follows the need's "
    "status; pattern nodes are colored by category. Hover any node or ribbon for detail."
)

if business_needs.empty:
    st.info("No business needs cataloged yet — nothing to diagram.")
else:
    def _truncate(text, n=46):
        text = str(text)
        return text if len(text) <= n else text[: n - 1].rstrip() + "…"

    def _rgba(hex_color, alpha):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        return f"rgba({r},{g},{b},{alpha})"

    def _swatch(hex_color, label):
        return (
            f'<span style="display:inline-block;width:10px;height:10px;border-radius:2px;'
            f'background:{hex_color};margin-right:4px;"></span>{label}'
        )

    needs_indexed = business_needs.set_index("id")
    patterns_indexed = patterns.set_index("id")

    node_labels, node_full, node_colors = [], [], []
    need_node_idx, pattern_node_idx, tool_node_idx = {}, {}, {}

    for need_id, row in needs_indexed.iterrows():
        need_node_idx[need_id] = len(node_labels)
        node_labels.append(_truncate(row["need_title"]))
        node_full.append(f"{row['need_title']}<br>Status: {row['status']}")
        node_colors.append(STATUS_COLORS.get(row["status"], OTHER_COLOR))

    for pattern_id, row in patterns_indexed.iterrows():
        pattern_node_idx[pattern_id] = len(node_labels)
        node_labels.append(_truncate(row["use_case_title"]))
        node_full.append(f"{row['use_case_title']}<br>Category: {row['category']}")
        node_colors.append(CATEGORY_COLORS.get(row["category"], OTHER_COLOR))

    not_linked_idx = len(node_labels)
    node_labels.append("Not yet linked")
    node_full.append("No pattern or tool-mapped use case linked yet")
    node_colors.append(OTHER_COLOR)

    def _tool_idx(tool_name):
        if tool_name not in tool_node_idx:
            tool_node_idx[tool_name] = len(node_labels)
            node_labels.append(tool_name)
            node_full.append(f"{tool_name} (tool-mapped use case)")
            node_colors.append(TOOL_NODE_COLOR)
        return tool_node_idx[tool_name]

    for _, row in pattern_use_case_links.iterrows():
        _tool_idx(row["tool_name"])
    for _, row in need_use_case_links.iterrows():
        _tool_idx(row["tool_name"])

    sources, targets, values, link_colors, link_hover = [], [], [], [], []
    linked_need_ids = set()

    for _, row in need_pattern_links.iterrows():
        need_id, pattern_id = row["business_need_id"], row["tool_agnostic_use_case_id"]
        linked_need_ids.add(need_id)
        sources.append(need_node_idx[need_id])
        targets.append(pattern_node_idx[pattern_id])
        values.append(1)
        link_colors.append(_rgba(STATUS_COLORS.get(needs_indexed.loc[need_id, "status"], OTHER_COLOR), 0.4))
        link_hover.append(f"{row['need_title']} → matches pattern: {row['pattern_title']}")

    for _, row in need_use_case_links.iterrows():
        need_id = row["business_need_id"]
        linked_need_ids.add(need_id)
        sources.append(need_node_idx[need_id])
        targets.append(_tool_idx(row["tool_name"]))
        values.append(1)
        link_colors.append(_rgba(STATUS_COLORS.get(needs_indexed.loc[need_id, "status"], OTHER_COLOR), 0.4))
        link_hover.append(
            f"{row['need_title']} → directly addressed by {row['tool_name']}: "
            f"{row['use_case_title']} ({row['match_type']})"
        )

    for need_id, row in needs_indexed.iterrows():
        if need_id not in linked_need_ids:
            sources.append(need_node_idx[need_id])
            targets.append(not_linked_idx)
            values.append(1)
            link_colors.append(_rgba(STATUS_COLORS.get(row["status"], OTHER_COLOR), 0.4))
            link_hover.append(f"{row['need_title']} — not yet linked to a pattern or tool-mapped use case")

    for _, row in pattern_use_case_links.iterrows():
        pattern_id = row["tool_agnostic_use_case_id"]
        sources.append(pattern_node_idx[pattern_id])
        targets.append(_tool_idx(row["tool_name"]))
        values.append(1)
        cat = patterns_indexed.loc[pattern_id, "category"]
        link_colors.append(_rgba(CATEGORY_COLORS.get(cat, OTHER_COLOR), 0.4))
        link_hover.append(
            f"{row['pattern_title']} → implemented by {row['tool_name']}: "
            f"{row['use_case_title']} ({row['match_type']})"
        )

    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(
                label=node_labels,
                customdata=node_full,
                hovertemplate="%{customdata}<extra></extra>",
                color=node_colors,
                pad=14,
                thickness=16,
                line=dict(width=0),
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors,
                customdata=link_hover,
                hovertemplate="%{customdata}<extra></extra>",
            ),
        )
    )
    fig.update_layout(height=560, margin=dict(l=10, r=10, t=10, b=10), font_size=12)
    st.plotly_chart(fig, width="stretch")

    present_categories = [c for c in CATEGORY_ORDER if c in patterns["category"].unique()]
    legend_bits = [_swatch(STATUS_COLORS[s], s) for s in STATUS_ORDER]
    legend_bits += [_swatch(CATEGORY_COLORS[c], c) for c in present_categories]
    legend_bits += [_swatch(TOOL_NODE_COLOR, "Tool-mapped use case"), _swatch(OTHER_COLOR, "Not yet linked")]
    st.markdown(
        '<div style="font-size:0.85rem;line-height:2;">' + " &nbsp;&nbsp; ".join(legend_bits) + "</div>",
        unsafe_allow_html=True,
    )

st.divider()
st.header("🧩 Business needs")
st.caption("Business problems/opportunities worth solving with agentic AI, tracked independently of whether a tool addresses them yet.")

if business_needs.empty:
    st.info(
        "No business needs cataloged yet. Add rows to `data/seed/business_needs_seed.csv` "
        "(and re-run `python -m scripts.seed_db`) to start populating this catalog."
    )
else:
    need_industries = ordered_with_extras(
        INDUSTRY_ORDER,
        set(business_needs["target_industries"].dropna().str.split(";").explode().str.strip()) - {""},
    )
    need_departments = ordered_with_extras(
        DEPARTMENT_ORDER,
        set(business_needs["target_departments"].dropna().str.split(";").explode().str.strip()) - {""},
    )
    need_company_sizes = ordered_with_extras(
        COMPANY_SIZE_ORDER,
        set(business_needs["target_company_size"].dropna().str.split(";").explode().str.strip()) - {""},
    )

    with st.sidebar:
        st.header("Business need filters")
        statuses = st.multiselect("Status", ordered_with_extras(STATUS_ORDER, business_needs["status"].dropna().unique()))
        need_ind_filter = st.multiselect("Industry (needs)", need_industries)
        need_dept_filter = st.multiselect("Department (needs)", need_departments)
        need_size_filter = st.multiselect("Company size (needs)", need_company_sizes)
        need_min_score = st.slider("Minimum business value score (needs)", 1, 5, 1)

    filtered_needs = business_needs.copy()
    if statuses:
        filtered_needs = filtered_needs[filtered_needs["status"].isin(statuses)]
    if need_ind_filter:
        filtered_needs = filtered_needs[
            filtered_needs["target_industries"].apply(
                lambda v: any(i in [p.strip() for p in str(v).split(";")] for i in need_ind_filter)
            )
        ]
    if need_dept_filter:
        filtered_needs = filtered_needs[
            filtered_needs["target_departments"].apply(
                lambda v: any(d in [p.strip() for p in str(v).split(";")] for d in need_dept_filter)
            )
        ]
    if need_size_filter:
        filtered_needs = filtered_needs[
            filtered_needs["target_company_size"].apply(
                lambda v: any(s in [p.strip() for p in str(v).split(";")] for s in need_size_filter)
            )
        ]
    filtered_needs = filtered_needs[filtered_needs["business_value_score"].fillna(0) >= need_min_score]

    st.caption(f"{len(filtered_needs)} of {len(business_needs)} business needs match the current filters.")

    st.dataframe(
        filtered_needs[
            [
                "need_title", "need_description", "status", "business_value_score",
                "target_industries", "target_departments", "target_company_size",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "need_description": st.column_config.TextColumn("Description", width="large"),
            "target_industries": st.column_config.TextColumn("Industries"),
            "target_departments": st.column_config.TextColumn("Departments"),
            "target_company_size": st.column_config.TextColumn("Company size"),
        },
    )

    if not filtered_needs.empty:
        options = filtered_needs.apply(lambda r: f"[{r['id']}] {r['need_title']}", axis=1)
        choice = st.selectbox("Select a business need", options)
        selected_id = int(choice.split("]")[0][1:])
        row = filtered_needs[filtered_needs["id"] == selected_id].iloc[0]

        st.markdown(f"### {row['need_title']}")
        st.markdown(f"**Status:** {row['status']} &nbsp;|&nbsp; **Business value score:** {row['business_value_score']}/5")
        st.write(row["need_description"])
        st.markdown(f"**Rationale:** {row['business_value_rationale']}")
        st.markdown(f"**Target industries:** {row['target_industries']}")
        st.markdown(f"**Target departments:** {row['target_departments']}")

        related_patterns = need_pattern_links[need_pattern_links["business_need_id"] == selected_id] if not need_pattern_links.empty else need_pattern_links
        related_use_cases = need_use_case_links[need_use_case_links["business_need_id"] == selected_id] if not need_use_case_links.empty else need_use_case_links

        if not related_patterns.empty or not related_use_cases.empty:
            st.markdown("**Path toward a solution:**")
            for _, link_row in related_patterns.iterrows():
                st.markdown(f"- Matches pattern *{link_row['pattern_title']}*")
            for _, link_row in related_use_cases.iterrows():
                st.markdown(f"- Directly addressed by **{link_row['tool_name']}** — {link_row['use_case_title']} (*{link_row['match_type']}*)")
        else:
            st.info("Not yet linked to a pattern or a specific tool-mapped use case.")

        if pd.notna(row.get("source_url")):
            urls = [u.strip() for u in str(row["source_url"]).split(";") if u.strip()]
            if urls:
                sources_md = " · ".join(f"[{u}]({u})" for u in urls)
                st.markdown(f"**Sources:** {sources_md} ({row['source_type']})")
        if row.get("notes"):
            st.caption(row["notes"])

st.divider()
st.header("🧬 Tool-agnostic use case patterns")
st.caption("Proven generic use-case shapes, independent of any single vendor's product -- the pattern several specific tools may implement.")

if patterns.empty:
    st.info(
        "No tool-agnostic patterns cataloged yet. Add rows to `data/seed/tool_agnostic_use_cases_seed.csv` "
        "(and re-run `python -m scripts.seed_db`) to start populating this catalog."
    )
else:
    pattern_industries = ordered_with_extras(
        INDUSTRY_ORDER,
        set(patterns["target_industries"].dropna().str.split(";").explode().str.strip()) - {""},
    )
    pattern_departments = ordered_with_extras(
        DEPARTMENT_ORDER,
        set(patterns["target_departments"].dropna().str.split(";").explode().str.strip()) - {""},
    )
    pattern_company_sizes = ordered_with_extras(
        COMPANY_SIZE_ORDER,
        set(patterns["target_company_size"].dropna().str.split(";").explode().str.strip()) - {""},
    )

    with st.sidebar:
        st.header("Pattern filters")
        pattern_categories = st.multiselect("Category (patterns)", ordered_with_extras(CATEGORY_ORDER, patterns["category"].dropna().unique()))
        pattern_maturities = st.multiselect("Maturity (patterns)", ordered_with_extras(MATURITY_ORDER, patterns["maturity"].dropna().unique()))
        pattern_ind_filter = st.multiselect("Industry (patterns)", pattern_industries)
        pattern_dept_filter = st.multiselect("Department (patterns)", pattern_departments)
        pattern_size_filter = st.multiselect("Company size (patterns)", pattern_company_sizes)
        pattern_min_score = st.slider("Minimum business value score (patterns)", 1, 5, 1)

    filtered_patterns = patterns.copy()
    if pattern_categories:
        filtered_patterns = filtered_patterns[filtered_patterns["category"].isin(pattern_categories)]
    if pattern_maturities:
        filtered_patterns = filtered_patterns[filtered_patterns["maturity"].isin(pattern_maturities)]
    if pattern_ind_filter:
        filtered_patterns = filtered_patterns[
            filtered_patterns["target_industries"].apply(
                lambda v: any(i in [p.strip() for p in str(v).split(";")] for i in pattern_ind_filter)
            )
        ]
    if pattern_dept_filter:
        filtered_patterns = filtered_patterns[
            filtered_patterns["target_departments"].apply(
                lambda v: any(d in [p.strip() for p in str(v).split(";")] for d in pattern_dept_filter)
            )
        ]
    if pattern_size_filter:
        filtered_patterns = filtered_patterns[
            filtered_patterns["target_company_size"].apply(
                lambda v: any(s in [p.strip() for p in str(v).split(";")] for s in pattern_size_filter)
            )
        ]
    filtered_patterns = filtered_patterns[filtered_patterns["business_value_score"].fillna(0) >= pattern_min_score]

    st.caption(f"{len(filtered_patterns)} of {len(patterns)} patterns match the current filters.")

    use_cases_by_pattern = (
        pattern_use_case_links.groupby("tool_agnostic_use_case_id")
        .apply(lambda g: list(zip(g["tool_name"], g["use_case_title"], g["match_type"])))
        if not pattern_use_case_links.empty
        else pd.Series(dtype=object)
    )

    for _, row in filtered_patterns.iterrows():
        implementations = use_cases_by_pattern.get(row["id"], [])
        with st.expander(f"{row['use_case_title']} -- implemented by {len(implementations)} tool-mapped use case(s)"):
            st.markdown(f"**Category:** {row['category']} &nbsp;|&nbsp; **Maturity:** {row['maturity']}")
            st.write(row["use_case_description"])
            st.markdown(f"**Business value score:** {row['business_value_score']}/5 -- {row['business_value_rationale']}")
            st.markdown(f"**ROI drivers:** {row['roi_drivers']}")
            if implementations:
                st.markdown("**Implemented by:**")
                for tool_name, use_case_title, match_type in implementations:
                    st.markdown(f"- **{tool_name}** — {use_case_title} (*{match_type}*)")
            if pd.notna(row.get("source_url")):
                urls = [u.strip() for u in str(row["source_url"]).split(";") if u.strip()]
                if urls:
                    sources_md = " · ".join(f"[{u}]({u})" for u in urls)
                    st.markdown(f"**Sources:** {sources_md} ({row['source_type']})")
