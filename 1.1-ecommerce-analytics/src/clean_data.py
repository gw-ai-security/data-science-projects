"""Clean the raw retail dataset into an analysis-ready parquet file."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from convert_to_parquet import convert_excel_to_parquet, project_root


def clean_data(input_path: Path, output_path: Path) -> Path:
    df = pd.read_parquet(input_path)

    # Normalize schema
    if "Description" in df.columns:
        df["Description"] = df["Description"].fillna("Unknown").map(str)
    if "InvoiceNo" in df.columns:
        df["InvoiceNo"] = df["InvoiceNo"].map(str)
    if "StockCode" in df.columns:
        df["StockCode"] = df["StockCode"].map(str)
    if "CustomerID" in df.columns:
        df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce").astype("Int64")
    if "Country" in df.columns:
        df["Country"] = df["Country"].map(str)
    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    # Data quality rules
    df = df.drop_duplicates()
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False, engine="pyarrow")
    return output_path


def resolve_input_path(root: Path) -> Path:
    parquet_path = root / "data" / "processed" / "retail_raw.parquet"
    if parquet_path.exists():
        return parquet_path
    # fallback: build from Excel if available
    return convert_excel_to_parquet()


def main() -> None:
    root = project_root()

    parser = argparse.ArgumentParser(description="Clean raw retail data.")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to retail_raw.parquet (optional).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data" / "processed" / "retail_clean.parquet",
        help="Path for cleaned parquet output.",
    )

    args = parser.parse_args()
    input_path = args.input if args.input else resolve_input_path(root)

    clean_data(input_path, args.output)
    print(f"Cleaned data written to: {args.output}")


if __name__ == "__main__":
    main()
