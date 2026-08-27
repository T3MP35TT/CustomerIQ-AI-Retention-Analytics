import sqlite3
from pathlib import Path
import pandas as pd


# ============================================================
# CUSTOMERIQ
# CHURN MODELING DATASET EXPORT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "customeriq.db"
)

SQL_FILE = (
    BASE_DIR
    / "sql"
    / "09_churn_dataset.sql"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "churn_modeling_dataset.csv"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONNECT TO DATABASE
# ============================================================

connection = sqlite3.connect(
    DATABASE_PATH
)


print("=" * 70)
print("CUSTOMERIQ — CHURN DATASET EXPORT")
print("=" * 70)

print(
    f"\nDatabase:\n{DATABASE_PATH}"
)

print(
    f"\nSQL File:\n{SQL_FILE}"
)


# ============================================================
# READ SQL FILE
# ============================================================

sql_script = SQL_FILE.read_text(
    encoding="utf-8"
)


# ============================================================
# SPLIT SQL STATEMENTS
# ============================================================

queries = [

    query.strip()

    for query in sql_script.split(";")

    if query.strip()
]


# ============================================================
# FIND FINAL DATASET QUERY
# ============================================================

data_query = None

for query in queries:

    try:

        cursor = connection.execute(
            query
        )

        if cursor.description:

            columns = [
                description[0]
                for description in cursor.description
            ]

            # The final modeling dataset must contain
            # customer_id and churned.
            if (
                "customer_id" in columns
                and "churned" in columns
            ):

                data_query = query

    except Exception as error:

        print(
            f"\nSkipping validation query: {error}"
        )


# ============================================================
# VALIDATE DATASET QUERY
# ============================================================

if data_query is None:

    connection.close()

    raise RuntimeError(
        "Could not find a SQL query containing "
        "'customer_id' and 'churned'."
    )


# ============================================================
# LOAD DATASET
# ============================================================

dataset = pd.read_sql_query(
    data_query,
    connection
)


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()


# ============================================================
# BASIC VALIDATION
# ============================================================

print(
    "\nDataset loaded successfully."
)

print(
    f"Rows: {len(dataset):,}"
)

print(
    f"Columns: {len(dataset.columns):,}"
)


# ============================================================
# TARGET VALIDATION
# ============================================================

if "churned" not in dataset.columns:

    raise RuntimeError(
        "Target column 'churned' is missing."
    )


target_values = (
    dataset["churned"]
    .dropna()
    .unique()
)


print(
    f"\nTarget values: {sorted(target_values.tolist())}"
)


if not set(target_values).issubset({0, 1}):

    raise ValueError(
        "Target column 'churned' contains values "
        "other than 0 and 1."
    )


# ============================================================
# CUSTOMER ID VALIDATION
# ============================================================

if "customer_id" not in dataset.columns:

    raise RuntimeError(
        "customer_id column is missing."
    )


duplicate_customer_ids = (
    dataset["customer_id"]
    .duplicated()
    .sum()
)


print(
    f"Duplicate customer IDs: "
    f"{duplicate_customer_ids:,}"
)


if duplicate_customer_ids > 0:

    raise ValueError(
        "Dataset contains duplicate customer IDs."
    )


# ============================================================
# MISSING VALUE CHECK
# ============================================================

missing_values = (
    dataset
    .isna()
    .sum()
    .sum()
)


print(
    f"Missing values: {missing_values:,}"
)


# ============================================================
# CHURN DISTRIBUTION
# ============================================================

churn_counts = (
    dataset["churned"]
    .value_counts()
    .sort_index()
)


print(
    "\nChurn distribution:"
)

for value, count in churn_counts.items():

    percentage = (
        count
        / len(dataset)
        * 100
    )

    label = (
        "Retained"
        if value == 0
        else "Churned"
    )

    print(
        f"{label}: "
        f"{count:,} "
        f"({percentage:.2f}%)"
    )


# ============================================================
# EXPORT CSV
# ============================================================

dataset.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "EXPORT COMPLETE"
)

print(
    "=" * 70
)

print(
    f"\nCSV:\n{OUTPUT_FILE}"
)

print(
    f"\nRows exported: {len(dataset):,}"
)

print(
    f"Columns exported: {len(dataset.columns):,}"
)

print(
    "\nCustomerIQ churn modeling dataset is ready."
)