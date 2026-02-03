# E-Commerce Analytics: RFM Customer Segmentation

Professional-grade RFM (Recency, Frequency, Monetary) analysis implementation for customer segmentation and targeted marketing campaigns.

## 🎯 What is RFM?

RFM is a data-driven customer segmentation technique that groups customers based on their purchasing behavior:

- **Recency (R)**: How recently did the customer make a purchase? (Lower = Better)
- **Frequency (F)**: How often do they purchase? (Higher = Better)  
- **Monetary (M)**: How much do they spend? (Higher = Better)

### Why RFM Over Clustering?

**RFM provides:**
- ✅ **Interpretability**: Non-technical stakeholders understand "High R-F-M = VIP"
- ✅ **Actionability**: Each segment maps to specific marketing tactics
- ✅ **Reproducibility**: Same rules always produce same segments
- ✅ **Explainability**: Can justify why a customer is in a segment

**Clustering (K-means, etc.) has:**
- ❌ Black-box algorithms hard to explain
- ❌ Arbitrary segment definitions
- ❌ Difficult to map to business actions

## 🚀 Quick Start

### Installation
```bash
pip install pandas pyarrow matplotlib seaborn scikit-learn
```

### Run the Pipeline
```bash
# Basic usage
python src/rfm.py --data data/processed/retail_clean.parquet

# Custom output and snapshot date
python src/rfm.py --data data/processed/retail_raw.parquet \
                   --snapshot 2011-12-09 \
                   --output reports/rfm_segmentation.parquet
```

### Output Files
```
reports/
  rfm_segmentation.parquet          # Full RFM scores + segments  
  rfm_report.md                     # Markdown summary
  rfm_segments.csv                  # Customers + segments (for CRM import)
  figures/
    rfm_scatter_3d.png             # R vs F vs M visualization
    segment_distribution.png        # Segment counts
    segment_revenue.png             # Revenue by segment  
    segment_heatmap.png             # R/F heatmap
```

## 📊 Customer Segments

Our implementation defines 6 business-driven segments:

| Segment | Criteria | Business Action |
|---------|----------|----------------|
| **VIP/Champions** | R≥4, F≥4, M≥4 | VIP programs, exclusive access, personalized service |
| **Loyal** | F≥4, M≥3, R≥2 | Loyalty rewards, early access to new products |
| **Growth Potential** | R≥4, F≤2, M≤2 | Cross-sell/upsell campaigns, nurture programs |
| **At Risk** | R≤2, F≥3, M≥2 | Win-back campaigns, special offers to prevent churn |
| **Dormant** | R≤1 | Re-engagement campaigns or remove from active marketing |
| **Mainstream** | All others | Regular engagement, standard promotions |

## 🏗️ Architecture

### Core Functions

#### 1. `load_transactions(path)`
Load and validate transaction data from parquet files.
- Validates required schema
- Drops guest purchases (missing CustomerID)
- Computes revenue = Quantity × UnitPrice

#### 2. `compute_rfm(df, snapshot_date)`
Calculate RFM metrics for each customer.
- **Recency**: Days since last purchase
- **Frequency**: Count of unique orders (InvoiceNo)
- **Monetary**: Sum of revenue

#### 3. `score_rfm(rfm, bins=5)`
Convert continuous metrics into 1-5 scores using quantiles.
- **R_Score**: Inverted (recent = high score)
- **F_Score**: Normal (frequent = high score)
- **M_Score**: Normal (high spend = high score)
- Handles duplicate values gracefully

#### 4. `assign_segments(rfm_scored)`
Apply business rules to assign customers to segments.
- Rule-based (not ML clustering)
- Priority order: VIP → Loyal → Growth → At Risk → Dormant → Mainstream

#### 5. Visualization Functions
- `plot_rfm_scatter()`: 3D scatter plot of R/F/M colored by segment
- `plot_segment_distribution()`: Bar chart of segment sizes
- `plot_segment_revenue()`: Revenue contribution by segment
- `plot_rfm_heatmap()`: Heatmap of R vs F scores

### Data Flow
```
Transaction Data (parquet)
    ↓
load_transactions()
    ↓
compute_rfm()
    ↓
score_rfm()
    ↓
assign_segments()
    ↓
Reports + Visualizations
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
pytest tests/test_rfm.py -v
```

**Test Coverage:**
- ✅ Data loading and validation
- ✅ RFM metric computation
- ✅ Quantile-based scoring with duplicates
- ✅ Segment assignment rules
- ✅ Edge cases (empty data, single customer, large datasets)
- ✅ Full pipeline integration

## 📝 Interview-Ready Features

Every function includes:
- **PURPOSE**: What problem does it solve?
- **INTERVIEW Q&A**: Common questions with answers
- **RATIONALE**: Why this approach vs alternatives?

### Example Interview Questions Answered

**Q: Why quantiles instead of fixed thresholds?**  
A: Quantiles adapt to data distribution. Fixed thresholds (e.g., "recency < 30 days = good") fail when data is skewed or changes over time.

**Q: Why count unique invoices instead of rows?**  
A: One order can have multiple line items (rows). We want purchase frequency, not line-item frequency.

**Q: Why is Recency inverted?**  
A: Lower recency (fewer days since purchase) is BETTER (more recent). We invert so high scores = good across all dimensions.

## 📁 Project Structure

```
1.1-ecommerce-analytics/
├── src/
│   └── rfm.py                    # Main RFM implementation
├── tests/
│   └── test_rfm.py              # Comprehensive test suite
├── data/
│   └── processed/
│       ├── retail_clean.parquet # Cleaned transaction data
│       └── retail_raw.parquet   # Raw transaction data
├── reports/
│   ├── rfm_report.md            # Generated summary
│   ├── rfm_segments.csv         # Customer segments
│   └── figures/                 # Visualizations
└── README.md                    # This file
```

## 🎓 Business Impact

RFM segmentation enables:
1. **Targeted Marketing**: Send relevant offers to each segment
2. **Resource Optimization**: Focus retention efforts on high-value customers
3. **Churn Prevention**: Identify at-risk customers before they leave
4. **Revenue Growth**: Nurture growth potential customers with cross-sell/upsell

### Example Results
From our retail dataset (4,338 customers):
- **VIP (13.2%)** generate **55.7% of revenue** → Focus retention here
- **At Risk (3.9%)** need **win-back campaigns** to prevent churn
- **Growth Potential (8.7%)** represent **untapped upsell opportunities**

## 📚 References

- **RFM Analysis**: [Wikipedia](https://en.wikipedia.org/wiki/RFM_(market_research))
- **Customer Segmentation**: [Harvard Business Review](https://hbr.org/2014/07/big-data-and-the-role-of-intuition-in-customer-segmentation)
- **Quantile-Based Binning**: Ensures balanced segments regardless of data skew

## 🤝 Contributing

This is a production-ready implementation suitable for:
- Portfolio projects
- Technical interviews
- Real-world marketing campaigns
- Educational purposes

---

**Author**: Professional Data Science Implementation  
**License**: MIT  
**Status**: Production-Ready ✅
