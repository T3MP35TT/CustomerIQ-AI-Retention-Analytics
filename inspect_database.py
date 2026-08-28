import sqlite3
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = Path("database") / "customeriq.db"


# ============================================================
# VALIDATE DATABASE
# ============================================================

if not DB_PATH.exists():
    print("=" * 70)
    print("CUSTOMERIQ — DATABASE INSPECTION")
    print("=" * 70)
    print()
    print("ERROR: Database not found.")
    print(f"Expected path: {DB_PATH.resolve()}")
    print()
    raise SystemExit(1)


# ============================================================
# CONNECT
# ============================================================

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


print("=" * 70)
print("CUSTOMERIQ — DATABASE INSPECTION")
print("=" * 70)

print()
print(f"DATABASE:")
print(DB_PATH.resolve())


# ============================================================
# DATABASE OBJECTS
# ============================================================

cursor.execute("""
    SELECT
        name,
        type
    FROM sqlite_master
    WHERE type IN ('table', 'view')
      AND name NOT LIKE 'sqlite_%'
    ORDER BY type, name
""")

objects = cursor.fetchall()


print()
print("=" * 70)
print("DATABASE OBJECTS")
print("=" * 70)

if not objects:
    print("No tables or views found.")
else:
    for name, object_type in objects:
        print(f"{object_type.upper():6} | {name}")


# ============================================================
# TABLE / VIEW DETAILS
# ============================================================

for object_name, object_type in objects:

    print()
    print("=" * 70)
    print(f"{object_type.upper()}: {object_name}")
    print("=" * 70)

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    if object_type == "table":

        cursor.execute(
            f'PRAGMA table_info("{object_name}")'
        )

        columns = cursor.fetchall()

        print()
        print("COLUMNS")
        print("-" * 70)

        for column in columns:

            cid = column[0]
            name = column[1]
            data_type = column[2]
            not_null = column[3]
            default_value = column[4]
            primary_key = column[5]

            print(
                f"{cid:3} | "
                f"{name:40} | "
                f"{data_type:12} | "
                f"PK={primary_key} | "
                f"NOT NULL={not_null}"
            )

    # --------------------------------------------------------
    # Row count
    # --------------------------------------------------------

    try:

        cursor.execute(
            f'SELECT COUNT(*) FROM "{object_name}"'
        )

        row_count = cursor.fetchone()[0]

        print()
        print(f"ROW COUNT: {row_count:,}")

    except sqlite3.Error as error:

        print()
        print(f"ROW COUNT ERROR: {error}")

    # --------------------------------------------------------
    # Sample rows
    # --------------------------------------------------------

    try:

        cursor.execute(
            f'SELECT * FROM "{object_name}" LIMIT 5'
        )

        rows = cursor.fetchall()

        column_names = [
            description[0]
            for description in cursor.description
        ]

        print()
        print("SAMPLE ROWS")
        print("-" * 70)

        if not rows:

            print("No rows found.")

        else:

            print(" | ".join(column_names))

            print("-" * 70)

            for row in rows:

                print(
                    " | ".join(
                        str(value)
                        for value in row
                    )
                )

    except sqlite3.Error as error:

        print()
        print(f"SAMPLE DATA ERROR: {error}")


# ============================================================
# FOREIGN KEYS
# ============================================================

print()
print("=" * 70)
print("FOREIGN KEY RELATIONSHIPS")
print("=" * 70)

tables = [
    name
    for name, object_type in objects
    if object_type == "table"
]

found_relationship = False

for table_name in tables:

    try:

        cursor.execute(
            f'PRAGMA foreign_key_list("{table_name}")'
        )

        foreign_keys = cursor.fetchall()

        for fk in foreign_keys:

            found_relationship = True

            print(
                f"{table_name}.{fk[3]} "
                f"-> "
                f"{fk[2]}.{fk[4]}"
            )

    except sqlite3.Error:
        pass


if not found_relationship:
    print("No explicit foreign key relationships found.")


# ============================================================
# CLOSE
# ============================================================

connection.close()


print()
print("=" * 70)
print("DATABASE INSPECTION COMPLETE")
print("=" * 70)