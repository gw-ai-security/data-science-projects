# Project Execution Plan  
## E-Commerce Analytics – Online Retail Dataset

---

## 1. Projektkontext (Purpose & Scope)

Dieses Projekt ist ein **End-to-End Data Science / Analytics Projekt**  
auf Basis des öffentlich verfügbaren *Online Retail Datasets* (UCI).

Ziel ist **nicht** ein einzelnes Modell, sondern ein **realistischer Analytics-Workflow**:

- Dateningestion (Raw → Processed)
- Performante Datenhaltung (Parquet)
- Explorative Data Analysis (EDA)
- Ableitung betriebswirtschaftlicher Kennzahlen (KPIs)
- Vorbereitung für weiterführende Analysen (Customer Analytics, Zeitreihen, ML)

Das Projekt ist **portfoliofähig**, **reproduzierbar** und **agentenfähig**.

---

## 2. Projektziele (Was soll erreicht werden?)

### Fachlich
- Verständnis von Kaufverhalten im E-Commerce
- Identifikation von:
  - Umsatztreibern
  - Retouren
  - Kunden ohne CustomerID
  - Anomalien (negative Mengen, Preise = 0)
- Ableitung klarer KPIs:
  - Umsatz
  - Anzahl Transaktionen
  - Kundenanzahl
  - Warenkorbgrößen
  - Zeitliche Muster

### Technisch
- Klare Trennung von:
  - `raw` Daten
  - `processed` Daten
  - Analyse (Notebooks)
- Nutzung von **Parquet als einziges Analyseformat**
- Saubere Pfadlogik (projekt-root-basiert)
- Reproduzierbare Python-Umgebung (`venv`, `requirements.txt`)

---

## 3. Nicht-Ziele (Explizit!)

Folgendes ist **nicht erlaubt**:

- ❌ Direktes Arbeiten mit Excel in Notebooks
- ❌ Hartkodierte absolute Pfade
- ❌ Vermischung von EDA und Modelltraining
- ❌ „Magic Cleaning“ ohne Begründung
- ❌ Löschen von Daten ohne Dokumentation

---

## 4. Projektstruktur (verbindlich)

```text
1.1-ecommerce-analytics/
├── data/
│   ├── raw/                 # Originaldaten (Excel, unverändert)
│   └── processed/           # Parquet (Analyse-Standard)
├── notebooks/
│   ├── 01_eda.ipynb         # Explorative Data Analysis
│   ├── 02_data_quality.ipynb
│   ├── 03_kpi_analysis.ipynb
│   └── 04_time_analysis.ipynb
├── src/
│   ├── download_data.py     # Download der Rohdaten
│   └── convert_to_parquet.py
├── tests/                   # (optional) Validierungen
├── reports/                 # Grafiken, Exports
├── docs/
│   └── PROJECT_EXECUTION_PLAN.md
├── requirements.txt
└── README.md
```

---

## 5. Arbeitsregeln für Coding Agents (SEHR WICHTIG)

Jeder Agent muss folgende Regeln einhalten:

1. **Kontext zuerst lesen**

   * Dieses Dokument ist verpflichtend zu berücksichtigen

2. **Parquet First**

   * Analysen ausschließlich auf `data/processed/*.parquet`

3. **Notebook-Regel**

   * Jede Code-Zelle MUSS eine erklärende Markdown-Zelle davor haben

4. **Keine Annahmen**

   * Unklare Punkte → kommentieren, nicht raten

5. **Real-World-Logik**

   * Negative Mengen = mögliche Retouren
   * Fehlende CustomerID = Gastkäufe
   * Preise = 0 → Datenfehler oder Promotion

---

## 6. Aktueller Projektstatus

✔ Daten erfolgreich geladen und konvertiert
✔ Parquet-Datei vorhanden (`retail_raw.parquet`)
✔ Python-Umgebung stabil
✔ Notebook 01 gestartet

➡ Aktuelle Phase: **Explorative Data Analysis (EDA)**

---

## 7. Nächste geplante Schritte

1. Strukturprüfung (Shape, Dtypes)
2. Missing-Value-Analyse
3. Duplikate & Inkonsistenzen
4. Erste KPIs
5. Visualisierung zentraler Muster

---

## 8. Zielzustand (Outcome)

Am Ende existiert:

* Ein nachvollziehbares EDA-Notebook
* Dokumentierte Datenqualitätsentscheidungen
* Klare KPIs mit Business-Relevanz
* Basis für ML / Advanced Analytics
* Ein professionelles GitHub-Projekt

---

**Dieses Dokument ist die zentrale Referenz für alle Coding Agents.**
