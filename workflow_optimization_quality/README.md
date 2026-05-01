# Sample 2: Pipeline Optimization and Data Quality Monitoring

## Purpose
This sample represents an anonymized pipeline optimization project. The goal is to improve runtime, reduce redundant processing, and create transparent run-level quality reporting.

## What this demonstrates
- Incremental processing design
- Pipeline performance optimization patterns
- Data quality monitoring and exception reporting
- SQL query optimization techniques
- Production-oriented Python structure

## Files to highlight
- `src/workflow_quality/optimized_pipeline.py`: optimized incremental pipeline pattern
- `src/workflow_quality/quality_report.py`: run-level data quality summary
- `sql/optimized_incremental_load.sql`: SQL optimization example
- `tests/test_quality_report.py`: test coverage for reporting logic

## How to run
```bash
pip install -r ../requirements.txt
python -m src.workflow_quality.optimized_pipeline
pytest tests
```
