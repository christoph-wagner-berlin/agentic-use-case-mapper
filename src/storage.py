"""DuckDB-backed storage for the ai_tooling_use_cases dataset (REQUIREMENTS.md section 3)."""

from pathlib import Path
from datetime import date

import duckdb
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "usecases.duckdb"

AI_TOOLING_USE_CASES_COLUMNS = [
    "id",
    "category",
    "tool_name",
    "vendor",
    "use_case_title",
    "use_case_description",
    "target_users",
    "maturity",
    "business_value_score",
    "business_value_rationale",
    "roi_drivers",
    "example_companies",
    "source_url",
    "source_type",
    "collected_at",
    "last_verified",
    "notes",
    "first_available",
    "target_industries",
    "target_departments",
    "target_company_size",
]

CASE_STUDY_COLUMNS = [
    "id",
    "company_name",
    "industry",
    "tool_or_platform",
    "related_category",
    "what_they_did",
    "reported_efficiency_gain",
    "gain_type",
    "confidence",
    "source_url",
    "source_type",
    "date_reported",
    "notes",
    "target_departments",
    "financial_impact_usd",
    "financial_impact_type",
    "deployment_status",
    "company_size_band",
    "implementation_cost_usd",
    "hq_region",
]

MARKET_CONTEXT_COLUMNS = [
    "id",
    "metric",
    "value_display",
    "value_numeric",
    "unit",
    "scope",
    "context_category",
    "time_period",
    "source_url",
    "source_type",
    "confidence",
    "notes",
]

TOPIC_COLUMNS = ["id", "name", "description"]

ACHIEVEMENT_COLUMNS = [
    "id",
    "title",
    "achievement_type",
    "tool_name",
    "company_name",
    "metric_display",
    "description",
    "date_achieved",
    "source_url",
    "source_type",
    "confidence",
    "notes",
]

AI_TOOLING_USE_CASE_CASE_STUDY_LINK_COLUMNS = ["ai_tooling_use_case_id", "case_study_id", "match_type", "notes"]

SOURCE_COLUMNS = ["id", "table_name", "record_id", "url", "source_type", "retrieved_at", "notes"]

AGENT_COLUMNS = [
    "id",
    "name",
    "vendor",
    "category",
    "architecture_summary",
    "autonomy_level",
    "interface",
    "open_source",
    "release_year",
    "description",
    "source_url",
    "source_type",
    "notes",
]

AGENT_PATTERN_COLUMNS = ["id", "name", "description", "when_it_works_well", "source_url", "source_type"]

AGENT_PATTERN_LINK_COLUMNS = ["agent_id", "pattern_id", "notes"]

ENTERPRISE_AI_STARTUP_COLUMNS = [
    "id",
    "company_name",
    "product_name",
    "target_departments",
    "what_they_do",
    "target_company_size",
    "engagement_model",
    "pricing_signal",
    "funding_stage",
    "notable_customers",
    "source_url",
    "source_type",
    "confidence",
    "collected_at",
    "last_verified",
    "notes",
    "hq_region",
]

BUSINESS_NEED_COLUMNS = [
    "id",
    "need_title",
    "need_description",
    "status",
    "business_value_score",
    "business_value_rationale",
    "source_url",
    "source_type",
    "confidence",
    "collected_at",
    "last_verified",
    "notes",
    "target_industries",
    "target_departments",
    "target_company_size",
]

TOOL_AGNOSTIC_USE_CASE_COLUMNS = [
    "id",
    "category",
    "use_case_title",
    "use_case_description",
    "target_users",
    "maturity",
    "business_value_score",
    "business_value_rationale",
    "roi_drivers",
    "example_companies",
    "source_url",
    "source_type",
    "collected_at",
    "last_verified",
    "notes",
    "first_available",
    "target_industries",
    "target_departments",
    "target_company_size",
]

BUSINESS_NEED_USE_CASE_LINK_COLUMNS = ["business_need_id", "ai_tooling_use_case_id", "match_type", "notes"]

BUSINESS_NEED_PATTERN_LINK_COLUMNS = ["business_need_id", "tool_agnostic_use_case_id", "notes"]

PATTERN_USE_CASE_LINK_COLUMNS = ["tool_agnostic_use_case_id", "ai_tooling_use_case_id", "match_type", "notes"]


