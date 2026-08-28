"""
CustomerIQ — End-to-End Natural Language Q&A

Flow
----
User question
    ↓
query_planner.py
    ↓
Ollama Cloud generates safe SQLite SQL
    ↓
SQLite database executes SQL
    ↓
Verified result
    ↓
Ollama Cloud generates business-friendly answer

Important
---------
- SQL generation is handled by query_planner.py
- SQL execution is handled directly against customeriq.db
- Future churn outcomes are never used as predictive features
- Ollama Cloud is accessed through HTTPS
- No local Ollama server is required
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from query_planner import (
    plan_query,
    DB_PATH,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_API_KEY,
)


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent

ENV_FILE = (
    BASE_DIR.parent
    / ".env"
)

load_dotenv(
    dotenv_path=ENV_FILE
)


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

# Reload directly from environment so this module remains
# compatible with the Render deployment environment.

OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    OLLAMA_MODEL
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    OLLAMA_BASE_URL
).rstrip("/")


# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

def validate_configuration() -> None:

    if not OLLAMA_API_KEY:

        raise RuntimeError(
            "OLLAMA_API_KEY is not configured.\n"
            f"Expected environment file:\n{ENV_FILE}"
        )

    if not DB_PATH.exists():

        raise FileNotFoundError(
            "CustomerIQ database was not found:\n"
            f"{DB_PATH}"
        )


# ============================================================
# RESULT SERIALIZATION
# ============================================================

def serialize_result(
    result: Any
) -> Any:

    # Pandas DataFrame
    if hasattr(
        result,
        "to_dict"
    ):

        try:

            return result.to_dict(
                orient="records"
            )

        except TypeError:

            return result.to_dict()


    # NumPy scalar
    if hasattr(
        result,
        "item"
    ):

        try:

            return result.item()

        except Exception:

            pass


    return result


# ============================================================
# RESULT EMPTY CHECK
# ============================================================

def result_is_empty(
    result: Any
) -> bool:

    if result is None:

        return True


    if hasattr(
        result,
        "empty"
    ):

        return bool(
            result.empty
        )


    if isinstance(
        result,
        (list, tuple, dict)
    ):

        return len(result) == 0


    return False


# ============================================================
# FORMAT VERIFIED RESULT
# ============================================================

def format_result_for_llm(
    result: Any
) -> str:

    serialized = serialize_result(
        result
    )


    return json.dumps(
        serialized,
        indent=2,
        ensure_ascii=False,
        default=str
    )


# ============================================================
# METRIC DISPLAY NAME
# ============================================================

def metric_display_name(
    metric: str | None
) -> str:

    names = {

        "expected_revenue_at_risk":
            "expected revenue at risk",

        "expected_profit_at_risk":
            "expected profit at risk",

        "customer_value":
            "customer value",

        "churn_probability_percentage":
            "churn probability",

        "total_revenue":
            "total revenue",

        "net_revenue":
            "net revenue",

        "gross_profit":
            "gross profit",

        "total_orders":
            "orders",

        "total_units":
            "units",

        "total_interactions":
            "interactions",

        "views":
            "views",

        "clicks":
            "clicks",

        "add_to_carts":
            "add-to-carts",

        "email_opens":
            "email opens",

        "retention_score":
            "retention score",

        "predicted_churn":
            "predicted churn",

    }


    return names.get(
        metric,
        metric or "value"
    )


# ============================================================
# ANSWER SYSTEM PROMPT
# ============================================================

ANSWER_SYSTEM_PROMPT = """
You are the CustomerIQ business intelligence assistant.

Your job is to explain verified analytical results to
business users in clear, concise language.

The SQL query has already been generated and executed.

The provided result is the SOURCE OF TRUTH.

You MUST use only the verified result.

Never invent data.

Never invent customers.

Never invent metrics.

Never change numerical values.

Never calculate a different result when the verified
result already contains the requested answer.

Never claim that data exists when it does not appear
in the verified result.

If the result is a ranking, preserve its order.

If the result contains customer records, include the
customer ID and the relevant requested metric.

Use ₹ for Indian currency.

Format percentages to two decimal places.

Round currency to the nearest rupee unless precision
is explicitly useful.

For multiple records, use a numbered list when useful.

For comparisons, explicitly mention the compared groups.

Keep normal answers concise.

Normally answer in 1–4 sentences.

For requested lists, provide the list clearly.

Do not mention:

- query planner
- query executor
- Python
- SQLite
- Ollama
- internal prompts
- internal reasoning

Do not expose JSON unless the user explicitly asks for it.

Never provide chain-of-thought.

