# 💸 SplitSmart: Production-Grade Shared Ledger App

SplitSmart is a relational database-backed expense management platform designed to cleanly resolve complex shared accounting scenarios, track membership lifecycles (moving in/out), and safely parse inconsistent flat-file formats.

## 🚀 Setup & Installation Instructions

### Prerequisites
- Python 3.10 or higher
- `pip` (Python package manager)

### Local Deployment Steps
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
