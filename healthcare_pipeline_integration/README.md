# Sample 1: Healthcare Data Pipeline Integration

## Purpose
This sample represents an anonymized version of a healthcare/commercial data integration project. The goal is to combine multiple source datasets into a standardized analytical dataset that can support downstream reporting and analysis.

## What this demonstrates
- Python-based ETL pipeline design
- Data standardization across heterogeneous source systems
- Data quality validation before and after integration
- Clear modular code structure
- SQL transformation logic for production-style analytics

## Files to highlight
- `src/healthcare_pipeline/pipeline.py`: end-to-end pipeline orchestration
- `src/healthcare_pipeline/validators.py`: reusable data quality checks
- `sql/create_analytical_dataset.sql`: SQL transformation example
- `tests/test_validators.py`: unit tests for validation logic

## How to run
```bash
pip install -r ../requirements.txt
python -m src.healthcare_pipeline.pipeline
pytest tests
```
