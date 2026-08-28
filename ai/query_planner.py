"""
CustomerIQ — Dynamic Natural Language → SQL Query Planner

Flow:
    User question
        ↓
    Semantic layer
        ↓
    Ollama Cloud
        ↓
    SQL
        ↓
    SQL validation
        ↓
    query_executor.py
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path
from typing import Dict, Any

import requests
from dotenv import load_dotenv

from semantic_layer import get_semantic_context


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR.parent / ".env"

load_dotenv(
    dotenv_path=ENV_FILE
)


# ============================================================
# PATHS
# ============================================================

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
        BASE_DIR.parent
        / DB_PATH
    ).resolve()


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "https://ollama.com"
).rstrip("/")


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gpt-oss:20b-cloud"
)


OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY"
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = f"""
You are the SQL query planner for CustomerIQ.

Your job is to translate ANY natural-language business
question into ONE safe SQLite SELECT query.

You are NOT limited to predefined questions.

The user may ask questions that were never explicitly
included in the application.

============================================================
DATABASE
============================================================

SQLite database:

{DB_PATH}

============================================================
SEMANTIC LAYER
============================================================

{get_semantic_context()}

============================================================
SQL GENERATION RULES
============================================================

1. Generate SQLite-compatible SQL.

2. Return ONLY the SQL query.

3. Do NOT return JSON.

4. Do NOT use markdown code fences.

5. Do NOT explain the query.

6. Generate exactly ONE SQL statement.

7. The query MUST be read-only.

8. Only SELECT or WITH ... SELECT queries are allowed.

9. Never generate:

   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   CREATE
   REPLACE
   ATTACH
   DETACH
   PRAGMA
   VACUUM
   REINDEX
   ANALYZE
   BEGIN
   COMMIT
   ROLLBACK
   SAVEPOINT

10. Use ONLY tables and columns documented in the semantic layer.

11. Never invent columns.

12. Customers join transactions using:

    customers.customer_id =
    transactions.customer_id

13. Customers join interactions using:

    customers.customer_id =
    interactions.customer_id

14. Transactions join products using:

    transactions.product_id =
    products.product_id

15. Customers join customer_scores using:

    customers.customer_id =
    customer_scores.customer_id

16. Orders mean:

    COUNT(DISTINCT transactions.transaction_id)

17. Customers mean:

    COUNT(DISTINCT customer_id)

18. Net revenue means:

    SUM(transactions.revenue)

19. Gross revenue means:

    SUM(transactions.gross_revenue)

20. Product cost means:

    SUM(transactions.quantity * products.cost)

21. Gross profit means:

    SUM(transactions.revenue)
    -
    SUM(transactions.quantity * products.cost)

22. Use NULLIF whenever division could have a zero denominator.

23. For rankings:

    top / highest / most / best → DESC

    bottom / lowest / least / worst → ASC

24. If the user says "top customers" without a number,
    return the top 10.

25. If the user specifies a number such as top 5 or bottom 10,
    use that number as LIMIT.

26. When ranking customers, include customer_id.

27. When ranking a dimension such as customer segment,
    location, acquisition channel or product category,
    include the dimension and requested metric.

28. Do not confuse:

    customers.customer_segment

    with:

    customer_scores.rfm_segment

29. RFM segments are analytically derived and should not
    be assumed to exist in customers.

30. If the user asks for location, city, state or region,
    use customers.location unless another explicit geographic
    field exists.

31. If the user asks about churn, retention, churn risk,
    churn probability, revenue at risk, profit at risk or
    retention priority, use customer_scores when model
    outputs are requested.

32. customer_scores joins customers using customer_id.

33. churn_probability_percentage is already stored as a
    percentage.

    Example:

    80 = 80%

34. Never use future transactions as predictive features
    for churn analysis.

35. Churn target:

    No purchase during:

    2026-01-01 through 2026-03-31

36. Churn observation period:

    2024-01-06 through 2025-12-31

37. Churn modeling features must use observation-period data.

