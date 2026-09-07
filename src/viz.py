"""Shared chart color palette and canonical axis ordering, validated via the dataviz skill's
CVD-safety checks (see scripts/validate_palette.js in that skill). Import from here instead of
hardcoding colors/order per page."""

from src.taxonomy import (
    category_names, department_names, industry_names, company_size_band_names, region_names,
)

CATEGORY_ORDER = category_names()
DEPARTMENT_ORDER = department_names()
INDUSTRY_ORDER = industry_names()
COMPANY_SIZE_ORDER = company_size_band_names()

# Full validated 8-hue categorical set, fixed order (palette.md) -- first 4 slots are CATEGORY_COLORS;
# use more slots only for a dimension with >4 groups (e.g. top-N + "Other" folding), never re-cycle.
CATEGORICAL_8 = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
CATEGORY_COLORS = dict(zip(CATEGORY_ORDER, CATEGORICAL_8[:4]))
OTHER_COLOR = "#898781"  # de-emphasis gray for a folded "Other" bucket -- never a competing hue

BRAND_BLUE = "#2a78d6"  # single-series bar/line default, replaces Plotly's untouched #636efa

MATURITY_ORDER = ["experimental", "emerging", "mainstream", "enterprise-standard"]
MATURITY_COLORS = dict(zip(MATURITY_ORDER, ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]))

CONFIDENCE_ORDER = ["high", "moderate", "directional"]  # validated ordinal, light=low/dark=high confidence
CONFIDENCE_COLORS = dict(zip(CONFIDENCE_ORDER, ["#0d366b", "#3987e5", "#86b6ef"]))

DEPLOYMENT_STATUS_ORDER = ["pilot", "scaled/production", "scaled then partially reversed", "discontinued"]
DEPLOYMENT_STATUS_COLORS = {  # fixed status palette -- these are outcomes, not identity
    "pilot": "#898781",                           # neutral -- not yet an outcome
    "scaled/production": "#0ca30c",                # status: good
    "scaled then partially reversed": "#fab219",   # status: warning
    "discontinued": "#d03b3b",                     # status: critical
}

SEQUENTIAL_BLUE = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
    "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]

# Binary "present/absent" heatmap treatment (the "emphasis" pattern: one accent hue + de-emphasis
# gray, not a 2-slot categorical pair -- gray is deliberately below the categorical chroma floor).
PRESENCE_SCALE = [[0, "#f0efec"], [1, BRAND_BLUE]]


REGION_ORDER = region_names()
REGION_COLORS = dict(zip(REGION_ORDER[:7], CATEGORICAL_8[:7]))
REGION_COLORS["Global/Multi-region"] = OTHER_COLOR


def ordered_with_extras(canonical_order, present_values):
    """Canonical order first, then any values not in the canonical list (free-text extensions
    beyond the curated taxonomy), in their original relative order. Use before pandas `.reindex()`
    on a pivoted heatmap so a free-text industry/department is never silently dropped -- unlike
    Plotly's own `category_orders=`, `.reindex()` drops anything not in the index list."""
    present = list(present_values)
    return [v for v in canonical_order if v in present] + [v for v in present if v not in canonical_order]
