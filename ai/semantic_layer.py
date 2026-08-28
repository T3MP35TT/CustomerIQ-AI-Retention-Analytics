"""
CustomerIQ — Semantic Layer

Purpose
-------
Provides the LLM with a controlled description of the CustomerIQ
SQLite database and the business definitions used throughout the
project.

The semantic layer is NOT a list of predefined questions.

It allows the system to interpret arbitrary business questions,
identify the correct tables/columns/metrics, and generate safe
SQLite SQL dynamically.

Database
--------
    database/customeriq.db

Core tables
-----------
    customers
    transactions
    interactions
    products
    customer_scores

Important
---------
    - Query SQLite for factual answers.
    - Never invent columns.
    - Use the documented relationships.
    - Never use future churn outcomes as predictive features.
    - customer_scores contains model outputs and risk estimates.
"""

from __future__ import annotations

from textwrap import dedent


# ============================================================
# DATABASE DESCRIPTION
# ============================================================

DATABASE_DESCRIPTION = dedent(
    """
    CustomerIQ is a customer intelligence and retention analytics
    database designed to answer business questions about:

      - customers
      - purchasing behavior
      - revenue
      - profitability
      - customer engagement
      - acquisition channels
      - locations
      - product performance
      - RFM segmentation
      - churn
      - retention risk
      - revenue at risk
      - profit at risk

    The LLM should translate natural-language business questions
    into SQLite SELECT queries.

    Questions are NOT restricted to predefined examples.

    Core relationships:

      customers.customer_id = transactions.customer_id
      customers.customer_id = interactions.customer_id
      products.product_id = transactions.product_id
      customers.customer_id = customer_scores.customer_id

    There are no explicit foreign-key constraints required for
    the semantic layer. The relationships above are the logical
    relationships used for analysis.

    Core analytical concepts:

      - Revenue:
            transactions.revenue

      - Gross revenue:
            transactions.gross_revenue

      - Product cost:
            transactions.quantity * products.cost

      - Gross profit:
            transactions.revenue
            - transactions.quantity * products.cost

      - Customer revenue:
            SUM(transactions.revenue)

      - Customer value:
            customer_scores.customer_value
            This is the customer value metric produced by the
            CustomerIQ scoring layer.

      - Orders:
            COUNT(DISTINCT transactions.transaction_id)

      - Customers:
            COUNT(DISTINCT customer_id)

      - Churn:
            No purchase during the prediction window
            2026-01-01 through 2026-03-31,
            among customers who purchased during the observation
            period.

      - Historical churn observation period:
            2024-01-06 through 2025-12-31

      - Churn prediction window:
            2026-01-01 through 2026-03-31

      - Model outputs:
            customer_scores contains customer-level churn
            probabilities, predicted churn, risk classification,
            retention priority and financial risk estimates.
    """
).strip()


# ============================================================
# TABLES AND COLUMNS
# ============================================================

