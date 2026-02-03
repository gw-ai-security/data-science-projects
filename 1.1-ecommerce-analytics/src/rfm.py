"""
RFM (Recency, Frequency, Monetary) Customer Segmentation Analysis

This module provides functions to segment customers based on their purchasing behavior
using the RFM framework, enabling targeted marketing and retention strategies.

KEY CONCEPTS:
- Recency (R): Days since last purchase (lower = more recent = better)
- Frequency (F): Number of unique orders (higher = more loyal = better)
- Monetary (M): Total revenue (higher = more valuable = better)

WHY RFM OVER CLUSTERING?
RFM provides interpretable, actionable segments based on business logic rather than
statistical algorithms. Non-technical stakeholders understand "high R, F, M = VIP"
immediately, making RFM superior for interviews and business communication.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D


def load_transactions(path: Path) -> pd.DataFrame:
    """
    Load and validate transactional data from parquet file.
    
    PURPOSE:
    Read raw transaction data, validate schema, clean invalid records,
    and compute revenue for RFM analysis.
    
    INTERVIEW Q&A:
    Q: Why drop rows with missing CustomerID?
    A: RFM is customer-centric. Guest purchases (no CustomerID) can't be
       attributed to a customer for retention/segmentation analysis.
       They're valuable for sales analysis but not RFM.
    
    Q: Why compute Revenue here instead of later?
    A: Single Responsibility Principle. This function handles all data loading
       and basic transformations. Revenue is a fundamental metric needed downstream.
    
    RATIONALE:
    - Assertions validate critical assumptions (schema exists)
    - Explicit type conversions handle messy real-world data
    - Logging dropped rows maintains audit trail
    """
    df = pd.read_parquet(path)
    
    required_cols = ["InvoiceNo", "InvoiceDate", "CustomerID", "Quantity", "UnitPrice"]
    assert all(col in df.columns for col in required_cols), \
        f"Missing required columns. Expected: {required_cols}, Got: {df.columns.tolist()}"
    
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    
    initial_rows = len(df)
    df = df.dropna(subset=["CustomerID"])
    dropped_rows = initial_rows - len(df)
    print(f"Dropped {dropped_rows} guest purchases (missing CustomerID) from {initial_rows} total")
    
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    return df


def compute_rfm(df: pd.DataFrame, snapshot_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
    """
    Compute RFM metrics for each customer from transaction data.
    
    PURPOSE:
    Aggregate raw transactions into customer-level RFM metrics:
    - Recency: Days since last purchase
    - Frequency: Number of unique orders
    - Monetary: Total revenue generated
    
    INTERVIEW Q&A:
    Q: Why use snapshot_date parameter?
    A: Makes analysis reproducible. Without it, "recency" changes daily,
       making comparisons impossible. Fixed snapshot date = consistent results.
    
    Q: Why count unique InvoiceNo instead of total rows?
    A: A single order (InvoiceNo) can have multiple line items (rows).
       We want order frequency, not line-item frequency.
    
    Q: Why assert non-negative values?
    A: Data quality check. Negative Recency means future purchase (impossible).
       Zero Frequency/Monetary means customer exists but never bought (logic error).
    
    RATIONALE:
    Default snapshot_date = max date + 1 day simulates "day after last transaction"
    which is common in batch RFM jobs run nightly on previous day's data.
    """
    if snapshot_date is None:
        snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    
    print(f"Snapshot date for RFM: {snapshot_date.date()}")
    
    rfm = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
        "InvoiceNo": "nunique",
        "Revenue": "sum",
    }).reset_index()
    
    rfm.columns = ["CustomerID", "Recency", "Frequency", "Monetary"]
    
    assert (rfm["Recency"] >= 0).all(), "Found negative Recency"
    assert (rfm["Frequency"] > 0).all(), "Found Frequency <= 0"
    assert (rfm["Monetary"] > 0).all(), "Found Monetary <= 0"
    
    return rfm.sort_values("Recency")


def score_rfm(rfm: pd.DataFrame, bins: int = 5) -> pd.DataFrame:
    """
    Assign scores (1-5) to R, F, M based on quantiles.
    
    PURPOSE:
    Convert continuous RFM metrics into discrete scores (1-5) for easier segmentation.
    Uses quantile-based binning to ensure balanced distribution across score ranges.
    
    INTERVIEW Q&A:
    Q: Why quantiles instead of fixed thresholds?
    A: Quantiles adapt to the actual distribution of data, ensuring each score bucket
       has roughly equal number of customers. Fixed thresholds fail when data is skewed.
    
    Q: Why invert Recency but not Frequency/Monetary?
    A: Lower recency (fewer days) is BETTER (more recent purchase), so we invert.
       Higher frequency and monetary are naturally BETTER, so no inversion needed.
    
    RATIONALE:
    - Handles edge cases where duplicate values prevent clean quintile splits
    - Returns integer scores for cleaner business rules
    - Creates composite RFM_Score string for quick pattern recognition
    """
    rfm_scored = rfm.copy()
    
    # Recency: inverted (lower days = higher score = more recent = better)
    rfm_scored["R_Score"] = pd.qcut(
        rfm["Recency"],
        q=bins,
        labels=False,
        duplicates="drop",
    )
    # Invert: map to bins, 0, -1 (descending)
    rfm_scored["R_Score"] = bins - rfm_scored["R_Score"]
    rfm_scored["R_Score"] = rfm_scored["R_Score"].astype(int)
    
    # Frequency: normal (more orders = higher score)
    rfm_scored["F_Score"] = pd.qcut(
        rfm["Frequency"],
        q=bins,
        labels=False,
        duplicates="drop",
    )
    # Map 0-indexed to 1-indexed
    rfm_scored["F_Score"] = rfm_scored["F_Score"] + 1
    rfm_scored["F_Score"] = rfm_scored["F_Score"].astype(int)
    
    # Monetary: normal (more revenue = higher score)
    rfm_scored["M_Score"] = pd.qcut(
        rfm["Monetary"],
        q=bins,
        labels=False,
        duplicates="drop",
    )
    # Map 0-indexed to 1-indexed
    rfm_scored["M_Score"] = rfm_scored["M_Score"] + 1
    rfm_scored["M_Score"] = rfm_scored["M_Score"].astype(int)
    
    # Combined RFM score string for pattern recognition
    rfm_scored["RFM_Score"] = (
        rfm_scored["R_Score"].astype(str)
        + rfm_scored["F_Score"].astype(str)
        + rfm_scored["M_Score"].astype(str)
    )
    
    return rfm_scored


def assign_segments(rfm_scored: pd.DataFrame) -> pd.DataFrame:
    """
    Assign business-friendly segment labels based on RFM scores.
    
    PURPOSE:
    Translate RFM scores into actionable customer segments for marketing campaigns.
    Each segment has specific characteristics and recommended business actions.
    
    INTERVIEW Q&A:
    Q: Why use rule-based segments instead of clustering (K-means, etc.)?
    A: Rule-based segments are:
       1. Interpretable - stakeholders understand "R>=4, F>=4, M>=4 = VIP"
       2. Actionable - each segment maps to specific marketing tactics
       3. Reproducible - same rules always produce same segments
       4. Explainable - can justify why a customer is in a segment
       Clustering is black-box and hard to explain to non-technical stakeholders.
    
    SEGMENT DEFINITIONS & BUSINESS ACTIONS:
    - VIP/Champions (R≥4, F≥4, M≥4): Best customers. VIP programs, exclusive access.
    - Loyal (F≥4, M≥3, R≥2): High value, regular buyers. Loyalty rewards, early access.
    - Growth Potential (R≥4, F≤2, M≤2): Recent but low spend. Cross-sell, upsell offers.
    - At Risk (R≤2, F≥3, M≥2): Used to buy, now fading. Win-back campaigns.
    - Dormant (R≤1): Haven't purchased recently. Re-engagement or cleanup.
    - Mainstream: Everyone else. Regular engagement.
    
    RATIONALE:
    Priority order matters: check VIP first (strictest), Dormant last (loosest).
    This ensures high-value segments aren't accidentally lumped into "Mainstream".
    """
    rfm = rfm_scored.copy()
    
    def assign_segment(row):
        R, F, M = row["R_Score"], row["F_Score"], row["M_Score"]
        
        # VIP/Champions: Best customers across all dimensions
        if R >= 4 and F >= 4 and M >= 4:
            return "VIP"
        
        # Loyal: High frequency and monetary, decent recency
        if F >= 4 and M >= 3 and R >= 2:
            return "Loyal"
        
        # Growth Potential: Recent buyers with low spend (nurture opportunity)
        if R >= 4 and F <= 2 and M <= 2:
            return "Growth Potential"
        
        # At Risk: Used to be good customers, now declining
        if R <= 2 and F >= 3 and M >= 2:
            return "At Risk"
        
        # Dormant: Haven't purchased recently at all
        if R <= 1:
            return "Dormant"
        
        # Mainstream: Everyone else
        return "Mainstream"
    
    rfm["Segment"] = rfm.apply(assign_segment, axis=1)
    return rfm


def save_segment_summary(rfm: pd.DataFrame, outpath: Path) -> None:
    """
    Generate and save markdown summary and CSV export of RFM segments.
    
    PURPOSE:
    Create stakeholder-ready reports showing segment distribution, revenue impact,
    and individual customer segment assignments for campaign execution.
    
    OUTPUTS:
    1. Markdown report with segment statistics and insights
    2. CSV file with all customers and their segment assignments
    
    INTERVIEW Q&A:
    Q: Why both markdown and CSV?
    A: Markdown for executive summary/presentations (human-readable),
       CSV for campaign execution (machine-readable, can import to CRM/email tools).
    """
    outpath.parent.mkdir(parents=True, exist_ok=True)
    
    # Aggregate statistics by segment
    summary = rfm.groupby("Segment").agg({
        "CustomerID": "count",
        "Recency": "mean",
        "Frequency": "mean", 
        "Monetary": ["mean", "sum"],
    }).reset_index()
    
    # Flatten column names
    summary.columns = ["Segment", "Customer_Count", "Avg_Recency", 
                       "Avg_Frequency", "Avg_Monetary", "Total_Revenue"]
    
    # Calculate percentages
    summary["% of Customers"] = (
        (summary["Customer_Count"] / summary["Customer_Count"].sum()) * 100
    ).round(2)
    summary["% of Revenue"] = (
        (summary["Total_Revenue"] / summary["Total_Revenue"].sum()) * 100
    ).round(2)
    
    # Sort by revenue (highest first)
    summary = summary.sort_values("Total_Revenue", ascending=False)
    
    # Build markdown table
    md_table = "| Segment | Count | Avg R | Avg F | Avg M | Total Revenue | % Customers | % Revenue |\n"
    md_table += "|---------|-------|-------|-------|-------|---------------|-------------|------------|\n"
    for _, row in summary.iterrows():
        md_table += (
            f"| {row['Segment']:18s} | {int(row['Customer_Count']):5d} | "
            f"{row['Avg_Recency']:5.1f} | {row['Avg_Frequency']:5.1f} | "
            f"${row['Avg_Monetary']:7,.0f} | ${row['Total_Revenue']:10,.0f} | "
            f"{row['% of Customers']:5.1f}% | {row['% of Revenue']:5.1f}% |\n"
        )
    
    # Build report
    report = [
        "# RFM Segmentation Summary",
        "",
        "## Segment Distribution",
        md_table,
        "",
        "## Business Actions by Segment",
        "- **VIP/Champions:** Focus retention with VIP programs and exclusive access",
        "- **Loyal:** Reward loyalty with early access to new products and special offers",
        "- **Growth Potential:** Nurture with cross-sell and upsell campaigns",
        "- **At Risk:** Win-back campaigns to reactivate before they churn",
        "- **Dormant:** Re-engagement campaigns or remove from active marketing",
        "- **Mainstream:** Regular engagement with standard promotions",
        "",
        "## Key Metrics",
        f"- Total Customers: {len(rfm):,}",
        f"- Total Revenue: ${rfm['Monetary'].sum():,.2f}",
        f"- VIP Customers: {len(rfm[rfm['Segment'] == 'VIP']):,} "
        f"({len(rfm[rfm['Segment'] == 'VIP']) / len(rfm) * 100:.1f}%)",
    ]
    
    # Save markdown report
    outpath.write_text("\n".join(report), encoding="utf-8")
    print(f"✓ Segment summary saved to {outpath}")
    
    # Save CSV export with customer segments for campaign execution
    csv_path = outpath.parent / "rfm_segments.csv"
    rfm[["CustomerID", "Recency", "Frequency", "Monetary", 
         "R_Score", "F_Score", "M_Score", "RFM_Score", "Segment"]].to_csv(
        csv_path, index=False
    )
    print(f"✓ Customer segments CSV saved to {csv_path}")


def plot_rfm_scatter(rfm: pd.DataFrame, output_dir: Path) -> None:
    """
    Create 3D scatter plot of R vs F vs M, colored by segment.
    
    PURPOSE:
    Visualize how RFM scores separate into distinct customer segments in 3D space.
    Helps validate that segments occupy different regions of the RFM space.
    
    INTERVIEW Q&A:
    Q: Why 3D scatter instead of 2D?
    A: RFM has 3 dimensions (R, F, M). 3D plot shows the full relationship.
       2D projections (R vs F, R vs M, etc.) would lose information.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define colors for each segment
    segment_colors = {
        "VIP": "#1f77b4",  # Blue
        "Loyal": "#2ca02c",  # Green
        "Growth Potential": "#ff7f0e",  # Orange
        "At Risk": "#d62728",  # Red
        "Dormant": "#9467bd",  # Purple
        "Mainstream": "#8c564b",  # Brown
    }
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot each segment with different color
    for segment in rfm["Segment"].unique():
        segment_data = rfm[rfm["Segment"] == segment]
        ax.scatter(
            segment_data["Recency"],
            segment_data["Frequency"],
            segment_data["Monetary"],
            c=segment_colors.get(segment, "gray"),
            label=segment,
            alpha=0.6,
            s=20,
        )
    
    ax.set_xlabel("Recency (days)", fontsize=10)
    ax.set_ylabel("Frequency (orders)", fontsize=10)
    ax.set_zlabel("Monetary ($)", fontsize=10)
    ax.set_title("RFM 3D Scatter Plot by Segment", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    
    plt.tight_layout()
    output_path = output_dir / "rfm_scatter_3d.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ 3D scatter plot saved to {output_path}")


