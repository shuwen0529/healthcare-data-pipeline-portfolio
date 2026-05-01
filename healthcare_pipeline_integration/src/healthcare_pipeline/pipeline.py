"""End-to-end healthcare/commercial data integration pipeline.

This sample uses synthetic data and simplified business rules. It demonstrates the
same structure used in production analytics pipelines: ingestion, validation,
standardization, integration, and final analytical dataset creation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .validators import (
    check_allowed_values,
    check_date_order,
    check_primary_key,
    require_columns,
)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "sample"
OUTPUT_DIR = BASE_DIR / "output"


REQUIRED_MEMBER_COLUMNS = ["member_id", "region", "coverage_start", "coverage_end"]
REQUIRED_ACTIVITY_COLUMNS = ["member_id", "activity_date", "activity_type", "amount"]


def load_sources() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load synthetic source data from CSV files."""
    members = pd.read_csv(DATA_DIR / "members.csv")
    activity = pd.read_csv(DATA_DIR / "activity.csv")
    return members, activity


def standardize_members(members: pd.DataFrame) -> pd.DataFrame:
    """Standardize member-level source data."""
    members = members.copy()
    members["region"] = members["region"].str.upper().str.strip()
    members["coverage_start"] = pd.to_datetime(members["coverage_start"])
    members["coverage_end"] = pd.to_datetime(members["coverage_end"])
    return members


def standardize_activity(activity: pd.DataFrame) -> pd.DataFrame:
    """Standardize activity/transaction-like data."""
    activity = activity.copy()
    activity["activity_type"] = activity["activity_type"].str.lower().str.strip()
    activity["activity_date"] = pd.to_datetime(activity["activity_date"])
    activity["amount"] = pd.to_numeric(activity["amount"], errors="coerce").fillna(0)
    return activity


def run_validations(members: pd.DataFrame, activity: pd.DataFrame) -> None:
    """Run critical validation checks and stop pipeline on failed checks."""
    checks = [
        require_columns(members, REQUIRED_MEMBER_COLUMNS),
        require_columns(activity, REQUIRED_ACTIVITY_COLUMNS),
        check_primary_key(members, ["member_id"]),
        check_allowed_values(activity, "activity_type", {"visit", "rx", "lab", "other"}),
        check_date_order(members, "coverage_start", "coverage_end"),
    ]

    failed = [result for result in checks if not result.passed]
    for result in checks:
        print(f"[{result.check_name}] {result.message}")

    if failed:
        messages = "; ".join(result.message for result in failed)
        raise ValueError(f"Pipeline failed validation: {messages}")


def build_analytical_dataset(members: pd.DataFrame, activity: pd.DataFrame) -> pd.DataFrame:
    """Create member-level analytical features for reporting/modeling."""
    eligible_activity = activity.merge(members, on="member_id", how="inner")
    eligible_activity = eligible_activity[
        (eligible_activity["activity_date"] >= eligible_activity["coverage_start"])
        & (eligible_activity["activity_date"] <= eligible_activity["coverage_end"])
    ]

    features = (
        eligible_activity.groupby(["member_id", "region"], as_index=False)
        .agg(
            total_activity_count=("activity_type", "size"),
            total_amount=("amount", "sum"),
            rx_count=("activity_type", lambda s: int((s == "rx").sum())),
            lab_count=("activity_type", lambda s: int((s == "lab").sum())),
            last_activity_date=("activity_date", "max"),
        )
        .sort_values("member_id")
    )
    return features


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    members, activity = load_sources()
    members = standardize_members(members)
    activity = standardize_activity(activity)
    run_validations(members, activity)
    analytical = build_analytical_dataset(members, activity)
    analytical.to_csv(OUTPUT_DIR / "member_analytical_dataset.csv", index=False)
    print(f"Created {len(analytical):,} analytical rows")


if __name__ == "__main__":
    main()