TABLES = {

    # --------------------------------------------------------
    # CUSTOMERS
    # --------------------------------------------------------

    "customers": {

        "description":
            "Customer profile and acquisition information.",

        "columns": {

            "customer_id":
                "TEXT — unique customer identifier",

            "signup_date":
                "TEXT — customer signup date, YYYY-MM-DD",

            "customer_segment":
                "TEXT — original customer segment such as low, medium, high",

            "location":
                "TEXT — customer city/location",

            "acquisition_channel":
                "TEXT — customer acquisition source/channel",

            "age":
                "INTEGER — customer age",

            "gender":
                "TEXT — customer gender",

            "signup_year":
                "INTEGER — year of customer signup",

            "signup_month":
                "TEXT — signup month in YYYY-MM format",
        },
    },


    # --------------------------------------------------------
    # TRANSACTIONS
    # --------------------------------------------------------

    "transactions": {

        "description":
            "Customer purchase transaction records.",

        "columns": {

            "transaction_id":
                "INTEGER — unique transaction/order identifier",

            "customer_id":
                "TEXT — logical FK to customers.customer_id",

            "product_id":
                "TEXT — logical FK to products.product_id",

            "transaction_date":
                "TEXT — transaction date, YYYY-MM-DD",

            "quantity":
                "INTEGER — units purchased in the transaction",

            "price":
                "INTEGER — unit/list price recorded on transaction",

            "discount":
                "REAL — discount stored as decimal, e.g. 0.10 = 10%",

            "launch_date":
                "TEXT — product launch date associated with transaction",

            "transaction_before_product_launch":
                "INTEGER — validation flag, 1/0",

            "gross_revenue":
                "INTEGER — quantity multiplied by transaction price",

            "discount_amount":
                "REAL — discount amount",

            "revenue":
                "REAL — gross revenue after discount",

            "transaction_year":
                "INTEGER — transaction year",

            "transaction_month":
                "TEXT — transaction month in YYYY-MM format",
        },
    },


    # --------------------------------------------------------
    # INTERACTIONS
    # --------------------------------------------------------

    "interactions": {

        "description":
            "Customer digital and engagement interactions.",

        "columns": {

            "interaction_id":
                "INTEGER — unique interaction identifier",

            "customer_id":
                "TEXT — logical FK to customers.customer_id",

            "interaction_type":
                (
                    "TEXT — interaction type. Examples include "
                    "view, click, add_to_cart and email_open"
                ),

            "product_id":
                "TEXT — optional product involved in interaction",

            "interaction_timestamp":
                "TEXT — interaction timestamp",

            "channel":
                "TEXT — interaction channel such as web/app",

            "interaction_date":
                "TEXT — interaction date, YYYY-MM-DD",

            "interaction_hour":
                "INTEGER — hour of interaction",

            "interaction_month":
                "TEXT — interaction month in YYYY-MM format",
        },
    },


    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    "products": {

        "description":
            "Product catalogue, pricing and cost information.",

        "columns": {

            "product_id":
                "TEXT — unique product identifier",

            "category":
                "TEXT — product category",

            "price":
                "INTEGER — product price",

            "cost":
                "REAL — product cost",

            "launch_date":
                "TEXT — product launch date, YYYY-MM-DD",

            "gross_margin":
                "REAL — product price minus product cost",

            "margin_percentage":
                "REAL — product margin percentage",
        },
    },


    # --------------------------------------------------------
    # CUSTOMER SCORES
    # --------------------------------------------------------

    "customer_scores": {

        "description": (
            "Customer-level churn model predictions, retention "
            "scores and financial risk estimates."
        ),

        "columns": {

            "customer_id":
                (
                    "TEXT — logical FK to customers.customer_id"
                ),

            "customer_value":
                (
                    "REAL — customer value metric used by "
                    "the scoring/model layer"
                ),

            "churn_probability_percentage":
                (
                    "REAL — predicted probability of churn "
                    "expressed as a percentage"
                ),

            "predicted_churn":
                (
                    "INTEGER — predicted churn outcome, 1/0"
                ),

            "churn_risk":
                (
                    "TEXT — churn risk classification such as "
                    "Low Risk, Medium Risk or High Risk"
                ),

            "retention_priority":
                (
                    "TEXT — retention priority classification "
                    "such as Low, Medium, High or Monitor"
                ),

            "expected_revenue_at_risk":
                (
                    "REAL — expected revenue exposed to churn risk"
                ),

            "expected_profit_at_risk":
                (
                    "REAL — expected profit exposed to churn risk"
                ),

            "retention_score":
                (
                    "REAL — customer retention score"
                ),

            "rfm_segment":
                (
                    "TEXT — analytically derived RFM customer segment"
                ),
        },
    },
}


# ============================================================
# LOGICAL RELATIONSHIPS
# ============================================================

RELATIONSHIPS = [

    {
        "left":
            "customers.customer_id",

        "right":
            "transactions.customer_id",

        "type":
            "one-to-many",

        "meaning":
            "A customer can have many transactions.",
    },


    {
        "left":
            "customers.customer_id",

        "right":
            "interactions.customer_id",

        "type":
            "one-to-many",

        "meaning":
            "A customer can have many interactions.",
    },


    {
        "left":
            "products.product_id",

        "right":
            "transactions.product_id",

        "type":
            "one-to-many",

        "meaning":
            "A product can appear in many transactions.",
    },


    {
        "left":
            "customers.customer_id",

        "right":
            "customer_scores.customer_id",

        "type":
            "one-to-one",

        "meaning":
            (
                "A customer has one current churn/model "
                "scoring record."
            ),
    },
]


# ============================================================
# METRIC DEFINITIONS
# ============================================================

