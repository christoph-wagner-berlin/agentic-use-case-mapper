import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
import plotly.express as px

from src import storage

st.set_page_config(page_title="Agent Catalog & Patterns", layout="wide")
st.title("Agent Catalog & Patterns")
st.warning(
    "This dataset is knowledge-based and **not independently re-verified**. Autonomy level, interface, "
    "and open-source status are AI-recalled from general public knowledge as of 2026-08 and may be stale "
    "or imprecise -- check the source before citing anything here externally.",
    icon="⚠️",
)
st.caption(
    "Which agents exist, what kind of agent each one is, and which underlying design patterns "
    "(per Anthropic's *Building Effective Agents* framework plus the ReAct, reflection, multi-agent, "
    "and human-in-the-loop patterns from broader practice) they're actually built on."
)

agents = storage.load_agents()
patterns = storage.load_agent_patterns()
links = storage.load_agent_pattern_links_joined()

if agents.empty or patterns.empty:
    st.warning("No agent catalog yet. Run `python -m scripts.seed_db` to load the curated seed dataset.")
    st.stop()

patterns_by_agent = links.groupby("agent_id")["pattern_name"].apply(list) if not links.empty else pd.Series(dtype=object)

st.divider()
st.header("Agent catalog")
st.caption(f"{len(agents)} agents tracked across {agents['category'].nunique()} categories.")

catalog_df = agents.copy()
catalog_df["patterns"] = catalog_df["id"].map(lambda i: "; ".join(patterns_by_agent.get(i, [])))

st.dataframe(
    catalog_df[
        [
            "name",
            "vendor",
            "category",
            "autonomy_level",
            "interface",
            "open_source",
            "release_year",
            "patterns",
            "description",
        ]
    ],
    width="stretch",
    hide_index=True,
    column_config={
        "name": st.column_config.TextColumn("Agent"),
        "autonomy_level": st.column_config.TextColumn("Autonomy"),
        "open_source": st.column_config.TextColumn("Open source"),
        "release_year": st.column_config.NumberColumn("Released", format="%d"),
        "patterns": st.column_config.TextColumn("Patterns used", width="medium"),
        "description": st.column_config.TextColumn("Description", width="large"),
    },
)

st.download_button(
    "Download agent catalog as CSV",
    catalog_df.to_csv(index=False).encode("utf-8"),
    file_name="agents_export.csv",
    mime="text/csv",
)

st.divider()
st.header("Which patterns are common -- and proven -- across these agents")
pattern_counts = (
    links.groupby("pattern_name").size().reset_index(name="agent_count").sort_values("agent_count", ascending=False)
    if not links.empty
    else pd.DataFrame(columns=["pattern_name", "agent_count"])
)
col_chart, col_matrix = st.columns([1, 2])
with col_chart:
    st.subheader("Pattern adoption")
    fig = px.bar(pattern_counts, x="agent_count", y="pattern_name", orientation="h", text="agent_count")
    fig.update_layout(xaxis_title="Agents using this pattern", yaxis_title="", yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, width="stretch")
with col_matrix:
    st.subheader("Agents × Patterns")
    if links.empty:
        st.info("No agent/pattern links yet.")
    else:
        matrix = links.assign(present=1).pivot_table(
            index="agent_name", columns="pattern_name", values="present", fill_value=0
        )
        fig = px.imshow(
            matrix,
            labels=dict(x="Pattern", y="Agent", color="Uses pattern"),
            color_continuous_scale="Purples",
            aspect="auto",
        )
        fig.update_layout(height=600, coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")

st.divider()
st.header("Pattern reference")
st.caption("What each pattern is, and when it actually works well -- with a source, and a live count of how many cataloged agents use it.")
for _, row in patterns.iterrows():
    count = int(pattern_counts.set_index("pattern_name")["agent_count"].get(row["name"], 0)) if not pattern_counts.empty else 0
    with st.expander(f"{row['name']} -- used by {count} of {len(agents)} agents"):
        st.write(row["description"])
        st.markdown(f"**When it works well:** {row['when_it_works_well']}")
        if pd.notna(row.get("source_url")):
            st.markdown(f"**Source:** [{row['source_url']}]({row['source_url']}) ({row['source_type']})")