38. Future transactions are outcomes/targets, not predictive
    features.

39. If the user asks for an individual customer,
    filter using customer_id.

40. If the user asks for a comparison,
    return one row per comparison group.

41. If the user asks for a customer-level result,
    include customer_id.

42. Use explicit column selection.

43. Avoid SELECT * unless genuinely necessary.

44. Use readable aliases for calculated metrics.

45. Use GROUP BY for aggregated results.

46. Use HAVING for aggregate filters.

47. Use WHERE for row-level filters.

48. Use COALESCE when missing values logically represent zero.

49. Use explicit date filters when a time period is requested.

50. Answer the user's ACTUAL question.

Do not force the question into a predefined template.

============================================================
OUTPUT REQUIREMENT
============================================================

Return ONLY one valid SQLite SELECT query.

No JSON.

No markdown.

No explanation.

No commentary.
"""


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_configuration() -> None:

    if not OLLAMA_API_KEY:

        raise RuntimeError(
            "OLLAMA_API_KEY is not set.\n"
            f"Expected .env file at:\n{ENV_FILE}\n\n"
            "Make sure your .env contains:\n"
            "OLLAMA_API_KEY=your_ollama_cloud_api_key"
        )

    if not DB_PATH.exists():

        raise FileNotFoundError(
            "CustomerIQ database not found:\n"
            f"{DB_PATH}"
        )


# ============================================================
# OLLAMA REQUEST
# ============================================================

def call_ollama(
    question: str
) -> str:

    validate_configuration()

    url = (
        f"{OLLAMA_BASE_URL}/api/chat"
    )

    headers = {
        "Authorization":
            f"Bearer {OLLAMA_API_KEY}",

        "Content-Type":
            "application/json",
    }

    payload = {

        "model":
            OLLAMA_MODEL,

        "messages": [

            {
                "role": "system",

                "content":
                    SYSTEM_PROMPT,
            },

            {
                "role": "user",

                "content":
                    question,
            },
        ],

        "stream":
            False,
    }

    try:

        response = requests.post(

            url,

            headers=headers,

            json=payload,

            timeout=120,
        )

    except requests.RequestException as exc:

        raise RuntimeError(
            "Could not connect to Ollama Cloud:\n"
            f"{exc}"
        ) from exc


    if response.status_code != 200:

        raise RuntimeError(
            "Ollama request failed:\n"
            f"{response.status_code}\n"
            f"{response.text}"
        )


    try:

        data = response.json()

    except ValueError as exc:

        raise RuntimeError(
            "Ollama returned an invalid HTTP response:\n"
            f"{response.text}"
        ) from exc


    try:

        content = (
            data["message"]["content"]
        )

    except (
        KeyError,
        TypeError
    ) as exc:

        raise RuntimeError(
            "Unexpected Ollama response:\n"
            f"{data}"
        ) from exc


    if not content:

        raise RuntimeError(
            "Ollama returned empty content."
        )


    return content.strip()


# ============================================================
# SQL CLEANING
# ============================================================

def clean_sql(
    sql: str
) -> str:

    if not sql:

        raise ValueError(
            "Ollama returned empty SQL."
        )


    sql = sql.strip()


    # --------------------------------------------------------
    # Remove markdown fences
    # --------------------------------------------------------

    sql = re.sub(

        r"^```(?:sql)?\s*",

        "",

        sql,

        flags=re.IGNORECASE
    )


    sql = re.sub(

        r"\s*```$",

        "",

        sql
    )


    sql = sql.strip()


    # --------------------------------------------------------
    # Remove accidental prefixes
    # --------------------------------------------------------

    sql = re.sub(

        r"^(SQL\s*:)\s*",

        "",

        sql,

        flags=re.IGNORECASE
    )


    # --------------------------------------------------------
    # Find first SELECT / WITH
    # --------------------------------------------------------

    match = re.search(

        r"\b(select|with)\b",

        sql,

        flags=re.IGNORECASE
    )


    if match:

        sql = sql[
            match.start():
        ]


    # --------------------------------------------------------
    # Remove trailing semicolons
    # --------------------------------------------------------

    sql = sql.rstrip(";").strip()


    if not sql:

        raise ValueError(
            "SQL became empty after cleaning."
        )


    return sql + ";"


# ============================================================
# SQL SAFETY VALIDATION
# ============================================================

def assert_read_only(
    sql: str
) -> None:

    normalized = re.sub(

        r"\s+",

        " ",

        sql.strip().lower()
    )


    if not normalized:

        raise ValueError(
            "Generated SQL is empty."
        )


    statement = (
        sql
        .strip()
        .rstrip(";")
    )


    # --------------------------------------------------------
    # One statement only
    # --------------------------------------------------------

    if ";" in statement:

        raise ValueError(
            "Only one SQL statement is allowed."
        )


    # --------------------------------------------------------
    # Must begin with SELECT or WITH
    # --------------------------------------------------------

    if not re.match(

        r"^(select|with)\b",

        normalized
    ):

        raise ValueError(
            "Generated SQL is not read-only."
        )


    # --------------------------------------------------------
    # Forbidden operations
    # --------------------------------------------------------

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

        raise ValueError(
            "Generated SQL contains "
            "a forbidden SQL operation."
        )


# ============================================================
# DATABASE VALIDATION
# ============================================================

def validate_against_database(
    sql: str
) -> None:

    if not DB_PATH.exists():

        raise FileNotFoundError(

            "CustomerIQ database not found:\n"
            f"{DB_PATH}"
        )


    assert_read_only(
        sql
    )


    try:

        with sqlite3.connect(
            str(DB_PATH)
        ) as connection:

            connection.execute(
                "EXPLAIN QUERY PLAN "
                + sql
            ).fetchall()


    except sqlite3.Error as exc:

        raise ValueError(

            "Generated SQL failed SQLite validation:\n"
            f"{exc}"

        ) from exc


# ============================================================
# MAIN QUERY PLANNER
# ============================================================

def plan_query(
    question: str
) -> Dict[str, Any]:

    if not isinstance(
        question,
        str
    ):

        raise TypeError(
            "Question must be a string."
        )


    question = question.strip()


    if not question:

        raise ValueError(
            "Question cannot be empty."
        )


    raw_sql = call_ollama(
        question
    )


    sql = clean_sql(
        raw_sql
    )


    validate_against_database(
        sql
    )


    return {

        "sql":
            sql,

        "intent":
            question,

        "tables_used":
            [],

        "result_grain":
            "SQL result",

        "model":
            OLLAMA_MODEL,
    }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def get_sql(
    question: str
) -> str:

    return plan_query(
        question
    )["sql"]


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    import sys


    if len(sys.argv) > 1:

        question = " ".join(
            sys.argv[1:]
        )

    else:

        question = input(
            "CustomerIQ question: "
        ).strip()


    print(
        "\n" + "=" * 70
    )

    print(
        "CUSTOMERIQ — DYNAMIC SQL PLANNER"
    )

    print(
        "=" * 70
    )


    print(
        "\nQUESTION:"
    )

    print(
        question
    )


    print(
        "\nCONFIGURATION:"
    )

    print(
        f"Environment file: {ENV_FILE}"
    )

    print(
        f"Database: {DB_PATH}"
    )

    print(
        f"Ollama URL: {OLLAMA_BASE_URL}"
    )

    print(
        f"Model: {OLLAMA_MODEL}"
    )

    print(
        "Ollama API key: "
        + (
            "configured"
            if OLLAMA_API_KEY
            else "NOT CONFIGURED"
        )
    )


    try:

        result = plan_query(
            question
        )


        print(
            "\nSQL:"
        )

        print(
            result["sql"]
        )


        print(
            "\nSQL VALIDATION:"
        )

        print(
            "PASSED"
        )


    except Exception as exc:

        print(
            "\nERROR:"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        raise SystemExit(1)