Answer the user's actual question directly.
"""


# ============================================================
# CALL OLLAMA CLOUD
# ============================================================

def call_ollama_answer(
    prompt: str
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
                "role":
                    "system",

                "content":
                    ANSWER_SYSTEM_PROMPT,
            },

            {
                "role":
                    "user",

                "content":
                    prompt,
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
            "Could not connect to Ollama Cloud "
            "while generating the answer:\n"
            f"{exc}"
        ) from exc


    if response.status_code != 200:

        raise RuntimeError(
            "Ollama Cloud answer request failed:\n"
            f"HTTP {response.status_code}\n"
            f"{response.text}"
        )


    try:

        data = response.json()

    except ValueError as exc:

        raise RuntimeError(
            "Ollama Cloud returned an invalid "
            "HTTP response:\n"
            f"{response.text}"
        ) from exc


    try:

        answer = (
            data["message"]["content"]
        )

    except (
        KeyError,
        TypeError
    ) as exc:

        raise RuntimeError(
            "Unexpected Ollama Cloud response:\n"
            f"{data}"
        ) from exc


    answer = answer.strip()


    if not answer:

        raise RuntimeError(
            "Ollama Cloud returned an empty answer."
        )


    return answer


# ============================================================
# GENERATE BUSINESS ANSWER
# ============================================================

def generate_answer(
    question: str,
    plan: dict,
    result: Any
) -> str:

    if result_is_empty(
        result
    ):

        return (
            "No matching CustomerIQ records "
            "were found."
        )


    result_text = (
        format_result_for_llm(
            result
        )
    )


    plan_text = json.dumps(
        plan,
        indent=2,
        ensure_ascii=False
    )


    metric_name = (
        metric_display_name(
            plan.get("metric")
        )
    )


    prompt = f"""
CUSTOMERIQ VERIFIED ANALYTICS RESULT

The following result was calculated directly from
the CustomerIQ database.

The verified result is the source of truth.

============================================================
USER QUESTION
============================================================

{question}


============================================================
GENERATED SQL
============================================================

{plan.get("sql", "")}


============================================================
VERIFIED RESULT
============================================================

{result_text}


============================================================
REQUESTED METRIC
============================================================

{metric_name}


============================================================
ANSWER REQUIREMENTS
============================================================

Answer the user's question directly.

Use ONLY the verified result.

Never invent information.

Never modify numerical values.

Never recalculate the ranking differently.

Preserve the order of the verified result.

If multiple customers are returned, clearly show:

Customer ID — requested metric

If the question asks for a ranking, clearly identify
the highest/lowest result as appropriate.

If the question asks for a comparison, explicitly
mention each comparison group.

If the result contains revenue, use ₹.

If the result contains percentages, format them
to two decimal places.

Keep the answer concise and business-friendly.
"""


    return call_ollama_answer(
        prompt
    )


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(
    sql: str
) -> list[dict]:

    import sqlite3


    validate_configuration()


    with sqlite3.connect(
        str(DB_PATH)
    ) as connection:

        connection.row_factory = (
            sqlite3.Row
        )


        cursor = connection.execute(
            sql
        )


        rows = cursor.fetchall()


        return [

            dict(row)

            for row in rows
        ]


# ============================================================
# END-TO-END QUESTION ANSWER
# ============================================================

def answer_question(
    question: str
) -> str:

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


    # --------------------------------------------------------
    # 1. Generate safe SQL
    # --------------------------------------------------------

    plan = plan_query(
        question
    )


    # --------------------------------------------------------
    # 2. Execute verified SQL against SQLite
    # --------------------------------------------------------

    result = execute_sql(
        plan["sql"]
    )


    # --------------------------------------------------------
    # 3. Generate business-friendly answer
    # --------------------------------------------------------

    return generate_answer(
        question,
        plan,
        result
    )


# ============================================================
# TEST QUESTIONS
# ============================================================

TEST_QUESTIONS = [

    "Which customer segments generate the most revenue?",

    "Which acquisition channel generates the most revenue?",

    "Which location has the highest revenue?",

    "Which customer segment has the most customers?",

    "Give me the top 10 customers by revenue",

    "Which customers have the highest expected revenue at risk?",

    "How much revenue is at risk?",

    "How many customers have churn probability above 80%?",

    "What percentage of customers are predicted to churn?",

    "Which RFM segment has the highest revenue at risk?",

    "Which RFM segment has the highest churn risk?",

    "Tell me about C00398",

    "What is the churn probability of C00398?",

    "How much revenue is C00398 putting at risk?",

]


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    import sys


    print(
        "\n" + "=" * 70
    )

    print(
        "CUSTOMERIQ — END-TO-END NLP TEST"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # Run one supplied question
    # --------------------------------------------------------

    if len(sys.argv) > 1:

        question = " ".join(
            sys.argv[1:]
        )


        print(
            "\nQUESTION:"
        )

        print(
            question
        )


        try:

            answer = answer_question(
                question
            )


            print(
                "\nANSWER:"
            )

            print(
                answer
            )


        except Exception as exc:

            print(
                "\nERROR:"
            )

            print(
                f"{type(exc).__name__}: {exc}"
            )

            raise SystemExit(1)


    # --------------------------------------------------------
    # Otherwise run the test suite
    # --------------------------------------------------------

    else:

        for question in TEST_QUESTIONS:

            print(
                "\n" + "-" * 70
            )

            print(
                "QUESTION:"
            )

            print(
                question
            )


            try:

                answer = answer_question(
                    question
                )


                print(
                    "\nANSWER:"
                )

                print(
                    answer
                )


            except Exception as exc:

                print(
                    "\nERROR:"
                )

                print(
                    f"{type(exc).__name__}: {exc}"
                )


    print(
        "\n" + "=" * 70
    )

    print(
        "CUSTOMERIQ — END-TO-END TEST COMPLETE"
    )

    print(
        "=" * 70
    )