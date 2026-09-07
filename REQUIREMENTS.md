# Agentic Use Case Map — Requirements

## 1. Project Goal

Build a research tool that catalogs known real-world use cases of AI agents across the agentic-AI landscape, organized by category and underlying tool/platform, and scores each use case by estimated business/ROI value — so the data can be explored, filtered, and compared through a Streamlit dashboard.

The end result should let someone answer questions like:
- "What are all known use cases for coding agents, and which deliver the most business value?"
- "Which category of agentic tools has the most high-value, proven use cases today?"
- "What use cases exist for Tool X specifically?"

## 2. Scope

### 2.1 Categories and tools to cover

| Category | Tools in scope |
|---|---|
| Coding/dev agents | Claude Code, GitHub Copilot Workspace, Cursor, Cline, Aider, OpenAI Codex CLI, Devin (Cognition) |
| General-purpose/browser agents | Claude with computer use, OpenAI Operator/ChatGPT agent mode, Google Project Mariner, Manus |
| Research/multi-step task agents | Perplexity, ChatGPT Deep Research, Claude Research mode, AutoGPT/BabyAGI (legacy) |
| Enterprise/workflow agents | LangChain/LangGraph, CrewAI, AutoGen (Microsoft), OpenAI Assistants API/Agents SDK, Claude Agent SDK |

This list is a starting point, not fixed — the tool should support adding new categories and tools without a schema change.

### 2.2 Unit of data: the "use case"

The core entity is not the tool itself but a **specific use case** of that tool — e.g. for Claude Code: "automated PR review and inline code fixes," or for CrewAI: "multi-agent customer support ticket triage." Each tool will typically have multiple use cases.

### 2.3 Out of scope (for v1)

- Real-time/live pricing data (capture pricing model qualitatively, not exact numbers that go stale)
- Benchmarking or hands-on testing of the tools
- Non-English sources (can be added later)

## 3. Data Schema

Each row in the dataset represents one **use case** with the following fields:

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier |
| `category` | text | One of the four categories above (extensible) |
| `tool_name` | text | The agent/platform name (e.g. "Claude Code") |
| `vendor` | text | Company behind the tool (e.g. "Anthropic") |
| `use_case_title` | text | Short name of the use case (e.g. "Automated PR review") |
| `use_case_description` | text | 2–4 sentence description of what it does and how |
| `target_users` | text | Who uses this (e.g. "software engineering teams," "enterprise ops") |
| `maturity` | enum | `experimental`, `emerging`, `mainstream`, `enterprise-standard` |
| `business_value_score` | integer (1–5) | See scoring rubric below |
| `business_value_rationale` | text | 1–3 sentence justification for the score |
| `roi_drivers` | text | Short tags of *how* value is created (e.g. "time saved," "cost reduction," "quality improvement," "revenue enablement") |
| `example_companies` | text | Semicolon-separated companies known to use this use case, or `Not publicly disclosed` when no specific company is confidently known |
| `source_url` | text | Link(s) to where this use case was documented/found. May contain multiple `; `-separated URLs |
| `source_type` | enum | `vendor_docs`, `case_study`, `news_article`, `community_report`, `academic` |
| `collected_at` | timestamp | When the record was collected |
| `last_verified` | date | Last time the info was checked for staleness |
| `notes` | text | Free-form notes, caveats, contradicting info |
| `first_available` | date | Approximate month the tool/use case first became publicly available (estimated from known launch/GA milestones) |
| `target_industries` | text | Semicolon-separated industries most relevant to this use case (e.g. "Software/Technology", "Automotive", "Energy/Utilities", "Cross-industry"). Suggested vocabulary lives in `config/taxonomy.yaml` (`industries`); free text beyond that list is accepted. |
| `target_departments` | text | Semicolon-separated business functions/departments this use case serves (e.g. "Sales", "After-Sales/Service", "IT", "R&D/Engineering", "Cross-functional"). Suggested vocabulary lives in `config/taxonomy.yaml` (`departments`); free text beyond that list is accepted. |
| `target_company_size` | text | Semicolon-separated company-size/revenue bands this tool/use case is realistically adoptable by (e.g. "SMB (<$10M)", "Mid-market ($10M-$100M)"). Suggested vocabulary lives in `config/taxonomy.yaml` (`company_size_bands`); free text beyond that list is accepted. Most rows default to all bands where no size signal is evident -- this is an honest "unknown," not a claim of universal fit. |

