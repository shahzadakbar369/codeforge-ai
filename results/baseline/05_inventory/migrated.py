import sqlite3
import threading

# Thread-local storage for the in-memory database connection
_db_lock = threading.Lock()
_db_conn = None

def _get_db():
    global _db_conn
    if _db_conn is None:
        _db_conn = sqlite3.connect(":memory:")
        _db_conn.execute("PRAGMA foreign_keys = ON;")
        _db_conn.row_factory = sqlite3.Row
        _seed_db(_db_conn)
    return _db_conn

def _seed_db(db):
    db.executescript(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        );
        """
    )
    rows = [
        (1, "Widget", "tools", 2.5, 100),
        (2, "Gadget", "tools", 10.0, 15),
        (3, "Gizmo", "toys", 7.25, 0),
        (4, "Doohickey", "toys", 3.99, 42),
        (5, "Thingamajig", "misc", 120.0, 3),
        (6, "Widget Pro", "tools", 19.99, 8),
    ]
    stmt = db.executemany(
        "INSERT INTO products (id, name, category, price, stock) VALUES (?, ?, ?, ?, ?)",
        rows,
    )

# Public API

def reset_inventory():
    db = _get_db()
    db.execute("DELETE FROM products")
    db.execute("DROP TABLE products")
    _seed_db(db)
    return count_products()

def count_products():
    row = _get_db().execute("SELECT COUNT(*) AS c FROM products").fetchone()
    return int(row["c"])

def get_product(id):
    stmt = _get_db().execute("SELECT * FROM products WHERE id = ?", (id,))
    row = stmt.fetchone()
    if row is None:
        raise ValueError(f"Product not found: {id}")
    return dict(row)

# Vulnerable function intentionally kept as is
def find_products_by_name(name):
    sql = f"SELECT id, name FROM products WHERE name LIKE '%{name}%' ORDER BY id"
    rows = _get_db().execute(sql).fetchall()
    return [row["name"] for row in rows]


def products_in_category(category):
    rows = _get_db().execute("SELECT name FROM products WHERE category = ? ORDER BY id", (category,)).fetchall()
    return [row["name"] for row in rows]


def add_stock(id, qty):
    if qty <= 0:
        raise ValueError("Quantity must be positive")
    get_product(id)  # validate existence
    _get_db().execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty, id))
    _get_db().commit()
    product = get_product(id)
    return product["stock"]


def remove_stock(id, qty):
    if qty <= 0:
        raise ValueError("Quantity must be positive")
    product = get_product(id)
    if product["stock"] < qty:
        raise RuntimeError(f"Not enough stock for {product['name']}")
    _get_db().execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, id))
    _get_db().commit()
    product = get_product(id)
    return product["stock"]


def low_stock(threshold=10):
    rows = _get_db().execute("SELECT name FROM products WHERE stock < ? ORDER BY stock, id", (threshold,)).fetchall()
    return [row["name"] for row in rows]


def inventory_value(category=None):
    if category is None:
        row = _get_db().execute("SELECT SUM(price * stock) AS v FROM products").fetchone()
    else:
        row = _get_db().execute("SELECT SUM(price * stock) AS v FROM products WHERE category = ?", (category,)).fetchone()
    value = row["v"] if row["v"] is not None else 0.0
    return round(float(value), 2)


def apply_discount(category, percent):
    if percent < 0 or percent > 100:
        raise ValueError("Percent must be between 0 and 100")
    cur = _get_db().execute(
        "UPDATE products SET price = ROUND(price * (1 - ? / 100.0), 2) WHERE category = ?",
        (percent, category),
    )
    _get_db().commit()
    return cur.rowcount


def category_summary():
    rows = _get_db().execute(
        "SELECT category, COUNT(*) AS items, SUM(stock) AS units FROM products GROUP BY category ORDER BY category"
    ).fetchall()
    out = {}
    for r in rows:
        out[r["category"]] = {"items": int(r["items"]), "units": int(r["units"])}
    return out
