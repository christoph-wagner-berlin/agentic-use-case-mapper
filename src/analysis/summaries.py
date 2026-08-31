"""Pure analysis functions over the use_cases DataFrame. No Streamlit imports here."""

import numpy as np
import pandas as pd


def counts_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("category").size().reset_index(name="count").sort_values("count", ascending=False)


def avg_score_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")["business_value_score"]
        .mean()
        .round(2)
        .reset_index(name="avg_business_value_score")
        .sort_values("avg_business_value_score", ascending=False)
    )


def counts_by_maturity(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("maturity").size().reset_index(name="count").sort_values("count", ascending=False)


def roi_driver_counts(df: pd.DataFrame) -> pd.DataFrame:
    tags = (
        df["roi_drivers"]
        .dropna()
        .str.split(";")
        .explode()
        .str.strip()
    )
    tags = tags[tags != ""]
    counts = tags.value_counts().reset_index(name="count")
    counts.columns = ["roi_driver", "count"]
    return counts


def _explode_tags(series: pd.Series) -> pd.Series:
    tags = series.dropna().str.split(";").explode().str.strip()
    return tags[tags != ""]


def counts_by_year(df: pd.DataFrame, date_column: str = "first_available") -> pd.DataFrame:
    years = pd.to_datetime(df[date_column]).dt.year
    return (
        years.value_counts()
        .sort_index()
        .reset_index(name="count")
        .rename(columns={"index": "year", date_column: "year"})
    )


def cumulative_by_year(df: pd.DataFrame, date_column: str = "first_available") -> pd.DataFrame:
    yearly = counts_by_year(df, date_column)
    yearly["cumulative_count"] = yearly["count"].cumsum()
    return yearly


def grouped_counts_by_year(
    df: pd.DataFrame, group_column: str, date_column: str = "first_available", explode: bool = False
) -> pd.DataFrame:
    """Count of rows per (year, group) pair, long format.

    explode=True splits group_column on ';' first (tag columns like target_industries/
    target_departments); explode=False groups the column directly (scalar columns like
    category/deployment_status).
    """
    work = df[[date_column, group_column]].copy()
    work["year"] = pd.to_datetime(work[date_column]).dt.year
    if explode:
        work[group_column] = work[group_column].str.split(";")
        work = work.explode(group_column)
        work[group_column] = work[group_column].str.strip()
    work = work[work[group_column].notna() & (work[group_column] != "")]
    return work.groupby(["year", group_column]).size().reset_index(name="count")


def growth_forecast(
    df: pd.DataFrame,
    group_column: str,
    date_column: str = "first_available",
    explode: bool = False,
    forecast_years: int = 2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Naive linear-trend extrapolation per group, for illustrative "which areas are growing"
    charts — NOT a statistical forecast (the underlying dataset is small and curated).

    Returns (series_df, summary_df):
      series_df: year, group, count, is_forecast — actual history plus `forecast_years` of
        projected points (clipped at >=0), for charting actual (solid) vs. projected (dashed).
      summary_df: one row per group with total_count, avg_business_value_score (if present
        in df), years_of_history, and recent_share (count in the latest observed year /
        total_count) — a size-normalized momentum metric so a small-but-accelerating group
        isn't drowned out by a large-but-flat one. years_of_history < 2 means no trend could
        be fit; those groups are still returned (recent_share only) but flagged insufficient.
    """
    counts = grouped_counts_by_year(df, group_column, date_column, explode)
    if counts.empty:
        return (
            pd.DataFrame(columns=["year", group_column, "count", "is_forecast"]),
            pd.DataFrame(columns=[group_column, "total_count", "years_of_history", "recent_share", "insufficient_history"]),
        )

    all_years = list(range(int(counts["year"].min()), int(counts["year"].max()) + 1))
    last_year = all_years[-1]
    groups = sorted(counts[group_column].unique())

    series_rows = []
    summary_rows = []
    for group in groups:
        g = counts[counts[group_column] == group].set_index("year")["count"]
        full_series = g.reindex(all_years, fill_value=0)
        years_of_history = int((full_series > 0).sum())
        total_count = int(full_series.sum())

        for year, count in full_series.items():
            series_rows.append({"year": year, group_column: group, "count": int(count), "is_forecast": False})

        insufficient = years_of_history < 2
        if not insufficient:
            slope, intercept = np.polyfit(all_years, full_series.values, 1)
            for offset in range(1, forecast_years + 1):
                year = last_year + offset
                projected = max(0.0, slope * year + intercept)
                series_rows.append({"year": year, group_column: group, "count": round(projected, 1), "is_forecast": True})

        recent_share = round(float(full_series.iloc[-1]) / total_count, 3) if total_count else 0.0
        summary_row = {
            group_column: group,
            "total_count": total_count,
            "years_of_history": years_of_history,
            "recent_share": recent_share,
            "insufficient_history": insufficient,
        }
        if "business_value_score" in df.columns:
            if explode:
                match = df[df[group_column].fillna("").str.split(";").apply(lambda parts: group in [p.strip() for p in parts])]
            else:
                match = df[df[group_column] == group]
            if len(match):
                summary_row["avg_business_value_score"] = round(float(match["business_value_score"].mean()), 2)
        summary_rows.append(summary_row)

    series_df = pd.DataFrame(series_rows)
    summary_df = pd.DataFrame(summary_rows)
    return series_df, summary_df


def quantification_rate_by_year(df: pd.DataFrame, date_column: str = "date_reported") -> pd.DataFrame:
    work = df.copy()
    work["year"] = pd.to_datetime(work[date_column]).dt.year
    grouped = work.groupby("year")["financial_impact_usd"].agg(
        quantified=lambda s: int(s.notna().sum()), total="size"
    ).reset_index()
    grouped["rate"] = (grouped["quantified"] / grouped["total"]).round(3)
    return grouped


def cumulative_financial_impact_by_year(df: pd.DataFrame, date_column: str = "date_reported") -> pd.DataFrame:
    quantified = df[df["financial_impact_usd"].notna()].copy()
    quantified["year"] = pd.to_datetime(quantified[date_column]).dt.year
    yearly = quantified.groupby("year")["financial_impact_usd"].sum().reset_index(name="annual_disclosed_usd")
    yearly["cumulative_disclosed_usd"] = yearly["annual_disclosed_usd"].cumsum()
    return yearly


def industry_counts(df: pd.DataFrame) -> pd.DataFrame:
    tags = _explode_tags(df["target_industries"])
    counts = tags.value_counts().reset_index(name="count")
    counts.columns = ["industry", "count"]
    return counts


def avg_score_by_industry(df: pd.DataFrame) -> pd.DataFrame:
    exploded = df[["business_value_score", "target_industries"]].copy()
    exploded["industry"] = exploded["target_industries"].str.split(";")
    exploded = exploded.explode("industry")
    exploded["industry"] = exploded["industry"].str.strip()
    exploded = exploded[exploded["industry"] != ""]
    return (
        exploded.groupby("industry")["business_value_score"]
        .mean()
        .round(2)
        .reset_index(name="avg_business_value_score")
        .sort_values("avg_business_value_score", ascending=False)
    )


def department_counts(df: pd.DataFrame) -> pd.DataFrame:
    tags = _explode_tags(df["target_departments"])
    counts = tags.value_counts().reset_index(name="count")
    counts.columns = ["department", "count"]
    return counts


def avg_score_by_department(df: pd.DataFrame) -> pd.DataFrame:
    exploded = df[["business_value_score", "target_departments"]].copy()
    exploded["department"] = exploded["target_departments"].str.split(";")
    exploded = exploded.explode("department")
    exploded["department"] = exploded["department"].str.strip()
    exploded = exploded[exploded["department"] != ""]
    return (
        exploded.groupby("department")["business_value_score"]
        .mean()
        .round(2)
        .reset_index(name="avg_business_value_score")
        .sort_values("avg_business_value_score", ascending=False)
    )


def industry_department_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Use-case counts for every (industry, department) pair, long format."""
    exploded = df[["target_industries", "target_departments"]].copy()
    exploded["industry"] = exploded["target_industries"].str.split(";")
    exploded["department"] = exploded["target_departments"].str.split(";")
    exploded = exploded.explode("industry").explode("department")
    exploded["industry"] = exploded["industry"].str.strip()
    exploded["department"] = exploded["department"].str.strip()
    exploded = exploded[(exploded["industry"] != "") & (exploded["department"] != "")]
    return exploded.groupby(["industry", "department"]).size().reset_index(name="count")


def case_studies_by_industry(df: pd.DataFrame) -> pd.DataFrame:
    counts = df.groupby("industry").size().reset_index(name="count")
    return counts.sort_values("count", ascending=False)


def case_studies_by_gain_type(df: pd.DataFrame) -> pd.DataFrame:
    tags = _explode_tags(df["gain_type"])
    counts = tags.value_counts().reset_index(name="count")
    counts.columns = ["gain_type", "count"]
    return counts


def case_studies_by_confidence(df: pd.DataFrame) -> pd.DataFrame:
    order = ["high", "moderate", "directional"]
    counts = df.groupby("confidence").size().reset_index(name="count")
    counts["confidence"] = pd.Categorical(counts["confidence"], categories=order, ordered=True)
    return counts.sort_values("confidence")


def case_studies_by_department(df: pd.DataFrame) -> pd.DataFrame:
    tags = _explode_tags(df["target_departments"])
    counts = tags.value_counts().reset_index(name="count")
    counts.columns = ["department", "count"]
    return counts


def case_studies_industry_department_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Case-study counts for every (industry, department) pair, long format."""
    exploded = df[["industry", "target_departments"]].copy()
    exploded["department"] = exploded["target_departments"].str.split(";")
    exploded = exploded.explode("department")
    exploded["industry"] = exploded["industry"].str.strip()
    exploded["department"] = exploded["department"].str.strip()
    exploded = exploded[(exploded["industry"] != "") & (exploded["department"] != "")]
    return exploded.groupby(["industry", "department"]).size().reset_index(name="count")


def financial_impact_by_industry(df: pd.DataFrame) -> pd.DataFrame:
    quantified = df[df["financial_impact_usd"].notna()]
    return (
        quantified.groupby("industry")["financial_impact_usd"]
        .sum()
        .reset_index(name="total_financial_impact_usd")
        .sort_values("total_financial_impact_usd", ascending=False)
    )


def financial_impact_by_department(df: pd.DataFrame) -> pd.DataFrame:
    quantified = df[df["financial_impact_usd"].notna()][["target_departments", "financial_impact_usd"]].copy()
    quantified["department"] = quantified["target_departments"].str.split(";")
    quantified = quantified.explode("department")
    quantified["department"] = quantified["department"].str.strip()
    quantified = quantified[quantified["department"] != ""]
    return (
        quantified.groupby("department")["financial_impact_usd"]
        .sum()
        .reset_index(name="total_financial_impact_usd")
        .sort_values("total_financial_impact_usd", ascending=False)
    )


def deployment_status_counts(df: pd.DataFrame) -> pd.DataFrame:
    order = ["pilot", "scaled/production", "scaled then partially reversed", "discontinued"]
    counts = df.groupby("deployment_status").size().reset_index(name="count")
    counts["deployment_status"] = pd.Categorical(counts["deployment_status"], categories=order, ordered=True)
    return counts.sort_values("deployment_status")


def quantification_rate(df: pd.DataFrame) -> dict:
    quantified = int(df["financial_impact_usd"].notna().sum())
    total = len(df)
    return {
        "quantified": quantified,
        "total": total,
        "rate": round(quantified / total, 3) if total else 0.0,
    }


def market_context_by_category(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split market_context rows into a dict keyed by context_category, each sorted by metric."""
    return {
        category: group.sort_values("metric")
        for category, group in df.groupby("context_category")
    }
