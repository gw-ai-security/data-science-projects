"""End-to-end pipeline for data prep, KPI report, and optional notebook execution."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from convert_to_parquet import convert_excel_to_parquet, project_root
from clean_data import clean_data
from kpi_analysis import run as run_kpi_report


def run_notebook(path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--execute",
            "--ExecutePreprocessor.timeout=300",
            "--to",
            "notebook",
            "--inplace",
            str(path),
        ],
        check=True,
    )


def export_html(path: Path, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "html",
            "--output-dir",
            str(outdir),
            str(path),
        ],
        check=True,
    )


def main() -> None:
    root = project_root()

    parser = argparse.ArgumentParser(description="Run full project pipeline.")
    parser.add_argument("--skip-notebook", action="store_true", help="Skip notebook execution")
    parser.add_argument("--skip-html", action="store_true", help="Skip HTML export")
    args = parser.parse_args()

    raw_parquet = convert_excel_to_parquet()
    clean_path = root / "data" / "processed" / "retail_clean.parquet"
    clean_data(raw_parquet, clean_path)

    reports_dir = root / "reports"
    run_kpi_report(clean_path, reports_dir)

    notebook_path = root / "notebooks" / "03_kpi_analysis.ipynb"
    if not args.skip_notebook:
        run_notebook(notebook_path)
    if not args.skip_html:
        export_html(notebook_path, reports_dir)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
