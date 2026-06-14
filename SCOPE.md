# 🔬 SCOPE.md: Relational Database Schema & Data Anomaly Log

## 🗄️ Relational Database Architecture

The application implements a normalized SQLite database containing 6 core tables to maintain strict data integrity and historical trace logs.

   [users] ──(1:N)──> [group_memberships] (Tracks Tenant Timelines)
      │
      ├──(1:N)──> [expenses] (Core Transaction Headers)
      │              └──(1:N)──> [expense_splits] (Granular Cost Breakdowns)
      │
      └──(1:N)──> [settlements] (Direct Balance Repayments)

---

## 📊 Data Quality Anomaly Log (12+ Deliberate Defects Handled)

| Row Index | Field in Error | Anomaly Description | Applied Ingestion Policy & Resolution |
| :--- | :--- | :--- | :--- |
| **3 & 4** | `all` | Exact duplicate row logged back-to-back (Marina Bites). | **Policy:** Quarantined. First item ingested; second item completely dropped from calculations ledger. |
| **5** | `amount` | Malformed numeric string containing formatting commas (`"1,200"`). | **Policy:** Automated formatting strip using regex prior to numeric conversion. |
| **7, 25** | `paid_by` | Inconsistent string text casing (`priya`, `rohan`). | **Policy:** Automated capitalization formatting via string normalization rules (`.title()`). |
| **8** | `amount` | Floating point precision violation (Sub-paisa resolution: `899.995`). | **Policy:** Enforced standard financial precision by rounding to exactly 2 decimal places. |
| **9** | `paid_by` | Alias identification string ambiguity (`Priya S`). | **Policy:** Dynamic alias mapping table maps value to primary user key record (`Priya`). |
| **11** | `paid_by` | Missing explicit transaction payer (`NaN`). | **Policy:** Quarantined to a dedicated system user profile labeled `Unassigned` for manual tracing. |
| **12, 36** | `split_type` | Settlement transaction mistakenly logged inside the expense sheet. | **Policy:** Intercepted and routed completely outside of the expense framework into the `settlements` table. |
| **14, 25, 32** | `date` | Inconsistent/mixed date formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `MMM DD`). | **Policy:** Implemented multi-format date string parser to safely convert entries to ISO format. |
| **18, 19, 21** | `currency` | Multi-currency transactions logged natively in USD. | **Policy:** Currency conversion layer standardizes values into home currency asset base using a fixed coefficient ($1 USD = 83 INR). |
| **21** | `split_with` | Non-group target member present inside the split matrix (`Kabir`). | **Policy:** Allocated Kabir's debt balance obligation directly to his operational sponsor (`Dev`). |
| **22 & 23** | `all` | Conflicting duplicate entry with data variance (Thalassa dinner). | **Policy:** Ingested header details but flagged field status as `pending_meera_approval` to lock out calculations until manually checked. |
| **24** | `amount` | Negative value expense column item (USD refund). | **Policy:** Handled as a classic credit adjustment. Reversed standard payment flows to credit group members. |
| **26** | `currency` | Missing currency data column (`NaN`). | **Policy:** Implemented standard localized fallback schema defaulting the missing cell property to `INR`. |
| **29** | `amount` | Zero-value transaction entry row items. | **Policy:** Flagged as informational log message warning and excluded from affecting ledger arithmetic. |
| **34** | `split_with` | Timeline/Tenancy lifecycle violation (Meera charged after lease end date). | **Policy:** Cross-referenced entry date with membership lifetime windows; excluded Meera from splits after March 31st. |
