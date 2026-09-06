# Data Model

Eleven DuckDB tables behind the use-case catalog, company case studies, market stats,
achievements, and the agent/pattern catalog. Schema defined in [`src/storage.py`](../src/storage.py)'s
`init_db()`; database file at `data/processed/usecases.duckdb`; seeded from `data/seed/*.csv`.

**None of this is enforced by DuckDB** — every `CREATE TABLE` uses plain `INTEGER` columns with
no `FOREIGN KEY` constraints. Every relationship below is upheld by `storage.py`'s load/join
functions and by the seed order in `scripts/seed_db.py`, not by the database.

## Table categories

| Category | Tables |
|---|---|
| Entity (own primary key) | `ai_tooling_use_cases`, `company_case_studies`, `market_context`, `achievements`, `agents`, `agent_patterns`, `topics` |
| Join (composite key of two FKs) | `ai_tooling_use_case_topics`, `ai_tooling_use_case_case_study_links`, `agent_pattern_links` |
| Derived (rebuilt from other tables) | `sources` |
| External config (not a DB table) | `config/taxonomy.yaml` — categories → tools, industries, departments; loaded by `src/taxonomy.py` for dropdown suggestions only, not enforced |

## Entity-relationship diagram

Solid lines are the three real join-table relationships. Dashed lines are `sources`' derived,
polymorphic references — rebuilt from `source_url`/`source_type` on the three tables shown,
never stored as an actual foreign key.

```mermaid
erDiagram
    AI_TOOLING_USE_CASES ||--o{ AI_TOOLING_USE_CASE_TOPICS : "tagged with"
    TOPICS ||--o{ AI_TOOLING_USE_CASE_TOPICS : "applied to"
    AI_TOOLING_USE_CASES ||--o{ AI_TOOLING_USE_CASE_CASE_STUDY_LINKS : "evidenced by"
    COMPANY_CASE_STUDIES ||--o{ AI_TOOLING_USE_CASE_CASE_STUDY_LINKS : "supports"
    AGENTS ||--o{ AGENT_PATTERN_LINKS : "implements"
    AGENT_PATTERNS ||--o{ AGENT_PATTERN_LINKS : "used by"
    AI_TOOLING_USE_CASES ||..o{ SOURCES : "cited in, derived"
    COMPANY_CASE_STUDIES ||..o{ SOURCES : "cited in, derived"
    MARKET_CONTEXT ||..o{ SOURCES : "cited in, derived"

    AI_TOOLING_USE_CASES {
        int id PK
        string category
        string tool_name
        string vendor
        string use_case_title
        string use_case_description
        string target_users
        string maturity
        int business_value_score
        string business_value_rationale
        string roi_drivers
        string example_companies
        string source_url
        string source_type
        date collected_at
        date last_verified
        string notes
        date first_available
        string target_industries
        string target_departments
        string target_company_size
    }

    COMPANY_CASE_STUDIES {
        int id PK
        string company_name
        string industry
        string tool_or_platform
        string related_category
        string what_they_did
        string reported_efficiency_gain
        string gain_type
        string confidence
        string source_url
        string source_type
        date date_reported
        string notes
        string target_departments
        double financial_impact_usd
        string financial_impact_type
        string deployment_status
        string company_size_band
        double implementation_cost_usd
    }

    MARKET_CONTEXT {
        int id PK
        string metric
        string value_display
        double value_numeric
        string unit
        string scope
        string context_category
        string time_period
        string source_url
        string source_type
        string confidence
        string notes
    }

    ACHIEVEMENTS {
        int id PK
        string title
        string achievement_type
        string tool_name
        string company_name
        string metric_display
        string description
        date date_achieved
        string source_url
        string source_type
        string confidence
        string notes
    }

    TOPICS {
        int id PK
        string name
        string description
    }

    AI_TOOLING_USE_CASE_TOPICS {
        int ai_tooling_use_case_id PK "references AI_TOOLING_USE_CASES"
        int topic_id PK "references TOPICS"
    }

    AI_TOOLING_USE_CASE_CASE_STUDY_LINKS {
        int ai_tooling_use_case_id PK "references AI_TOOLING_USE_CASES"
        int case_study_id PK "references COMPANY_CASE_STUDIES"
        string match_type
        string notes
    }

    AGENTS {
        int id PK
        string name
        string vendor
        string category
        string architecture_summary
        string autonomy_level
        string interface
        string open_source
        int release_year
        string description
        string source_url
        string source_type
        string notes
    }

    AGENT_PATTERNS {
        int id PK
        string name
        string description
        string when_it_works_well
        string source_url
        string source_type
    }

    AGENT_PATTERN_LINKS {
        int agent_id PK "references AGENTS"
        int pattern_id PK "references AGENT_PATTERNS"
        string notes
    }

    SOURCES {
        int id PK
        string table_name "which table this cites, e.g. ai_tooling_use_cases"
        int record_id "polymorphic reference, not a real FK"
        string url
        string source_type
        date retrieved_at
        string notes
    }
```

## Field notes

**Company size and cost are asymmetric fields, on purpose.**
`ai_tooling_use_cases.target_company_size` is semicolon-separated (like `target_industries`) since
one tool/use case can fit many size bands; `company_case_studies.company_size_band` is a single
value since one case study is about one company. `implementation_cost_usd` mirrors
`financial_impact_usd`'s "hard number or NULL, never invent" policy — as of the last reseed, **zero**
case studies disclose both a gain and a cost, so `src/analysis/summaries.py::net_roi()` (surfaced on
the Revenue & ROI+ page) is expected to render empty. That emptiness is itself the finding: public
AI case studies report the win far more often than the spend.

**No constraint enforces any of this.**
DuckDB's `CREATE TABLE` statements declare plain `INTEGER` columns — there isn't a single
`FOREIGN KEY` in the schema. Every relationship above is upheld by `storage.py`'s load/join
functions and by the seed order in `scripts/seed_db.py`, not by the database.

**`taxonomy.yaml` suggests, it doesn't constrain.**
`config/taxonomy.yaml` lists categories → tools plus 15 industries and 12 departments, loaded by
`src/taxonomy.py` purely for dropdown suggestions on `category`, `target_industries`, and
`target_departments`. None of it is enforced — free text is accepted everywhere.

**`sources` only knows about three tables.**
`backfill_sources_from_existing()` rebuilds `sources` from scratch every run, exploding the
semicolon-separated `source_url`/`source_type` on `ai_tooling_use_cases`, `company_case_studies`, and
`market_context`. `achievements`, `agents`, and `agent_patterns` carry the same `source_url`
column but are never included.

**Two seed files link by name, not id.**
`ai_tooling_use_case_topics_seed.csv` carries `topic_name` and `agent_pattern_links_seed.csv` carries
`agent_name`/`pattern_name` — `storage.py` resolves both to ids with a SQL join at seed time, so
`topics` and `agents`/`agent_patterns` must already be seeded first.

**Most of this isn't on screen yet.**
`ai_tooling_use_case_topics` and `ai_tooling_use_case_case_study_links` are rendered via their
joined loaders in `pages/3_Explore_Data.py` (the "Topics" column and "Related case studies"
section), and `agent_pattern_links` in `pages/7_Agent_Catalog_and_Patterns.py`. `achievements` and
`sources` still have loader functions in `storage.py` with no page consuming them.

---

`src/storage.py` is the source of truth. `REQUIREMENTS.md` §3 documents only `ai_tooling_use_cases`,
`company_case_studies`, and `market_context` — the rest were added later, in code only.
