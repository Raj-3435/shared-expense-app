# 🤖 AI_USAGE.md: Generative AI Collaboration Audit Log

## 💡 Key Prompts Utilized
- *"Write a Python script using sqlite3 to initialize a relational schema for a shared expenses application..."*
- *"Write a Streamlit application (app.py) that implements four distinct views..."*

---

## 🪲 Concrete Bug Containment Cases (AI Mistakes Caught & Resolved)

### Case 1: Python String Formatting Injected Directly into SQL Statements
- **What the AI Generated:** The model attempted to place a Python f-string literal syntax directly inside an unparameterized SQL execute query string: `cursor.execute("INSERT INTO... f'Inconsistent casing: {payer_raw}'...")`.
- **How it was Caught:** The ingestion process crashed immediately with an explicit `sqlite3.OperationalError` highlighting a syntax failure near the curly braces.
- **Resolution Strategy:** Rewrote the block to separate the Python string generation logic and pass the value securely using standard SQL query placeholders (`?`).

### Case 2: Hallucinated Front-End Library API Method
- **What the AI Generated:** Inside the manual transaction form tab component, the AI code called `st.form_submit_with_button()`.
- **How it was Caught:** The local Streamlit compilation server crashed on boot, throwing an explicit `AttributeError: module 'streamlit' has no attribute 'form_submit_with_button'`.
- **Resolution Strategy:** Audited the official documentation API and changed the hallucinated method name to the legitimate native function: `st.form_submit_button()`.

### Case 3: Silent Denominator Calculation Error for Static Expense Splits
- **What the AI Generated:** An early iteration of the engine computed equal split distributions by statically dividing the expense amount across all names extracted from the raw string row via `len(split_with)`.
- **How it was Caught:** Manual calculations check during testing revealed that Sam was being incorrectly charged for historical March utility records, and Meera was being charged for April items.
- **Resolution Strategy:** Restructured the engine to filter the active split array against the relational `group_memberships` matrix *before* computing the partition denominator, ensuring the division only counts active tenants on that transaction date.