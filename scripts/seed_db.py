"""Load the curated seed CSV into the DuckDB store. Run with: python -m scripts.seed_db"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import storage

SEED_CSV = Path(__file__).resolve().parent.parent / "data" / "seed" / "use_cases_seed.csv"
CASE_STUDIES_SEED_CSV = Path(__file__).resolve().parent.parent / "data" / "seed" / "company_case_studies_seed.csv"
MARKET_CONTEXT_SEED_CSV = Path(__file__).resolve().parent.parent / "data" / "seed" / "market_context_seed.csv"


def main() -> None:
    storage.init_db()
    count = storage.seed_from_csv(SEED_CSV)
    print(f"Seeded {count} use cases into {storage.DB_PATH}")
    case_study_count = storage.seed_case_studies_from_csv(CASE_STUDIES_SEED_CSV)
    print(f"Seeded {case_study_count} company case studies into {storage.DB_PATH}")
    market_context_count = storage.seed_market_context_from_csv(MARKET_CONTEXT_SEED_CSV)
    print(f"Seeded {market_context_count} market context rows into {storage.DB_PATH}")


if __name__ == "__main__":
    main()
