"""KPI analysis utilities and report generation for the Online Retail dataset.

PURPOSE:
Generate business-ready KPI reports from cleaned transaction data.
Each KPI is designed to answer a specific business question:
- Revenue: How much did we sell?
- Orders: How many transactions?
- Customers: How many unique buyers?
- AOV (Average Order Value): What's typical order size? (Useful for marketing/inventory planning)
- Monthly Revenue: Are there seasonal patterns? (Useful for inventory allocation)

INTERVIEW RATIONALE:
"I chose these KPIs because they answer the questions a Head of E-Commerce would ask.
They're simple (not ML), auditable (not black-box), and actionable (directly inform decisions)." 
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

def load_data(path: Path) -> pd.DataFrame:
    """
    Load cleaned parquet and compute revenue (Quantity × UnitPrice).
    
    Why compute Revenue here?
    - Revenue is a derived metric (not in raw data).
    - It's used in almost every KPI aggregation.
    - Computing it once (here) vs. many times (in functions) improves efficiency.
    """
    df = pd.read_parquet(path)
    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    return df

def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Compute core business KPIs.
    
    Interview question: "Why these KPIs and not others?"
    
    Answer: "These five metrics answer the core business questions:
    - Total Revenue: How much business did we do?
    - Orders: Volume of transactions.
    - Customers: Size of customer base.
    - Average Order Value: Typical transaction size (informs marketing efficiency).
    - Monthly Revenue: Seasonality patterns (informs inventory planning).
    
    These are simple, auditable, and actionable. Advanced metrics (like cohort retention
    or product affinity) can be built on top once we validate these basics."
    """
    orders = df["InvoiceNo"].nunique()
    customers = df["CustomerID"].dropna().nunique()
    total_revenue = df["Revenue"].sum()
    total_quantity = df["Quantity"].sum()
    avg_order_value = total_revenue / orders if orders else 0.0
    avg_items_per_order = total_quantity / orders if orders else 0.0
    avg_unique_items = (
        df.groupby("InvoiceNo")["StockCode"].nunique().mean()
        if orders
        else 0.0
    )
    date_min = df["InvoiceDate"].min()
    date_max = df["InvoiceDate"].max()

    return {
        "date_min": date_min,
        "date_max": date_max,
        "orders": orders,
        "customers": customers,
        "total_revenue": total_revenue,
        "total_quantity": total_quantity,
        "avg_order_value": avg_order_value,
        "avg_items_per_order": avg_items_per_order,
        "avg_unique_items": avg_unique_items,
    }

