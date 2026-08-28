import pandas as pd


# ============================================================
# CUSTOMERIQ — GENERAL ANALYTICS ENGINE
# ============================================================

"""
This module is the deterministic execution layer for CustomerIQ.

The LLM NEVER executes Python or SQL directly.

The LLM produces a structured query plan.
This module validates that plan and performs the actual
calculation against the CustomerIQ dataframe.
"""


# ============================================================
# ALLOWED DATASET FIELDS
# ============================================================

ALLOWED_METRICS = {
    "total_orders",
    "total_units",
    "total_revenue",
    "net_revenue",
    "total_cost",
    "gross_profit",
    "gross_margin_percentage",
    "average_order_value",
    "total_interactions",
    "views",
    "clicks",
    "add_to_carts",
    "email_opens",
    "channels_used",
    "interaction_types_used",
    "has_interaction_history",
    "annualized_order_frequency",
    "click_rate",
    "add_to_cart_rate",
    "email_open_share",
    "customer_value",

    # Churn / predictive
    "churn_probability",
    "churn_probability_percentage",
    "predicted_churn",
    "churn_risk",
    "expected_revenue_at_risk",
    "expected_profit_at_risk",
    "retention_score",
    "retention_priority",
    "retention_action",

    # RFM
    "rfm_recency_score",
    "rfm_frequency_score",
    "rfm_monetary_score",
    "rfm_score",
    "rfm_total_score",
    "rfm_segment",

    # Customer attributes
    "age",
    "recency_days",
    "customer_lifespan_days",
}


ALLOWED_GROUPS = {
    "customer_segment",
    "acquisition_channel",
    "location",
    "gender",
    "rfm_segment",
    "churn_risk",
    "retention_priority",
    "retention_action",
}


ALLOWED_FILTER_COLUMNS = (
    ALLOWED_METRICS
    | ALLOWED_GROUPS
    | {
        "customer_id",
        "first_purchase_date",
        "last_purchase_date",
    }
)


ALLOWED_OPERATORS = {
    "==",
    "!=",
    ">",
    ">=",
    "<",
    "<=",
}


ALLOWED_OPERATIONS = {
    "count",
    "sum",
    "average",
    "median",
    "minimum",
    "maximum",
    "rank",
    "filter",
    "group",
    "lookup",
    "percentage",
    "compare",
}


# ============================================================
# VALIDATION
# ============================================================

def validate_metric(column):
    """
    Validate a metric requested by the query planner.
    """

    if column is None:
        return

    if column not in ALLOWED_METRICS:
        raise ValueError(
            f"Metric is not allowed: {column}"
        )


def validate_group(column):
    """
    Validate a grouping column.
    """

    if column is None:
        return

    if column not in ALLOWED_GROUPS:
        raise ValueError(
            f"Grouping column is not allowed: {column}"
        )


def validate_filter_column(df, column):
    """
    Validate a filter column against both the whitelist
    and the actual dataframe.
    """

    if column not in ALLOWED_FILTER_COLUMNS:
        raise ValueError(
            f"Filter column is not allowed: {column}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column does not exist in dataset: {column}"
        )


def validate_query_plan(plan):
    """
    Validate the complete query plan before execution.
    """

    if not isinstance(plan, dict):
        raise ValueError(
            "Query plan must be a JSON object."
        )

    required_fields = {
        "operation",
        "metric",
        "group_by",
        "filter",
        "sort",
        "limit",
        "customer_id",
    }

    missing = (
        required_fields
        - set(plan.keys())
    )

    if missing:
        raise ValueError(
            f"Query plan is missing fields: {missing}"
        )

    operation = plan["operation"]

    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )

    validate_metric(
        plan.get("metric")
    )

    validate_group(
        plan.get("group_by")
    )

    sort = plan.get("sort")

    if sort not in {
        None,
        "asc",
        "desc",
    }:
        raise ValueError(
            f"Unsupported sort direction: {sort}"
        )

    limit = plan.get("limit")

    if limit is not None:

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
        ):
            raise ValueError(
                "Limit must be an integer."
            )

        if limit < 1:
            raise ValueError(
                "Limit must be at least 1."
            )

    if (
        operation == "lookup"
        and not plan.get("customer_id")
    ):
        raise ValueError(
            "Customer lookup requires customer_id."
        )

    return True


