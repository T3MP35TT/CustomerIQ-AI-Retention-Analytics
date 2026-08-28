"""
CustomerIQ — Synchronize Customer Scores

Loads the generated churn/model scoring dataset into the
CustomerIQ SQLite database as the customer_scores table.

Expected structure:

Project root/
│
├── database/
│   └── customeriq.db
│
├── data/
│   └── churn_scored_customers.csv
│
└── ai/
    └── sync_customer_scores.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

# sync_customer_scores.py is inside:
#
# CustomerIQ/
#     ai/
#         sync_customer_scores.py
#
# Therefore parent.parent = project root.

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "customeriq.db"
)

DATA_PATH = (
    BASE_DIR
    / "data"
    / "churn_scored_customers.csv"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = {

    "customer_id",

    "customer_value",

    "churn_probability_percentage",

    "predicted_churn",

    "churn_risk",

    "retention_priority",

    "expected_revenue_at_risk",

    "expected_profit_at_risk",

    "retention_score",

    "rfm_segment",
}


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "CUSTOMERIQ — CUSTOMER SCORES SYNC"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # DATABASE CHECK
    # --------------------------------------------------------

    print(
        f"\nDatabase:\n{DATABASE_PATH}"
    )

    if not DATABASE_PATH.exists():

        raise FileNotFoundError(
            "CustomerIQ database not found:\n"
            f"{DATABASE_PATH}"
        )


    # --------------------------------------------------------
    # CSV CHECK
    # --------------------------------------------------------

    print(
        f"\nScoring dataset:\n{DATA_PATH}"
    )

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            "Customer scoring dataset not found:\n"
            f"{DATA_PATH}"
        )


    # --------------------------------------------------------
    # LOAD CSV
    # --------------------------------------------------------

    print(
        "\nLoading customer scoring dataset..."
    )

    df = pd.read_csv(
        DATA_PATH
    )


    print(
        f"Rows loaded: {len(df):,}"
    )


    # --------------------------------------------------------
    # VALIDATE COLUMNS
    # --------------------------------------------------------

    missing_columns = (
        REQUIRED_COLUMNS
        - set(df.columns)
    )


    if missing_columns:

        raise ValueError(
            "Customer scoring dataset is missing "
            "required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in sorted(
                    missing_columns
                )
            )
        )


    # --------------------------------------------------------
    # SELECT MODEL COLUMNS
    # --------------------------------------------------------

    scores = df[
        [
            "customer_id",
            "customer_value",
            "churn_probability_percentage",
            "predicted_churn",
            "churn_risk",
            "retention_priority",
            "expected_revenue_at_risk",
            "expected_profit_at_risk",
            "retention_score",
            "rfm_segment",
        ]
    ].copy()


    # --------------------------------------------------------
    # CLEAN TYPES
    # --------------------------------------------------------

    numeric_columns = [

        "customer_value",

        "churn_probability_percentage",

        "predicted_churn",

        "expected_revenue_at_risk",

        "expected_profit_at_risk",

        "retention_score",
    ]


    for column in numeric_columns:

        scores[column] = pd.to_numeric(
            scores[column],
            errors="coerce"
        )


    scores["customer_id"] = (
        scores["customer_id"]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if scores["customer_id"].duplicated().any():

        duplicate_count = (
            scores["customer_id"]
            .duplicated()
            .sum()
        )

        raise ValueError(
            "Duplicate customer_id values found "
            f"in scoring dataset: {duplicate_count}"
        )


    if scores["customer_id"].isna().any():

        raise ValueError(
            "Scoring dataset contains missing customer_id values."
        )


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    print(
        "\nConnecting to CustomerIQ database..."
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )


    try:

        # ----------------------------------------------------
        # VERIFY CUSTOMERS TABLE
        # ----------------------------------------------------

        customers_exists = connection.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'customers'
            """
        ).fetchone()


        if not customers_exists:

            raise ValueError(
                "The customers table does not exist "
                "in the CustomerIQ database."
            )


        # ----------------------------------------------------
        # CREATE CUSTOMER_SCORES TABLE
        # ----------------------------------------------------

        connection.execute(
            """
            DROP TABLE IF EXISTS customer_scores
            """
        )


        connection.execute(
            """
            CREATE TABLE customer_scores (

                customer_id TEXT PRIMARY KEY,

                customer_value REAL,

                churn_probability_percentage REAL,

                predicted_churn INTEGER,

                churn_risk TEXT,

                retention_priority TEXT,

                expected_revenue_at_risk REAL,

                expected_profit_at_risk REAL,

                retention_score REAL,

                rfm_segment TEXT

            )
            """
        )


        # ----------------------------------------------------
        # INSERT SCORES
        # ----------------------------------------------------

        scores.to_sql(
            "customer_scores",
            connection,
            if_exists="append",
            index=False
        )


        connection.commit()


        # ----------------------------------------------------
        # VERIFY
        # ----------------------------------------------------

        table_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM customer_scores
            """
        ).fetchone()[0]


        print(
            "\nCustomer scores synchronized successfully."
        )

        print(
            f"Rows inserted: {table_count:,}"
        )


        # ----------------------------------------------------
        # SAMPLE
        # ----------------------------------------------------

        sample = connection.execute(
            """
            SELECT
                customer_id,
                customer_value,
                churn_probability_percentage,
                predicted_churn,
                churn_risk,
                retention_priority
            FROM customer_scores
            ORDER BY customer_id
            LIMIT 5
            """
        ).fetchall()


        print(
            "\nSample records:"
        )


        for row in sample:

            print(
                row
            )


    finally:

        connection.close()


    print(
        "\n" + "=" * 70
    )

    print(
        "CUSTOMERIQ — CUSTOMER SCORES SYNC COMPLETE"
    )

    print(
        "=" * 70
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()