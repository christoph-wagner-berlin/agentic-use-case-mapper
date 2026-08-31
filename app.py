import pandas as pd
import streamlit as st

from src import storage

st.set_page_config(page_title="Agentic Use Case Map", layout="wide")
st.title("Agentic Use Case Map")
st.write("Use the sidebar to collect data, explore results, or view analysis.")

df = storage.load_use_cases()

if df.empty:
    st.warning("No data yet. Run `python -m scripts.seed_db` from the project root to load the curated seed dataset.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Use cases", len(df))
    col2.metric("Categories", df["category"].nunique())
    col3.metric("Tools", df["tool_name"].nunique())
    col4.metric("Avg. business value score", round(df["business_value_score"].mean(), 2))

    col5, col6, col7 = st.columns(3)
    industries = df["target_industries"].dropna().str.split(";").explode().str.strip()
    col5.metric("Industries covered", industries[industries != ""].nunique())
    departments = df["target_departments"].dropna().str.split(";").explode().str.strip()
    col6.metric("Departments covered", departments[departments != ""].nunique())
    first_available = pd.to_datetime(df["first_available"])
    col7.metric(
        "Use cases span",
        f"{first_available.dt.year.min()}–{first_available.dt.year.max()}",
    )

    st.divider()
    st.subheader("Use cases per category")
    st.bar_chart(df.groupby("category").size())