# ============================================================
# FILTER ENGINE
# ============================================================

def apply_filter(df, filter_spec):
    """
    Apply structured filters.

    Supported:

    Single:
    {
        "location": {
            "operator": "==",
            "value": "Chennai"
        }
    }

    AND:
    {
        "and": [
            {...},
            {...}
        ]
    }

    OR:
    {
        "or": [
            {...},
            {...}
        ]
    }
    """

    if not filter_spec:
        return df.copy()

    if not isinstance(
        filter_spec,
        dict
    ):
        raise ValueError(
            "Filter must be a JSON object."
        )


    # --------------------------------------------------------
    # AND
    # --------------------------------------------------------

    if "and" in filter_spec:

        conditions = filter_spec["and"]

        if not isinstance(
            conditions,
            list
        ):
            raise ValueError(
                "'and' filter must contain a list."
            )

        result = df.copy()

        for condition in conditions:

            result = apply_filter(
                result,
                condition
            )

        return result


    # --------------------------------------------------------
    # OR
    # --------------------------------------------------------

    if "or" in filter_spec:

        conditions = filter_spec["or"]

        if not isinstance(
            conditions,
            list
        ):
            raise ValueError(
                "'or' filter must contain a list."
            )

        if not conditions:
            return df.iloc[0:0].copy()

        masks = []

        for condition in conditions:

            filtered = apply_filter(
                df,
                condition
            )

            masks.append(
                df.index.isin(
                    filtered.index
                )
            )

        combined_mask = masks[0]

        for mask in masks[1:]:
            combined_mask = (
                combined_mask | mask
            )

        return df[
            combined_mask
        ].copy()


    # --------------------------------------------------------
    # SINGLE COLUMN CONDITION
    # --------------------------------------------------------

    if len(filter_spec) != 1:
        raise ValueError(
            "Invalid filter structure."
        )

    column = next(
        iter(filter_spec)
    )

    condition = filter_spec[column]

    validate_filter_column(
        df,
        column
    )

    if not isinstance(
        condition,
        dict
    ):
        raise ValueError(
            "Filter condition must be an object."
        )

    operator = condition.get(
        "operator"
    )

    value = condition.get(
        "value"
    )

    if operator not in ALLOWED_OPERATORS:
        raise ValueError(
            f"Unsupported operator: {operator}"
        )

    series = df[column]


    if operator == "==":
        mask = series == value

    elif operator == "!=":
        mask = series != value

    elif operator == ">":
        mask = series > value

    elif operator == ">=":
        mask = series >= value

    elif operator == "<":
        mask = series < value

    elif operator == "<=":
        mask = series <= value

    else:
        raise ValueError(
            f"Unsupported operator: {operator}"
        )

    return df[
        mask
    ].copy()


# ============================================================
# BASIC AGGREGATIONS
# ============================================================

def aggregate(
    df,
    column,
    operation
):
    """
    Execute a scalar aggregation.
    """

    validate_metric(
        column
    )

    if column not in df.columns:
        raise ValueError(
            f"Column does not exist: {column}"
        )

    series = df[column]

    if operation == "sum":
        return series.sum()

    if operation in {
        "average",
        "mean"
    }:
        return series.mean()

    if operation == "median":
        return series.median()

    if operation in {
        "minimum",
        "min"
    }:
        return series.min()

    if operation in {
        "maximum",
        "max"
    }:
        return series.max()

    if operation == "count":
        return series.count()

    raise ValueError(
        f"Unsupported aggregation: {operation}"
    )


# ============================================================
# GROUPED ANALYTICS
# ============================================================

def group_aggregate(
    df,
    group_column,
    value_column,
    operation="sum",
    ascending=False,
    limit=None
):
    """
    Group data and calculate an aggregation.
    """

    validate_group(
        group_column
    )

    validate_metric(
        value_column
    )

    if group_column not in df.columns:
        raise ValueError(
            f"Group column does not exist: {group_column}"
        )

    if value_column not in df.columns:
        raise ValueError(
            f"Metric does not exist: {value_column}"
        )

    grouped = df.groupby(
        group_column,
        dropna=False
    )[value_column]


    if operation == "sum":
        result = grouped.sum()

    elif operation in {
        "average",
        "mean"
    }:
        result = grouped.mean()

    elif operation == "median":
        result = grouped.median()

    elif operation == "count":
        result = grouped.count()

    elif operation in {
        "minimum",
        "min"
    }:
        result = grouped.min()

    elif operation in {
        "maximum",
        "max"
    }:
        result = grouped.max()

    else:
        raise ValueError(
            f"Unsupported group operation: {operation}"
        )


    result = (
        result
        .sort_values(
            ascending=ascending
        )
        .reset_index()
    )


    if limit is not None:
        result = result.head(
            limit
        )


    return result