METRICS = {

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    "total_revenue": {

        "definition":
            "SUM(transactions.revenue)",

        "meaning":
            "Net revenue after transaction discount.",

        "aliases": [
            "revenue",
            "sales",
            "sales revenue",
            "money made",
            "income from sales",
            "net sales",
        ],
    },


    "gross_revenue": {

        "definition":
            "SUM(transactions.gross_revenue)",

        "meaning":
            "Revenue before transaction discount.",

        "aliases": [
            "gross sales",
            "gross sales revenue",
            "sales before discount",
        ],
    },


    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    "orders": {

        "definition":
            "COUNT(DISTINCT transactions.transaction_id)",

        "meaning":
            "Number of distinct transactions/orders.",

        "aliases": [
            "orders",
            "purchases",
            "transactions",
            "order count",
            "number of orders",
        ],
    },


    # --------------------------------------------------------
    # CUSTOMERS
    # --------------------------------------------------------

    "customers": {

        "definition":
            "COUNT(DISTINCT customer_id)",

        "meaning":
            "Number of distinct customers in the relevant scope.",

        "aliases": [
            "customers",
            "customer count",
            "number of customers",
            "customer population",
        ],
    },


    # --------------------------------------------------------
    # UNITS
    # --------------------------------------------------------

    "units_sold": {

        "definition":
            "SUM(transactions.quantity)",

        "meaning":
            "Total units purchased.",

        "aliases": [
            "units",
            "quantity sold",
            "items sold",
            "units sold",
        ],
    },


    # --------------------------------------------------------
    # AOV
    # --------------------------------------------------------

    "average_order_value": {

        "definition":
            (
                "SUM(transactions.revenue) / "
                "COUNT(DISTINCT transactions.transaction_id)"
            ),

        "meaning":
            "Average net revenue per order.",

        "aliases": [
            "AOV",
            "average order value",
            "average order",
            "average purchase value",
        ],
    },


    # --------------------------------------------------------
    # PROFIT
    # --------------------------------------------------------

    "gross_profit": {

        "definition":
            (
                "SUM(transactions.revenue) - "
                "SUM(transactions.quantity * products.cost)"
            ),

        "meaning":
            "Net revenue less product cost.",

        "aliases": [
            "profit",
            "gross profit",
            "profitability",
            "gross earnings",
        ],
    },


    # --------------------------------------------------------
    # MARGIN
    # --------------------------------------------------------

    "gross_margin_percentage": {

        "definition":
            (
                "(SUM(transactions.revenue) - "
                "SUM(transactions.quantity * products.cost)) "
                "/ NULLIF(SUM(transactions.revenue), 0) * 100"
            ),

        "meaning":
            "Gross profit as a percentage of net revenue.",

        "aliases": [
            "gross margin",
            "margin percentage",
            "profit margin",
            "margin",
        ],
    },


    # --------------------------------------------------------
    # REVENUE PER CUSTOMER
    # --------------------------------------------------------

    "revenue_per_customer": {

        "definition":
            (
                "SUM(transactions.revenue) / "
                "NULLIF("
                "COUNT(DISTINCT transactions.customer_id), "
                "0)"
            ),

        "meaning":
            (
                "Revenue generated per purchasing customer "
                "in the selected scope."
            ),

        "aliases": [
            "revenue per customer",
            "RPC",
            "average customer revenue",
        ],
    },


    # --------------------------------------------------------
    # PROFIT PER CUSTOMER
    # --------------------------------------------------------

    "profit_per_customer": {

        "definition":
            (
                "(SUM(transactions.revenue) - "
                "SUM(transactions.quantity * products.cost)) "
                "/ NULLIF("
                "COUNT(DISTINCT transactions.customer_id), "
                "0)"
            ),

        "meaning":
            (
                "Gross profit generated per purchasing "
                "customer in the selected scope."
            ),

        "aliases": [
            "profit per customer",
            "average customer profit",
        ],
    },


    # --------------------------------------------------------
    # INTERACTIONS
    # --------------------------------------------------------

    "total_interactions": {

        "definition":
            "COUNT(interactions.interaction_id)",

        "meaning":
            "Total customer engagement interactions.",

        "aliases": [
            "interactions",
            "engagements",
            "activity",
            "engagement count",
            "engagement activity",
        ],
    },


    "views": {

        "definition":
            (
                "SUM("
                "CASE "
                "WHEN interactions.interaction_type = 'view' "
                "THEN 1 ELSE 0 "
                "END"
                ")"
            ),

        "meaning":
            "Product/content views.",

        "aliases": [
            "views",
            "view count",
            "product views",
        ],
    },


    "clicks": {

        "definition":
            (
                "SUM("
                "CASE "
                "WHEN interactions.interaction_type = 'click' "
                "THEN 1 ELSE 0 "
                "END"
                ")"
            ),

        "meaning":
            "Customer clicks.",

        "aliases": [
            "clicks",
            "click count",
        ],
    },


    "add_to_carts": {

        "definition":
            (
                "SUM("
                "CASE "
                "WHEN interactions.interaction_type = 'add_to_cart' "
                "THEN 1 ELSE 0 "
                "END"
                ")"
            ),

        "meaning":
            "Add-to-cart interactions.",

        "aliases": [
            "add to carts",
            "carts",
            "add to cart",
            "cart additions",
        ],
    },


    "email_opens": {

        "definition":
            (
                "SUM("
                "CASE "
                "WHEN interactions.interaction_type = 'email_open' "
                "THEN 1 ELSE 0 "
                "END"
                ")"
            ),

        "meaning":
            "Email-open interactions.",

        "aliases": [
            "email opens",
            "email engagement",
            "opened emails",
        ],
    },


    # --------------------------------------------------------
    # CHURN MODEL METRICS
    # --------------------------------------------------------

    "churn_probability_percentage": {

        "definition":
            "customer_scores.churn_probability_percentage",

        "meaning":
            "Predicted probability that the customer will churn.",

        "aliases": [
            "churn probability",
            "probability of churn",
            "churn likelihood",
            "likelihood to churn",
        ],
    },


    "expected_revenue_at_risk": {

        "definition":
            "customer_scores.expected_revenue_at_risk",

        "meaning":
            (
                "Expected revenue exposed to churn risk "
                "based on the customer scoring model."
            ),

        "aliases": [
            "revenue at risk",
            "rev at risk",
            "money at risk",
            "revenue risk",
        ],
    },


    "expected_profit_at_risk": {

        "definition":
            "customer_scores.expected_profit_at_risk",

        "meaning":
            (
                "Expected profit exposed to churn risk "
                "based on the customer scoring model."
            ),

        "aliases": [
            "profit at risk",
            "profit risk",
            "expected profit risk",
        ],
    },


    "customer_value": {

        "definition":
            "customer_scores.customer_value",

        "meaning":
            "Customer value metric produced by the scoring layer.",

        "aliases": [
            "customer value",
            "customer val",
            "cust value",
            "cust val",
            "CX value",
            "valuable customer",
            "customer worth",
        ],
    },
}


