"""Data quality reporting utilities for analytics pipelines."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone

import pandas as pd


@dataclass(frozen=True)
class QualityMetric:
    pipeline_name: str
    check_name: str
    value: float
    threshold: float
    status: str
    run_timestamp: str


def metric_status(value: float, threshold: float, direction: str = "max") -> str:
    """Return PASS/FAIL based on a numeric threshold."""
    if direction == "max":
        return "PASS" if value <= threshold else "FAIL"
    if direction == "min":
        return "PASS" if value >= threshold else "FAIL"
    raise ValueError("direction must be either 'max' or 'min'")


def build_quality_report(df: pd.DataFrame, pipeline_name: str) -> pd.DataFrame:
    """Create a compact run-level quality report for monitoring."""
    timestamp = datetime.now(timezone.utc).isoformat()
    row_count = len(df)
    null_member_rate = float(df["member_id"].isna().mean()) if row_count else 0.0
    negative_amount_rate = float((df["amount"] < 0).mean()) if row_count else 0.0
    duplicate_rate = float(df.duplicated(subset=["member_id", "activity_date", "activity_type"]).mean()) if row_count else 0.0

    metrics = [
        QualityMetric(pipeline_name, "row_count", row_count, 1, metric_status(row_count, 1, "min"), timestamp),
        QualityMetric(pipeline_name, "null_member_rate", null_member_rate, 0.001, metric_status(null_member_rate, 0.001), timestamp),
        QualityMetric(pipeline_name, "negative_amount_rate", negative_amount_rate, 0.0, metric_status(negative_amount_rate, 0.0), timestamp),
        QualityMetric(pipeline_name, "duplicate_rate", duplicate_rate, 0.0, metric_status(duplicate_rate, 0.0), timestamp),
    ]
    return pd.DataFrame([asdict(metric) for metric in metrics])
