import streamlit as st
import pandas as pd
import sqlite3
import re
from importer import run_import

DB_NAME = "expenses.db"

st.set_page_config(page_title="SplitSmart - Shared Ledger App", layout="wide", page_icon="💸")
# Auto-initialize database tables if the file is missing or empty on the cloud server
import os
import init_db

if not os.path.exists(DB_NAME) or os.path.getsize(DB_NAME) == 0:
    init_db.initialize_database()
# --- DATABASE UTILITIES ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Fetch user list
def get_users():
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT id, name FROM users WHERE name != 'Unassigned';", conn)

def normalize_user_name(name_str):
    name = str(name_str).strip().title()
    mapping = {"Priya S": "Priya", "Priya": "Priya", "Rohan": "Rohan", "Aisha": "Aisha", "Meera": "Meera", "Sam": "Sam", "Dev": "Dev"}
    return mapping.get(name, name)

# Compute live net position matrix for everyone
def calculate_net_balances():
    with get_db_connection() as conn:
        paid_df = pd.read_sql_query("""
            SELECT u.name, COALESCE(SUM(e.amount_inr), 0) as total_paid
            FROM users u
            LEFT JOIN expenses e ON u.id = e.paid_by_id AND e.import_status = 'approved'
            GROUP BY u.name;
        """, conn)
        
        owed_df = pd.read_sql_query("""
            SELECT u.name, COALESCE(SUM(s.share_amount), 0) as total_owed
            FROM users u
            LEFT JOIN expense_splits s ON u.id = s.user_id
            LEFT JOIN expenses e ON s.expense_id = e.id
            WHERE e.import_status IS NULL OR e.import_status = 'approved'
            GROUP BY u.name;
        """, conn)
        
        settlements_paid = pd.read_sql_query("""
            SELECT u.name, COALESCE(SUM(s.amount), 0) as settled_out
            FROM users u
            LEFT JOIN settlements s ON u.id = s.payer_id
            GROUP BY u.name;
        """, conn)
        
        settlements_received = pd.read_sql_query("""
            SELECT u.name, COALESCE(SUM(s.amount), 0) as settled_in
            FROM users u
            LEFT JOIN settlements s ON u.id = s.payee_id
            GROUP BY u.name;
        """, conn)
        
    summary = paid_df.merge(owed_df, on="name").merge(settlements_paid, on="name").merge(settlements_received, on="name")
    summary = summary[summary['name'] != 'Unassigned']
    summary['net_balance'] = (summary['total_paid'] + summary['settled_out']) - (summary['total_owed'] + summary['settled_in'])
    return summary

# --- SIMULATED SECURE LOGIN ---
st.sidebar.image("https://img.icons8.com/fluent/96/000000/property-development.png", width=60)
st.sidebar.title("🔐 Secure Login Portal")
user_profiles = ["Aisha", "Rohan", "Priya", "Meera", "Sam", "Dev"]
logged_in_user = st.sidebar.selectbox("Access Account As:", user_profiles)
st.sidebar.caption(f"Authenticated session: **{logged_in_user}** (Flatmate Mode)")

# --- PRODUCT INTERFACE TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Aisha's Summary Ledger", 
    "🔍 Rohan's Audit Trail", 
    "🛠️ Meera's Approval Queue",
    "📥 Ingestion Report",
    "➕ Create Expense",
    "💸 Settle Debt"
])

# -------------------------------------------------------------
# TAB 1: AISHA'S SUMMARY LEDGER
# -------------------------------------------------------------
with tab1:
    st.header("📋 Group Financial Status Summary")
    balances_df = calculate_net_balances()
    
    cols = st.columns(len(balances_df))
    for idx, row in balances_df.iterrows():
        with cols[idx]:
            val = row['net_balance']
            color_prefix = "🟢" if val >= 0 else "🔴"
            st.metric(label=f"{row['name']}'s Balance", value=f"₹{val:,.2f}", delta=f"{color_prefix} Position")

    st.subheader("💡 Minimal Settlement Transactions Graph (Aisha's View)")
    
    debtors = [] 
    creditors = [] 
    
    for _, r in balances_df.iterrows():
        b = round(r['net_balance'], 2)
        if b < -0.01:
            debtors.append([r['name'], abs(b)])
        elif b > 0.01:
            creditors.append([r['name'], b])
            
    settlement_instructions = []
    while debtors and creditors:
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)
        
        d_name, d_amt = debtors[0]
        c_name, c_amt = creditors[0]
        
        settle_amt = min(d_amt, c_amt)
        settlement_instructions.append(f"💳 **{d_name}** pays **{c_name}** → **₹{settle_amt:,.2f}**")
        
        debtors[0][1] -= settle_amt
        creditors[0][1] -= settle_amt
        
        if debtors[0][1] < 0.01: debtors.pop(0)
        if creditors[0][1] < 0.01: creditors.pop(0)

    if settlement_instructions:
        for ins in settlement_instructions:
            st.info(ins)
    else:
        st.success("🎉 All balances are perfectly settled! Nobody owes anything.")

