from __future__ import annotations

import time
from pathlib import Path

import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def convert_excel_to_parquet(force: bool = False) -> Path:
    root = project_root()

    excel_path = root / "data" / "raw" / "Online_Retail.xlsx"
    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = out_dir / "retail_raw.parquet"

    if parquet_path.exists() and not force:
        print(f"Parquet already exists: {parquet_path}")
        return parquet_path

    if not excel_path.exists():
        raise FileNotFoundError(f"Missing input file: {excel_path}. Run src/download_data.py first.")

    print("Reading Excel (one-time slow step)...")
    t0 = time.time()

    df = pd.read_excel(excel_path)

    print(f"Excel loaded: {len(df):,} rows in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------
    # HARD FIX: Excel has mixed types (Description contains ints, etc.)
    # Force critical text columns to real Python strings
    # ------------------------------------------------------------------
    if "Description" in df.columns:
        df["Description"] = df["Description"].fillna("").map(str)

    if "InvoiceNo" in df.columns:
        df["InvoiceNo"] = df["InvoiceNo"].fillna("").map(str)

    if "StockCode" in df.columns:
        df["StockCode"] = df["StockCode"].fillna("").map(str)

    # CustomerID should be numeric nullable if present
    if "CustomerID" in df.columns:
        df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce").astype("Int64")

    # Country can stay as string/category; keep simple and robust:
    if "Country" in df.columns:
        df["Country"] = df["Country"].fillna("").map(str)

    print("Writing Parquet...")
    t1 = time.time()

    df.to_parquet(
        parquet_path,
        index=False,
        engine="pyarrow",
    )

    print(f"Parquet written in {time.time() - t1:.1f}s")
    print(f"Output: {parquet_path}")
    return parquet_path


if __name__ == "__main__":
    convert_excel_to_parquet()
