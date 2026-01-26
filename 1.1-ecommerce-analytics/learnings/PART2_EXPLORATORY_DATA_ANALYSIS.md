# Data Science Learning Journey
## Teil 2: Explorative Datenanalyse (EDA) – Der "Gesundheits-Check"

Im Notebook `01_eda.ipynb` führen wir die **Explorative Data Analysis (EDA)** durch. Dies ist oft der wichtigste Schritt in einem Data-Science-Projekt.

---

## 1. Was ist EDA und warum tun wir das?

Stell dir vor, du bist ein Arzt und bekommst einen neuen Patienten (deinen Datensatz). Bevor du eine komplexe Operation durchführst (Machine Learning), machst du erst einmal einen allgemeinen Gesundheits-Check.
* Fieber messen (Verteilungen prüfen)
* Blutbild (Datentypen und Null-Values prüfen)
* Anamnese (Verstehen, wo die Daten herkommen)

**Ziele dieses Notebooks:**
1.  **Vertrauen aufbauen**: Stimmen die Daten? Kann ich ihnen glauben?
2.  **Fehler finden**: Gibt es negative Preise? Kunden ohne ID?
3.  **Business-Verständnis**: Was ist der meistverkaufte Artikel? Aus welchem Land kommen die Kunden?

---

## 2. Die konkreten Schritte im Notebook erklärt

### Schritt 1: Laden und der "Shape"
```python
df = pd.read_parquet(DATA_PATH)
print(df.shape)
```
**Warum?**
`shape` gibt dir `(Zeilen, Spalten)`.
*   Zu wenige Zeilen? Vielleicht ist beim Download etwas schiefgegangen.
*   Zu viele Spalten? Vielleicht wurden Excel-Hilfsspalten mit eingelesen.
*   *Learning*: Kenne immer die grobe Größe deiner Daten. 500.000 Transaktionen erfordern andere Tools als 50 Millionen.

### Schritt 2: Datentypen (`dtypes`)
```python
df.info()  # oder df.dtypes
```
**Warum?**
Ein Computer ist dumm. Für ihn ist die Zahl `5` etwas anderes als der Text `"5"`.
*   `InvoiceNo`: Ist oft Text (wegen "C" für Cancelled/Storno).
*   `UnitPrice`: Muss `float` (Kommazahl) sein.
*   `Quantity`: Muss `int` (Ganzzahl) sein.
*   `InvoiceDate`: Muss `datetime` sein (Ganz wichtig für Zeitreihen-Analysen!).

**Der Fehlerteufel:** Oft liest Pandas Datumsangaben als simplen Text ("Object"). Wenn du dann fragen willst "Wie viel Umsatz im Dezember?", scheitert der Code. Deshalb prüfen wir das hier sofort.

### Schritt 3: Fehlende Werte (`Missing Values`)
```python
df.isnull().sum()
```
**Interpretation für E-Commerce:**
*   **Description fehlt?** Unschön, aber vielleicht nicht kritisch für den Umsatz.
*   **CustomerID fehlt?** **SEHR WICHTIG!**
    *   Bedeutet das einen Code-Fehler?
    *   Oder sind das **Gast-Bestellungen** (Guest Checkout), wo der Kunde kein Konto angelegt hat?
    *   *Entscheidung*: In einer Kundenanalyse (Clustering) müssen wir diese Zeilen löschen. In einer Umsatzanalyse dürfen wir sie behalten.

### Schritt 4: Statistische Zusammenfassung (`describe`)
```python
df.describe()
```
Dieser Befehl zeigt Min, Max, Mean (Durchschnitt) für alle Zahlen-Spalten. Hier finden wir die "Leichen im Keller":
*   **Min Quantity < 0?** → Aha! Es gibt Retouren (Stornierungen). Das ist eine wichtige Business-Logik.
*   **Min UnitPrice = 0?** → Werden Artikel verschenkt? Ist das ein Fehler? Oder sind das Promo-Artikel?
*   **Max Quantity = 80995?** → Ein einzelner Kauf mit riesiger Menge? Ist das ein B2B-Kunde (Großhändler) oder ein Tippfehler?

---

## 3. Die "Business-Fragen" (Was wollen wir eigentlich wissen?)

Wir machen EDA nicht zum Selbstzweck, sondern um Fragen zu beantworten:

1.  **Wer sind unsere Kunden?** (Länderverteilung)
2.  **Was kaufen sie?** (Top Seller vs. Ladenhüter)
3.  **Wann kaufen sie?** (Saisonalität: Weihnachten, Wochenende, Uhrzeit)

## Zusammenfassung
Das Notebook `01_eda.ipynb` ist dein **Labor**. Hier darfst du experimentieren.
*   Wir löschen hier noch keine Daten (das machen wir in einer Pipeline oder einem separaten Cleaning-Schritt).
*   Wir dokumentieren hier unsere **Auffälligkeiten**.

**Merke:** Ein Data Scientist verbringt 80% der Zeit mit EDA und Cleaning, und nur 20% mit "Cooler AI". Wenn die EDA schlampig ist, wird das AI-Modell nutzlos ("Garbage In, Garbage Out").
