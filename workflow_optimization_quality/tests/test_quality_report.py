import pandas as pd

from workflow_quality.quality_report import build_quality_report, metric_status


def test_metric_status_max_threshold():
    assert metric_status(0.01, 0.05, "max") == "PASS"
    assert metric_status(0.10, 0.05, "max") == "FAIL"


def test_quality_report_contains_expected_checks():
    df = pd.DataFrame(
        {
            "member_id": [1001, 1002],
            "activity_date": ["2025-02-01", "2025-02-02"],
            "activity_type": ["rx", "lab"],
            "amount": [10.0, 20.0],
        }
    )
    report = build_quality_report(df, "test_pipeline")
    assert set(report["check_name"]) == {
        "row_count",
        "null_member_rate",
        "negative_amount_rate",
        "duplicate_rate",
    }
    assert report.loc[report["check_name"] == "row_count", "status"].item() == "PASS"
