# Day 01 – Repo Setup & First Dataset
--------------------------------------------------------
## Ziel des Tages
- Projektstruktur sauber aufsetzen
- Erstes CSV-Dataset laden
- Basis-Checks durchführen
--------------------------------------------------------
## Technische Schritte
- Ordnerstruktur erstellt
- README angelegt
- pandas installiert (falls notwendig)
- CSV-Datei in data/raw abgelegt
- Dataset geladen
-------------------------------------------------------------
## Output-Checks
- shape: (8, 4)

- head(5):
customer_id age country revenue
1 25 AT 120
2 31 DE 200
3 22 AT 150
4 45 CH 300
5 29 DE 180
---------------------------------
- isna().sum():
customer_id    0
age            1
country        0
revenue        1

------------------------------------------

## Mini-Interpretation (3 Sätze)
1. Das Dataset enthält 8 Beobachtungen und 4 Merkmale
2. Es existieren fehlende Werte in den Variablen age und revenue
3. Vor einer Modellierung müsste eine Missing-Value-Strategie definiert werden
--------------------------------------------
## Done Definition (DoD)
- [x] Ordnerstruktur steht
- [x] pandas liest CSV
- [x] Evidence-Datei ausgefüllt
- [ ] Commit erstellt
