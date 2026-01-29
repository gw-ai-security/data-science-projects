"""KPI analysis utilities and report generation for the Online Retail dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
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
    top_products = (
        df.groupby(["StockCode", "Description"], dropna=False)["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    top_countries = (
        df.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10)
    ).reset_index()
    top_customers = (
        df.dropna(subset=["CustomerID"])
        .groupby("CustomerID")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    monthly_revenue = (
        df.set_index("InvoiceDate")["Revenue"]
        .resample("ME")
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
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_figures(tables: dict, outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)

    figures = {}

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

    fig, ax = plt.subplots(figsize=(8, 4.5))
    top_countries = tables["top_countries"].sort_values("Revenue")
    ax.barh(top_countries["Country"], top_countries["Revenue"])
    ax.set_title("Top 10 Countries by Revenue")
    ax.set_xlabel("Revenue")
    figures["top_countries"] = outdir / "top_countries.png"
    _save_plot(fig, figures["top_countries"])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    top_products = tables["top_products"].sort_values("Revenue")
    labels = top_products["Description"].fillna("Unknown").astype(str)
    ax.barh(labels, top_products["Revenue"])
    ax.set_title("Top 10 Products by Revenue")
    ax.set_xlabel("Revenue")
    figures["top_products"] = outdir / "top_products.png"
    _save_plot(fig, figures["top_products"])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    top_customers = tables["top_customers"].sort_values("Revenue")
    ax.barh(top_customers["CustomerID"].astype(str), top_customers["Revenue"])
    ax.set_title("Top 10 Customers by Revenue")
    ax.set_xlabel("Revenue")
    figures["top_customers"] = outdir / "top_customers.png"
    _save_plot(fig, figures["top_customers"])

    return figures


def _to_markdown_table(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        values = [str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(kpis: dict, tables: dict, figures: dict, outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    date_range = f"{kpis['date_min'].date()} to {kpis['date_max'].date()}"
    rel_figures = {key: Path("figures") / value.name for key, value in figures.items()}

    report = [
        "# KPI Summary Report - Online Retail Dataset",
        "",
        "## Overview",
        f"Analysis window: **{date_range}**",
        "",
        "## Core KPIs",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total Revenue | {kpis['total_revenue']:,.2f} |",
        f"| Orders | {kpis['orders']:,} |",
        f"| Customers | {kpis['customers']:,} |",
        f"| Average Order Value | {kpis['avg_order_value']:,.2f} |",
        f"| Items per Order | {kpis['avg_items_per_order']:,.2f} |",
        f"| Unique Items per Order | {kpis['avg_unique_items']:,.2f} |",
        "",
        "## Revenue by Month",
        f"![Monthly Revenue]({rel_figures['monthly_revenue'].as_posix()})",
        "",
        "## Top Countries by Revenue",
        f"![Top Countries]({rel_figures['top_countries'].as_posix()})",
        "",
        "## Top Products by Revenue",
        f"![Top Products]({rel_figures['top_products'].as_posix()})",
        "",
        "## Top Customers by Revenue",
        f"![Top Customers]({rel_figures['top_customers'].as_posix()})",
        "",
        "## Tables",
        "### Top 10 Products by Revenue",
        _to_markdown_table(tables["top_products"]),
        "",
        "### Top 10 Countries by Revenue",
        _to_markdown_table(tables["top_countries"]),
        "",
        "### Top 10 Customers by Revenue",
        _to_markdown_table(tables["top_customers"]),
        "",
        "## Evaluation",
        "- Revenue is concentrated in a small number of countries and customers, indicating dependency risk.",
        "- Monthly revenue shows seasonality and potential end-of-year spikes; this suggests inventory planning impact.",
        "- High-performing SKUs can drive bundling strategies; long tail likely benefits from targeted promotions.",
    ]

    outpath.write_text("\n".join(report), encoding="utf-8")


def run(input_path: Path, outdir: Path) -> None:
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
