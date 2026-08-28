"""
CustomerIQ — SQL Query Executor

The planner creates SQL.
This file executes the SQL against customeriq.db.

The executor does NOT contain predefined business questions.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent

DEFAULT_DB_PATH = (
    BASE_DIR.parent
    / "database"
    / "customeriq.db"
)

DB_PATH = Path(
    os.getenv(
        "CUSTOMER_DB_PATH",
        str(DEFAULT_DB_PATH)
    )
).expanduser()

if not DB_PATH.is_absolute():

    DB_PATH = (
        BASE_DIR / DB_PATH
    ).resolve()


# ============================================================
# EXCEPTION
# ============================================================

class QueryExecutionError(
    Exception
):
    """Raised when CustomerIQ SQL cannot be executed safely."""


# ============================================================
# SQL VALIDATION
# ============================================================

def validate_sql(
    sql: str
) -> str:

    if not isinstance(
        sql,
        str
    ):

        raise QueryExecutionError(
            "SQL must be a string."
        )

    sql = sql.strip()

    if not sql:

        raise QueryExecutionError(
            "SQL query is empty."
        )

    normalized = re.sub(
        r"\s+",
        " ",
        sql.lower()
    )

    statement = (
        sql
        .rstrip(";")
        .strip()
    )

    # Only one statement.
    if ";" in statement:

        raise QueryExecutionError(
            "Only one SQL statement is allowed."
        )

    # Only SELECT / WITH.
    if not re.match(
        r"^(select|with)\b",
        normalized
    ):

        raise QueryExecutionError(
            "Only SELECT/WITH queries are allowed."
        )

    forbidden = re.compile(
        r"\b("
        r"insert|"
        r"update|"
        r"delete|"
        r"drop|"
        r"alter|"
        r"create|"
        r"replace|"
        r"attach|"
        r"detach|"
        r"pragma|"
        r"vacuum|"
        r"reindex|"
        r"analyze|"
        r"begin|"
        r"commit|"
        r"rollback|"
        r"savepoint"
        r")\b",
        re.IGNORECASE
    )

    if forbidden.search(
        normalized
    ):

        raise QueryExecutionError(
            "SQL contains a forbidden "
            "mutating or administrative operation."
        )

    return sql


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(
    sql: str,
    db_path: Optional[Path] = None
) -> pd.DataFrame:

    sql = validate_sql(
        sql
    )

    path = Path(
        db_path or DB_PATH
    )

    if not path.exists():

        raise QueryExecutionError(
            f"Database not found:\n{path}"
        )

    try:

        with sqlite3.connect(
            str(path)
        ) as conn:

            result = pd.read_sql_query(
                sql,
                conn
            )

        return result

    except sqlite3.Error as exc:

        raise QueryExecutionError(
            f"SQLite execution failed:\n{exc}"
        ) from exc

    except Exception as exc:

        raise QueryExecutionError(
            f"Query execution failed:\n{exc}"
        ) from exc


# ============================================================
# EXECUTE PLAN
# ============================================================

def execute_plan(
    plan: Dict[str, Any]
) -> Dict[str, Any]:

    if not isinstance(
        plan,
        dict
    ):

        raise QueryExecutionError(
            "Query plan must be a dictionary."
        )

    sql = plan.get(
        "sql"
    )

    if not sql:

        raise QueryExecutionError(
            "Query plan does not contain SQL."
        )

    result = execute_sql(
        sql
    )

    return {

        "sql": sql,

        "intent": plan.get(
            "intent"
        ),

        "tables_used": plan.get(
            "tables_used",
            []
        ),

        "result_grain": plan.get(
            "result_grain"
        ),

        "row_count": len(
            result
        ),

        "result": result
    }


# ============================================================
# BACKWARD-COMPATIBLE ENTRY POINT
# ============================================================

def execute_query(
    df_or_plan: Any = None,
    plan: Optional[
        Dict[str, Any]
    ] = None
) -> Dict[str, Any]:

    """
    New usage:

        execute_query(plan=plan)

    Also accepts:

        execute_query(plan)

    The old pandas DataFrame argument is ignored because
    CustomerIQ now executes generated SQL against SQLite.
    """

    if (
        plan is None
        and isinstance(
            df_or_plan,
            dict
        )
    ):

        plan = df_or_plan

    if plan is None:

        raise QueryExecutionError(
            "A SQL query plan is required."
        )

    return execute_plan(
        plan
    )


# ============================================================
# DISPLAY
# ============================================================

def display_result(
    execution_result: Dict[str, Any],
    max_rows: int = 50
) -> None:

    result = execution_result.get(
        "result"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "CUSTOMERIQ — QUERY RESULT"
    )

    print(
        "=" * 70
    )

    print(
        "\nINTENT:"
    )

    print(
        execution_result.get(
            "intent"
        )
    )

    print(
        "\nSQL:"
    )

    print(
        execution_result.get(
            "sql"
        )
    )

    print(
        "\nRESULT:"
    )

    if isinstance(
        result,
        pd.DataFrame
    ):

        if result.empty:

            print(
                "No matching records found."
            )

        else:

            print(
                result
                .head(max_rows)
                .to_string(
                    index=False
                )
            )

            if len(result) > max_rows:

                print(
                    f"\nShowing "
                    f"{max_rows:,} "
                    f"of "
                    f"{len(result):,} "
                    f"rows."
                )

    else:

        print(
            result
        )


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) < 2:

        print(
            'Usage: python query_executor.py '
            '"your question"'
        )

        raise SystemExit(1)

    question = " ".join(
        sys.argv[1:]
    )

    from query_planner import (
        plan_query
    )

    try:

        plan = plan_query(
            question
        )

        print(
            "\nQUERY PLAN:"
        )

        print(
            json.dumps(
                plan,
                indent=2
            )
        )

        execution = execute_plan(
            plan
        )

        display_result(
            execution
        )

    except Exception as exc:

        print(
            f"\nERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        raise SystemExit(1)