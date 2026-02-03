# RFM Customer Segmentation – E-Commerce Analytics

## Project Overview

This project implements **RFM (Recency, Frequency, Monetary) Customer Segmentation Analysis** on the UCI Online Retail dataset.

RFM is a marketing analytics technique that segments customers based on three dimensions:
- **Recency (R)**: How recently a customer made a purchase (days)
- **Frequency (F)**: How often a customer makes purchases
- **Monetary (M)**: How much money a customer has spent

## Why RFM Over Clustering?

RFM provides **interpretable, actionable business segments** based on transparent rules—not statistical algorithms:

✅ **Non-technical stakeholders understand immediately**: "High R, F, M = VIP"  
✅ **Transparent & auditable**: Every decision is documented  
✅ **Actionable**: Each segment maps to specific marketing actions  
✅ **Fast**: Computes instantly with quantile-based logic  
✅ **Interview-friendly**: No need to explain ML algorithms  

## Project Structure

```
1.1-ecommerce-analytics/
├── data/
│   ├── raw/                    # Original dataset
│   └── processed/
│       └── retail_raw.parquet  # Cleaned transaction data
├── src/
│   ├── download_data.py        # Download UCI Online Retail dataset
│   ├── kpi_analysis.py         # KPI computation & reporting
│   └── rfm.py                  # **NEW** RFM segmentation module
├── notebooks/
│   ├── 01_eda.ipynb            # Exploratory Data Analysis
│   └── 02_rfm_analysis.ipynb   # **NEW** RFM analysis & insights
├── tests/
│   └── test_rfm.py             # **NEW** Unit tests for RFM module
├── reports/
│   ├── kpi_summary.md          # KPI report
│   ├── rfm_report.md           # **NEW** RFM segment summary
│   ├── rfm_segments.csv        # **NEW** Customer segments (CSV)
│   └── figures/
│       ├── segment_distribution.png  # Segment counts
│       ├── segment_revenue.png       # Revenue by segment
│       └── rfm_scatter.png           # F vs M visualization
└── docs/
    ├── RFM_GUIDE.md            # Interview guide
    ├── RFM_IMPLEMENTATION.md   # Implementation details
    └── skill-mapping.md        # Skills demonstrated
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run RFM Segmentation

```bash
# Basic usage (uses max date in data as snapshot)
python src/rfm.py --data data/processed/retail_raw.parquet

# Specify snapshot date for Recency calculation
python src/rfm.py --data data/processed/retail_raw.parquet \
                   --snapshot 2011-12-09 \
                   --output reports/rfm_segmentation.parquet
