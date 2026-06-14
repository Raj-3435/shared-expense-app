# 💸 SplitSmart: Shared Expenses Ledger Application

SplitSmart is a production-grade, relational-backed financial ledger application designed to ingest, clean, and manage shared household expenses. It dynamically accounts for shifting roommate tenancy timelines, converts multi-currency entries, automatically flags spreadsheet anomalies, and minimizes overall group debt through an optimized transactional settlement engine.

---

## 🔗 Project Deliverables & Live Links
* **Public Deployed Application URL:** `https://shared-expense-app.streamlit.app/`
* **GitHub Repository URL:** `https://github.com/Raj-3435/shared_expense_app`

---

## 🛠️ System Architecture & Technology Stack
* **Frontend Interface:** Streamlit (Python-native reactive UI layer optimized for rapid dashboard construction)
* **Database Engine:** SQLite (`sqlite3`) — Normalized relational modeling with strict foreign key constraints enforced via database pragmas.
* **Data Processing Layer:** Pandas & Regular Expressions (RegEx) for string formatting extractions and robust date transformations.

---

## ✨ Core Application Features

### 1. Dynamic Tenancy Timeline Validation
* Automatically references a database-backed membership timeline to prevent roommates from being charged for expenses outside their active occupancy lease window.
* Ensures March utility bills are isolated from mid-April additions while ensuring departed tenants are excluded from calculations after their move-out date.

### 2. Aisha's Strategic Settlement Engine
* Implements a greedy pairwise debt-simplification graph engine to calculate the absolute minimal number of direct financial transfers required to settle the group ledger.
* Surfaces clear, scannable balance metrics displaying every user's precise credit or debt standing at a single glance.

### 3. Rohan's Exhaustive Audit Trail
* Banish "magic numbers" by offering an itemized ledger lookup for every user session.
* Roommates can drill down into a granular personal view showing exactly which paid expenses, custom split breakdowns, and logged repayments comprise their exact net position.

### 4. Meera's Conflict Remediation Queue
* Implements an interactive database staging area for duplicate or conflicting transaction rows.
* Prevents disputed double-entries from corrupting calculation balances until they are explicitly approved or dropped via user intervention.

### 5. In-App Data Ingestion Hub
* Features an integrated drop-zone widget allowing users to upload a messy exported tracking sheet directly through the browser.
* Generates a structural ingestion audit report summarizing every anomaly caught and the automated correction policy applied.

---

## ⚙️ Setup, Installation & Local Execution

### Prerequisites
* **Python Engine:** Version 3.10 or higher
* **Package Manager:** `pip`

### Step-by-Step Execution Guide

1. **Clone the Repository:**
2. **Install Core Engine Dependencies:**
   ```bash
   pip install streamlit pandas
   ```
3. **Initialize the Relational Database Layer:**
Run the schema initialization script to build tables, set up    constraints, and seed active user timeline structures:
    ```bash
    python init_db.py
    ```
4. **Ingest and Normalize the CSV Log:**
Run the processing pipeline engine to clean up data quality defects, resolve multi-currency conversions, calculate splits, and populate the database tables:
    ```bash
    python importer.py
    ```
5. **Launch the Streamlit Frontend:**
Start the interactive web application to visualize ledger data, audit anomaly reports, and perform settlement operations:
    ```bash
    streamlit run app.py
    ```