### 3.1 Business/ROI value scoring rubric (`business_value_score`)

A 1–5 scale, since it should stay judgable from public sources rather than needing hard financial data:

| Score | Meaning |
|---|---|
| 1 | Speculative/marginal — theoretical value, no evidence of real adoption or impact |
| 2 | Niche value — used successfully in narrow contexts, limited or unclear ROI evidence |
| 3 | Moderate, demonstrated value — clear efficiency/quality gains reported, adoption growing |
| 4 | High, well-evidenced value — case studies/data show significant cost/time savings or revenue impact, used at scale |
| 5 | Transformative — use case is reshaping how the target function/industry operates, strong quantified evidence |

Scoring should be based on **evidence found during research** (case studies, reported metrics, vendor claims cross-checked against independent sources), not personal opinion — `business_value_rationale` should always cite what drove the score.

## 4. Functional Requirements

### 4.1 Data collection
- FR1: Support manually curated entries (research-and-fill, likely the primary method given source diversity) as well as scripted collection from structured sources where available (e.g. vendor changelogs, RSS feeds).
- FR2: Store all entries with full source attribution (no unsourced claims).
- FR3: Support incremental updates — re-verifying and updating `last_verified` without duplicating rows.

### 4.2 Storage
- FR4: Persist data locally (DuckDB or CSV — see project scaffold) in a way that both collection scripts and the Streamlit app read/write consistently.
- FR5: Support export to CSV/Excel for sharing outside the tool.

