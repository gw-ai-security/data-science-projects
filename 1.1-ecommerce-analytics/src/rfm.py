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


def load_transactions(path: Path) -> pd.DataFrame:
    """Load and validate transactional data."""
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
    """Compute RFM metrics for each customer."""
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
    """Assign scores (1-5) to R, F, M based on quantiles."""
    rfm_scored = rfm.copy()
    
    # Recency: inverted (lower days = higher score)
    rfm_scored["R_Score"] = pd.qcut(
        rfm["Recency"],
        q=bins,
        labels=range(bins, 0, -1),
        duplicates="drop",
    ).astype(int)
    
    # Frequency: normal (more orders = higher score)
    rfm_scored["F_Score"] = pd.qcut(
        rfm["Frequency"],
        q=bins,
        labels=range(1, bins + 1),
        duplicates="drop",
    ).astype(int)
    
    # Monetary: normal (more revenue = higher score)
    rfm_scored["M_Score"] = pd.qcut(
        rfm["Monetary"],
        q=bins,
        labels=range(1, bins + 1),
        duplicates="drop",
    ).astype(int)
    
    # Combined RFM score
    rfm_scored["RFM_Score"] = (
        rfm_scored["R_Score"].astype(str)
        + rfm_scored["F_Score"].astype(str)
        + rfm_scored["M_Score"].astype(str)
    )
    
    return rfm_scored


def assign_segments(rfm_scored: pd.DataFrame) -> pd.DataFrame:
    """Assign business-friendly segment labels based on RFM scores."""
    rfm = rfm_scored.copy()
    
    def assign_segment(row):
        R, F, M = row["R_Score"], row["F_Score"], row["M_Score"]
        
        if R == 5 and F == 5 and M == 5:
            return "VIP"
        if F == 5 and M >= 4:
            return "Loyal"
        if R == 1 and 2 <= F <= 3:
            return "At Risk"
        if R == 1 and F <= 2 and M <= 2:
            return "Dormant"
        if R == 5 and 2 <= F <= 3 and M <= 3:
            return "Growth Potential"
        return "Mainstream"
    
    rfm["Segment"] = rfm.apply(assign_segment, axis=1)
    return rfm


def save_segment_summary(rfm: pd.DataFrame, outpath: Path) -> None:
    """Generate and save markdown summary of RFM segments."""
    outpath.parent.mkdir(parents=True, exist_ok=True)
    
    summary = rfm.groupby("Segment").agg({
        "CustomerID": "count",
        "Monetary": "sum",
    }).reset_index()
    
    summary.columns = ["Segment", "Customer_Count", "Total_Revenue"]
    summary["% of Customers"] = (
        (summary["Customer_Count"] / summary["Customer_Count"].sum()) * 100
    ).round(2)
    summary["% of Revenue"] = (
        (summary["Total_Revenue"] / summary["Total_Revenue"].sum()) * 100
    ).round(2)
    summary = summary.sort_values("Total_Revenue", ascending=False)
    
    md_table = "| Segment | Customer Count | Total Revenue | % of Customers | % of Revenue |\n"
    md_table += "|---------|----------------|---------------|----------------|---------------|\n"
    for _, row in summary.iterrows():
        md_table += (
            f"| {row['Segment']} | {int(row['Customer_Count'])} | "
            f"${row['Total_Revenue']:,.2f} | {row['% of Customers']:.1f}% | "
            f"{row['% of Revenue']:.1f}% |\n"
        )
    
    report = [
        "# RFM Segmentation Summary",
        "",
        "## Segment Distribution",
        md_table,
        "",
        "## Key Insights",
        "- **VIP & Loyal:** Focus retention efforts on high-value customers",
        "- **At Risk & Dormant:** Win-back campaigns to reactivate",
        "- **Growth Potential:** Nurture with targeted cross-sell and upsell",
    ]
    
    outpath.write_text("\n".join(report), encoding="utf-8")
    print(f"Segment summary saved to {outpath}")


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
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rfm_segmented.to_parquet(output_path, index=False)
    print(f"✓ RFM table saved to {output_path}\n")
    
    summary_path = Path("reports") / "rfm_segment_summary.md"
    save_segment_summary(rfm_segmented, summary_path)
    
    print("=" * 60)
    print("RFM PIPELINE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute RFM segmentation from transaction data.")
    parser.add_argument("--input", type=Path, required=True, help="Path to cleaned transaction parquet")
    parser.add_argument("--output", type=Path, default=Path("data/processed/rfm_customers.parquet"), help="Output path for RFM table")
    args = parser.parse_args()
    run(args.input, args.output)