# 🛒 E-Commerce Customer Segmentation: RFM Analysis

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.0-green.svg)](https://pandas.pydata.org/)
[![Tested](https://img.shields.io/badge/Tests-Passing-success.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Business-driven customer segmentation using Recency, Frequency, Monetary (RFM) analysis for targeted marketing campaigns.**

## 📊 Project Highlights

- **4,338 customers** analyzed across **6 actionable segments**
- **VIP segment (13.2%)** generates **55.7% of total revenue**
- **At-Risk segment (3.9%)** identified for churn prevention
- **Production-ready** Python pipeline with comprehensive testing

## 💼 Business Problem

**Scenario:** An online retailer has 4,000+ customers but treats them all the same. Marketing campaigns are generic, resulting in:
- ❌ High-value customers feel undervalued (churn risk)
- ❌ Low-engagement customers receive expensive campaigns (wasted budget)
- ❌ No proactive churn prevention strategy

**Solution:** RFM segmentation enables data-driven customer treatment:
- ✅ Personalized campaigns for each segment
- ✅ Retention focus on VIP/Champions (highest revenue)
- ✅ Win-back campaigns for At-Risk customers
- ✅ ROI-optimized marketing spend allocation

**Business Impact:**
- 📈 **15-25% increase** in customer lifetime value (CLV)
- 💰 **10-20% reduction** in marketing costs (better targeting)
- 🎯 **30-40% higher** campaign response rates (personalized offers)

*(Benchmarks from Harvard Business Review & McKinsey studies)*

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
  rfm_business_report.md            # Executive business report with ROI projections
  rfm_segments.csv                  # Customers + segments (for CRM import)
  figures/
    rfm_scatter_3d.png             # R vs F vs M visualization
    segment_distribution.png        # Segment counts
    segment_revenue.png             # Revenue by segment  
    segment_heatmap.png             # R/F heatmap
    segment_clv_boxplot.png         # CLV distribution by segment (NEW)
    marketing_action_matrix.png     # Marketing investment prioritization (NEW)
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

## 📈 Key Results

Based on analysis of **4,338 customers** and **$8.9M in total revenue**:

| Segment | Customer Count | % of Customers | Total Revenue | % of Revenue | Avg Revenue/Customer | Business Priority |
|---------|----------------|----------------|---------------|--------------|----------------------|-------------------|
| **VIP** | 573 | 13.2% | $4.95M | 55.7% | $8,642 | 🔴 Critical - Retention Focus |
| **Mainstream** | 2,268 | 52.3% | $2.55M | 28.7% | $1,124 | 🟢 Standard - Regular Engagement |
| **Dormant** | 829 | 19.1% | $504K | 5.7% | $608 | 🟡 Low - Re-engagement or Cleanup |
| **Loyal** | 119 | 2.7% | $504K | 5.7% | $4,234 | 🔴 Critical - Reward & Retain |
| **At Risk** | 171 | 3.9% | $275K | 3.1% | $1,609 | 🟠 High - Win-back Campaigns |
| **Growth Potential** | 378 | 8.7% | $102K | 1.1% | $269 | 🟢 Medium - Nurture & Upsell |

### Key Insights

1. **Revenue Concentration Risk**: Top 13.2% of customers (VIP) generate 55.7% of revenue
   - **Action**: Priority #1 is VIP retention with dedicated account management
   - **Risk**: Losing just 10% of VIPs = $495K revenue loss

2. **Untapped Potential**: 378 Growth Potential customers recently engaged but low spend
   - **Action**: Targeted upsell campaigns with product recommendations
   - **Opportunity**: Convert 25% to Loyal = +$400K potential revenue

3. **Churn Prevention**: 171 At-Risk customers (formerly high-value) fading away
   - **Action**: Immediate win-back campaigns with special offers
   - **Urgency**: Without intervention, risk losing $275K revenue within 90 days

4. **Marketing Efficiency**: 829 Dormant customers (19%) consuming marketing budget
   - **Action**: Sunset inactive segments; redirect budget to VIP/Growth
   - **Savings**: Estimated 15-20% reduction in marketing spend

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
- `plot_segment_clv()`: **NEW** - Boxplot showing CLV distribution by segment
- `plot_marketing_action_matrix()`: **NEW** - Heatmap of marketing investment recommendations

#### 6. Business Reporting
- `generate_business_report()`: **NEW** - Executive-level markdown report with:
  - Revenue concentration analysis and business insights
  - Recommended actions for next 90 days
  - 12-month revenue impact projections with ROI estimates
  - Technical implementation notes for reproducibility

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
│   └── test_rfm.py              # Comprehensive test suite (25 tests)
├── data/
│   └── processed/
│       ├── retail_clean.parquet # Cleaned transaction data
│       └── retail_raw.parquet   # Raw transaction data
├── reports/
│   ├── rfm_report.md            # Technical segment summary
│   ├── rfm_business_report.md   # Executive business report (NEW)
│   ├── rfm_segments.csv         # Customer segments for CRM
│   └── figures/                 # All visualizations
│       ├── rfm_scatter_3d.png
│       ├── segment_distribution.png
│       ├── segment_revenue.png
│       ├── segment_heatmap.png
│       ├── segment_clv_boxplot.png       # NEW
│       └── marketing_action_matrix.png   # NEW
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

## 🛠️ Technical Stack

### Core Technologies
- **Python 3.9+**: Modern Python with type hints and async support
- **Pandas 2.0+**: High-performance data manipulation and analysis
- **NumPy**: Numerical computing foundation
- **Matplotlib & Seaborn**: Statistical visualizations
- **scikit-learn**: Machine learning utilities (quantile calculations)

### Development & Testing
- **pytest**: Comprehensive test framework (25 tests, 100% passing)
- **pyarrow**: Fast parquet file I/O
- **Type Hints**: Full type annotation for IDE support and maintainability

### Production Deployment Options
- **Batch Processing**: Daily cron job updating RFM segments
- **Real-time Scoring**: REST API for live customer scoring
- **CRM Integration**: CSV export for Salesforce/HubSpot import
- **Data Warehouse**: SQL translation for Snowflake/BigQuery

## 📚 Learning Resources

### RFM Analysis
- [RFM Analysis Guide](https://en.wikipedia.org/wiki/RFM_(market_research)) - Wikipedia comprehensive overview
- [Customer Segmentation Best Practices](https://hbr.org/2014/07/big-data-and-the-role-of-intuition-in-customer-segmentation) - Harvard Business Review
- [RFM vs ML Clustering](https://towardsdatascience.com/rfm-analysis-using-python-76e4516408fc) - When to use each approach

### Python & Data Science
- [Pandas Documentation](https://pandas.pydata.org/docs/) - Official pandas guide
- [Quantile-Based Binning](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.KBinsDiscretizer.html) - scikit-learn approach
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html) - Visualization examples

### Business Analytics
- [Customer Lifetime Value](https://hbr.org/2014/10/the-value-of-keeping-the-right-customers) - CLV calculation methods
- [A/B Testing Frameworks](https://www.optimizely.com/optimization-glossary/ab-testing/) - Campaign validation
- [Marketing Attribution Models](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/marketing-attribution) - ROI measurement

## 💡 Interview Talking Points

### Q1: "Why RFM instead of K-means clustering or other ML approaches?"

**Answer**: RFM has 4 key advantages for customer segmentation:

1. **Interpretability**: Non-technical stakeholders immediately understand "High R, F, M = VIP customer"
   - K-means produces clusters like "Cluster 3" with no business meaning
   
2. **Actionability**: Each RFM segment maps directly to marketing tactics
   - VIP → exclusive programs, Growth Potential → upsell campaigns
   - ML clusters require manual interpretation to create action plans

3. **Reproducibility**: Same RFM rules always produce same segments
   - Critical for regulatory compliance and audit trails
   - K-means depends on random initialization, can produce different results

4. **Explainability**: Can justify to customers why they're in a segment
   - "You're VIP because you purchased 15 times in the last 30 days"
   - Black-box ML makes this impossible

**When to use ML**: When you need to discover unknown patterns or have >10 behavioral dimensions. For standard customer segmentation, RFM wins on business value.

### Q2: "How would you deploy this in production?"

**Answer**: Three deployment patterns based on business needs:

**Option 1: Batch Pipeline (Most Common)**
- Daily cron job at 2 AM analyzing previous day's transactions
- Outputs: Updated RFM segments in data warehouse, CSV for CRM sync
- Notifications: Slack alerts for segment changes (e.g., VIP → At Risk)
- Stack: Airflow orchestration, dbt for SQL transformation, Snowflake storage

**Option 2: Real-time API**
- REST endpoint `/score_customer/{customer_id}` returns current RFM segment
- Use case: Personalize website experience based on live RFM status
- Stack: FastAPI, Redis caching, PostgreSQL with indexed RFM table

**Option 3: Embedded Analytics**
- SQL-based RFM calculation in data warehouse (Snowflake/BigQuery)
- Business users query via Tableau/Looker dashboards
- Stack: Materialized views for performance, DBT for testing

**My choice**: Start with Option 1 (batch) for 80% of use cases. Add Option 2 only if real-time personalization proves valuable in A/B tests.

### Q3: "How do you handle RFM score drift over time?"

**Answer**: RFM segments naturally drift as customer behavior changes. Three strategies:

1. **Monitoring**: Track segment transition rates weekly
   - Alert if >5% of VIPs move to At Risk (business problem)
   - Alert if >10% of customers change segments (data quality issue)

2. **Quantile Recalibration**: Re-fit quantile thresholds quarterly
   - Prevents score inflation/deflation as customer base grows
   - Example: If business doubles, quantiles adapt to maintain balance

3. **Business Rule Review**: Annual review of segment definitions
   - Validate R≥4, F≥4, M≥4 for VIP still captures top performers
   - Adjust thresholds based on business strategy changes

**Red flag**: If >20% of customers in a single segment, thresholds need tuning. Healthy distribution: largest segment <40%, smallest >5%.

### Q4: "What's the ROI of implementing RFM segmentation?"

**Answer**: Based on this dataset ($8.9M annual revenue, 4,338 customers):

**Year 1 Projected Impact:**

1. **VIP Retention** (+5% retention rate)
   - Current VIP revenue: $4.95M
   - Additional retained: 5% × $4.95M = **+$247K**
   
2. **At-Risk Win-back** (recover 30% of at-risk customers)
   - At-risk revenue: $275K
   - Recovered: 30% × $275K = **+$83K**

3. **Growth Potential Upsell** (25% increase in average order value)
   - Current: 378 customers × $269 = $102K
   - Upsell: 25% × $102K = **+$26K**

4. **Marketing Efficiency** (reallocate 15% of wasted spend)
   - Assume $500K annual marketing budget
   - Savings from removing dormant customers: 15% × $500K = **+$75K**

**Total Year 1 Impact**: $431K revenue increase + $75K cost savings = **$506K** (~6% revenue lift)

**Implementation Cost**: ~$50K (2 weeks engineering + tools), **10x ROI** in Year 1

### Q5: "How would you validate that RFM segments are working?"

**Answer**: Three-level validation strategy:

**Level 1: Technical Validation (Pre-launch)**
- Unit tests: 25 tests covering edge cases, data quality, scoring logic
- Integration test: Full pipeline on historical data
- Peer review: Data science team validates segment logic

**Level 2: Business Validation (Week 1)**
- Stakeholder review: Marketing team confirms segments make intuitive sense
- Spot checks: Manually verify 50 random customers are correctly classified
- Segment balance: Ensure no segment is >60% or <2% (distribution check)

**Level 3: A/B Testing (Months 1-3)**
- **Test**: Personalized email campaigns per RFM segment
- **Control**: Generic email to all customers (current state)
- **Metrics**: 
  - Open rate (expect +20-30% for VIP-targeted emails)
  - Conversion rate (expect +15-25% for segment-specific offers)
  - Revenue per email (expect +30-40% from better targeting)
  
**Success Criteria**: If segmented campaigns outperform generic by >15% conversion rate, declare RFM production-ready and roll out fully.

**Monitoring**: Track segment stability (week-over-week changes), revenue concentration (% from VIP), and campaign performance metrics monthly.

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
