import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# CUSTOMERIQ
# SQLITE DATABASE SETUP
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CLEAN_DIR = BASE_DIR / "data" / "clean"

DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = (
    DATABASE_DIR
    / "customeriq.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

print("=" * 70)
print("CUSTOMERIQ — SQLITE DATABASE SETUP")
print("=" * 70)

print("\nConnecting to SQLite...")

connection = sqlite3.connect(
    DATABASE_PATH
)

print(
    f"✓ Database created at:\n"
    f"  {DATABASE_PATH}"
)


# ============================================================
# LOAD CLEAN DATA
# ============================================================

print("\nLoading cleaned datasets...")

customers = pd.read_csv(
    CLEAN_DIR / "customers_clean.csv"
)

transactions = pd.read_csv(
    CLEAN_DIR / "transactions_clean.csv"
)

products = pd.read_csv(
    CLEAN_DIR / "products_clean.csv"
)

interactions = pd.read_csv(
    CLEAN_DIR / "interactions_clean.csv"
)


print(
    f"✓ Customers: {len(customers):,}"
)

print(
    f"✓ Transactions: {len(transactions):,}"
)

print(
    f"✓ Products: {len(products):,}"
)

print(
    f"✓ Interactions: {len(interactions):,}"
)


# ============================================================
# CONVERT DATE COLUMNS
# ============================================================

customers["signup_date"] = pd.to_datetime(
    customers["signup_date"]
).dt.strftime("%Y-%m-%d")


transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
).dt.strftime("%Y-%m-%d")


products["launch_date"] = pd.to_datetime(
    products["launch_date"]
).dt.strftime("%Y-%m-%d")


interactions["interaction_timestamp"] = pd.to_datetime(
    interactions["interaction_timestamp"]
).dt.strftime(
    "%Y-%m-%d %H:%M:%S"
)


# ============================================================
# WRITE TABLES
# ============================================================

print("\nWriting tables to SQLite...")


customers.to_sql(
    "customers",
    connection,
    if_exists="replace",
    index=False
)

print("✓ customers table created")


transactions.to_sql(
    "transactions",
    connection,
    if_exists="replace",
    index=False
)

print("✓ transactions table created")


products.to_sql(
    "products",
    connection,
    if_exists="replace",
    index=False
)

print("✓ products table created")


interactions.to_sql(
    "interactions",
    connection,
    if_exists="replace",
    index=False
)

print("✓ interactions table created")


# ============================================================
# CREATE INDEXES
# ============================================================

print("\nCreating indexes...")


indexes = [

    """
    CREATE INDEX IF NOT EXISTS
    idx_customers_customer_id
    ON customers(customer_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_transactions_customer_id
    ON transactions(customer_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_transactions_product_id
    ON transactions(product_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_transactions_date
    ON transactions(transaction_date)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_products_product_id
    ON products(product_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_interactions_customer_id
    ON interactions(customer_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_interactions_product_id
    ON interactions(product_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_interactions_timestamp
    ON interactions(interaction_timestamp)
    """
]


for index_sql in indexes:

    connection.execute(
        index_sql
    )


connection.commit()

print(
    "✓ Indexes created"
)


# ============================================================
# VERIFY TABLES
# ============================================================

print("\n" + "=" * 70)
print("DATABASE VALIDATION")
print("=" * 70)


tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """,
    connection
)


print("\nTables:")

for table in tables["name"]:

    print(
        f"  ✓ {table}"
    )


# ============================================================
# RECORD COUNT VALIDATION
# ============================================================

print("\nRecord counts:")


for table in [
    "customers",
    "transactions",
    "products",
    "interactions"
]:

    result = pd.read_sql_query(
        f"""
        SELECT COUNT(*) AS row_count
        FROM {table}
        """,
        connection
    )

    count = result.iloc[0]["row_count"]

    print(
        f"  {table:<15} "
        f"{count:,}"
    )


# ============================================================
# BASIC JOIN VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("RELATIONSHIP VALIDATION")
print("=" * 70)


query = """

SELECT COUNT(*) AS invalid_records

FROM transactions t

LEFT JOIN customers c
    ON t.customer_id = c.customer_id

WHERE c.customer_id IS NULL

"""


result = pd.read_sql_query(
    query,
    connection
)


print(
    "Transactions → Customers:",
    result.iloc[0]["invalid_records"],
    "invalid"
)


query = """

SELECT COUNT(*) AS invalid_records

FROM transactions t

LEFT JOIN products p
    ON t.product_id = p.product_id

WHERE p.product_id IS NULL

"""


result = pd.read_sql_query(
    query,
    connection
)


print(
    "Transactions → Products:",
    result.iloc[0]["invalid_records"],
    "invalid"
)


query = """

SELECT COUNT(*) AS invalid_records

FROM interactions i

LEFT JOIN customers c
    ON i.customer_id = c.customer_id

WHERE c.customer_id IS NULL

"""


result = pd.read_sql_query(
    query,
    connection
)


print(
    "Interactions → Customers:",
    result.iloc[0]["invalid_records"],
    "invalid"
)


# ============================================================
# CLOSE CONNECTION
# ============================================================

connection.close()


print("\n" + "=" * 70)
print("DATABASE SETUP COMPLETE")
print("=" * 70)

print(
    f"\nSQLite database:\n"
    f"{DATABASE_PATH}"
)