# ============================================================
# RANKING
# ============================================================

def rank_data(
    df,
    column,
    ascending=False,
    n=10
):
    """
    Rank individual records.
    """

    validate_metric(
        column
    )

    if column not in df.columns:
        raise ValueError(
            f"Column does not exist: {column}"
        )

    if n is None:
        n = 10

    if n < 1:
        raise ValueError(
            "Limit must be at least 1."
        )

    return (
        df
        .sort_values(
            column,
            ascending=ascending
        )
        .head(n)
        .copy()
    )


# ============================================================
# CUSTOMER LOOKUP
# ============================================================

def lookup_customer(
    df,
    customer_id
):
    """
    Return a specific customer.
    """

    if "customer_id" not in df.columns:
        raise ValueError(
            "customer_id column is missing."
        )

    result = df[
        df["customer_id"]
        .astype(str)
        .str.upper()
        == str(customer_id).upper()
    ].copy()

    return result


# ============================================================
# PERCENTAGE
# ============================================================

def calculate_percentage(
    numerator,
    denominator
):
    """
    Safely calculate percentage.
    """

    if denominator == 0:
        return 0.0

    return (
        numerator
        / denominator
        * 100
    )


# ============================================================
# CHURN RATE
# ============================================================

def calculate_churn_rate(df):
    """
    Calculate predicted churn rate.
    """

    if len(df) == 0:
        return 0.0

    if "predicted_churn" not in df.columns:
        raise ValueError(
            "predicted_churn column is missing."
        )

    return (
        df["predicted_churn"]
        .mean()
        * 100
    )


# ============================================================
# GROUPED CHURN RATE
# ============================================================

def grouped_churn_rate(
    df,
    group_column,
    ascending=False,
    limit=None
):
    """
    Calculate predicted churn rate by group.
    """

    validate_group(
        group_column
    )

    if group_column not in df.columns:
        raise ValueError(
            f"Group column does not exist: {group_column}"
        )

    result = (
        df.groupby(
            group_column,
            dropna=False
        )["predicted_churn"]
        .agg(
            customers="count",
            predicted_churners="sum",
            predicted_churn_rate="mean"
        )
        .reset_index()
    )

    result[
        "predicted_churn_rate"
    ] = (
        result["predicted_churn_rate"]
        * 100
    )

    result = result.sort_values(
        "predicted_churn_rate",
        ascending=ascending
    )

    if limit is not None:
        result = result.head(
            limit
        )

    return result.reset_index(
        drop=True
    )


# ============================================================
# COMPARISON
# ============================================================

def compare_groups(
    df,
    group_column,
    metric,
    groups,
    operation="average"
):
    """
    Compare explicitly requested groups.

    Example:

    Hibernating vs Champions
    """

    validate_group(
        group_column
    )

    validate_metric(
        metric
    )

    if not groups:
        raise ValueError(
            "Comparison requires groups."
        )

    filtered = df[
        df[group_column].isin(
            groups
        )
    ].copy()

    result = group_aggregate(
        filtered,
        group_column,
        metric,
        operation=operation,
        ascending=False
    )

    return result


# ============================================================
# QUERY EXECUTOR
# ============================================================

