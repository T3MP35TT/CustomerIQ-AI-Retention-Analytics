import sqlite3
from pathlib import Path


# ============================================================
# CUSTOMERIQ
# SQL QUERY RUNNER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "customeriq.db"
)

SQL_DIR = (
    BASE_DIR
    / "sql"
)


# ============================================================
# CONNECT
# ============================================================

connection = sqlite3.connect(
    DATABASE_PATH
)


print("=" * 70)
print("CUSTOMERIQ — SQL ANALYTICS")
print("=" * 70)

print(
    f"\nDatabase:\n{DATABASE_PATH}"
)


# ============================================================
# READ SQL FILE
# ============================================================

sql_file = (
    SQL_DIR
    / "10_export_churn_dataset.sql"
)


sql_script = sql_file.read_text(
    encoding="utf-8"
)


# ============================================================
# SPLIT QUERIES
# ============================================================

queries = [

    query.strip()

    for query in sql_script.split(";")

    if query.strip()
]


# ============================================================
# EXECUTE QUERIES
# ============================================================

for index, query in enumerate(
    queries,
    start=1
):

    print("\n" + "-" * 70)

    print(
        f"QUERY {index}"
    )

    print("-" * 70)

    try:

        cursor = connection.execute(
            query
        )

        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = cursor.fetchmany(10)

        print(
            "\nColumns:"
        )

        print(
            columns
        )

        print(
            f"\nShowing first "
            f"{len(rows)} rows:"
        )

        for row in rows:

            print(
                row
            )

    except Exception as error:

        print(
            f"ERROR: {error}"
        )


# ============================================================
# CLOSE
# ============================================================

connection.close()

print(
    "\n" + "=" * 70
)

print(
    "SQL ANALYSIS COMPLETE"
)

print(
    "=" * 70
)   