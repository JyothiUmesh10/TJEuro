import streamlit as st
from datetime import date

import db  # our database helper


# ---------- App setup ----------
st.set_page_config(page_title="TJEuro Budget App", page_icon="💶")

# Make sure the database & table exist
db.init_db()

CATEGORIES = [
    "Groceries",
    "Rent",
    "Family Maintenance",
    "Fuel",
    "Miscellaneous",
    "Savings",
]

# ---------- Layout: sidebar navigation ----------
st.sidebar.title("TJEuro")
page = st.sidebar.radio(
    "Go to",
    ["Add transaction", "View transactions", "Monthly insights"],
)

st.title("TJEuro – Personal Budget App 💶")
st.caption("Version 1 – Built with Python & SQLite (no pandas)")


# ---------- Page: Add transaction ----------
if page == "Add transaction":
    st.subheader("Add a new transaction")

    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            txn_date = st.date_input("Date", value=date.today())
            txn_type = st.radio("Type", ["Expense", "Income"])

        with col2:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=0.01,
                format="%.2f",
            )
            category = st.selectbox("Category", CATEGORIES)

        description = st.text_input("Description (optional)")

        submitted = st.form_submit_button("Save transaction")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            db.add_transaction(
                txn_date=txn_date,
                description=description,
                amount=amount,
                txn_type=txn_type,
                category=category,
            )
            st.success("Transaction saved!")
            st.balloons()


# ---------- Page: View transactions ----------
elif page == "View transactions":
    st.subheader("All transactions")

    rows = db.get_all_transactions()

    if rows:
        # rows: list of tuples -> convert to list of dicts for nicer table
        table_data = []
        for row in rows:
            txn_id, txn_date, desc, amount, txn_type, category = row
            table_data.append(
                {
                    "ID": txn_id,
                    "Date": txn_date,
                    "Description": desc,
                    "Amount": f"{amount:.2f}",
                    "Type": txn_type,
                    "Category": category,
                }
            )

        st.table(table_data)
    else:
        st.info("No transactions yet. Add your first one on the 'Add transaction' page.")


# ---------- Page: Monthly insights ----------
elif page == "Monthly insights":
    st.subheader("Monthly insights")

    today = date.today()
    col1, col2 = st.columns(2)

    with col1:
        selected_year = st.selectbox(
            "Year",
            options=[today.year - 1, today.year, today.year + 1],
            index=1,
        )

    with col2:
        selected_month = st.selectbox(
            "Month (1–12)",
            options=list(range(1, 13)),
            index=today.month - 1,
        )

    summary = db.get_monthly_summary(selected_year, selected_month)

    st.markdown("### Key metrics")
    m1, m2, m3 = st.columns(3)

    m1.metric("Total income", f"€{summary['income']:.2f}")
    m2.metric("Total expenses", f"€{summary['expenses']:.2f}")
    m3.metric("Net savings", f"€{summary['net']:.2f}")

    st.markdown("### Spending by category")

    if summary["categories"]:
        cat_table = []
        for cat, amt in summary["categories"]:
            cat_table.append(
                {
                    "Category": cat,
                    "Amount": f"{amt:.2f}",
                }
            )
        st.table(cat_table)
    else:
        st.info("No transactions found for this month.")