# ============================================================
# DERIVED CONCEPTS
# ============================================================

DERIVED_CONCEPTS = {

    "recency_days": (
        "Days since a customer's latest purchase relative to "
        "the relevant analysis/snapshot date. For churn modeling, "
        "the observation-end date is 2025-12-31."
    ),


    "customer_lifespan_days": (
        "Days between a customer's first and latest purchase."
    ),


    "annualized_order_frequency": (
        "total_orders * 365 / customer_lifespan_days "
        "when customer_lifespan_days > 0; otherwise total_orders."
    ),


    "click_rate": (
        "clicks / total_interactions when total_interactions > 0."
    ),


    "add_to_cart_rate": (
        "add_to_carts / total_interactions "
        "when total_interactions > 0."
    ),


    "email_open_share": (
        "email_opens / total_interactions "
        "when total_interactions > 0."
    ),


    "churned": (
        "1 when a historical purchasing customer has zero "
        "transactions between 2026-01-01 and 2026-03-31; "
        "otherwise 0."
    ),


    "predicted_churn": (
        "Model-predicted churn outcome stored in customer_scores. "
        "1 indicates predicted churn and 0 indicates predicted retention."
    ),


    "churn_risk": (
        "Model-generated customer churn risk classification."
    ),


    "retention_priority": (
        "Model-generated priority for customer retention action."
    ),
}


# ============================================================
# RFM DEFINITIONS
# ============================================================