def execute_query_plan(
    df,
    plan
):
    """
    Execute a validated query plan.

    The LLM determines WHAT to calculate.

    Python determines HOW to calculate it.
    """

    validate_query_plan(
        plan
    )

    operation = plan[
        "operation"
    ]

    metric = plan.get(
        "metric"
    )

    group_by = plan.get(
        "group_by"
    )

    filter_spec = plan.get(
        "filter"
    )

    sort = plan.get(
        "sort"
    )

    limit = plan.get(
        "limit"
    )

    customer_id = plan.get(
        "customer_id"
    )


    # ========================================================
    # CUSTOMER LOOKUP
    # ========================================================

    if operation == "lookup":

        return lookup_customer(
            df,
            customer_id
        )


    # ========================================================
    # FILTER
    # ========================================================

    working_df = apply_filter(
        df,
        filter_spec
    )


    # ========================================================
    # COUNT
    # ========================================================

    if operation == "count":

        return len(
            working_df
        )


    # ========================================================
    # SUM
    # ========================================================

    if operation == "sum":

        return aggregate(
            working_df,
            metric,
            "sum"
        )


    # ========================================================
    # AVERAGE
    # ========================================================

    if operation == "average":

        return aggregate(
            working_df,
            metric,
            "average"
        )


    # ========================================================
    # MEDIAN
    # ========================================================

    if operation == "median":

        return aggregate(
            working_df,
            metric,
            "median"
        )


    # ========================================================
    # MINIMUM
    # ========================================================

    if operation == "minimum":

        return aggregate(
            working_df,
            metric,
            "minimum"
        )


    # ========================================================
    # MAXIMUM
    # ========================================================

    if operation == "maximum":

        return aggregate(
            working_df,
            metric,
            "maximum"
        )


    # ========================================================
    # RANK
    # ========================================================

    if operation == "rank":

        ascending = (
            sort == "asc"
        )

        if group_by:

            return group_aggregate(
                working_df,
                group_by,
                metric,
                operation="sum",
                ascending=ascending,
                limit=limit
            )

        return rank_data(
            working_df,
            metric,
            ascending=ascending,
            n=limit or 10
        )


    # ========================================================
    # GROUP
    # ========================================================

    if operation == "group":

        if not group_by:
            raise ValueError(
                "Group operation requires group_by."
            )

        return group_aggregate(
            working_df,
            group_by,
            metric,
            operation="sum",
            ascending=(
                sort == "asc"
            ),
            limit=limit
        )


    # ========================================================
    # FILTER RESULT
    # ========================================================

    if operation == "filter":

        return working_df


    # ========================================================
    # COMPARE
    # ========================================================

    if operation == "compare":

        if not group_by:

            raise ValueError(
                "Compare operation requires group_by."
            )

        if not metric:

            raise ValueError(
                "Compare operation requires metric."
            )

        return group_aggregate(
            working_df,
            group_by,
            metric,
            operation="sum",
            ascending=False,
            limit=limit
        )


    # ========================================================
    # PERCENTAGE
    # ========================================================

    if operation == "percentage":

        numerator = aggregate(
            working_df,
            metric,
            "sum"
        )

        denominator = aggregate(
            df,
            metric,
            "sum"
        )

        return calculate_percentage(
            numerator,
            denominator
        )


    raise ValueError(
        f"Operation not implemented: {operation}"
    )


# ============================================================
# TEST SUITE
# ============================================================