def plot_segment_distribution(rfm: pd.DataFrame, output_dir: Path) -> None:
    """
    Create bar chart showing customer count by segment.
    
    PURPOSE:
    Quickly see segment sizes to identify which groups need attention.
    VIP and At Risk segments may be small but critical for business.
    
    INTERVIEW Q&A:
    Q: Why is this useful if we have the markdown report?
    A: Visuals are faster to digest than tables. Executives prefer charts.
       Also useful for presentations and dashboards.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    segment_counts = rfm["Segment"].value_counts().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(segment_counts.index, segment_counts.values, 
                   color=["#1f77b4", "#2ca02c", "#8c564b", "#ff7f0e", "#d62728", "#9467bd"][:len(segment_counts)])
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel("Segment", fontsize=12, fontweight="bold")
    ax.set_ylabel("Number of Customers", fontsize=12, fontweight="bold")
    ax.set_title("Customer Distribution by Segment", fontsize=14, fontweight="bold")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    
    output_path = output_dir / "segment_distribution.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ Segment distribution chart saved to {output_path}")


def plot_segment_revenue(rfm: pd.DataFrame, output_dir: Path) -> None:
    """
    Create bar chart showing total revenue by segment.
    
    PURPOSE:
    Identify which segments drive the most revenue. VIP may be small in count
    but could generate disproportionate revenue, justifying special treatment.
    
    INTERVIEW Q&A:
    Q: Why separate charts for count vs revenue?
    A: They tell different stories. A segment could be small (count) but high-value
       (revenue), or vice versa. Both metrics guide different business decisions.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    segment_revenue = rfm.groupby("Segment")["Monetary"].sum().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(segment_revenue.index, segment_revenue.values,
                   color=["#1f77b4", "#2ca02c", "#8c564b", "#ff7f0e", "#d62728", "#9467bd"][:len(segment_revenue)])
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height/1000:.0f}K',
                ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel("Segment", fontsize=12, fontweight="bold")
    ax.set_ylabel("Total Revenue ($)", fontsize=12, fontweight="bold")
    ax.set_title("Revenue by Segment", fontsize=14, fontweight="bold")
    ax.tick_params(axis='x', rotation=45)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    
    plt.tight_layout()
    output_path = output_dir / "segment_revenue.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ Segment revenue chart saved to {output_path}")


