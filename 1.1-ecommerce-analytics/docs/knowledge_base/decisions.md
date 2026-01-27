# Decision Log (ADR)

## 2026-01-27: Data Quality & Cleaning Strategy

### Context
Der Rohdatensatz enthält negative Mengen (Retouren), Preise von 0 und fehlende CustomerIDs. Für eine Umsatzanalyse benötigen wir "saubere" Verkaufsdaten.

### Decision
1.  **Duplicate Removal**: Vollständige Duplikate werden entfernt.
2.  **Invalid Transactions**:
    -   `Quantity <= 0` wird entfernt (da keine Umsatzgenerierung im positiven Sinn).
    -   `UnitPrice <= 0` wird entfernt.
3.  **Missing CustomerID**:
    -   Werden **BEHALTEN**.
    -   Grund: Auch anonyme Transaktionen generieren Umsatz. Sie werden nur für Kohortenanalysen ausgeschlossen.
    -   Fehlende `Description` wurde mit "Unknown" aufgefüllt.

### Consequences
-   Der Datensatz `retail_clean.parquet` ist kleiner als raw (Zeilen-technisch), aber sauberer.
-   Analysen, die Retouren untersuchen wollen, müssen auf `retail_raw.parquet` zurückgreifen.
