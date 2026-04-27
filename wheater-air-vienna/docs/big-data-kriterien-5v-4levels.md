# Big-Data-Kriterien für `weather-air-vienna` (5 Vs + 4 Levels)

Stand: 2026-04-21

Dieses Dokument erfüllt das Bewertungskriterium **Big Data criteria** aus der Projektspezifikation:
- Beschreibung des Setups in Big-Data-Begriffen
- Einordnung nach den **5 Vs**
- Einordnung nach den **4 Levels of Data Handling**
- Konsistente Argumentation zur Übungslogik (End-to-End Data Pipeline)

## Projektkontext (kurz)

Das Projekt verarbeitet Wetter- und Luftqualitätsdaten für Wien.
Der Hauptpfad nutzt Open-Meteo (Wetter + Luftqualität), speichert Rohdaten in MongoDB, bereinigt und normalisiert diese in einer Staging-Schicht und aggregiert sie per Python-MapReduce auf Tagesebene.

Relevante Artefakte:
- Infrastruktur: `docker-compose.yml`
- Ingest: `notebooks/1_data_source_open_meteo.ipynb`
- Optionaler Fallback-Ingest: `notebooks/fallback/1_1_data_source_geo_eea.ipynb`
- Storage/Staging: `notebooks/2_data_storage_extraction_cleaning_staging.ipynb`
- Aggregation (Python-MapReduce): `notebooks/3_data_analysis_mapreduce.ipynb`
- Analyse/Output: `notebooks/4_data_output_storytelling.ipynb`
- Architektur: `docs/architektur-setup-infrastruktur.md`

## 1) Einordnung nach den 5 Vs

| V | Bedeutung im Projekt | Implikation für Architektur/Umsetzung | Projektbeleg |
|---|---|---|---|
| **Volume** | Stündliche Zeitreihendaten über viele Jahre (aktuell 2013-01-01 bis 2025-12-31) erzeugen eine relevante Datenmenge über Raw, Staging und Daily Layer. | Schichtenaufbau in MongoDB und Aggregation auf Tagesebene reduzieren Datenrauschen und halten den Analysepfad effizient. | `data/raw/open_meteo/*.json`, Collections `weather_open_meteo_raw`, `air_open_meteo_raw`, `weather_air_staged`, `weather_air_mapreduce_daily` |
| **Velocity** | Daten werden regelmäßig über APIs abgerufen; die Pipeline ist für wiederholte Ausführung ausgelegt. | Notebooks sind auf reproduzierbare Re-Runs ausgelegt (Up/Down, erneuter Ingest, erneute Aggregation). | Notebook-Reihenfolge `0 -> 5`, `0_docker_compose_up.ipynb`, `5_docker_compose_down.ipynb` |
| **Variety** | Unterschiedliche Datentypen und Schemata (Wetter- und Luftqualitätsmessungen; optional zusätzliche Quellen GeoSphere/EEA). | Vereinheitlichung in eine gemeinsame stündliche Staging-Struktur (`weather_air_staged`). | `2_data_storage_extraction_cleaning_staging.ipynb`, optional `fallback/1_1_data_source_geo_eea.ipynb` |
| **Veracity** | Rohdaten enthalten potenzielle Qualitätsprobleme (fehlende Werte, Duplikate, uneinheitliche Felder). | Cleaning + Normalisierung + eindeutige Indexe sorgen für konsistente Datenqualität je Zeitraum. | `staging_collection.create_index("time", unique=True)`, `daily_coll.create_index("date", unique=True)`, Bereinigung per `delete_many(...)` in Notebook 2/3 |
| **Value** | Fachlicher Nutzen: nachvollziehbare Aussagen zum Zusammenhang von Wetterregimen und PM2.5-Belastung. | Tagesaggregation schafft belastbare Kennzahlen für Storytelling, Korrelationen und robuste Interpretationen. | `weather_air_mapreduce_daily`, `4_data_output_storytelling.ipynb` |

## 2) Einordnung nach den 4 Levels of Data Handling

| Level | Umsetzung im Projekt | Warum das Big-Data-relevant ist | Projektbeleg |
|---|---|---|---|
| **Data Source** | Primär Open-Meteo APIs, optional zusätzlicher Fallback-Ingest aus GeoSphere/EEA. | Mehrquellenfähigkeit und API-basierte Zeitreihenintegration sind zentrale Data-Engineering-Aufgaben. | `1_data_source_open_meteo.ipynb`, `fallback/1_1_data_source_geo_eea.ipynb` |
| **Data Storage** | MongoDB in Schichten: Raw (`*_raw`) -> Staged (`weather_air_staged`) -> Daily (`weather_air_mapreduce_daily`). | Dokumentenmodell passt zu JSON-APIs und erleichtert iterative Aufbereitung sowie Wiederholbarkeit. | `docker-compose.yml`, Notebooks 1-3 |
| **Data Analysis** | Pandas-gestützte Verarbeitung plus Python-MapReduce-Logik im Notebook. | Trennung von Datenaufbereitung und Aggregation ermöglicht reproduzierbare Batch-Analysen auf Tagesebene. | `2_data_storage_extraction_cleaning_staging.ipynb`, `3_data_analysis_mapreduce.ipynb` |
| **Data Output** | Visualisierung, Korrelationen und interpretierte Ergebnisse für PM2.5 im Wetterkontext. | Ergebnisse werden in entscheidungsrelevante Aussagen überführt (nicht nur technisch berechnet). | `4_data_output_storytelling.ipynb` |


