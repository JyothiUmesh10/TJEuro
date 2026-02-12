import sqlite3
from datetime import datetime
from pathlib import Path

DB_NAME = "budget.db"


def get_connection():
    """
    Returns a connection to the SQLite database.
    The file will be created in the current folder if it doesn't exist.
    """
    db_path = Path(DB_NAME)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn


def init_db():
    """
    Creates the transactions table if it doesn't exist.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            type TEXT NOT NULL,         -- 'Income' or 'Expense'
            category TEXT NOT NULL,     -- Groceries, Rent, etc.
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def add_transaction(txn_date, description, amount, txn_type, category):
    """
    Inserts a new transaction row.
    txn_date is a datetime.date object.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO transactions (date, description, amount, type, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            txn_date.isoformat(),
            description,
            float(amount),
            txn_type,
            category,
            datetime.utcnow().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


def get_all_transactions():
    """
    Returns all transactions as a list of tuples.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, date, description, amount, type, category
        FROM transactions
        ORDER BY date DESC, id DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_monthly_summary(year: int, month: int):
    """
    Returns aggregated income, expenses, net, and category totals
    for a given month (year, month).
    """
    conn = get_connection()
    cur = conn.cursor()

    # Dates are stored as 'YYYY-MM-DD' strings; we match 'YYYY-MM'
    month_str = f"{year:04d}-{month:02d}"

    # Total income (type = 'Income')
    cur.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'Income'
        AND substr(date, 1, 7) = ?
        """,
        (month_str,),
    )
    total_income = cur.fetchone()[0] or 0.0

    # Total expenses (type = 'Expense')
    cur.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'Expense'
        AND substr(date, 1, 7) = ?
        """,
        (month_str,),
    )
    total_expenses = cur.fetchone()[0] or 0.0

    # Category-wise expenses (only Expense type)
    cur.execute(
        """
        SELECT category, SUM(amount)
        FROM transactions
        WHERE type = 'Expense'
        AND substr(date, 1, 7) = ?
        GROUP BY category
        """,
        (month_str,),
    )
    category_rows = cur.fetchall()

    conn.close()

    return {
        "income": float(total_income),
        "expenses": float(total_expenses),
        "net": float(total_income) - float(total_expenses),
        "categories": category_rows,
    }