def get_connection() -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def init_db() -> None:
    con = get_connection()
    con.execute("""
        CREATE SEQUENCE IF NOT EXISTS ai_tooling_use_cases_id_seq START 1;
        CREATE TABLE IF NOT EXISTS ai_tooling_use_cases (
            id INTEGER PRIMARY KEY DEFAULT nextval('ai_tooling_use_cases_id_seq'),
            category TEXT,
            tool_name TEXT,
            vendor TEXT,
            use_case_title TEXT,
            use_case_description TEXT,
            target_users TEXT,
            maturity TEXT,
            business_value_score INTEGER,
            business_value_rationale TEXT,
            roi_drivers TEXT,
            example_companies TEXT,
            source_url TEXT,
            source_type TEXT,
            collected_at DATE,
            last_verified DATE,
            notes TEXT,
            first_available DATE,
            target_industries TEXT,
            target_departments TEXT,
            target_company_size TEXT
        );
        CREATE SEQUENCE IF NOT EXISTS company_case_studies_id_seq START 1;
        CREATE TABLE IF NOT EXISTS company_case_studies (
            id INTEGER PRIMARY KEY DEFAULT nextval('company_case_studies_id_seq'),
            company_name TEXT,
            industry TEXT,
            tool_or_platform TEXT,
            related_category TEXT,
            what_they_did TEXT,
            reported_efficiency_gain TEXT,
            gain_type TEXT,
            confidence TEXT,
            source_url TEXT,
            source_type TEXT,
            date_reported DATE,
            notes TEXT,
            target_departments TEXT,
            financial_impact_usd DOUBLE,
            financial_impact_type TEXT,
            deployment_status TEXT,
            company_size_band TEXT,
            implementation_cost_usd DOUBLE,
            hq_region TEXT
        );
        CREATE SEQUENCE IF NOT EXISTS market_context_id_seq START 1;
        CREATE TABLE IF NOT EXISTS market_context (
            id INTEGER PRIMARY KEY DEFAULT nextval('market_context_id_seq'),
            metric TEXT,
            value_display TEXT,
            value_numeric DOUBLE,
            unit TEXT,
            scope TEXT,
            context_category TEXT,
            time_period TEXT,
            source_url TEXT,
            source_type TEXT,
            confidence TEXT,
            notes TEXT
        );
        CREATE SEQUENCE IF NOT EXISTS topics_id_seq START 1;
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY DEFAULT nextval('topics_id_seq'),
            name TEXT,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_tooling_use_case_topics (
            ai_tooling_use_case_id INTEGER,
            topic_id INTEGER,
            PRIMARY KEY (ai_tooling_use_case_id, topic_id)
        );
        CREATE SEQUENCE IF NOT EXISTS achievements_id_seq START 1;
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY DEFAULT nextval('achievements_id_seq'),
            title TEXT,
            achievement_type TEXT,
            tool_name TEXT,
            company_name TEXT,
            metric_display TEXT,
            description TEXT,
            date_achieved DATE,
            source_url TEXT,
            source_type TEXT,
            confidence TEXT,
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_tooling_use_case_case_study_links (
            ai_tooling_use_case_id INTEGER,
            case_study_id INTEGER,
            match_type TEXT,
            notes TEXT,
            PRIMARY KEY (ai_tooling_use_case_id, case_study_id)
        );
        CREATE SEQUENCE IF NOT EXISTS sources_id_seq START 1;
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY DEFAULT nextval('sources_id_seq'),
            table_name TEXT,
            record_id INTEGER,
            url TEXT,
            source_type TEXT,
            retrieved_at DATE,
            notes TEXT
        );
        CREATE SEQUENCE IF NOT EXISTS agents_id_seq START 1;
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY DEFAULT nextval('agents_id_seq'),
            name TEXT,
            vendor TEXT,
            category TEXT,
            architecture_summary TEXT,
            autonomy_level TEXT,
            interface TEXT,
            open_source TEXT,
            release_year INTEGER,
            description TEXT,
            source_url TEXT,
            source_type TEXT,
            notes TEXT
        );
        CREATE SEQUENCE IF NOT EXISTS agent_patterns_id_seq START 1;
        CREATE TABLE IF NOT EXISTS agent_patterns (
            id INTEGER PRIMARY KEY DEFAULT nextval('agent_patterns_id_seq'),
            name TEXT,
            description TEXT,
            when_it_works_well TEXT,
            source_url TEXT,
            source_type TEXT
        );
        CREATE TABLE IF NOT EXISTS agent_pattern_links (
            agent_id INTEGER,
            pattern_id INTEGER,
            notes TEXT,
            PRIMARY KEY (agent_id, pattern_id)
        );
        CREATE SEQUENCE IF NOT EXISTS enterprise_ai_startups_id_seq START 1;
        CREATE TABLE IF NOT EXISTS enterprise_ai_startups (
            id INTEGER PRIMARY KEY DEFAULT nextval('enterprise_ai_startups_id_seq'),
            company_name TEXT,
            product_name TEXT,
            target_departments TEXT,
            what_they_do TEXT,
            target_company_size TEXT,
            engagement_model TEXT,
            pricing_signal TEXT,
            funding_stage TEXT,
            notable_customers TEXT,
            source_url TEXT,
            source_type TEXT,
            confidence TEXT,
            collected_at DATE,
            last_verified DATE,
            notes TEXT,
            hq_region TEXT
        );
        CREATE SEQUENCE IF NOT EXISTS business_needs_id_seq START 1;
        CREATE TABLE IF NOT EXISTS business_needs (
            id INTEGER PRIMARY KEY DEFAULT nextval('business_needs_id_seq'),
            need_title TEXT,
            need_description TEXT,
            status TEXT,
            business_value_score INTEGER,
            business_value_rationale TEXT,
            source_url TEXT,
            source_type TEXT,
            confidence TEXT,
            collected_at DATE,
            last_verified DATE,
            notes TEXT,
            target_industries TEXT,
            target_departments TEXT,
            target_company_size TEXT
        );
        CREATE SEQUENCE IF NOT EXISTS tool_agnostic_use_cases_id_seq START 1;
        CREATE TABLE IF NOT EXISTS tool_agnostic_use_cases (
            id INTEGER PRIMARY KEY DEFAULT nextval('tool_agnostic_use_cases_id_seq'),
            category TEXT,
            use_case_title TEXT,
            use_case_description TEXT,
            target_users TEXT,
            maturity TEXT,
            business_value_score INTEGER,
            business_value_rationale TEXT,
            roi_drivers TEXT,
            example_companies TEXT,
            source_url TEXT,
            source_type TEXT,
            collected_at DATE,
            last_verified DATE,
            notes TEXT,
            first_available DATE,
            target_industries TEXT,
            target_departments TEXT,
            target_company_size TEXT
        );
        CREATE TABLE IF NOT EXISTS business_need_use_case_links (
            business_need_id INTEGER,
            ai_tooling_use_case_id INTEGER,
            match_type TEXT,
            notes TEXT,
            PRIMARY KEY (business_need_id, ai_tooling_use_case_id)
        );
        CREATE TABLE IF NOT EXISTS business_need_pattern_links (
            business_need_id INTEGER,
            tool_agnostic_use_case_id INTEGER,
            notes TEXT,
            PRIMARY KEY (business_need_id, tool_agnostic_use_case_id)
        );
        CREATE TABLE IF NOT EXISTS pattern_use_case_links (
            tool_agnostic_use_case_id INTEGER,
            ai_tooling_use_case_id INTEGER,
            match_type TEXT,
            notes TEXT,
            PRIMARY KEY (tool_agnostic_use_case_id, ai_tooling_use_case_id)
        )
    """)
    con.close()


