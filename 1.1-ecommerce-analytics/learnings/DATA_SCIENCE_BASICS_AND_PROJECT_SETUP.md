# Data Science Learning Journey
## Teil 1: Projekt-Setup & Data Ingestion

Dieses Dokument erklärt die **Vorgehensweise**, **Methodik** und die **technischen Hintergründe** dieses Projekts. Es richtet sich an Einsteiger, die verstehen wollen, warum professionelle Data-Science-Projekte so strukturiert sind, wie sie sind.

---

## 1. Warum diese Projektstruktur?

Ein typischer Anfängerfehler ist es, alles in einem einzigen Ordner oder Notebook zu haben. Wir trennen bewusst:

```text
├── data/
│   ├── raw/                 # Unberührte Originaldaten (Read-Only!)
│   └── processed/           # Optimierte Daten für die Analyse
├── notebooks/               # Ort für Experimente und Visualisierungen
├── src/                     # Python-Skripte für wiederholbare Aufgaben
```

### Die "Golden Rules":
1. **Raw Data is Sacred**: Wir überschreiben niemals die Rohdaten (`data/raw`). Wenn wir einen Fehler beim Bereinigen machen, können wir immer neu anfangen.
2. **Notebooks sind keine Pipelines**: Notebooks sind toll zum *Anschauen* von daten, aber schlecht für *automatisierte Prozesse*. Deshalb liegen Download- und Konvertierungslogik in `src/` (Source Code).
3. **Reproduzierbarkeit**: Jeder (oder du in 6 Monaten) muss das Projekt mit `pip install -r requirements.txt` wieder zum Laufen bringen können.

---

## 2. Der Weg der Daten (ETL: Extract, Transform, Load)

Anstatt die Excel-Datei einfach im Notebook zu öffnen, haben wir eine Mini-Pipeline gebaut.

### Schritt 1: Extract (`src/download_data.py`)
**Was der Code macht:**
* Prüft, ob `data/raw/Online_Retail.xlsx` existiert.
* Wenn nein: Lädt sie automatisch von der UCI-Webseite herunter.

**Warum so kompliziert?**
* **Automatisierung**: Wenn du das Projekt auf einen neuen Laptop kopierst, musst du nicht manuell auf Webseiten herumsuchen. Ein Befehl genügt.

### Schritt 2: Transform (`src/convert_to_parquet.py`)
Das ist der wichtigste technische Schritt bisher. Wir konvertieren Excel (.xlsx) nach Parquet (.parquet).

**Warum Excel schlecht für Data Science ist:**
* **Langsam**: Excel zu laden dauert lange (in diesem Projekt ca. 40-60 Sekunden jedes Mal).
* **Datentypen-Chaos**: Eine Spalte in Excel kann Text und Zahlen gemischt enthalten. Pandas rät dann oft falsch.
* **Dateigröße**: Excel-Dateien sind oft unnötig groß.

**Warum Parquet besser ist:**
* **Columnar Storage**: Speichert Daten spaltenweise. Das macht Analysen extrem schnell.
* **Strict Types**: Eine Spalte ist entweder "Text" oder "Zahl", nicht beides.
* **Performance**: Das Laden der Parquet-Datei im Notebook dauert Millisekunden statt Minuten.

### Deep Dive: Der Code in `convert_to_parquet.py` erklärt
Hier passieren kritische Dinge, die Anfänger oft übersehen:

```python
# 1. Mischen von Typen verhindern
if "Description" in df.columns:
    df["Description"] = df["Description"].fillna("").map(str)
```
* **Problem**: In der Excel-Spalte "Description" stehen meist Texte, aber manchmal auch Zahlen (z.B. Artikelnummern, die wie Zahlen aussehen). Pandas ist verwirrt und macht daraus einen "Object"-Mix.
* **Lösung**: Wir zwingen alles zu Text (`map(str)`), damit spätere Analysen nicht abstürzen.

```python
# 2. Korrekte Behandlung von fehlenden IDs
if "CustomerID" in df.columns:
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce").astype("Int64")
```
* **Problem**: `NaN` (Not a Number = fehlender Wert) ist in Python technisch ein Float (Kommazahl). Eine ID wie `12345` wird dadurch zu `12345.0`. Das sieht hässlich aus und ist technisch falsch.
* **Lösung**: Wir nutzen den pandas-Typ `Int64` (mit großem I). Dieser kann **Ganzzahlen und fehlende Werte** gleichzeitig speichern. Eine ID bleibt `12345`, eine fehlende ID bleibt `<NA>`.

---

## 3. Die Notebook-Strategie (`notebooks/01_eda.ipynb`)

Wenn du das Notebook öffnest, siehst du diesen Code-Block gleich am Anfang:

```python
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
```

### Warum machen wir das?
Dies löst das ewige Problem: `FileNotFoundError`.
* Startest du das Skript aus dem Root-Ordner? Dann ist der Pfad `./data`.
* Startest du das Notebook aus dem `notebooks/` Ordner? Dann ist der Pfad `../data`.

Dieser Code macht den Pfad **dynamisch**. Egal von wo du startest, Python findet den Hauptordner.

### Markdown vor Code
Jede Analyse beginnt mit einer Erklärung.
* **Falsch**: Ein Notebook voller Code-Blöcke ohne Erklärung.
* **Richtig**: Überschrift -> Erklärung was wir tun -> Code -> Interpretation des Ergebnisses.

---

## Zusammenfassung
Bisher hast du nicht einfach "Code geschrieben", sondern eine **robuste Daten-Architektur** aufgebaut.
1. Deine Rohdaten sind sicher (`data/raw`).
2. Deine Analysedaten sind performant und typ-sicher (`data/processed/retail_raw.parquet`).
3. Dein Notebook muss sich nicht mehr mit Ladezeiten oder Datentyp-Fehlern herumschlagen, sondern kann sich rein auf die Analyse konzentrieren.

Das ist der Unterschied zwischen "ein bisschen Pandas ausprobieren" und "Data Engineering".
