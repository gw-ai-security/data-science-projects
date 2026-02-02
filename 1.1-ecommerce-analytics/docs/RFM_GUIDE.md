# RFM Segmentation Interview Guide

## What is RFM?
RFM stands for **Recency, Frequency, Monetary**—three dimensions that measure customer value:
- **Recency**: Days since last purchase (lower = more recent = better)
- **Frequency**: Number of purchases (higher = more loyal = better)
- **Monetary**: Total revenue (higher = more valuable = better)

## Why RFM Instead of Clustering?
1. **Interpretable**: "High R, F, M = VIP" is immediately clear to non-technical stakeholders
2. **Transparent**: Every decision is documented and explainable
3. **Actionable**: Each segment maps directly to marketing actions
4. **Fast**: Computes instantly with simple quantile logic
5. **Interview-Friendly**: No need to explain ML algorithms

## RFM Segments

| Segment | Definition | Actions |
|---------|-----------|---------|
| **VIP** | High on all three (R, F, M) | VIP programs, exclusive offers |
| **Loyal** | High F & M, any R | Re-engagement campaigns |
| **At Risk** | Low R, moderate F | Win-back offers |
| **Dormant** | Low on all three | Survey or cleanup |
| **Growth Potential** | High R, low-moderate F & M | Cross-sell, upsell |
| **Mainstream** | Moderate values | Regular engagement |

## Common Interview Questions

### Q1: "Why choose quantile-based scoring over raw thresholds?"
**Answer**: "Quantiles are distribution-agnostic. A score of 5 always means 'top 20%', regardless of how the data is distributed. Raw thresholds would require manual adjustment if the data changes. Quantiles adapt automatically."

### Q2: "What are the limitations of RFM?"
**Answer**: "Three main ones: (1) Seasonality-blind—Christmas spikes inflate recency scores. (2) Margin-blind—treats all revenue equally, ignoring product mix profitability. (3) Non-purchase engagement ignored—doesn't capture email opens, site visits, support tickets."

### Q3: "How would you improve RFM in Phase 2?"
**Answer**: "Weight RFM by product margin (true customer value), add churn prediction on top, track segment migration over time (cohort analysis), and integrate with non-purchase engagement metrics."

### Q4: "Why drop customers with missing CustomerID?"
**Answer**: "RFM requires tracking individuals across time. Guest purchases (missing ID) represent ~25% of transactions but can't be tracked individually. We drop them from customer-level RFM but include them in revenue KPIs."

### Q5: "How do you define segments—rules vs. statistics?"
**Answer**: "I use business logic, not statistical thresholds. A VIP is someone who bought recently, buys often, and spends heavily—three simple conditions. Statistics give us scores (1-5); business logic gives us segments."

## Code Quality

✓ All functions documented with PURPOSE and RATIONALE  
✓ Interview questions embedded in docstrings  
✓ Assertions validate data quality  
✓ Edge cases handled explicitly  
✓ CLI interface for reproducibility  
✓ Outputs documented (Parquet + Markdown)  

---

This is interview-ready: every step is transparent, explainable, and defensible.