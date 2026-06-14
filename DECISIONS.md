# 🧠 DECISIONS.md: Architecture & Technology Selection Log

### 1. Technology Selection: Streamlit + SQLite vs Next.js + PostgreSQL
- **Options Considered:** Next.js with Supabase (PostgreSQL) vs Python (Streamlit + SQLite).
- **Decision:** Selected **Streamlit + SQLite**.
- **Justification:** Given the short timeline, writing full frontend React components, API routes, and deployment pipelines introduces boilerplate that does not add core value to ledger calculations. A Streamlit frontend allows for rapid UI construction completely inside Python, while a local SQLite instance retains clean database relational modeling capabilities, foreign key support, and rapid schema teardowns.

### 2. Multi-Currency Management Architecture
- **Options Considered:** Dynamic real-time API exchange fetching vs Static normalization factor.
- **Decision:** Implemented a **Static Normalization Factor** (1 USD = 83 INR) during file ingestion.
- **Justification:** Financial ledgers require deterministic inputs. Fetching variable live currency rates at runtime would dynamically shift historical totals, which violates Rohan's requirement for a reliable, fixed audit trail.

### 3. Tenant Timeline/Lifecycle Processing Blockers
- **Options Considered:** Hardcoding row filtering inside the UI views vs Normalizing date ranges within a database membership table.
- **Decision:** Implemented relational **`group_memberships` table lifetimes** (`joined_date`, `left_date`).
- **Justification:** Hardcoding row boundaries breaks scalability. Storing occupancy windows explicitly inside the database lets the system filter out inactive members automatically on any transaction date, which solves Sam and Meera's timeline edge cases cleanly.