RFM = {

    "raw_metrics": {

        "recency":
            (
                "Days from snapshot date to latest transaction; "
                "lower is better."
            ),

        "frequency":
            (
                "COUNT(DISTINCT transaction_id); "
                "higher is better."
            ),

        "monetary":
            (
                "SUM(transactions.revenue); "
                "higher is better."
            ),
    },


    "scoring": {

        "recency_score":
            "NTILE(5) over recency DESC",

        "frequency_score":
            "NTILE(5) over frequency ASC",

        "monetary_score":
            "NTILE(5) over monetary ASC",
    },


    "segments": [

        "Champions",

        "Loyal Customers",

        "Potential Loyalists",

        "At Risk",

        "Lost Customers",

        "New / Promising",

        "Needs Attention",
    ],
}


# ============================================================
# CHURN DEFINITIONS
# ============================================================

CHURN = {

    "observation_start":
        "2024-01-06",

    "observation_end":
        "2025-12-31",

    "prediction_start":
        "2026-01-01",

    "prediction_end":
        "2026-03-31",

    "definition":
        (
            "No purchase during the 90-day prediction "
            "window = churned."
        ),

    "modeling_rule":
        (
            "Use observation-period data for model features. "
            "Future transactions are outcomes/targets, "
            "not predictive features."
        ),

    "eligible_population":
        (
            "Customers with at least one purchase during "
            "the historical observation period."
        ),
}


# ============================================================
# SQL SAFETY AND GENERATION RULES
# ============================================================

SQL_RULES = [

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    "Generate SQLite-compatible SELECT statements only.",

    (
        "Never generate INSERT, UPDATE, DELETE, DROP, ALTER, "
        "CREATE, REPLACE, ATTACH, DETACH, PRAGMA, VACUUM, "
        "REINDEX, ANALYZE or transaction-control SQL."
    ),

    "Generate exactly one SQL statement.",

    "Use only tables and columns defined in this semantic layer.",

    "Never invent columns.",


    # --------------------------------------------------------
    # JOINS
    # --------------------------------------------------------

    (
        "When joining customers to transactions, use "
        "customers.customer_id = transactions.customer_id."
    ),

    (
        "When joining customers to interactions, use "
        "customers.customer_id = interactions.customer_id."
    ),

    (
        "When joining transactions to products, use "
        "transactions.product_id = products.product_id."
    ),

    (
        "When joining customers to customer_scores, use "
        "customers.customer_id = customer_scores.customer_id."
    ),


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    "Use COUNT(DISTINCT transaction_id) for order counts.",

    (
        "Use COUNT(DISTINCT customer_id) for customer counts "
        "unless the question explicitly asks for transaction rows."
    ),

    (
        "Use transactions.revenue for net revenue unless "
        "the user explicitly asks for gross revenue."
    ),

    (
        "Use transactions.gross_revenue when the user explicitly "
        "asks for gross revenue."
    ),

    (
        "When calculating profit, join products and use "
        "transactions.quantity * products.cost."
    ),

    "Use NULLIF for division denominators to avoid division-by-zero.",


    # --------------------------------------------------------
    # RANKINGS
    # --------------------------------------------------------

    (
        "For rankings, apply ORDER BY metric DESC for "
        "'top', 'highest', 'most', 'best' and ASC for "
        "'bottom', 'lowest', 'least', 'worst'."
    ),

    (
        "If the user specifies a number such as top 5 or "
        "bottom 10, use that number as LIMIT."
    ),

    (
        "If the user says 'top customers' without a number, "
        "default to top 10."
    ),


    # --------------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------------

    (
        "If a question asks which state, city, region or location, "
        "interpret location using the customers.location field "
        "unless another explicit geographic field exists."
    ),

    (
        "Do not confuse customers.customer_segment with "
        "RFM rfm_segment."
    ),

    (
        "RFM segments are analytically derived and should not "
        "be assumed to exist in the core customers table."
    ),


    # --------------------------------------------------------
    # CUSTOMER-LEVEL QUESTIONS
    # --------------------------------------------------------

    (
        "If a question requires a customer-level result, "
        "include customer_id and group by customer_id."
    ),

    (
        "If the user asks about an individual customer, "
        "filter using customer_id."
    ),

    (
        "If the user asks for a comparison, return one row "
        "per requested comparison group."
    ),


    # --------------------------------------------------------
    # MODEL / CHURN
    # --------------------------------------------------------

    (
        "For churn, retention risk, churn probability, "
        "revenue at risk, profit at risk or retention priority, "
        "use customer_scores when model outputs are requested."
    ),

    (
        "Do not use future transactions as predictive features "
        "for churn analysis."
    ),

    (
        "The churn target is based on future purchase behavior "
        "during 2026-01-01 through 2026-03-31."
    ),

    (
        "customer_scores contains model outputs and should be "
        "treated as scoring information, not raw transaction history."
    ),


    # --------------------------------------------------------
    # DERIVED METRICS
    # --------------------------------------------------------

    (
        "If a requested metric is derived, calculate it from "
        "its documented definition rather than assuming a "
        "physical database column exists."
    ),

    (
        "Use explicit aliases for calculated metrics so that "
        "the returned result is understandable."
    ),


    # --------------------------------------------------------
    # GENERAL SQL QUALITY
    # --------------------------------------------------------

    (
        "Avoid SELECT * when only a small set of fields "
        "is required."
    ),

    (
        "Prefer explicit column selection and readable aliases."
    ),

    (
        "Use appropriate GROUP BY clauses for aggregated results."
    ),

    (
        "Use HAVING for filters on aggregated metrics."
    ),

    (
        "Use WHERE for row-level filters."
    ),

    (
        "Use COALESCE when missing values should logically "
        "be treated as zero."
    ),

    (
        "Use date filters explicitly when the user asks about "
        "a particular time period."
    ),
]


