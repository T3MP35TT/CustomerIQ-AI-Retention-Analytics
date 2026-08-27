import os
import requests

from customeriq_ai import load_customer_data
from prompts import SYSTEM_PROMPT

from query_engine import (
    get_top_predicted_churners,
    get_high_value_churners,
    get_high_probability_customers,
    get_rfm_churn_analysis,
    get_customer,
    get_business_summary,
    format_customer_records,
    format_rfm_analysis
)


# ============================================================
# CUSTOMERIQ — AI QUESTION ANSWERING
# ============================================================

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:4b"
)

OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"


def ask_ollama(prompt):
    """
    Send relevant CustomerIQ facts to Ollama.

    Works with:
    - Local Ollama during development
    - Ollama Cloud when deployed
    """

    payload = {
        "model": OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    if OLLAMA_API_KEY:
        headers["Authorization"] = (
            f"Bearer {OLLAMA_API_KEY}"
        )

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        headers=headers,
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"].strip()


# ============================================================
# QUESTION ROUTING
# ============================================================

def detect_question_type(question):
    """
    Determine which CustomerIQ analysis should be used.
    """

    q = question.lower()

    # Customer-specific lookup
    if "c0" in q and any(char.isdigit() for char in q):
        return "customer_lookup"

    # Top retention targets
    if (
        ("contact" in q or "target" in q or "priorit" in q)
        and ("customer" in q or "customers" in q)
    ):
        return "top_churners"

    # High-value customers
    if (
        "high-value" in q
        or "high value" in q
        or "valuable customers" in q
    ):
        return "high_value_churners"

    # Churn probability threshold
    if (
        "churn probability" in q
        or "probability above" in q
        or "probability over" in q
        or "probability greater" in q
    ):
        return "high_probability"

    # RFM analysis
    if (
        "rfm" in q
        or "segment" in q
    ):
        return "rfm_analysis"

    # Financial summary
    if (
        "revenue at risk" in q
        or "profit at risk" in q
        or "financial risk" in q
        or "financial exposure" in q
    ):
        return "business_summary"

    # General churn summary
    if (
        "churn" in q
        or "risk" in q
        or "retention" in q
    ):
        return "business_summary"

    return "business_summary"


# ============================================================
# BUILD DATA CONTEXT
# ============================================================

def get_relevant_context(df, question):
    """
    Run the appropriate Python analysis based on the question.
    """

    question_type = detect_question_type(question)


    # --------------------------------------------------------
    # TOP CHURNERS
    # --------------------------------------------------------

    if question_type == "top_churners":

        result = get_top_predicted_churners(df, 5)

        context = f"""
QUESTION TYPE: Top predicted churn customers

CUSTOMERIQ FACTS:

{format_customer_records(result)}
"""

        return context


    # --------------------------------------------------------
    # HIGH-VALUE CHURNERS
    # --------------------------------------------------------

    if question_type == "high_value_churners":

        result = get_high_value_churners(df, 5)

        context = f"""
QUESTION TYPE: High-value customers predicted to churn

CUSTOMERIQ FACTS:

{format_customer_records(result)}
"""

        return context


    # --------------------------------------------------------
    # HIGH CHURN PROBABILITY
    # --------------------------------------------------------

    if question_type == "high_probability":

        result = get_high_probability_customers(
            df,
            threshold=80,
            n=10
        )

        context = f"""
QUESTION TYPE: Customers with high churn probability

CUSTOMERIQ FACTS:

{format_customer_records(result)}
"""

        return context


    # --------------------------------------------------------
    # RFM ANALYSIS
    # --------------------------------------------------------

    if question_type == "rfm_analysis":

        result = get_rfm_churn_analysis(df)

        context = f"""
QUESTION TYPE: RFM churn analysis

CUSTOMERIQ FACTS:

{format_rfm_analysis(result)}
"""

        return context


    # --------------------------------------------------------
    # CUSTOMER LOOKUP
    # --------------------------------------------------------

    if question_type == "customer_lookup":

        import re

        match = re.search(
            r"(C\d+)",
            question.upper()
        )

        if match:

            customer_id = match.group(1)

            customer = get_customer(
                df,
                customer_id
            )

            if customer is not None:

                customer_data = customer.to_dict()

                relevant_fields = {
                    key: value
                    for key, value in customer_data.items()
                    if key in [
                        "customer_id",
                        "customer_segment",
                        "acquisition_channel",
                        "location",
                        "total_orders",
                        "total_revenue",
                        "gross_profit",
                        "recency_days",
                        "churn_probability_percentage",
                        "predicted_churn",
                        "rfm_segment",
                        "churn_risk",
                        "customer_value",
                        "expected_revenue_at_risk",
                        "expected_profit_at_risk",
                        "retention_score",
                        "retention_priority",
                        "retention_action"
                    ]
                }

                context = f"""
QUESTION TYPE: Individual customer lookup

CUSTOMERIQ FACTS:

{relevant_fields}
"""

                return context

        return "No matching customer was found."


    # --------------------------------------------------------
    # BUSINESS SUMMARY
    # --------------------------------------------------------

    summary = get_business_summary(df)

    context = f"""
QUESTION TYPE: CustomerIQ business summary

CUSTOMERIQ FACTS:

Total Customers:
{summary['total_customers']:,}

Predicted Churners:
{summary['predicted_churners']:,}

Predicted Churn Rate:
{summary['predicted_churn_rate']:.2f}%

Expected Revenue at Risk:
₹{summary['revenue_at_risk']:,.2f}

Expected Profit at Risk:
₹{summary['profit_at_risk']:,.2f}
"""

    return context


# ============================================================
# ANSWER QUESTION
# ============================================================

def answer_question(question):
    """
    Answer a CustomerIQ question using Python-generated facts.
    """

    df = load_customer_data()

    context = get_relevant_context(
        df,
        question
    )

    prompt = f"""
CUSTOMERIQ DATA:

{context}

BUSINESS QUESTION:

{question}

Answer the question using ONLY the CustomerIQ facts provided.

Keep the answer concise.

Prefer one or two sentences.

Do not explain your reasoning.

Do not invent information.

If the data does not answer the question, say so clearly.
"""

    return ask_ollama(prompt)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("CUSTOMERIQ — AI QUERY ENGINE TEST")
    print("=" * 60)

    questions = [
        "Which customers should I contact first?",
        "Which RFM segment has the highest predicted churn?",
        "How much revenue is at risk?",
        "Tell me about C00398",
        "Which high-value customers are predicted to churn?"
    ]

    for question in questions:

        print(f"\nQuestion: {question}")

        answer = answer_question(question)

        print(f"Answer: {answer}")

    print("\n" + "=" * 60)