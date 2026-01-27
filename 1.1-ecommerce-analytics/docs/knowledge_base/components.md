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
