"""Load the curated seed CSV into the DuckDB store. Run with: python -m scripts.seed_db"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import storage

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"
SEED_CSV = SEED_DIR / "ai_tooling_use_cases_seed.csv"
CASE_STUDIES_SEED_CSV = SEED_DIR / "company_case_studies_seed.csv"
MARKET_CONTEXT_SEED_CSV = SEED_DIR / "market_context_seed.csv"
TOPICS_SEED_CSV = SEED_DIR / "topics_seed.csv"
USE_CASE_TOPICS_SEED_CSV = SEED_DIR / "ai_tooling_use_case_topics_seed.csv"
ACHIEVEMENTS_SEED_CSV = SEED_DIR / "achievements_seed.csv"
LINKS_SEED_CSV = SEED_DIR / "ai_tooling_use_case_case_study_links_seed.csv"
AGENTS_SEED_CSV = SEED_DIR / "agents_seed.csv"
AGENT_PATTERNS_SEED_CSV = SEED_DIR / "agent_patterns_seed.csv"
AGENT_PATTERN_LINKS_SEED_CSV = SEED_DIR / "agent_pattern_links_seed.csv"


def main() -> None:
    storage.init_db()
    count = storage.seed_ai_tooling_use_cases_from_csv(SEED_CSV)
    print(f"Seeded {count} AI tooling use cases into {storage.DB_PATH}")
    case_study_count = storage.seed_case_studies_from_csv(CASE_STUDIES_SEED_CSV)
    print(f"Seeded {case_study_count} company case studies into {storage.DB_PATH}")
    market_context_count = storage.seed_market_context_from_csv(MARKET_CONTEXT_SEED_CSV)
    print(f"Seeded {market_context_count} market context rows into {storage.DB_PATH}")

    # Depends on ai_tooling_use_cases/company_case_studies already being seeded above.
    topics_count = storage.seed_topics_from_csv(TOPICS_SEED_CSV)
    print(f"Seeded {topics_count} topics into {storage.DB_PATH}")
    use_case_topics_count = storage.seed_ai_tooling_use_case_topics_from_csv(USE_CASE_TOPICS_SEED_CSV)
    print(f"Seeded {use_case_topics_count} use-case/topic tags into {storage.DB_PATH}")
    achievements_count = storage.seed_achievements_from_csv(ACHIEVEMENTS_SEED_CSV)
    print(f"Seeded {achievements_count} achievements into {storage.DB_PATH}")
    links_count = storage.seed_ai_tooling_use_case_case_study_links_from_csv(LINKS_SEED_CSV)
    print(f"Seeded {links_count} use-case/case-study links into {storage.DB_PATH}")
    sources_count = storage.backfill_sources_from_existing()
    print(f"Derived {sources_count} normalized source rows into {storage.DB_PATH}")

    agents_count = storage.seed_agents_from_csv(AGENTS_SEED_CSV)
    print(f"Seeded {agents_count} agents into {storage.DB_PATH}")
    agent_patterns_count = storage.seed_agent_patterns_from_csv(AGENT_PATTERNS_SEED_CSV)
    print(f"Seeded {agent_patterns_count} agent patterns into {storage.DB_PATH}")
    agent_pattern_links_count = storage.seed_agent_pattern_links_from_csv(AGENT_PATTERN_LINKS_SEED_CSV)
    print(f"Seeded {agent_pattern_links_count} agent/pattern links into {storage.DB_PATH}")


if __name__ == "__main__":
    main()