# -------------------------------------------------------------
# TAB 2: ROHAN'S AUDIT TRAIL
# -------------------------------------------------------------
with tab2:
    st.header(f"🔍 Itemized Ledger Breakdown for {logged_in_user}")
    st.caption("Satisfying Rohan's Clause: Total visibility into how balances are compiled.")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE name = ?;", (logged_in_user,))
        uid = cursor.fetchone()['id']
        
        st.subheader("💵 Expenses You Paid")
        paid_items = pd.read_sql_query("""
            SELECT date, description, original_amount, original_currency, amount_inr, split_type, notes
            FROM expenses WHERE paid_by_id = ? AND import_status = 'approved';
        """, conn, params=(uid,))
        st.dataframe(paid_items, use_container_width=True)
        
        st.subheader("📉 Your Shared Obligations (Splits)")
        split_items = pd.read_sql_query("""
            SELECT e.date, e.description, u.name as paid_by, e.original_amount, 
                   e.original_currency, e.amount_inr, es.share_amount, e.notes
            FROM expense_splits es
            JOIN expenses e ON es.expense_id = e.id
            JOIN users u ON e.paid_by_id = u.id
            WHERE es.user_id = ? AND e.import_status = 'approved';
        """, conn, params=(uid,))
        st.dataframe(split_items, use_container_width=True)

        st.subheader("🔄 Repayments & Settlements Linked To You")
        set_items = pd.read_sql_query("""
            SELECT s.date, u1.name as payer, u2.name as payee, s.amount, s.notes
            FROM settlements s
            JOIN users u1 ON s.payer_id = u1.id
            JOIN users u2 ON s.payee_id = u2.id
            WHERE s.payer_id = ? OR s.payee_id = ?;
        """, conn, params=(uid, uid))
        st.dataframe(set_items, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: MEERA'S APPROVAL QUEUE
# -------------------------------------------------------------
with tab3:
    st.header("🛠️ Conflict Remediation Queue")
    st.caption("Satisfying Meera's Clause: Manual controls over disputed row duplicates.")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    pending_expenses = cursor.execute("""
        SELECT id, date, description, original_amount, original_currency, amount_inr, notes 
        FROM expenses WHERE import_status = 'pending_meera_approval';
    """).fetchall()
    
    if not pending_expenses:
        st.success("✨ Zero conflict flags pending. Your transaction queue is completely clean!")
    else:
        for row in pending_expenses:
            st.warning(f"⚠️ **Disputed Row Detected:** {row['description']} | {row['date']} | {row['original_amount']} {row['original_currency']} (INR: ₹{row['amount_inr']})")
            c1, c2, _ = st.columns([1, 1, 4])
            
            if c1.button("✅ Approve Entry", key=f"app_{row['id']}"):
                cursor.execute("UPDATE expenses SET import_status = 'approved' WHERE id = ?;", (row['id'],))
                conn.commit()
                st.rerun()
                
            if c2.button("❌ Reject & Delete", key=f"rej_{row['id']}"):
                cursor.execute("DELETE FROM expenses WHERE id = ?;", (row['id'],))
                cursor.execute("DELETE FROM expense_splits WHERE expense_id = ?;", (row['id'],))
                conn.commit()
                st.rerun()
    conn.close()

# -------------------------------------------------------------
# TAB 4: INGESTION REPORT
# -------------------------------------------------------------
with tab4:
    st.header("📥 Data Ingestion Panel")
    st.caption("Upload your expenses CSV file directly into the application engine.")
    
    uploaded_file = st.file_uploader("Upload expenses_export.csv", type=["csv"])
    if st.button("Trigger Ingestion Engine"):
        with st.spinner("Processing file..."):
            run_import(uploaded_file)
        st.success("Ingestion successful!")
        st.rerun()

    st.subheader("📋 Automated Data Quality Audit Log")
    with get_db_connection() as conn:
        anomalies_df = pd.read_sql_query("SELECT csv_row_index as 'CSV Row', field_in_error as 'Field', description as 'Issue Identified', action_taken as 'Automated Remediation Policy' FROM import_anomalies;", conn)
    
    st.dataframe(anomalies_df, use_container_width=True)

# -------------------------------------------------------------
# TAB 5: CREATE NEW EXPENSE
# -------------------------------------------------------------
with tab5:
    st.header("➕ Add an Expense Manually")
    
    user_data = get_users()
    user_options = {row['name']: row['id'] for idx, row in user_data.iterrows()}
    
    with st.form("manual_expense_form"):
        date_input = st.date_input("Transaction Date")
        desc_input = st.text_input("Description/Merchant")
        payer_input = st.selectbox("Paid By", list(user_options.keys()))
        amount_input = st.number_input("Amount", min_value=0.0, step=100.0)
        currency_input = st.selectbox("Currency Base", ["INR", "USD"])
        
        st.subheader("Split Details")
        split_profile = st.multiselect("Split Between Matrix Members", list(user_options.keys()), default=list(user_options.keys()))
        split_type = st.selectbox("Split Type", ["equal", "percentage", "share", "unequal"])
        split_details = st.text_input("Split Logic Details (e.g. 'Aisha 30%; Rohan 70%' or 'Aisha 1; Rohan 2' or 'Aisha 500; Rohan 200')", help="Leave blank for 'equal'")
        notes_input = st.text_input("Notes")
        
        submitted = st.form_submit_button("Commit Entry to Ledger")
        if submitted:
            if not desc_input or amount_input <= 0 or not split_profile:
                st.error("❌ Form validation failed: Ensure fields are populated completely.")
            else:
                final_inr = amount_input * 83.0 if currency_input == "USD" else amount_input
                pid = user_options[payer_input]
                date_str = str(date_input)
                
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Validate active members on the given date
                    valid_members = []
                    for m in split_profile:
                        cursor.execute("SELECT joined_date, left_date FROM group_memberships WHERE user_id = ?;", (user_options[m],))
                        res = cursor.fetchone()
                        if res:
                            jd, ld = res['joined_date'], res['left_date']
                            if jd and date_str < jd:
                                st.warning(f"Skipped {m} - date before lease start.")
                                continue
                            if ld and date_str > ld:
                                st.warning(f"Skipped {m} - date after lease end.")
                                continue
                            valid_members.append(m)

                    if not valid_members:
                        st.error("❌ No valid members to split the expense with on this date.")
                    else:
                        cursor.execute("""
                            INSERT INTO expenses (date, description, paid_by_id, original_amount, original_currency, amount_inr, split_type, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                        """, (date_str, desc_input, pid, amount_input, currency_input, final_inr, split_type, notes_input))
                        
                        new_exp_id = cursor.lastrowid
                        splits_computed = {}
                        N = len(valid_members)

                        if split_type == "equal":
                            share = final_inr / N
                            for m in valid_members:
                                splits_computed[user_options[m]] = share

                        elif split_type == "percentage":
                            matches = re.findall(r'([A-Za-z]+)\s+(\d+)%', split_details)
                            total_p = sum(int(p) for _, p in matches)
                            for name, pct in matches:
                                m_norm = normalize_user_name(name)
                                if m_norm in valid_members:
                                    actual_pct = int(pct) if total_p == 100 or total_p == 0 else (int(pct) / total_p) * 100
                                    splits_computed[user_options[m_norm]] = final_inr * (actual_pct / 100)

                        elif split_type == "share":
                            matches = re.findall(r'([A-Za-z]+)\s+(\d+)', split_details)
                            total_shares = sum(int(s) for _, s in matches)
                            for name, shares in matches:
                                m_norm = normalize_user_name(name)
                                if m_norm in valid_members and total_shares > 0:
                                    splits_computed[user_options[m_norm]] = final_inr * (int(shares) / total_shares)

                        elif split_type == "unequal":
                            matches = re.findall(r'([A-Za-z]+)\s+(\d+(?:\.\d+)?)', split_details)
                            for name, fixed_val in matches:
                                m_norm = normalize_user_name(name)
                                if m_norm in valid_members:
                                    splits_computed[user_options[m_norm]] = float(fixed_val)

                        for uid, share_val in splits_computed.items():
                            cursor.execute("""
                                INSERT INTO expense_splits (expense_id, user_id, share_amount)
                                VALUES (?, ?, ?);
                            """, (new_exp_id, uid, round(share_val, 2)))
                        
                        conn.commit()
                        st.success("🚀 Entry logged successfully! Balances updated.")

# -------------------------------------------------------------
# TAB 6: SETTLE DEBT
# -------------------------------------------------------------
with tab6:
    st.header("💸 Settle a Debt or Record a Payment")
    
    user_data = get_users()
    user_options = {row['name']: row['id'] for idx, row in user_data.iterrows()}
    
    with st.form("manual_settlement_form"):
        s_date = st.date_input("Settlement Date")
        s_payer = st.selectbox("Who Paid?", list(user_options.keys()), index=0)
        s_payee = st.selectbox("Who Received?", list(user_options.keys()), index=1)
        s_amount = st.number_input("Amount (INR)", min_value=1.0, step=100.0)
        s_notes = st.text_input("Notes (e.g. 'Cleared March utilities')")
        
        submitted_settlement = st.form_submit_button("Log Settlement")
        
        if submitted_settlement:
            if s_payer == s_payee:
                st.error("❌ Payer and Payee cannot be the same person.")
            else:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO settlements (payer_id, payee_id, amount, date, notes)
                        VALUES (?, ?, ?, ?, ?);
                    """, (user_options[s_payer], user_options[s_payee], s_amount, str(s_date), s_notes))
                    conn.commit()
                st.success(f"✅ Logged payment of ₹{s_amount:,.2f} from {s_payer} to {s_payee}.")