import sqlite3
import os

DB_NAME = "expenses.db"

def initialize_database():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"🗑️ Clean reset: Dropped old {DB_NAME}.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("🛠️ Constructing normalized relational schema tables...")

    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE group_memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        joined_date TEXT NOT NULL,  -- YYYY-MM-DD
        left_date TEXT,             -- YYYY-MM-DD (NULL if currently active)
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,         -- YYYY-MM-DD
        description TEXT NOT NULL,
        paid_by_id INTEGER,
        original_amount REAL NOT NULL,
        original_currency TEXT NOT NULL,
        amount_inr REAL NOT NULL,
        split_type TEXT NOT NULL,
        notes TEXT,
        import_status TEXT DEFAULT 'approved',
        FOREIGN KEY (paid_by_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE expense_splits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        share_amount REAL NOT NULL,
        FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE settlements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payer_id INTEGER NOT NULL,
        payee_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (payer_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (payee_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE import_anomalies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        csv_row_index INTEGER,
        raw_row_data TEXT,
        field_in_error TEXT,
        description TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        resolution_status TEXT DEFAULT 'auto_fixed'
    );
    """)

    print("🌱 Seeding dynamic user profiles and tenancy windows...")
    flatmates = ["Aisha", "Rohan", "Priya", "Meera", "Sam", "Dev", "Unassigned"]
    user_ids = {}
    for name in flatmates:
        cursor.execute("INSERT INTO users (name) VALUES (?);", (name,))
        user_ids[name] = cursor.lastrowid

    # Enforce tenancy lifecycles: Meera moves out end of March. Sam moves in mid-April.
    memberships = [
        (user_ids["Aisha"], "2026-02-01", None),
        (user_ids["Rohan"], "2026-02-01", None),
        (user_ids["Priya"], "2026-02-01", None),
        (user_ids["Meera"], "2026-02-01", "2026-03-31"),
        (user_ids["Sam"], "2026-04-15", None),
        (user_ids["Dev"], "2026-02-01", None),
    ]

    cursor.executemany("""
        INSERT INTO group_memberships (user_id, joined_date, left_date)
        VALUES (?, ?, ?);
    """, memberships)

    conn.commit()
    conn.close()
    print("✅ System tables successfully initialized and seeded.")

if __name__ == "__main__":
    initialize_database()