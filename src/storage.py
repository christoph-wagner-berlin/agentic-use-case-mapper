"""DuckDB-backed storage for the use_cases dataset (REQUIREMENTS.md section 3)."""

from pathlib import Path
from datetime import date

import duckdb
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "usecases.duckdb"

COLUMNS = [
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


def get_connection() -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def init_db() -> None:
    con = get_connection()
    con.execute("""
        CREATE SEQUENCE IF NOT EXISTS use_cases_id_seq START 1;
        CREATE TABLE IF NOT EXISTS use_cases (
            id INTEGER PRIMARY KEY DEFAULT nextval('use_cases_id_seq'),
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
        )
    """)
    con.close()


def load_use_cases(filters: dict | None = None) -> pd.DataFrame:
    con = get_connection()
    df = con.execute("SELECT * FROM use_cases ORDER BY id").fetchdf()
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


def insert_use_case(record: dict) -> int:
    con = get_connection()
    record = {**record}
    record.setdefault("collected_at", date.today())
    record.setdefault("last_verified", date.today())
    fields = [c for c in COLUMNS if c != "id" and c in record]
    placeholders = ", ".join(["?"] * len(fields))
    values = [record[f] for f in fields]
    new_id = con.execute(
        f"INSERT INTO use_cases ({', '.join(fields)}) VALUES ({placeholders}) RETURNING id",
        values,
    ).fetchone()[0]
    con.close()
    return new_id


def update_use_case(id: int, record: dict) -> None:
    con = get_connection()
    record = {**record, "last_verified": date.today()}
    fields = [c for c in COLUMNS if c != "id" and c in record]
    set_clause = ", ".join(f"{f} = ?" for f in fields)
    values = [record[f] for f in fields] + [id]
    con.execute(f"UPDATE use_cases SET {set_clause} WHERE id = ?", values)
    con.close()


def seed_from_csv(path: str | Path) -> int:
    con = get_connection()
    con.execute("DROP TABLE IF EXISTS use_cases")
    con.execute("DROP SEQUENCE IF EXISTS use_cases_id_seq")
    con.close()
    init_db()

    df = pd.read_csv(path)
    con = get_connection()
    con.register("seed_df", df)
    cols = [c for c in COLUMNS if c in df.columns and c != "id"]
    con.execute(f"INSERT INTO use_cases ({', '.join(cols)}) SELECT {', '.join(cols)} FROM seed_df")
    count = con.execute("SELECT COUNT(*) FROM use_cases").fetchone()[0]
    con.close()
    return count


def export_csv(path: str | Path) -> None:
    df = load_use_cases()
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