# ============================================================
# NATURAL LANGUAGE SYNONYMS
# ============================================================

SYNONYMS = {

    "customer": [

        "customer",
        "customers",
        "cx",
        "client",
        "clients",
        "buyer",
        "buyers",
    ],


    "customer_value": [

        "customer value",
        "customer val",
        "cust value",
        "cust val",
        "cx value",
        "valuable customer",
        "customer worth",
        "customer lifetime value",
        "CLV",
    ],


    "high_risk": [

        "high risk",
        "high-risk",
        "risky",
        "at risk",
        "likely to leave",
        "might leave",
        "about to churn",
        "likely to churn",
        "churn risk",
    ],


    "revenue_at_risk": [

        "revenue at risk",
        "rev at risk",
        "money at risk",
        "revenue risk",
        "sales at risk",
    ],


    "profit_at_risk": [

        "profit at risk",
        "profit risk",
        "earnings at risk",
    ],


    "churn_probability": [

        "churn probability",
        "probability of churn",
        "likelihood of churn",
        "churn likelihood",
        "chance of churn",
    ],


    "location": [

        "location",
        "city",
        "state",
        "region",
        "place",
        "area",
        "geography",
    ],


    "acquisition_channel": [

        "channel",
        "acquisition channel",
        "source",
        "marketing channel",
        "customer source",
    ],


    "customer_segment": [

        "customer segment",
        "segment",
        "high segment",
        "medium segment",
        "low segment",
    ],


    "rfm_segment": [

        "rfm segment",
        "rfm",
        "champions",
        "loyal customers",
        "potential loyalists",
        "at risk",
        "lost customers",
        "new / promising",
        "needs attention",
    ],


    "revenue": [

        "revenue",
        "sales",
        "net sales",
        "sales revenue",
        "money made",
    ],


    "gross_revenue": [

        "gross revenue",
        "gross sales",
        "sales before discount",
        "revenue before discount",
    ],


    "orders": [

        "orders",
        "purchases",
        "transactions",
        "order count",
    ],


    "units": [

        "units",
        "quantity",
        "items",
        "items sold",
        "units sold",
    ],


    "profit": [

        "profit",
        "gross profit",
        "profitability",
        "earnings",
    ],


    "engagement": [

        "engagement",
        "interactions",
        "activity",
        "customer activity",
        "digital engagement",
    ],
}


# ============================================================
# SEMANTIC CONTEXT GENERATOR
# ============================================================

