# Architecture

## Overview
- Data flow: raw -> processed -> analysis notebooks and KPI report.
- Source of truth for analysis: `data/processed/retail_clean.parquet`.

## Key Artifacts
- Data cleaning: `notebooks/02_data_quality.ipynb`
- KPI analysis: `src/kpi_analysis.py` and `notebooks/03_kpi_analysis.ipynb`
- Report: `reports/kpi_summary.md`
