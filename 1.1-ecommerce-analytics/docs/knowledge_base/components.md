# Component Documentation

## Notebooks

### `02_data_quality.ipynb`
**Purpose**: Bereinigung des Rohdatensatzes.
**Input**: `data/processed/retail_raw.parquet`
**Output**: `data/processed/retail_clean.parquet`
**Logic**:
-   Imputiert fehlende Beschreibungen.
-   Filtert Duplikate.
-   Entfernt Stornos (Quantity < 0) und Preisfehler.

### `03_kpi_analysis.ipynb`
**Purpose**: KPI Berechnung und Business-Insights.
**Input**: `data/processed/retail_clean.parquet`
**Output**: Visuals und Tabellen im Notebook.

### `src/kpi_analysis.py`
**Purpose**: Reproduzierbarer KPI-Report als Script.
**Input**: `data/processed/retail_clean.parquet`
**Output**: `reports/kpi_summary.md`, `reports/figures/*.png`

### `src/clean_data.py`
**Purpose**: Reproduzierbare Datenbereinigung fuer den KPI-Report.
**Input**: `data/processed/retail_raw.parquet`
**Output**: `data/processed/retail_clean.parquet`

### `src/run_pipeline.py`
**Purpose**: End-to-end Pipeline (raw -> clean -> report -> optional notebook/html).
**Input**: `data/raw/Online_Retail.xlsx`
**Output**: `reports/kpi_summary.md`, `reports/figures/*.png`, `reports/03_kpi_analysis.html`