def load_ai_tooling_use_cases(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM ai_tooling_use_cases ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if field == "min_score":
            df = df[df["business_value_score"] >= value]
        elif field == "search_text":
            needle = str(value).lower()
            df = df[
                df["use_case_title"].str.lower().str.contains(needle, na=False)
                | df["roi_drivers"].str.lower().str.contains(needle, na=False)
            ]
        elif isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def insert_ai_tooling_use_case(record: dict) -> int:
    con = get_connection()
    record = {**record}
    record.setdefault("collected_at", date.today())
    record.setdefault("last_verified", date.today())
    fields = [c for c in AI_TOOLING_USE_CASES_COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO ai_tooling_use_cases ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def update_ai_tooling_use_case(id: int, record: dict) -> None:
    con = get_connection()
    record = {**record, "last_verified": date.today()}
    fields = [c for c in AI_TOOLING_USE_CASES_COLUMNS if c != "id" and c in record]
    set_clause = ", ".join(f"{f} = ?" for f in fields)
    values = [record[f] for f in fields] + [id]
    con.execute(f"UPDATE ai_tooling_use_cases SET {set_clause} WHERE id = ?", values)
    con.close()


def seed_ai_tooling_use_cases_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS ai_tooling_use_cases")
    con.execute("DROP SEQUENCE IF EXISTS ai_tooling_use_cases_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in AI_TOOLING_USE_CASES_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO ai_tooling_use_cases ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM ai_tooling_use_cases").fetchone()[0]
    con.close()
    return count


def export_ai_tooling_use_cases_csv(path: str | Path) -> None:
    df = load_ai_tooling_use_cases()
    df.to_csv(path, index=False)


def load_case_studies(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM company_case_studies ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def insert_case_study(record: dict) -> int:
    con = get_connection()
    record = {**record}
    record.setdefault("date_reported", date.today())
    fields = [c for c in CASE_STUDY_COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO company_case_studies ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def update_case_study(id: int, record: dict) -> None:
    con = get_connection()
    record = {**record}
    fields = [c for c in CASE_STUDY_COLUMNS if c != "id" and c in record]
    set_clause = ", ".join(f"{f} = ?" for f in fields)
    values = [record[f] for f in fields] + [id]
    con.execute(f"UPDATE company_case_studies SET {set_clause} WHERE id = ?", values)
    con.close()


def seed_case_studies_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS company_case_studies")
    con.execute("DROP SEQUENCE IF EXISTS company_case_studies_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in CASE_STUDY_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO company_case_studies ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM company_case_studies").fetchone()[0]
    con.close()
    return count


def load_market_context(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM market_context ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def insert_market_context(record: dict) -> int:
    con = get_connection()
    record = {**record}
    fields = [c for c in MARKET_CONTEXT_COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO market_context ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def update_market_context(id: int, record: dict) -> None:
    con = get_connection()
    record = {**record}
    fields = [c for c in MARKET_CONTEXT_COLUMNS if c != "id" and c in record]
    set_clause = ", ".join(f"{f} = ?" for f in fields)
    values = [record[f] for f in fields] + [id]
    con.execute(f"UPDATE market_context SET {set_clause} WHERE id = ?", values)
    con.close()


def seed_market_context_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS market_context")
    con.execute("DROP SEQUENCE IF EXISTS market_context_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in MARKET_CONTEXT_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO market_context ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM market_context").fetchone()[0]
    con.close()
    return count


def load_topics() -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM topics ORDER BY name").fetchdf()
    con.close()
    return df


def insert_topic(record: dict) -> int:
    con = get_connection()
    fields = [c for c in TOPIC_COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO topics ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def seed_topics_from_csv(path: str | Path) -> int:
    # Topic ids are reassigned on reseed, so any existing tagging would point at stale ids.
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS ai_tooling_use_case_topics")
    con.execute("DROP TABLE IF EXISTS topics")
    con.execute("DROP SEQUENCE IF EXISTS topics_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in TOPIC_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO topics ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
    con.close()
    return count


def load_ai_tooling_use_case_topics_joined() -> pd.DataFrame:
    con = get_connection()
    df = con.execute("""
        SELECT uct.ai_tooling_use_case_id, t.id AS topic_id, t.name AS topic_name, t.description AS topic_description
        FROM ai_tooling_use_case_topics uct
        JOIN topics t ON t.id = uct.topic_id
        ORDER BY uct.ai_tooling_use_case_id, t.name
    """).fetchdf()
    con.close()
    return df


def seed_ai_tooling_use_case_topics_from_csv(path: str | Path) -> int:
    """Seed CSV has (ai_tooling_use_case_id, topic_name) -- topic_name is resolved to topic_id here,
    so `topics` must already be seeded before this runs."""
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS ai_tooling_use_case_topics")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    con.execute("""
        INSERT INTO ai_tooling_use_case_topics (ai_tooling_use_case_id, topic_id)
        SELECT seed_df.ai_tooling_use_case_id, t.id
        FROM seed_df
        JOIN topics t ON t.name = seed_df.topic_name
    """)
    count = con.execute("SELECT COUNT(*) FROM ai_tooling_use_case_topics").fetchone()[0]
    con.close()
    return count


def load_achievements(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM achievements ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def insert_achievement(record: dict) -> int:
    con = get_connection()
    record = {**record}
    fields = [c for c in ACHIEVEMENT_COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO achievements ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def update_achievement(id: int, record: dict) -> None:
    con = get_connection()
    record = {**record}
    fields = [c for c in ACHIEVEMENT_COLUMNS if c != "id" and c in record]
    set_clause = ", ".join(f"{f} = ?" for f in fields)
    values = [record[f] for f in fields] + [id]
    con.execute(f"UPDATE achievements SET {set_clause} WHERE id = ?", values)
    con.close()


def seed_achievements_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS achievements")
    con.execute("DROP SEQUENCE IF EXISTS achievements_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in ACHIEVEMENT_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO achievements ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM achievements").fetchone()[0]
    con.close()
    return count


def load_ai_tooling_use_case_case_study_links_joined() -> pd.DataFrame:
    con = get_connection()
    df = con.execute("""
        SELECT l.ai_tooling_use_case_id, l.case_study_id, cs.company_name, cs.tool_or_platform, l.match_type, l.notes
        FROM ai_tooling_use_case_case_study_links l
        JOIN company_case_studies cs ON cs.id = l.case_study_id
        ORDER BY l.ai_tooling_use_case_id
    """).fetchdf()
    con.close()
    return df


def seed_ai_tooling_use_case_case_study_links_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS ai_tooling_use_case_case_study_links")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in AI_TOOLING_USE_CASE_CASE_STUDY_LINK_COLUMNS if c in df.columns]
    con.execute(f"INSERT INTO ai_tooling_use_case_case_study_links ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM ai_tooling_use_case_case_study_links").fetchone()[0]
    con.close()
    return count


def load_sources(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM sources ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def backfill_sources_from_existing() -> int:
    """Explode the semicolon-separated source_url/source_type already on ai_tooling_use_cases,
    company_case_studies, and market_context into individual `sources` rows. Derived from
    those tables rather than hand-authored -- always rebuilds from scratch, safe to re-run."""
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS sources")
    con.execute("DROP SEQUENCE IF EXISTS sources_id_seq")
    con.close()
    init_db()

    con = get_connection()
    specs = [
        ("ai_tooling_use_cases", "collected_at"),
        ("company_case_studies", "date_reported"),
        ("market_context", None),
        ("business_needs", "collected_at"),
        ("tool_agnostic_use_cases", "collected_at"),
    ]
    for table_name, date_column in specs:
        date_expr = f"sub.{date_column}" if date_column else "NULL"
        date_select = f", {date_column}" if date_column else ""
        con.execute(f"""
            INSERT INTO sources (table_name, record_id, url, source_type, retrieved_at)
            SELECT '{table_name}', sub.id, sub.url, sub.source_type, {date_expr}
            FROM (
                SELECT id, source_type{date_select}, TRIM(unnest(string_split(source_url, ';'))) AS url
                FROM {table_name}
                WHERE source_url IS NOT NULL
            ) sub
            WHERE sub.url != ''
        """)
    count = con.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    con.close()
    return count


def load_agents(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM agents ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def insert_agent(record: dict) -> int:
    con = get_connection()
    fields = [c for c in AGENT_COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO agents ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def seed_agents_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS agent_pattern_links")
    con.execute("DROP TABLE IF EXISTS agents")
    con.execute("DROP SEQUENCE IF EXISTS agents_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in AGENT_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO agents ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
    con.close()
    return count


def load_agent_patterns() -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM agent_patterns ORDER BY id").fetchdf()
    con.close()
    return df


def seed_agent_patterns_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS agent_pattern_links")
    con.execute("DROP TABLE IF EXISTS agent_patterns")
    con.execute("DROP SEQUENCE IF EXISTS agent_patterns_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in AGENT_PATTERN_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO agent_patterns ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM agent_patterns").fetchone()[0]
    con.close()
    return count


def load_agent_pattern_links_joined() -> pd.DataFrame:
    con = get_connection()
    df = con.execute("""
        SELECT a.id AS agent_id, a.name AS agent_name, p.id AS pattern_id, p.name AS pattern_name, l.notes
        FROM agent_pattern_links l
        JOIN agents a ON a.id = l.agent_id
        JOIN agent_patterns p ON p.id = l.pattern_id
        ORDER BY a.name, p.name
    """).fetchdf()
    con.close()
    return df


def seed_agent_pattern_links_from_csv(path: str | Path) -> int:
    """Seed CSV has (agent_name, pattern_name, notes) -- both names are resolved to ids here,
    so `agents` and `agent_patterns` must already be seeded before this runs."""
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS agent_pattern_links")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    con.execute("""
        INSERT INTO agent_pattern_links (agent_id, pattern_id, notes)
        SELECT a.id, p.id, seed_df.notes
        FROM seed_df
        JOIN agents a ON a.name = seed_df.agent_name
        JOIN agent_patterns p ON p.name = seed_df.pattern_name
    """)
    count = con.execute("SELECT COUNT(*) FROM agent_pattern_links").fetchone()[0]
    con.close()
    return count


def load_enterprise_ai_startups(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM enterprise_ai_startups ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def seed_enterprise_ai_startups_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS enterprise_ai_startups")
    con.execute("DROP SEQUENCE IF EXISTS enterprise_ai_startups_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in ENTERPRISE_AI_STARTUP_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO enterprise_ai_startups ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM enterprise_ai_startups").fetchone()[0]
    con.close()
    return count


def load_business_needs(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM business_needs ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if field == "min_score":
            df = df[df["business_value_score"] >= value]
        elif field == "search_text":
            needle = str(value).lower()
            df = df[
                df["need_title"].str.lower().str.contains(needle, na=False)
                | df["need_description"].str.lower().str.contains(needle, na=False)
            ]
        elif isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def insert_business_need(record: dict) -> int:
    con = get_connection()
    record = {**record}
    record.setdefault("collected_at", date.today())
    record.setdefault("last_verified", date.today())
    fields = [c for c in BUSINESS_NEED_COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO business_needs ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def update_business_need(id: int, record: dict) -> None:
    con = get_connection()
    record = {**record, "last_verified": date.today()}
    fields = [c for c in BUSINESS_NEED_COLUMNS if c != "id" and c in record]
    set_clause = ", ".join(f"{f} = ?" for f in fields)
    values = [record[f] for f in fields] + [id]
    con.execute(f"UPDATE business_needs SET {set_clause} WHERE id = ?", values)
    con.close()


def seed_business_needs_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS business_need_use_case_links")
    con.execute("DROP TABLE IF EXISTS business_need_pattern_links")
    con.execute("DROP TABLE IF EXISTS business_needs")
    con.execute("DROP SEQUENCE IF EXISTS business_needs_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in BUSINESS_NEED_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO business_needs ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM business_needs").fetchone()[0]
    con.close()
    return count


def load_tool_agnostic_use_cases(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM tool_agnostic_use_cases ORDER BY id").fetchdf()
    con.close()

    if not filters:
        return df

    for field, value in filters.items():
        if value in (None, "", [], ()):
            continue
        if field == "min_score":
            df = df[df["business_value_score"] >= value]
        elif field == "search_text":
            needle = str(value).lower()
            df = df[
                df["use_case_title"].str.lower().str.contains(needle, na=False)
                | df["roi_drivers"].str.lower().str.contains(needle, na=False)
            ]
        elif isinstance(value, (list, tuple, set)):
            df = df[df[field].isin(value)]
        else:
            df = df[df[field] == value]

    return df


def insert_tool_agnostic_use_case(record: dict) -> int:
    con = get_connection()
    record = {**record}
    record.setdefault("collected_at", date.today())
    record.setdefault("last_verified", date.today())
    fields = [c for c in TOOL_AGNOSTIC_USE_CASE_COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO tool_agnostic_use_cases ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def update_tool_agnostic_use_case(id: int, record: dict) -> None:
    con = get_connection()
    record = {**record, "last_verified": date.today()}
    fields = [c for c in TOOL_AGNOSTIC_USE_CASE_COLUMNS if c != "id" and c in record]
    set_clause = ", ".join(f"{f} = ?" for f in fields)
    values = [record[f] for f in fields] + [id]
    con.execute(f"UPDATE tool_agnostic_use_cases SET {set_clause} WHERE id = ?", values)
    con.close()


def seed_tool_agnostic_use_cases_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS business_need_pattern_links")
    con.execute("DROP TABLE IF EXISTS pattern_use_case_links")
    con.execute("DROP TABLE IF EXISTS tool_agnostic_use_cases")
    con.execute("DROP SEQUENCE IF EXISTS tool_agnostic_use_cases_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in TOOL_AGNOSTIC_USE_CASE_COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO tool_agnostic_use_cases ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM tool_agnostic_use_cases").fetchone()[0]
    con.close()
    return count


def load_business_need_use_case_links_joined() -> pd.DataFrame:
    con = get_connection()
    df = con.execute("""
        SELECT l.business_need_id, bn.need_title, l.ai_tooling_use_case_id, uc.tool_name, uc.use_case_title,
               l.match_type, l.notes
        FROM business_need_use_case_links l
        JOIN business_needs bn ON bn.id = l.business_need_id
        JOIN ai_tooling_use_cases uc ON uc.id = l.ai_tooling_use_case_id
        ORDER BY l.business_need_id
    """).fetchdf()
    con.close()
    return df


def seed_business_need_use_case_links_from_csv(path: str | Path) -> int:
    """Seed CSV has (need_title, tool_name, use_case_title, match_type, notes) -- resolved to ids
    here via join, so `business_needs` and `ai_tooling_use_cases` must already be seeded first."""
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS business_need_use_case_links")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    con.execute("""
        INSERT INTO business_need_use_case_links (business_need_id, ai_tooling_use_case_id, match_type, notes)
        SELECT bn.id, uc.id, seed_df.match_type, seed_df.notes
        FROM seed_df
        JOIN business_needs bn ON bn.need_title = seed_df.need_title
        JOIN ai_tooling_use_cases uc
            ON uc.tool_name = seed_df.tool_name AND uc.use_case_title = seed_df.use_case_title
    """)
    count = con.execute("SELECT COUNT(*) FROM business_need_use_case_links").fetchone()[0]
    con.close()
    return count


def load_business_need_pattern_links_joined() -> pd.DataFrame:
    con = get_connection()
    df = con.execute("""
        SELECT l.business_need_id, bn.need_title, l.tool_agnostic_use_case_id, p.use_case_title AS pattern_title,
               l.notes
        FROM business_need_pattern_links l
        JOIN business_needs bn ON bn.id = l.business_need_id
        JOIN tool_agnostic_use_cases p ON p.id = l.tool_agnostic_use_case_id
        ORDER BY l.business_need_id
    """).fetchdf()
    con.close()
    return df


def seed_business_need_pattern_links_from_csv(path: str | Path) -> int:
    """Seed CSV has (need_title, pattern_title, notes) -- resolved to ids here via join, so
    `business_needs` and `tool_agnostic_use_cases` must already be seeded first."""
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS business_need_pattern_links")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    con.execute("""
        INSERT INTO business_need_pattern_links (business_need_id, tool_agnostic_use_case_id, notes)
        SELECT bn.id, p.id, seed_df.notes
        FROM seed_df
        JOIN business_needs bn ON bn.need_title = seed_df.need_title
        JOIN tool_agnostic_use_cases p ON p.use_case_title = seed_df.pattern_title
    """)
    count = con.execute("SELECT COUNT(*) FROM business_need_pattern_links").fetchone()[0]
    con.close()
    return count


def load_pattern_use_case_links_joined() -> pd.DataFrame:
    con = get_connection()
    df = con.execute("""
        SELECT l.tool_agnostic_use_case_id, p.use_case_title AS pattern_title, l.ai_tooling_use_case_id,
               uc.tool_name, uc.use_case_title, l.match_type, l.notes
        FROM pattern_use_case_links l
        JOIN tool_agnostic_use_cases p ON p.id = l.tool_agnostic_use_case_id
        JOIN ai_tooling_use_cases uc ON uc.id = l.ai_tooling_use_case_id
        ORDER BY l.tool_agnostic_use_case_id
    """).fetchdf()
    con.close()
    return df


def seed_pattern_use_case_links_from_csv(path: str | Path) -> int:
    """Seed CSV has (pattern_title, tool_name, use_case_title, match_type, notes) -- resolved to
    ids here via join, so `tool_agnostic_use_cases` and `ai_tooling_use_cases` must already be
    seeded first."""
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS pattern_use_case_links")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    con.execute("""
        INSERT INTO pattern_use_case_links (tool_agnostic_use_case_id, ai_tooling_use_case_id, match_type, notes)
        SELECT p.id, uc.id, seed_df.match_type, seed_df.notes
        FROM seed_df
        JOIN tool_agnostic_use_cases p ON p.use_case_title = seed_df.pattern_title
        JOIN ai_tooling_use_cases uc
            ON uc.tool_name = seed_df.tool_name AND uc.use_case_title = seed_df.use_case_title
    """)
    count = con.execute("SELECT COUNT(*) FROM pattern_use_case_links").fetchone()[0]
    con.close()
    return count
