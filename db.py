import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
_raw_db = os.getenv("SQLITE_PATH", "agent.db")
DB_PATH = Path(_raw_db) if Path(_raw_db).is_absolute() else BASE_DIR / _raw_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(SCHEMA)
        row = conn.execute("SELECT COUNT(*) AS cnt FROM products").fetchone()
        count = row["cnt"] if row is not None else 0

        if count == 0:
            products = [
                ("Keyboard", "Accessories", 1500.0),
                ("Mouse", "Accessories", 800.0),
                ("Monitor", "Electronics", 12000.0),
                ("USB-C Hub", "Accessories", 2200.0),
                ("Desk Lamp", "Home Office", 1800.0),
            ]
            conn.executemany(
                "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
                products,
            )

            sales = [
                (1, 5, "2026-10-01"),
                (1, 4, "2026-10-03"),
                (2, 10, "2026-10-02"),
                (3, 1, "2026-10-04"),
                (4, 3, "2026-10-05"),
                (5, 2, "2026-10-06"),
            ]
            conn.executemany(
                "INSERT INTO sales (product_id, quantity, sale_date) VALUES (?, ?, ?)",
                sales,
            )
        conn.commit()


def run_query(sql: str) -> list[dict]:
    init_db()
    with _connect() as conn:
        cursor = conn.execute(sql)
        return [dict(row) for row in cursor.fetchall()]


def get_stats() -> dict:
    init_db()
    with _connect() as conn:
        p_row = conn.execute("SELECT COUNT(*) AS cnt FROM products").fetchone()
        s_row = conn.execute("SELECT COUNT(*) AS cnt FROM sales").fetchone()
        return {
            "db_file": DB_PATH.name,
            "products_count": p_row["cnt"] if p_row is not None else 0,
            "sales_count": s_row["cnt"] if s_row is not None else 0,
        }


def add_sample_sale() -> dict:
    init_db()
    with _connect() as conn:
        products = conn.execute("SELECT id, name FROM products ORDER BY id").fetchall()
        if not products:
            return {"message": "No products found in database."}

        s_row = conn.execute("SELECT COUNT(*) AS cnt FROM sales").fetchone()
        sales_count = s_row["cnt"] if s_row is not None else 0
        chosen = products[sales_count % len(products)]
        quantity = (sales_count % 4) + 1
        sale_date = "2026-11-23"

        conn.execute(
            "INSERT INTO sales (product_id, quantity, sale_date) VALUES (?, ?, ?)",
            (chosen["id"], quantity, sale_date),
        )
        conn.commit()
        return {
            "message": f"Added sale: {quantity} × {chosen['name']} on {sale_date}."
        }


def reset_db() -> dict:
    with _connect() as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS sales;
            DROP TABLE IF EXISTS products;
            """
        )
        conn.commit()
    init_db()
    return {"message": "Database reset to default sample products and sales."}