"""Loader for config/taxonomy.yaml."""

from pathlib import Path
import yaml

TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "config" / "taxonomy.yaml"


def load_taxonomy() -> dict:
    with open(TAXONOMY_PATH) as f:
        return yaml.safe_load(f)


def category_names() -> list[str]:
    return [c["name"] for c in load_taxonomy()["categories"]]


def tools_for_category(category: str) -> list[dict]:
    for c in load_taxonomy()["categories"]:
        if c["name"] == category:
            return c["tools"]
    return []


def vendor_for_tool(category: str, tool_name: str) -> str:
    for t in tools_for_category(category):
        if t["name"] == tool_name:
            return t["vendor"]
    return ""


def industry_names() -> list[str]:
    return load_taxonomy().get("industries", [])


def department_names() -> list[str]:
    return load_taxonomy().get("departments", [])


def company_size_band_names() -> list[str]:
    return load_taxonomy().get("company_size_bands", [])


def region_names() -> list[str]:
    return load_taxonomy().get("regions", [])