def plot_rfm_heatmap(rfm: pd.DataFrame, output_dir: Path) -> None:
    """
    Create heatmap showing segment composition by R and F scores.
    
    PURPOSE:
    Visualize how R and F scores combine to create segments. Helps identify
    patterns like "high R + high F = VIP" and validates segment logic.
    
    INTERVIEW Q&A:
    Q: Why R vs F instead of including M?
    A: 3D heatmaps are hard to visualize. R and F are often the most discriminative
       dimensions for segmentation (recency + loyalty). M adds nuance but R/F
       tells most of the story.
    
    RATIONALE:
    Uses count (not revenue) to show customer distribution patterns.
    Alternative: could create separate heatmap for average revenue per cell.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create pivot table: R_Score vs F_Score with count
    pivot = rfm.pivot_table(
        values="CustomerID",
        index="R_Score",
        columns="F_Score",
        aggfunc="count",
        fill_value=0
    )
    # Convert to numeric type for seaborn heatmap compatibility
    pivot = pivot.astype(float)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", 
                cbar_kws={'label': 'Customer Count'}, ax=ax)
    
    ax.set_xlabel("Frequency Score (1=Low, 5=High)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Recency Score (1=Long ago, 5=Recent)", fontsize=12, fontweight="bold")
    ax.set_title("RFM Heatmap: Customer Count by R and F Scores", fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    output_path = output_dir / "segment_heatmap.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ RFM heatmap saved to {output_path}")


def run(input_path: Path, output_path: Path) -> None:
    """Execute full RFM pipeline end-to-end."""
    print("\n" + "=" * 60)
    print("RFM SEGMENTATION PIPELINE")
    print("=" * 60 + "\n")
    
    df = load_transactions(input_path)
    print(f"✓ Loaded {len(df):,} transactions for {df['CustomerID'].nunique():,} customers\n")
    
    rfm = compute_rfm(df)
    print(f"✓ Computed RFM for {len(rfm):,} customers\n")
    
    rfm_scored = score_rfm(rfm)
    print("✓ Scored RFM metrics (1-5 scale)\n")
    
    rfm_segmented = assign_segments(rfm_scored)
    print("✓ Assigned customer segments\n")
    
    print("Segment Breakdown:")
    print("-" * 40)
    segment_counts = rfm_segmented["Segment"].value_counts().sort_index()
    for segment, count in segment_counts.items():
        pct = (count / len(rfm_segmented)) * 100
        print(f"  {segment:20s}: {count:5d} ({pct:5.1f}%)")
    print()
    
    # Save main RFM output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rfm_segmented.to_parquet(output_path, index=False)
    print(f"✓ RFM table saved to {output_path}\n")
    
    # Generate reports
    summary_path = Path("reports") / "rfm_report.md"
    save_segment_summary(rfm_segmented, summary_path)
    print()
    
    # Generate visualizations
    print("Generating visualizations...")
    figures_dir = Path("reports") / "figures"
    plot_rfm_scatter(rfm_segmented, figures_dir)
    plot_segment_distribution(rfm_segmented, figures_dir)
    plot_segment_revenue(rfm_segmented, figures_dir)
    plot_rfm_heatmap(rfm_segmented, figures_dir)
    print()
    
    print("=" * 60)
    print("RFM PIPELINE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RFM Customer Segmentation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default output
  python src/rfm.py --data data/processed/retail_clean.parquet
  
  # Custom output path and snapshot date
  python src/rfm.py --data data/processed/retail_raw.parquet \\
                     --snapshot 2011-12-09 \\
                     --output reports/rfm_segmentation.parquet
        """
    )
    parser.add_argument(
        "--data", 
        type=Path, 
        required=True, 
        help="Path to transaction data (parquet format)"
    )
    parser.add_argument(
        "--snapshot",
        type=str,
        help="Snapshot date for RFM calculation (YYYY-MM-DD). Defaults to day after last transaction."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/rfm_segmentation.parquet"),
        help="Output path for RFM segmentation table (default: reports/rfm_segmentation.parquet)"
    )
    
    args = parser.parse_args()
    run(args.data, args.output)