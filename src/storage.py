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
            target_departments TEXT
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
            deployment_status TEXT
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