def get_semantic_context() -> str:
    """
    Return compact semantic context suitable for inclusion
    in an LLM system prompt.
    """

    sections = [

        "CUSTOMERIQ SEMANTIC LAYER",

        DATABASE_DESCRIPTION,

        "",

        "TABLES AND COLUMNS",
    ]


    # --------------------------------------------------------
    # TABLES
    # --------------------------------------------------------

    for table_name, table_info in TABLES.items():

        sections.append(
            f"\n[{table_name}] — "
            f"{table_info['description']}"
        )

        for column, description in (
            table_info["columns"].items()
        ):

            sections.append(
                f"  - {column}: {description}"
            )


    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    sections.append(
        "\nLOGICAL RELATIONSHIPS"
    )

    for relationship in RELATIONSHIPS:

        sections.append(

            f"  - "
            f"{relationship['left']} = "
            f"{relationship['right']} "
            f"({relationship['meaning']})"

        )


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    sections.append(
        "\nMETRIC DEFINITIONS"
    )

    for metric_name, metric in METRICS.items():

        aliases = ", ".join(
            metric["aliases"]
        )

        sections.append(

            f"  - {metric_name}: "
            f"{metric['definition']}\n"
            f"    Meaning: "
            f"{metric['meaning']}\n"
            f"    Aliases: "
            f"{aliases}"

        )


    # --------------------------------------------------------
    # DERIVED CONCEPTS
    # --------------------------------------------------------

    sections.append(
        "\nDERIVED CONCEPTS"
    )

    for name, definition in (
        DERIVED_CONCEPTS.items()
    ):

        sections.append(
            f"  - {name}: {definition}"
        )


    # --------------------------------------------------------
    # RFM
    # --------------------------------------------------------

    sections.append(
        "\nRFM DEFINITIONS"
    )

    sections.append(
        str(RFM)
    )


    # --------------------------------------------------------
    # CHURN
    # --------------------------------------------------------

    sections.append(
        "\nCHURN DEFINITIONS"
    )

    sections.append(
        str(CHURN)
    )


    # --------------------------------------------------------
    # SQL RULES
    # --------------------------------------------------------

    sections.append(
        "\nSQL SAFETY AND GENERATION RULES"
    )

    for rule in SQL_RULES:

        sections.append(
            f"  - {rule}"
        )


    # --------------------------------------------------------
    # SYNONYMS
    # --------------------------------------------------------

    sections.append(
        "\nCOMMON NATURAL-LANGUAGE SYNONYMS"
    )

    for concept, words in (
        SYNONYMS.items()
    ):

        sections.append(
            f"  - {concept}: "
            f"{', '.join(words)}"
        )


    return "\n".join(
        sections
    )


# ============================================================
# STRUCTURED SCHEMA
# ============================================================

def get_schema_dict() -> dict:
    """
    Return structured semantic metadata for programmatic use.
    """

    return {

        "database_description":
            DATABASE_DESCRIPTION,

        "tables":
            TABLES,

        "relationships":
            RELATIONSHIPS,

        "metrics":
            METRICS,

        "derived_concepts":
            DERIVED_CONCEPTS,

        "rfm":
            RFM,

        "churn":
            CHURN,

        "sql_rules":
            SQL_RULES,

        "synonyms":
            SYNONYMS,
    }


# ============================================================
# SIMPLE VALIDATION
# ============================================================

def validate_semantic_layer() -> bool:
    """
    Basic internal validation to catch accidental structural
    errors before the application uses the semantic layer.
    """

    required_tables = {

        "customers",
        "transactions",
        "interactions",
        "products",
        "customer_scores",
    }

    missing_tables = (
        required_tables
        - set(TABLES.keys())
    )

    if missing_tables:

        raise ValueError(
            "Semantic layer is missing tables: "
            + ", ".join(
                sorted(missing_tables)
            )
        )


    required_relationships = [

        (
            "customers.customer_id",
            "transactions.customer_id"
        ),

        (
            "customers.customer_id",
            "interactions.customer_id"
        ),

        (
            "products.product_id",
            "transactions.product_id"
        ),

        (
            "customers.customer_id",
            "customer_scores.customer_id"
        ),
    ]


    relationship_pairs = {

        (
            relationship["left"],
            relationship["right"]
        )

        for relationship
        in RELATIONSHIPS
    }


    for relationship in required_relationships:

        if relationship not in relationship_pairs:

            raise ValueError(
                "Missing logical relationship: "
                f"{relationship[0]} = "
                f"{relationship[1]}"
            )


    return True


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    validate_semantic_layer()

    print(
        get_semantic_context()
    )