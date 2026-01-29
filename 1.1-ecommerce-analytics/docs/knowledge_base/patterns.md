# Patterns

## KPI Report Pipeline
**Problem**: KPI report should be reproducible and not depend on a notebook run.
**Solution**: Use a Python script (`src/kpi_analysis.py`) to compute KPIs, tables and figures, then write `reports/kpi_summary.md`.
**Why it works**: It keeps a single source of truth, can be executed in CI, and is easy to review in code.
