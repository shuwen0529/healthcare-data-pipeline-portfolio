"""Optimized incremental processing pipeline.

This sample demonstrates how a batch pipeline can be redesigned to process only
new/changed records, pre-aggregate expensive transformations, and write a quality
report for each run.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .quality_report import build_quality_report

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "sample"
OUTPUT_DIR = BASE_DIR / "output"


def load_incremental_records(last_processed_date: str) -> pd.DataFrame:
    """Load only records after the latest successful processing date."""
    source = pd.read_csv(DATA_DIR / "daily_activity.csv", parse_dates=["activity_date"])
    return source[source["activity_date"] > pd.Timestamp(last_processed_date)].copy()


def optimize_transformations(df: pd.DataFrame) -> pd.DataFrame:
    """Apply efficient vectorized transformations and pre-aggregation.

    Optimization principles demonstrated here:
    - Filter early to reduce rows before joins/aggregations.
    - Use vectorized operations instead of row-by-row loops.
    - Pre-aggregate to the reporting grain before writing output.
    """
    if df.empty:
        return pd.DataFrame(
            columns=["member_id", "activity_month", "activity_type", "activity_count", "total_amount"]
        )

    df = df[df["status"].eq("valid")].copy()
    df["activity_type"] = df["activity_type"].str.lower().str.strip()
    df["activity_month"] = df["activity_date"].dt.to_period("M").astype(str)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    aggregated = (
        df.groupby(["member_id", "activity_month", "activity_type"], as_index=False)
        .agg(activity_count=("activity_date", "size"), total_amount=("amount", "sum"))
        .sort_values(["member_id", "activity_month", "activity_type"])
    )
    return aggregated


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    raw_incremental = load_incremental_records(last_processed_date="2025-01-31")
    quality_report = build_quality_report(raw_incremental, pipeline_name="daily_activity_incremental")
    optimized_output = optimize_transformations(raw_incremental)

    quality_report.to_csv(OUTPUT_DIR / "quality_report.csv", index=False)
    optimized_output.to_csv(OUTPUT_DIR / "monthly_activity_features.csv", index=False)

    print(f"Processed {len(raw_incremental):,} incremental source records")
    print(f"Created {len(optimized_output):,} aggregated analytical rows")


if __name__ == "__main__":
    main()
