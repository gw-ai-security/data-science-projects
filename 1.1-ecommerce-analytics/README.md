# E-Commerce Analytics - Online Retail Dataset

> Purpose: End-to-end E-Commerce Analytics with EDA, data quality, KPI analysis and a recruiter-ready report.

## Highlights
- Cleaned transactional dataset with documented quality rules.
- KPI report with revenue trends, top products, top countries and top customers.
- Reproducible pipeline and notebooks.

## Results (from cleaned data)
- Time window: 2010-12-01 to 2011-12-09
- Total revenue: 10,642,110.80
- Orders: 19,960
- Customers: 4,338
- Average order value: 533.17

See `reports/kpi_summary.md` and `reports/03_kpi_analysis.html` for charts and tables.

## Data Source
- Online Retail dataset (UCI Machine Learning Repository).
- Raw file: `data/raw/Online_Retail.xlsx`.

## Project Structure
- `.agent/` - Skills and agent workflow instructions
- `data/` - Raw and processed data
- `notebooks/` - EDA, data quality, KPI analysis
- `reports/` - KPI report, figures, and HTML notebook export
- `src/` - Reusable scripts
- `docs/` - Knowledge base and project status snapshots

## Quickstart
1. Create venv: `python -m venv venv`
2. Install deps: `pip install -r requirements.txt`
3. Run pipeline (raw -> clean -> report + notebook + HTML):
   `python src/run_pipeline.py`
4. Open notebooks: `jupyter lab`

## Pipeline Commands
- Convert raw Excel to parquet: `python src/convert_to_parquet.py`
- Clean data: `python src/clean_data.py`
- Generate KPI report only: `python src/kpi_analysis.py --input data/processed/retail_clean.parquet --outdir reports`
- Full pipeline: `python src/run_pipeline.py --skip-notebook --skip-html`

## Reproducibility
- Minimal deps in `requirements.txt`.
- Locked environment in `requirements-lock.txt`.

## Workflow (Agents)
- Orchestrate -> Document -> Learn
- Check `docs/project_status/` for the latest snapshot

## Notes
- Language: German (DE) in documentation and notebooks.
- Timestamp: `YYYY-MM-DD_HH-mm` (Europe/Vienna)
