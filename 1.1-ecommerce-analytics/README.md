# E-Commerce Analytics – Online Retail Dataset

> **Purpose**: Dieses Repo nutzt ein strukturiertes Multi-Agenten-System für Entwicklung, Dokumentation und Wissensmanagement.

## 📂 Struktur & Navigation

- **`.agent/`**: Gehirn des Systems. Enthält Skills (Prompts) und Rollendefinitionen.
- **`docs/knowledge_base/`**: Langzeitgedächtnis. Architektur, Entscheidungen, Glossar.
- **`docs/project_status/`**: Kurzzeitgedächtnis & Verlauf. Timestamped Snapshots für Handovers.
- **`docs/skill-mapping.md`**: Kompetenz-Matrix dieses Projekts.

## 🤖 Workflow & Rollen

Wir arbeiten nach dem **O-D-L Prinzip**:
1.  **O**rchestrate: Der Orchestrator plant und verteilt Aufgaben.
2.  **D**ocument: Bevor/Nachdem Code geschrieben wird, wird der Status festgehalten.
3.  **L**earn: Erkenntnisse werden explizit extrahiert und gespeichert.

## 🛠 Quickstart für Agenten

1.  **Lese Skills**: Prüfe `.agent/skills/` für deine spezifischen Instruktionen.
2.  **Check Status**: Lese den neuesten Report in `docs/project_status/`.
3.  **Update Status**: Erstelle VOR und NACH großen Änderungen einen Snapshot.

## 📝 Conventions

-   **Timestamp**: `YYYY-MM-DD_HH-mm` (Europe/Vienna)
-   **Status Files**: Immer Markdown.
-   **Sprache**: Deutsch (DE).

## 🚀 Getting Started (Human)

1.  Setup: `python -m venv venv`
2.  Install: `pip install -r requirements.txt`
3.  Notebooks: `jupyter notebook`

## 📊 Project Status
Siehe `docs/project_status/` für die neuesten Updates.
