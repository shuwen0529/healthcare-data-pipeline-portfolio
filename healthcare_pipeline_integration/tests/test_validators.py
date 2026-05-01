import pandas as pd

from healthcare_pipeline.validators import check_primary_key, require_columns


def test_require_columns_passes_when_columns_exist():
    df = pd.DataFrame({"member_id": [1], "region": ["NE"]})
    result = require_columns(df, ["member_id", "region"])
    assert result.passed


def test_require_columns_fails_when_columns_missing():
    df = pd.DataFrame({"member_id": [1]})
    result = require_columns(df, ["member_id", "region"])
    assert not result.passed
    assert result.failed_count == 1


def test_primary_key_detects_duplicates():
    df = pd.DataFrame({"member_id": [1, 1, 2]})
    result = check_primary_key(df, ["member_id"])
    assert not result.passed
    assert result.failed_count == 2