```

### 3. Explore Results

- **`reports/rfm_report.md`** – Segment statistics and marketing recommendations
- **`reports/rfm_segments.csv`** – Full customer list with segments
- **`reports/figures/`** – Visualizations (segment distribution, revenue breakdown, scatter plots)

### 4. Run Notebook

```bash
jupyter notebook notebooks/02_rfm_analysis.ipynb
```

## RFM Segment Definitions

| Segment | Rules | Count | Revenue | Action |
|---------|-------|-------|---------|--------|
| **VIP/Champions** | R≥4, F≥4, M≥4 | ~1% | ~30% | VIP programs, exclusive offers, priority support |
| **Loyal** | F≥4, M≥3, R≥2 | ~5% | ~25% | Loyalty rewards, early access, upsell |
| **Growth Potential** | R≥4, F≤2, M≤2 | ~15% | ~10% | Cross-sell, engagement nurture |
| **At Risk** | R≤2, F≥3, M≥2 | ~10% | ~15% | Win-back campaigns, special offers |
| **Dormant** | R≤1 | ~20% | ~5% | Re-engagement or cleanup |
| **Mainstream** | All others | ~50% | ~15% | Regular campaigns |

## Data

- **Source**: [UCI Online Retail Dataset](https://archive.ics.uci.edu/ml/datasets/online+retail)
- **Records**: ~500K transactions
- **Customers**: ~4,300 unique
- **Period**: Dec 2010 – Dec 2011
- **Format**: Cleaned, deduplicated Parquet file

## Files Description

### src/rfm.py – Core RFM Module

Functions:
- `load_transactions(path)` – Load & validate transaction data
- `compute_rfm(df, snapshot_date)` – Calculate R, F, M metrics
- `score_rfm(rfm, bins)` – Quantile-based scoring (1-5 scale)
- `segment_rfm(rfm_scored)` – Assign business logic segments
- `generate_rfm_report(rfm_segmented)` – Create markdown report
- `plot_rfm_segments(rfm_segmented, output_dir)` – Generate visualizations
- `main()` – CLI entry point

**Interview-Ready**: All functions include PURPOSE, RATIONALE, and Q&A in docstrings.

### notebooks/02_rfm_analysis.ipynb – Analysis Notebook

Step-by-step RFM analysis with:
- Data loading & exploration
- RFM metric computation
- Score interpretation
- Segment profiling
- Visualizations
- Marketing recommendations

### tests/test_rfm.py – Unit Tests

Coverage:
- Data loading validation
- RFM computation correctness
- Quantile scoring verification
- Segment assignment logic
- Edge cases (single customer, identical values, NaNs)
- Full pipeline integration test

Run tests:
```bash
pytest tests/test_rfm.py -v
```

## Output Artifacts

### 1. rfm_segmentation.parquet
Full dataset with RFM scores and segments:
```
CustomerID | Recency | Frequency | Monetary | R_Score | F_Score | M_Score | RFM_Score | Segment
12345      | 5       | 20        | 5000.0   | 5       | 5       | 5       | 555       | VIP/Champions
...
```

### 2. rfm_report.md
Markdown summary:
- Segment overview table
- Segment definitions & actions
- Top customers per segment

### 3. rfm_segments.csv
Excel-friendly export for marketing teams

### 4. Visualizations (figures/)
- `segment_distribution.png` – Customer count by segment
- `segment_revenue.png` – Total revenue by segment
- `rfm_scatter.png` – Frequency vs Monetary (colored by segment)

## Key Insights (Example)

- **VIP Segment** (~1% of customers) generates ~30% of revenue
- **Dormant Segment** (~20% of customers) generates ~5% of revenue
- **At-Risk Segment** represents reactivation opportunity
- **Growth Potential** segment ready for upsells/cross-sells

## Interview Questions & Answers

### Q1: Why RFM over clustering algorithms?
**A:** "RFM uses business logic, not statistical algorithms. Non-technical stakeholders immediately understand 'high R, F, M = VIP'. Clustering requires explaining hyperparameters and distance metrics, which doesn't translate to business actions."

### Q2: Why quantile-based scoring instead of fixed thresholds?
**A:** "Quantiles are distribution-agnostic. A score of 5 always means 'top 20%', regardless of data distribution. Fixed thresholds require manual adjustment if data changes; quantiles adapt automatically."

### Q3: Why invert Recency scoring?
**A:** "Lower days since purchase = more recent = better customer. By inverting, we align all scores: 5 = best, 1 = worst across R, F, M. Consistency in interpretation."

### Q4: What are RFM limitations?
**A:** "Three main: (1) Seasonality-blind—Christmas spikes inflate recency scores. (2) Margin-blind—treats all revenue equally, ignoring profitability. (3) Non-purchase engagement ignored—doesn't capture clicks, opens, support tickets."

### Q5: How would you improve RFM in Phase 2?
**A:** "Weight RFM by product margin (true customer value), add churn prediction on top, track segment migration over time (cohort analysis), integrate non-purchase engagement metrics."

## Code Quality Standards

✅ Type hints on all functions  
✅ Docstrings with PURPOSE, INTERVIEW_Q&A, RATIONALE  
✅ Error handling with informative assertions  
✅ Logging of data transformations  
✅ CLI interface for reproducibility  
✅ Production-ready: no notebooks in src/, modular functions  
✅ Comprehensive unit tests  
✅ Visualization & reporting functions  

## Requirements

See `requirements.txt` and `requirements-lock.txt` for full dependency list.

Key packages:
- pandas >= 3.0.0
- numpy >= 2.4.1
- matplotlib >= 3.10.8
- seaborn (included in matplotlib)
- pytest >= available

## Author & License

**Project**: RFM Customer Segmentation Analysis  
**Dataset**: UCI Online Retail (public domain)  
**License**: MIT (see LICENSE file)

---

**Next Steps**: Use RFM segments for targeted marketing campaigns, retention strategies, and customer lifetime value (CLV) analysis.