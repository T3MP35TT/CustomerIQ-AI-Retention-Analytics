import pandas as pd


# ============================================================
# CUSTOMERIQ — QUERY ENGINE
# ============================================================

def _clean_number(value):
    """Safely convert a value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def get_top_predicted_churners(df, n=3):
    """
    Return customers with predicted churn, ranked by
    expected revenue at risk.
    """

    result = df[df["predicted_churn"] == 1].copy()

    result = result.sort_values(
        "expected_revenue_at_risk",
        ascending=False
    ).head(n)

    return result[
        [
            "customer_id",
            "churn_probability_percentage",
            "customer_value",
            "expected_revenue_at_risk",
            "retention_priority",
            "retention_action"
        ]
    ]

def get_top_high_risk_customers(df, n=10):
    """
    Return high-risk customers ranked by
    expected revenue at risk.
    """

    result = df[
        (df["churn_risk"] == "High Risk") &
        (df["predicted_churn"] == 1)
    ].copy()

    result = result.sort_values(
        "expected_revenue_at_risk",
        ascending=False
    ).head(n)

    return result[
        [
            "customer_id",
            "churn_probability_percentage",
            "customer_value",
            "expected_revenue_at_risk",
            "retention_priority",
            "retention_action"
        ]
    ]

def get_high_value_churners(df, n=5):
    """
    Return predicted churners with the highest customer value.
    """

    result = df[df["predicted_churn"] == 1].copy()

    result = result.sort_values(
        "customer_value",
        ascending=False
    ).head(n)

    return result[
        [
            "customer_id",
            "customer_value",
            "churn_probability_percentage",
            "expected_revenue_at_risk",
            "retention_priority",
            "retention_action"
        ]
    ]


def get_high_probability_customers(df, threshold=80, n=10):
    """
    Return customers whose churn probability exceeds
    the specified percentage.
    """

    result = df[
        df["churn_probability_percentage"] >= threshold
    ].copy()

    result = result.sort_values(
        "churn_probability_percentage",
        ascending=False
    ).head(n)

    return result[
        [
            "customer_id",
            "churn_probability_percentage",
            "customer_value",
            "expected_revenue_at_risk",
            "retention_priority",
            "retention_action"
        ]
    ]


def get_rfm_churn_analysis(df):
    """
    Calculate predicted churn statistics by RFM segment.
    """

    result = (
        df.groupby("rfm_segment")
        .agg(
            customers=("customer_id", "count"),
            predicted_churners=("predicted_churn", "sum")
        )
        .reset_index()
    )

    result["predicted_churn_rate"] = (
        result["predicted_churners"]
        / result["customers"]
        * 100
    )

    result = result.sort_values(
        "predicted_churn_rate",
        ascending=False
    )

    return result


def get_customer(df, customer_id):
    """
    Retrieve a specific customer.
    """

    customer_id = str(customer_id).strip().upper()

    result = df[
        df["customer_id"].astype(str).str.upper()
        == customer_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


def get_business_summary(df):
    """
    Calculate overall CustomerIQ metrics.
    """

    total_customers = len(df)

    predicted_churners = int(
        df["predicted_churn"].sum()
    )

    churn_rate = (
        predicted_churners / total_customers * 100
        if total_customers
        else 0
    )

    revenue_at_risk = df[
        "expected_revenue_at_risk"
    ].sum()

    profit_at_risk = df[
        "expected_profit_at_risk"
    ].sum()

    return {
        "total_customers": total_customers,
        "predicted_churners": predicted_churners,
        "predicted_churn_rate": churn_rate,
        "revenue_at_risk": revenue_at_risk,
        "profit_at_risk": profit_at_risk
    }


def format_customer_records(df):
    """
    Convert customer records into compact text
    for the LLM.
    """

    if df is None or len(df) == 0:
        return "No matching customers found."

    records = []

    for _, row in df.iterrows():

        records.append(
            f"""
Customer: {row['customer_id']}
Churn Probability: {row['churn_probability_percentage']:.2f}%
Customer Value: ₹{row['customer_value']:,.2f}
Expected Revenue at Risk: ₹{row['expected_revenue_at_risk']:,.2f}
Retention Priority: {row['retention_priority']}
Recommended Action: {row['retention_action']}
""".strip()
        )

    return "\n\n".join(records)


def format_rfm_analysis(result):
    """
    Convert RFM analysis into compact text.
    """

    records = []

    for _, row in result.iterrows():

        records.append(
            f"""
RFM Segment: {row['rfm_segment']}
Customers: {int(row['customers'])}
Predicted Churners: {int(row['predicted_churners'])}
Predicted Churn Rate: {row['predicted_churn_rate']:.2f}%
""".strip()
        )

    return "\n\n".join(records)

if __name__ == "__main__":


    from customeriq_ai import load_customer_data

    df = load_customer_data()

    print("\n" + "=" * 60)
    print("CUSTOMERIQ — QUERY ENGINE TEST")
    print("=" * 60)

    print("\nTOP PREDICTED CHURNERS")
    print(
        get_top_predicted_churners(df, 3)
        .to_string(index=False)
    )

    print("\nTOP HIGH-RISK CUSTOMERS")
    print(
    get_top_high_risk_customers(df, 10)
    .to_string(index=False)
    )

    print("\nHIGH-VALUE CHURNERS")
    print(
        get_high_value_churners(df, 3)
        .to_string(index=False)
    )

    print("\nRFM CHURN ANALYSIS")
    print(
        get_rfm_churn_analysis(df)
        .to_string(index=False)
    )

    print("\nCUSTOMER LOOKUP — C00398")

    customer = get_customer(df, "C00398")

    if customer is not None:
        print(customer.to_string())

    print("\n" + "=" * 60)