def build_tables(df: pd.DataFrame) -> dict:
    """
    Build aggregated tables for top products, countries, customers, and monthly trends.
    
    Why these aggregations?
    - Top products: Which SKUs drive revenue? (Inventory focus)
    - Top countries: Geographic concentration risk? (Market risk)
    - Top customers: Revenue dependency on few customers? (Account risk)
    - Monthly trends: Seasonality for inventory/staffing planning.
    
    Each directly informs business decisions.
    """
    # Top products: Used for inventory allocation and bundling strategy.
    top_products = (
        df.groupby(["StockCode", "Description"], dropna=False)["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    
    # Top countries: Used to identify geographic concentration risk and expansion opportunities.
    top_countries = (
        df.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10)
    ).reset_index()
    
    # Top customers: Used for account management prioritization.
    # Note: Excludes NaN CustomerID (guest purchases) because we can't manage accounts without IDs.
    top_customers = (
        df.dropna(subset=["CustomerID"])
        .groupby("CustomerID")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    
    # Monthly revenue: Used for seasonality analysis → inventory planning and staffing.
    monthly_revenue = (
        df.set_index("InvoiceDate")["Revenue"]
        .resample("ME")  # Month-end frequency
        .sum()
        .reset_index()
    )

    return {
        "top_products": top_products,
        "top_countries": top_countries,
        "top_customers": top_customers,
        "monthly_revenue": monthly_revenue,
    }

def _save_plot(fig, path: Path) -> None:
    """Save matplotlib figure to disk and close."""
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

def save_figures(tables: dict, outdir: Path) -> dict:
    """
    Generate and save publication-ready charts.
    
    Why simple charts (not dashboards)?
    - Stakeholders can review quickly.
    - Easy to email or include in presentations.
    - No software dependency (just PNG files).
    """
    outdir.mkdir(parents=True, exist_ok=True)

    figures = {}

    # Chart 1: Monthly Revenue Trend
    # Purpose: Visualize seasonality. Helps plan inventory buildup for peak months.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(
        tables["monthly_revenue"]["InvoiceDate"],
        tables["monthly_revenue"]["Revenue"],
        marker="o",
        linewidth=2,
    )
    ax.set_title("Monthly Revenue")
    ax.set_ylabel("Revenue")
    ax.set_xlabel("Month")
    ax.grid(True, alpha=0.3)
    figures["monthly_revenue"] = outdir / "monthly_revenue.png"
    _save_plot(fig, figures["monthly_revenue"])

    # Chart 2: Top 10 Countries
    # Purpose: Show geographic concentration. Identifies dependency risk and expansion opportunities.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    top_countries = tables["top_countries"].sort_values("Revenue")
    ax.barh(top_countries["Country"], top_countries["Revenue"])
    ax.set_title("Top 10 Countries by Revenue")
    ax.set_xlabel("Revenue")
    figures["top_countries"] = outdir / "top_countries.png"
    _save_plot(fig, figures["top_countries"])

    # Chart 3: Top 10 Products
    # Purpose: Identify high-revenue SKUs for inventory prioritization.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    top_products = tables["top_products"].sort_values("Revenue")
    labels = top_products["Description"].fillna("Unknown").astype(str)
    ax.barh(labels, top_products["Revenue"])
    ax.set_title("Top 10 Products by Revenue")
    ax.set_xlabel("Revenue")
    figures["top_products"] = outdir / "top_products.png"
    _save_plot(fig, figures["top_products"])

    # Chart 4: Top 10 Customers
    # Purpose: Show customer concentration. Identifies dependency risk and account management priorities.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    top_customers = tables["top_customers"].sort_values("Revenue")
    ax.barh(top_customers["CustomerID"].astype(str), top_customers["Revenue"])
    ax.set_title("Top 10 Customers by Revenue")
    ax.set_xlabel("Revenue")
    figures["top_customers"] = outdir / "top_customers.png"
    _save_plot(fig, figures["top_customers"])

    return figures

def _to_markdown_table(df: pd.DataFrame) -> str:
    """Convert pandas DataFrame to markdown table."""
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        values = [str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)

def write_report(kpis: dict, tables: dict, figures: dict, outpath: Path) -> None:
    """
    Write markdown report with KPIs, charts, and tables.
    
    Structure:
    1. Executive Summary (key KPIs)
    2. Charts (trends and distributions)
    3. Tables (detailed rankings)
    4. Interpretation (what does this mean for business?)
    
    Interview rationale: "I structured this for a busy stakeholder.
    Exec summary first (they might not read further), then supporting charts and tables."
    """
    outpath.parent.mkdir(parents=True, exist_ok=True)
    date_range = f"{kpis['date_min'].date()} to {kpis['date_max'].date()}"
    rel_figures = {key: Path("figures") / value.name for key, value in figures.items()}

    report = [
        "# KPI Summary Report - Online Retail Dataset",
        "",
        "## Overview",
        f"Analysis window: **{date_range}**",
        "",
        "## Core KPIs (Executive Summary)",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total Revenue | {kpis['total_revenue']:,.2f} |",
        f"| Orders | {kpis['orders']:,} |",
        f"| Customers | {kpis['customers']:,} |",
        f"| Average Order Value | {kpis['avg_order_value']:,.2f} |",
        f"| Items per Order | {kpis['avg_items_per_order']:,.2f} |",
        f"| Unique Items per Order | {kpis['avg_unique_items']:,.2f} |",
        "",
        "## Revenue by Month (Seasonality)",
        f"![Monthly Revenue]({rel_figures['monthly_revenue'].as_posix()})",
        "",
        "## Top Countries by Revenue (Geographic Concentration)",
        f"![Top Countries]({rel_figures['top_countries'].as_posix()})",
        "",
        "## Top Products by Revenue (SKU Focus)",
        f"![Top Products]({rel_figures['top_products'].as_posix()})",
        "",
        "## Top Customers by Revenue (Customer Concentration)",
        f"![Top Customers]({rel_figures['top_customers'].as_posix()})",
        "",
        "## Detailed Tables",
        "### Top 10 Products by Revenue",
        _to_markdown_table(tables["top_products"]),
        "",
        "### Top 10 Countries by Revenue",
        _to_markdown_table(tables["top_countries"]),
        "",
        "### Top 10 Customers by Revenue",
        _to_markdown_table(tables["top_customers"]),
        "",
        "## Interpretation & Business Implications",
        "",
        "### Finding 1: Revenue Concentration",
        "- Revenue is concentrated in a small number of countries and customers.",
        "- **Implication:** Dependency risk. If top customer leaves or UK market softens, revenue drops significantly.",
        "- **Action:** Diversify across geographies and customers. Build retention programs for top accounts.",
        "",
        "### Finding 2: Seasonality",
        "- Monthly revenue shows clear end-of-year spikes (visible in chart above).",
        "- **Implication:** Inventory must be built up in Q3 to support Q4 peak demand.",
        "- **Action:** Align procurement, warehousing, and staffing with peak months.",
        "",
        "### Finding 3: SKU Concentration",
        "- A small set of products drives most revenue.",
        "- **Implication:** Operational focus needed on stock-outs for top SKUs. Long-tail products may not justify shelf space.",
        "- **Action:** Ensure top products are always in stock. Use them as anchors for cross-sell bundles.",
    ]

    outpath.write_text("\n".join(report), encoding="utf-8")

def run(input_path: Path, outdir: Path) -> None:
    """Execute full KPI analysis pipeline."""
    df = load_data(input_path)
    kpis = compute_kpis(df)
    tables = build_tables(df)
    figures = save_figures(tables, outdir / "figures")
    write_report(kpis, tables, figures, outdir / "kpi_summary.md")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate KPI report from cleaned retail data.")
    parser.add_argument("--input", type=Path, required=True, help="Path to retail_clean.parquet")
    parser.add_argument("--outdir", type=Path, default=Path("reports"), help="Output directory")
    args = parser.parse_args()
    run(args.input, args.outdir)