### 4.3 Streamlit frontend
- FR6: **Explore page** — filterable/sortable table of all use cases (filter by category, tool, maturity, value score, ROI driver tags, industry, department).
- FR7: **Analysis page** — visual breakdown: average value score by category/department, count of use cases by maturity, distribution of ROI drivers, category comparison chart, and an over-time section (use cases by year, cumulative growth, category/department growth over time).
- FR8: Detail view for a single use case showing all fields including sources and rationale.
- FR9: **Trends & Industries page** — adoption-over-time charts (including industry growth over time), per-industry breakdowns, an industry × department mapping (heatmap + browsable pairs), and a **Forecast & Momentum** section: a naive linear-trend extrapolation (explicitly labeled illustrative, not a statistical forecast) by category/industry/department, with "fastest-growing" and "largest/most established" leaderboards.
- FR10: **Real-World Impact page** — browsable/filterable `company_case_studies`, with an industry × department evidence heatmap, an over-time section (case studies by year reported, cumulative, deployment-status mix by year), behind a persistent "not independently re-verified" disclaimer.
- FR11: **Revenue & ROI+ page** — disclosed $ impact by industry/department, a quantification-rate KPI (how many case studies actually have a hard $ figure vs. don't) including its trend by year, cumulative disclosed $ over time, a deployment-status funnel (pilot/scaled/reversed/discontinued), and macro investment-vs-realized-ROI context from `market_context`.
- FR12: **Growth & Opportunities page** — a value × growth × maturity bubble chart per category/industry/department (untruncated — every group, not a top-N leaderboard), an opportunity/white-space finder (department patterns proven valuable elsewhere but barely applied in a given industry), and a maturity-readiness ranking cross-checked against real scaled deployments from `company_case_studies`.

## 5. Non-Functional Requirements

- NFR1: Runs fully locally (WSL/Ubuntu) with no required paid API keys for core functionality (web research done manually or via free-tier search).
- NFR2: Data model must be extensible — adding a new category, tool, or field should not require restructuring existing data.
- NFR3: All value scores must be traceable to a rationale and source — no unexplained numbers.
- NFR4: Reasonable performance for a dataset up to a few thousand rows (no need to optimize beyond that for v1).

## 5a. Company Case Studies (real-world evidence layer)

The `ai_tooling_use_cases` table catalogs *types* of agentic-AI applications, not who actually uses them. A separate `company_case_studies` table captures the other half: specific companies that have **publicly reported concrete efficiency gains**, and what they did to achieve them. This is evidence, not taxonomy — one company can report on more than one tool/initiative, and not every case study maps cleanly onto one of the 20 tracked tools.

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier |
| `company_name` | text | The company reporting the result |
| `industry` | text | Reuses the `target_industries` vocabulary where it fits |
| `tool_or_platform` | text | Free text — may match a tracked `tool_name`, or be a proprietary/internal tool out of scope for section 2.1 |
| `related_category` | text | One of the 4 categories, when the platform used maps cleanly onto one (nullable) |
| `what_they_did` | text | 2–4 sentences on the specific application |
| `reported_efficiency_gain` | text | The headline claim as reported (may be a percentage, a dollar figure, or a qualitative description) |
| `gain_type` | text | Semicolon-separated tags reusing the `roi_drivers` vocabulary, plus `headcount efficiency` where relevant |
| `confidence` | enum | `high`, `moderate`, `directional` — how solid the recalled figure is, not how big the company is |
| `source_url` | text | Same multi-URL convention as `ai_tooling_use_cases` |
| `source_type` | enum | Same set as `ai_tooling_use_cases` |
| `date_reported` | date | Approximate month/year the result was publicized |
| `notes` | text | Verification caveats |
| `target_departments` | text | Semicolon-separated business functions/departments involved (same vocabulary as `ai_tooling_use_cases.target_departments`, see `config/taxonomy.yaml`) |
| `financial_impact_usd` | double, nullable | A single best-estimate annualized USD figure, populated **only** when a hard number is genuinely publicly reported (e.g. Klarna's $40M). Left `NULL` everywhere else rather than invented — the resulting quantification rate (how many case studies have a real $ figure vs. don't) is itself a finding, surfaced on the Revenue & ROI+ page. |
| `financial_impact_type` | enum | `profit impact`, `cost savings`, `revenue impact`, `cost avoidance`, `headcount efficiency`, `not quantified` |
| `deployment_status` | enum | `pilot`, `scaled/production`, `scaled then partially reversed`, `discontinued` — not every pilot survives; this tracks that funnel |
| `company_size_band` | text | This company's size/revenue band (e.g. "SMB (<$10M)", "Enterprise ($1B+)"). Single value, since a case study is about one company. Suggested vocabulary lives in `config/taxonomy.yaml` (`company_size_bands`). |
| `implementation_cost_usd` | double, nullable | The disclosed cost/investment required to achieve the reported gain, populated **only** when a hard number is genuinely publicly reported. Left `NULL` otherwise (the overwhelming majority of rows) — same "don't invent" policy as `financial_impact_usd`. Paired with it at read time (`src/analysis/summaries.py::net_roi`) to compute a net gain-minus-cost figure, never stored. |
| `hq_region` | text | This company's real headquarters region (e.g. "North America", "Europe", "China"). Single value, since a case study is about one company. Suggested vocabulary lives in `config/taxonomy.yaml` (`regions`) — the demand-side view of "where is AI already in use," distinct from `enterprise_ai_startups.hq_region` (the supply side). |

This dataset is knowledge-based and **not independently re-verified** — the Real-World Impact page (`pages/4_Real_World_Impact.py`) carries a persistent disclaimer to that effect, and `confidence` is meant to be read before treating any figure as fact.

## 5b. Financial Impact & Market Context

Two more layers sit on top of 5a, both surfaced on `pages/5_Revenue_and_ROI+.py` ("Revenue & ROI+"):

1. The `financial_impact_usd` / `financial_impact_type` / `deployment_status` fields on `company_case_studies` (above), which let the app compute how much of the disclosed evidence is actually quantified in dollar terms, broken down by industry and department.
2. A separate `market_context` table of macro-level reference facts (investment/market-size figures, independent survey findings on realized ROI, analyst forecasts on project failure rates) — these describe the *market*, not any one company's deployment, so they don't belong on `company_case_studies`.

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier |
| `metric` | text | Short label |
| `value_display` | text | Human-readable claim, written like `business_value_rationale` — a full, hedged sentence |
| `value_numeric` | double, nullable | For the figures clean enough to chart |
| `unit` | text, nullable | e.g. "USD billions", "percent" |
| `scope` | text | e.g. "Global", "Enterprise GenAI", "Agentic AI" |
| `context_category` | enum | `investment/market size`, `realized ROI evidence`, `pilot-to-production funnel`, `risk/failure signal` |
| `time_period` | text | e.g. "2025", "2024–2027 forecast" |
| `source_url`, `source_type` | text, enum | Same convention as other tables |
| `confidence` | enum | `high` / `moderate` / `directional` — realistically nothing here is `high`; these are contested macro figures, not audited financials |
| `notes` | text | Caveats |

Seeded from `data/seed/market_context_seed.csv` via `storage.seed_market_context_from_csv()`, called by `scripts/seed_db.py` alongside the other two seed files.

## 5c. Enterprise AI Startup Vendors

`company_case_studies` tracks companies that *use* AI tools; `enterprise_ai_startups` tracks the *vendors/startups* that build non-engineering enterprise-workflow AI (finance, sales, support, legal, HR — coding/dev-agent startups are already covered by the `agents` table in section 2.1). Surfaced on `pages/8_Startup_Vendors.py` ("Startup Vendors"), which cross-references `company_case_studies.tool_or_platform` against a startup's name at read time — no join table, same pattern as `sources`.

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier |
| `company_name`, `product_name` | text | Often identical; kept separate for cases like Cognition/Devin-style naming |
| `target_departments` | text | Semicolon-separated, same `config/taxonomy.yaml` vocabulary as elsewhere |
| `what_they_do` | text | 1-2 sentence description |
| `target_company_size` | text | Semicolon-separated company-size bands (`config/taxonomy.yaml`'s `company_size_bands`) this vendor is realistically built/priced for |
| `engagement_model` | text | The field this table exists for: what a prospect actually has to do to engage this vendor (e.g. "self-serve signup, no sales gate" vs. "fully sales-gated, demo call required") |
| `pricing_signal` | text, nullable | Usage-based / per-seat / custom-enterprise-only / not publicly disclosed — "not disclosed" is an honest value here, not a gap to fill in |
| `funding_stage` | text, nullable | Most recent known round and total raised; genuinely conflicting source data is noted as such rather than resolved by guessing |
| `notable_customers` | text, nullable | Semicolon-separated; cross-references `company_case_studies.company_name` where applicable |
| `source_url`, `source_type`, `confidence` | text/enum | Same convention as other tables |
| `collected_at`, `last_verified` | date | Same convention as `ai_tooling_use_cases` |
| `notes` | text | Caveats |
| `hq_region` | text | This vendor's real headquarters region. Suggested vocabulary lives in `config/taxonomy.yaml` (`regions`) — the supply-side view of where AI vendors are based, distinct from `company_case_studies.hq_region` (the demand side). |

Seeded from `data/seed/enterprise_ai_startups_seed.csv` via `storage.seed_enterprise_ai_startups_from_csv()`.

## 6. Research/Data Sources (starting points)

- Vendor documentation and official case studies/blogs
- Independent case studies and analyst reports (e.g. industry press covering AI adoption)
- Community reports (e.g. developer forums, GitHub discussions, Show HN, Reddit) — flagged clearly via `source_type` since reliability is lower
- News coverage of adoption/impact

## 7. Deliverables / Success Criteria

- A populated dataset covering at least the tools listed in Section 2.1, with 2+ use cases per tool where findable.
- A working Streamlit app with Explore and Analysis pages reading from the same data store.
- Every use case entry has a sourced, justified business value score.
- README documenting how to run collection scripts and launch the app.

## 8. Open Questions / Assumptions to revisit

- Should categories/tools be hard-coded initially or loaded from a config file for easy editing? *(Recommendation: config file — e.g. `config/taxonomy.yaml` — so the taxonomy can grow without code changes.)*
- Should there be a way to flag "conflicting evidence" when sources disagree on a use case's value?
- Should historical score changes be tracked over time (versioning), or only the latest score kept?
