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
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in API keys as needed
```

## Data model & running the app

See `REQUIREMENTS.md` for the full spec. Each row is a single **use case** of an agentic-AI tool, scored 1-5 for business value with a sourced rationale, tagged with the **industries** (Automotive, Retail/E-commerce, Energy/Utilities, Manufacturing/Industrial, Financial Services, ...) and **departments/business functions** (Sales, After-Sales/Service, IT, R&D/Engineering, Customer Support, ...) it's relevant to. A separate `company_case_studies` table tracks specific companies that have publicly reported concrete results, tagged the same way. The taxonomy of categories/tools/industries/departments lives in `config/taxonomy.yaml` — extend it there without touching code (the industry/department fields also accept free text beyond that list).

Data is stored in a local DuckDB file (`data/processed/usecases.duckdb`), loaded from the curated seed datasets at `data/seed/use_cases_seed.csv`, `data/seed/company_case_studies_seed.csv`, and `data/seed/market_context_seed.csv` (macro investment/ROI reference figures). The seed data is AI-curated from general knowledge and flagged as needing source verification — treat scores/sources as a starting point, not ground truth.

Load the seed data once (idempotent — safe to re-run):

```bash
python -m scripts.seed_db
```

Then launch the app:

```bash
streamlit run app.py
```

- **Data Collection** page — add or edit use cases and company case studies, or reload the seed datasets.
- **Explore Data** page — filter/search the catalog (including by industry and department) and inspect full use case details.
- **Analysis** page — category/maturity/ROI-driver/department breakdowns and charts, plus an over-time section (category/department growth).
- **Trends & Industries** page — adoption over time (including industry growth over time), industry breakdowns, an industry × department mapping (heatmap + browsable pairs), and a **Forecast & Momentum** section: naive linear-trend extrapolation by category/industry/department with "fastest-growing" vs. "largest/most established" leaderboards — explicitly labeled illustrative, not a statistical forecast, given the dataset's size.
- **Real-World Impact** page — what companies are actually doing: browsable, filterable company case studies with an industry × department evidence heatmap and an over-time view (case studies by year, deployment-status mix by year). Carries a persistent disclaimer — this data is knowledge-based and not independently re-verified.
- **Revenue & ROI+** page — how much of that real-world evidence is actually quantified in dollar terms (most isn't, including its trend by year), disclosed $ impact by industry/department, a pilot → scaled → reversed → discontinued deployment-status breakdown, and macro market-size/investment-vs-realized-ROI context. No forward projection here (too few quantified data points to extrapolate honestly) — that's what the Trends & Industries forecast is for.
- **Growth & Opportunities** page — a value × growth × maturity bubble chart across every category/industry/department (nothing truncated to a top-N), an opportunity finder surfacing department patterns proven valuable elsewhere but barely applied in a given industry yet, and a maturity-readiness ranking cross-checked against real scaled deployments from the Real-World Impact data.

All time-series charts reuse the same `first_available` (use cases) / `date_reported` (case studies) fields already in the schema — no new date fields were needed to add them.