if __name__ == "__main__":

    from customeriq_ai import (
        load_customer_data
    )


    df = load_customer_data()


    print("\n" + "=" * 60)
    print("CUSTOMERIQ — GENERAL ANALYTICS ENGINE TEST")
    print("=" * 60)


    # ========================================================
    # TEST 1
    # TOP 10 HIGH-RISK CUSTOMERS
    # ========================================================

    print(
        "\nTOP 10 HIGH-RISK CUSTOMERS"
    )

    plan = {
        "operation": "rank",
        "metric": "expected_revenue_at_risk",
        "group_by": None,
        "filter": {
            "churn_risk": {
                "operator": "==",
                "value": "High Risk"
            }
        },
        "sort": "desc",
        "limit": 10,
        "customer_id": None
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(
        result[
            [
                "customer_id",
                "churn_probability_percentage",
                "expected_revenue_at_risk"
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # TEST 2
    # TOTAL REVENUE AT RISK
    # ========================================================

    print(
        "\nTOTAL REVENUE AT RISK"
    )

    plan = {
        "operation": "sum",
        "metric": "expected_revenue_at_risk",
        "group_by": None,
        "filter": None,
        "sort": None,
        "limit": None,
        "customer_id": None
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(
        f"₹{result:,.2f}"
    )


    # ========================================================
    # TEST 3
    # CUSTOMERS ABOVE 80% CHURN PROBABILITY
    # ========================================================

    print(
        "\nCUSTOMERS ABOVE 80% CHURN PROBABILITY"
    )

    plan = {
        "operation": "count",
        "metric": "churn_probability_percentage",
        "group_by": None,
        "filter": {
            "churn_probability_percentage": {
                "operator": ">",
                "value": 80
            }
        },
        "sort": None,
        "limit": None,
        "customer_id": None
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(result)


    # ========================================================
    # TEST 4
    # RFM REVENUE AT RISK
    # ========================================================

    print(
        "\nREVENUE AT RISK BY RFM SEGMENT"
    )

    plan = {
        "operation": "rank",
        "metric": "expected_revenue_at_risk",
        "group_by": "rfm_segment",
        "filter": None,
        "sort": "desc",
        "limit": 8,
        "customer_id": None
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(
        result.to_string(
            index=False
        )
    )


    # ========================================================
    # TEST 5
    # AVERAGE CUSTOMER VALUE
    # ========================================================

    print(
        "\nAVERAGE CUSTOMER VALUE"
    )

    plan = {
        "operation": "average",
        "metric": "customer_value",
        "group_by": None,
        "filter": None,
        "sort": None,
        "limit": None,
        "customer_id": None
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(
        f"₹{result:,.2f}"
    )


    # ========================================================
    # TEST 6
    # HIGH-RISK CUSTOMER VALUE
    # ========================================================

    print(
        "\nAVERAGE CUSTOMER VALUE — HIGH RISK"
    )

    plan = {
        "operation": "average",
        "metric": "customer_value",
        "group_by": None,
        "filter": {
            "churn_risk": {
                "operator": "==",
                "value": "High Risk"
            }
        },
        "sort": None,
        "limit": None,
        "customer_id": None
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(
        f"₹{result:,.2f}"
    )


    # ========================================================
    # TEST 7
    # MULTI-CONDITION FILTER
    # ========================================================

    print(
        "\nHIGH-RISK CUSTOMERS ABOVE 80% PROBABILITY"
    )

    plan = {
        "operation": "filter",
        "metric": None,
        "group_by": None,
        "filter": {
            "and": [
                {
                    "churn_risk": {
                        "operator": "==",
                        "value": "High Risk"
                    }
                },
                {
                    "churn_probability_percentage": {
                        "operator": ">",
                        "value": 80
                    }
                }
            ]
        },
        "sort": None,
        "limit": None,
        "customer_id": None
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(
        result[
            [
                "customer_id",
                "churn_probability_percentage",
                "expected_revenue_at_risk"
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # TEST 8
    # CUSTOMER LOOKUP
    # ========================================================

    print(
        "\nCUSTOMER LOOKUP — C00398"
    )

    plan = {
        "operation": "lookup",
        "metric": None,
        "group_by": None,
        "filter": None,
        "sort": None,
        "limit": None,
        "customer_id": "C00398"
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(
        result[
            [
                "customer_id",
                "customer_value",
                "churn_probability_percentage",
                "expected_revenue_at_risk",
                "expected_profit_at_risk",
                "churn_risk",
                "retention_priority",
                "retention_action"
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # TEST 9
    # GROUP BY ACQUISITION CHANNEL
    # ========================================================

    print(
        "\nREVENUE BY ACQUISITION CHANNEL"
    )

    plan = {
        "operation": "group",
        "metric": "total_revenue",
        "group_by": "acquisition_channel",
        "filter": None,
        "sort": "desc",
        "limit": None,
        "customer_id": None
    }

    result = execute_query_plan(
        df,
        plan
    )

    print(
        result.to_string(
            index=False
        )
    )


    # ========================================================
    # TEST 10
    # GROUP BY CUSTOMER SEGMENT
    # ========================================================

    print(
        "\nAVERAGE CUSTOMER VALUE BY CUSTOMER SEGMENT"
    )

    result = group_aggregate(
        df,
        "customer_segment",
        "customer_value",
        operation="average",
        ascending=False
    )

    print(
        result.to_string(
            index=False
        )
    )


    # ========================================================
    # TEST 11
    # CHURN RATE BY RFM SEGMENT
    # ========================================================

    print(
        "\nPREDICTED CHURN RATE BY RFM SEGMENT"
    )

    result = grouped_churn_rate(
        df,
        "rfm_segment",
        ascending=False
    )

    print(
        result.to_string(
            index=False
        )
    )


    print(
        "\n" + "=" * 60
    )
    print(
        "ANALYTICS ENGINE TEST COMPLETE"
    )
    print(
        "=" * 60
    )