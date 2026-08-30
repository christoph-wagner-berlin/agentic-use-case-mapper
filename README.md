# Agentic Use Case Map

A research project for collecting, exploring, and analyzing real-world agentic AI use cases.

## Structure

- `app.py` — Streamlit entry point.
- `pages/` — additional Streamlit pages (data collection, exploration, analysis).
- `src/collectors/` — fetch data from sources (APIs, web pages, search).
- `src/processors/` — clean & normalize collected data.
- `src/analysis/` — analysis functions, importable from pages and testable standalone.
- `src/storage.py` — save/load data (sqlite or duckdb), shared by CLI and Streamlit.
- `data/raw/` — untouched collected data.
- `data/processed/` — cleaned/normalized data.
- `notebooks/` — exploratory analysis.
- `tests/` — test suite.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in API keys as needed
```

## Run

```bash
streamlit run app.py
```
