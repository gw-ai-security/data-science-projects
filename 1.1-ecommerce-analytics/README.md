# E-Commerce Analytics – Online Retail Dataset

> Purpose: A clear, interview‑ready KPI analysis that supports business decisions in e‑commerce.

## Business Context
The Head of E‑Commerce needs to decide **where to focus inventory, merchandising, and account management**. The dataset captures transactional sales, which are suitable for answering questions about revenue concentration, seasonality, and top‑performing products.

## Objective
Deliver a **reproducible KPI report** from cleaned transaction data that answers:
- Which products, countries, and customers drive revenue?
- How concentrated is revenue (risk of dependency)?
- Are there seasonal patterns that affect inventory planning?

## Methodology (Simple by Design)
1. Load raw Excel → convert to Parquet for stable, fast analysis.
2. Clean data with explicit rules (remove duplicates, filter invalid quantities/prices).
3. Calculate core KPIs and simple aggregates.
4. Generate a compact report with tables and charts.

This project deliberately favors **clarity over complexity** so a candidate can explain every step calmly in an interview.

## Results (from cleaned sales data)
- Time window: 2010‑12‑01 to 2011‑12‑09
- Total revenue: 10,642,110.80
- Orders: 19,960
- Customers: 4,338
- Average order value: 533.17

See `reports/kpi_summary.md` and `reports/03_kpi_analysis.html` for charts and tables.

## Decision Implications (Business)
- **Revenue concentration risk:** A small set of countries and customers drive most revenue → diversify markets and reduce dependency risk.
- **Seasonality:** End‑of‑year spikes → align inventory and staffing with peak months.
- **SKU focus:** A small group of products drives revenue → keep them in stock and use them for bundles.

## Scope & Limitations
- **Missing CustomerID:** Limits customer‑level analysis for anonymous purchases.
- **No cost/margin data:** Revenue is available, but profitability is not.
- **No marketing/channel data:** Cannot attribute revenue to campaigns or channels.

## What Was Deliberately Not Done (and Why)
- **No ML models:** KPI analysis already answers the business questions; ML would reduce explainability for interview settings.
- **No price optimization:** Requires margin and promotion data, which is not available.
- **No customer segmentation (yet):** Needs stable customer identifiers and additional features.

## Next Logical Steps
- **RFM segmentation** for customer prioritization and churn risk.
- **Returns analysis** using negative quantities to understand refund behavior.
- **Product bundling tests** for high‑performing SKUs.

## Interview Readiness
See `docs/INTERVIEW_READINESS.md` for typical interview questions and short, realistic answers.

## Data Source
- Online Retail dataset (UCI Machine Learning Repository).
- Raw file: `data/raw/Online_Retail.xlsx`.

## Project Structure
- `.agent/` – Skills and agent workflow instructions
- `data/` – Raw and processed data
- `notebooks/` – EDA, data quality, KPI analysis
- `reports/` – KPI report, figures, and HTML notebook export
- `src/` – Reusable scripts
- `docs/` – Knowledge base and project status snapshots

## Quickstart
1. Create venv: `python -m venv venv`
2. Install deps: `pip install -r requirements.txt`
3. Run pipeline (raw → clean → report + notebook + HTML):
   `python src/run_pipeline.py`
4. Open notebooks: `jupyter lab`

## Pipeline Commands
- Convert raw Excel to Parquet: `python src/convert_to_parquet.py`
- Clean data: `python src/clean_data.py`
- Generate KPI report only: `python src/kpi_analysis.py --input data/processed/retail_clean.parquet --outdir reports`
- Full pipeline: `python src/run_pipeline.py --skip-notebook --skip-html`

## Reproducibility
- Minimal deps in `requirements.txt`.
- Locked environment in `requirements-lock.txt`.

## Notes
- Language: German (DE) in documentation and notebooks.
- Timestamp: `YYYY‑MM‑DD_HH‑mm` (Europe/Vienna)