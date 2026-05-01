"""Reusable data quality validators for healthcare analytics pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class ValidationResult:
    check_name: str
    passed: bool
    failed_count: int
    message: str


def require_columns(df: pd.DataFrame, required_columns: Iterable[str]) -> ValidationResult:
    """Verify that all required columns exist before downstream processing."""
    missing = sorted(set(required_columns) - set(df.columns))
    return ValidationResult(
        check_name="required_columns",
        passed=len(missing) == 0,
        failed_count=len(missing),
        message="All required columns present" if not missing else f"Missing columns: {missing}",
    )


def check_primary_key(df: pd.DataFrame, key_columns: list[str]) -> ValidationResult:
    """Check that a compound key is not null and is unique."""
    null_mask = df[key_columns].isna().any(axis=1)
    duplicate_mask = df.duplicated(subset=key_columns, keep=False)
    failed_count = int((null_mask | duplicate_mask).sum())
    return ValidationResult(
        check_name="primary_key",
        passed=failed_count == 0,
        failed_count=failed_count,
        message=f"{failed_count} rows have null or duplicate keys",
    )


def check_allowed_values(df: pd.DataFrame, column: str, allowed_values: set[str]) -> ValidationResult:
    """Validate domain values such as status, channel, or record type."""
    invalid_mask = ~df[column].isin(allowed_values)
    failed_count = int(invalid_mask.sum())
    return ValidationResult(
        check_name=f"allowed_values:{column}",
        passed=failed_count == 0,
        failed_count=failed_count,
        message=f"{failed_count} invalid values found in {column}",
    )


def check_date_order(df: pd.DataFrame, start_col: str, end_col: str) -> ValidationResult:
    """Ensure date ranges are logically valid."""
    invalid_mask = pd.to_datetime(df[end_col]) < pd.to_datetime(df[start_col])
    failed_count = int(invalid_mask.sum())
    return ValidationResult(
        check_name="date_order",
        passed=failed_count == 0,
        failed_count=failed_count,
        message=f"{failed_count} rows have end date before start date",
    )
