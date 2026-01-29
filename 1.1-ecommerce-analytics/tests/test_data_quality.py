"""Basic data quality checks for the cleaned retail dataset."""

from pathlib import Path

import pandas as pd
import pytest

DATA_PATH = Path("data/processed/retail_clean.parquet")


def test_clean_data_exists():
    if not DATA_PATH.exists():
        pytest.skip("Cleaned dataset not found. Run the pipeline to generate it.")
    assert DATA_PATH.exists(), "Expected cleaned dataset to exist."


def test_clean_data_schema():
    if not DATA_PATH.exists():
        pytest.skip("Cleaned dataset not found. Run the pipeline to generate it.")
    df = pd.read_parquet(DATA_PATH)
    expected = {
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country",
    }
    assert expected.issubset(df.columns)


def test_no_nonpositive_values():
    if not DATA_PATH.exists():
        pytest.skip("Cleaned dataset not found. Run the pipeline to generate it.")
    df = pd.read_parquet(DATA_PATH)
    assert (df["Quantity"] > 0).all()
    assert (df["UnitPrice"] > 0).all()


def test_invoice_dates_present():
    if not DATA_PATH.exists():
        pytest.skip("Cleaned dataset not found. Run the pipeline to generate it.")
    df = pd.read_parquet(DATA_PATH)
    assert df["InvoiceDate"].notna().all()
