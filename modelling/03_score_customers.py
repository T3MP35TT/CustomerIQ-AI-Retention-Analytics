import pandas as pd
import numpy as np

from pathlib import Path
import joblib


# ============================================================
# CUSTOMERIQ
# CUSTOMER CHURN SCORING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "churn_modeling_dataset.csv"
)

MODEL_FILE = (
    BASE_DIR
    / "models"
    / "customeriq_churn_model.joblib"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "churn_scored_customers.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "churned"

MODEL_FEATURES = [
    "customer_segment",
    "acquisition_channel",
    "location",
    "age",
    "gender",
    "total_orders",
    "total_revenue",
    "gross_margin_percentage",
    "average_order_value",
    "recency_days",
    "customer_lifespan_days",
    "total_interactions",
    "channels_used",
    "interaction_types_used",
    "annualized_order_frequency",
    "click_rate",
    "add_to_cart_rate",
    "email_open_share"
]


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)


print("=" * 70)
print("CUSTOMERIQ — CUSTOMER CHURN SCORING")
print("=" * 70)

print(
    f"\nDataset:\n{DATA_FILE}"
)

print(
    f"Rows: {len(df):,}"
)


# ============================================================
# LOAD MODEL
# ============================================================

print(
    f"\nLoading model:\n{MODEL_FILE}"
)

model = joblib.load(MODEL_FILE)

print(
    "\nModel loaded successfully."
)


# ============================================================
# VALIDATE FEATURES
# ============================================================

missing_features = [
    column
    for column in MODEL_FEATURES
    if column not in df.columns
]

if missing_features:

    print("\nERROR: Missing model features:")

    for column in missing_features:
        print(f"  - {column}")

    raise ValueError(
        "Required model features are missing from the dataset."
    )


print(
    "\nAll required model features are available."
)


# ============================================================
# MODEL INPUT
# ============================================================

X = df[MODEL_FEATURES].copy()


print(
    f"\nModel input rows: {len(X):,}"
)

print(
    f"Model input features: {len(X.columns)}"
)


# ============================================================
# GENERATE CHURN PROBABILITIES
# ============================================================

print(
    "\nGenerating churn probabilities..."
)

churn_probability = model.predict_proba(X)[:, 1]

predicted_churn = (
    churn_probability >= 0.50
).astype(int)


# ============================================================
# ADD MODEL OUTPUTS
# ============================================================

df["churn_probability"] = churn_probability

df["churn_probability_percentage"] = (
    churn_probability * 100
)

df["predicted_churn"] = predicted_churn

# ============================================================
# RFM SEGMENTATION
# ============================================================
#
# RFM = Recency, Frequency, Monetary
#
# Recency:
#   Fewer days since last purchase = better
#
# Frequency:
#   More orders = better
#
# Monetary:
#   Higher revenue = better
#
# RFM is calculated using observation-window customer
# behaviour only. Future orders/revenue are NOT used.
# ============================================================

print(
    "\nCalculating RFM segments..."
)


# ------------------------------------------------------------
# RFM SCORES
# ------------------------------------------------------------

# Recency:
# Lower recency is better, therefore reverse the ranking.

df["rfm_recency_score"] = pd.qcut(
    df["recency_days"].rank(
        method="first"
    ),
    5,
    labels=[5, 4, 3, 2, 1]
).astype(int)


# Frequency:
# Higher order frequency is better.

df["rfm_frequency_score"] = pd.qcut(
    df["total_orders"].rank(
        method="first"
    ),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)


# Monetary:
# Higher revenue is better.

df["rfm_monetary_score"] = pd.qcut(
    df["total_revenue"].rank(
        method="first"
    ),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)


# ------------------------------------------------------------
# COMBINED RFM SCORE
# ------------------------------------------------------------

df["rfm_score"] = (
    df["rfm_recency_score"].astype(str)
    + df["rfm_frequency_score"].astype(str)
    + df["rfm_monetary_score"].astype(str)
)


# Numeric total score for easier Power BI analysis.

df["rfm_total_score"] = (
    df["rfm_recency_score"]
    + df["rfm_frequency_score"]
    + df["rfm_monetary_score"]
)


# ------------------------------------------------------------
# RFM SEGMENT
# ------------------------------------------------------------

def assign_rfm_segment(row):

    r = row["rfm_recency_score"]
    f = row["rfm_frequency_score"]
    m = row["rfm_monetary_score"]

    # Strong across all three dimensions
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"

    # Recent + frequent customers
    elif r >= 4 and f >= 4:
        return "Loyal Customers"

    # High-value customers
    elif m >= 4 and r >= 3:
        return "High Value"

    # Recent customers with lower frequency
    elif r >= 4 and f <= 3:
        return "Recent Customers"

    # Previously valuable but becoming inactive
    elif r <= 2 and m >= 4:
        return "At Risk High Value"

    # Low recency and low frequency
    elif r <= 2 and f <= 2:
        return "Hibernating"

    # Moderate / average customers
    elif r >= 3 and f >= 3:
        return "Potential Loyalists"

    else:
        return "Needs Attention"


df["rfm_segment"] = (
    df.apply(
        assign_rfm_segment,
        axis=1
    )
)


# ============================================================
# RFM SUMMARY
# ============================================================

print(
    "\n" + "-" * 70
)

print(
    "RFM SEGMENTATION"
)

print(
    "-" * 70
)

rfm_summary = (
    df["rfm_segment"]
    .value_counts()
)


for segment, count in rfm_summary.items():

    percentage = (
        count
        / len(df)
        * 100
    )

    print(
        f"  {segment}: "
        f"{count:,} "
        f"({percentage:.2f}%)"
    )
# ============================================================
# CHURN RISK BAND
# ============================================================

def assign_risk(probability):

    if probability >= 0.70:
        return "High Risk"

    elif probability >= 0.40:
        return "Medium Risk"

    else:
        return "Low Risk"


df["churn_risk"] = (
    df["churn_probability"]
    .apply(assign_risk)
)


# ============================================================
# CUSTOMER VALUE
# ============================================================
#
# Customer value is based on gross profit where available.
#
# If gross profit is negative, revenue is used as the
# economic value floor so that loss-making customers are
# not assigned a negative retention value.
#
# This avoids negative values distorting the retention score.
# ============================================================

df["customer_value"] = np.maximum(
    df["gross_profit"],
    0
)

df.loc[
    df["customer_value"] <= 0,
    "customer_value"
] = df.loc[
    df["customer_value"] <= 0,
    "total_revenue"
]


# ============================================================
# EXPECTED VALUE AT RISK
# ============================================================

df["expected_revenue_at_risk"] = (
    df["churn_probability"]
    * df["total_revenue"]
)

df["expected_profit_at_risk"] = (
    df["churn_probability"]
    * df["customer_value"]
)


# ============================================================
# RETENTION SCORE
# ============================================================
#
# The score combines:
#
#   1. Churn probability
#   2. Expected profit at risk
#
# The economic risk is normalized so that extremely
# large customers do not completely dominate the score.
#
# log1p reduces the influence of extreme customer values.
# ============================================================

value_component = np.log1p(
    df["expected_profit_at_risk"]
)

if value_component.max() > value_component.min():

    value_component = (
        (value_component - value_component.min())
        /
        (
            value_component.max()
            - value_component.min()
        )
    )

else:

    value_component = 0


df["retention_score"] = (
    0.60 * df["churn_probability"]
    +
    0.40 * value_component
)


# ============================================================
# RETENTION PRIORITY
# ============================================================
#
# Priority is based primarily on churn risk and economic
# value at risk.
#
# High:
#   Strong churn signal + meaningful economic exposure
#
# Medium:
#   Moderate churn/value exposure
#
# Monitor:
#   Some potential risk but lower immediate urgency
#
# Low:
#   Low immediate retention risk
# ============================================================

def assign_priority(row):

    probability = row["churn_probability"]

    expected_profit = row[
        "expected_profit_at_risk"
    ]

    expected_revenue = row[
        "expected_revenue_at_risk"
    ]

    # High priority:
    # high churn probability AND meaningful economic risk

    if (
        probability >= 0.70
        and expected_profit > 0
    ):

        return "High"

    # Medium priority:
    # moderate/high probability but lower economic exposure

    elif (
        probability >= 0.40
        and expected_revenue > 0
    ):

        return "Medium"

    # Monitor customers with meaningful risk signals

    elif probability >= 0.20:

        return "Monitor"

    else:

        return "Low"


df["retention_priority"] = (
    df.apply(
        assign_priority,
        axis=1
    )
)


# ============================================================
# RETENTION ACTION
# ============================================================

def assign_action(row):

    priority = row[
        "retention_priority"
    ]

    segment = row[
        "customer_segment"
    ]

    probability = row[
        "churn_probability"
    ]

    recency = row[
        "recency_days"
    ]


    if priority == "High":

        if segment == "high":

            return (
                "Immediate high-value retention outreach"
            )

        return (
            "Targeted retention campaign"
        )


    elif priority == "Medium":

        return (
            "Personalized re-engagement campaign"
        )


    elif priority == "Monitor":

        if recency >= 60:

            return (
                "Re-engagement monitoring"
            )

        return (
            "Monitor engagement and purchase activity"
        )


    return (
        "Low-touch retention monitoring"
    )


df["retention_action"] = (
    df.apply(
        assign_action,
        axis=1
    )
)


# ============================================================
# RETENTION RANK
# ============================================================
#
# Rank by economic retention priority:
#
#   1. Retention score
#   2. Expected profit at risk
#   3. Churn probability
#
# This prevents the list from being based purely on
# probability of churn.
# ============================================================

df = df.sort_values(
    by=[
        "retention_score",
        "expected_profit_at_risk",
        "churn_probability"
    ],
    ascending=[
        False,
        False,
        False
    ]
).reset_index(
    drop=True
)


df["retention_rank"] = (
    df.index + 1
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CHURN SCORING SUMMARY")
print("=" * 70)

print(
    f"\nCustomers scored: {len(df):,}"
)


# ============================================================
# RISK DISTRIBUTION
# ============================================================

risk_counts = (
    df["churn_risk"]
    .value_counts()
)


print("\nRisk distribution:")

for risk in [
    "High Risk",
    "Medium Risk",
    "Low Risk"
]:

    count = risk_counts.get(
        risk,
        0
    )

    percentage = (
        count
        /
        len(df)
        *
        100
    )

    print(
        f"  {risk}: "
        f"{count:,} "
        f"({percentage:.2f}%)"
    )


# ============================================================
# PREDICTED CHURN
# ============================================================

predicted_count = (
    df["predicted_churn"]
    .sum()
)

predicted_percentage = (
    predicted_count
    /
    len(df)
    *
    100
)


print(
    f"\nPredicted churn:"
)

print(
    f"  Predicted churners: "
    f"{predicted_count:,} "
    f"({predicted_percentage:.2f}%)"
)


# ============================================================
# RETENTION PRIORITY DISTRIBUTION
# ============================================================

priority_order = [
    "Critical",
    "High",
    "Medium",
    "Monitor",
    "Low"
]


print(
    "\nRetention priority:"
)

for priority in priority_order:

    count = (
        df["retention_priority"]
        .eq(priority)
        .sum()
    )

    print(
        f"  {priority}: {count:,}"
    )


# ============================================================
# CUSTOMER VALUE BY PRIORITY
# ============================================================

print(
    "\nCustomer value by retention priority:"
)

for priority in [
    "High",
    "Medium",
    "Monitor",
    "Low"
]:

    subset = df[
        df["retention_priority"]
        == priority
    ]

    if len(subset) == 0:

        print(
            f"  {priority}: 0 customers"
        )

        continue


    revenue = (
        subset["total_revenue"]
        .sum()
    )

    value = (
        subset["customer_value"]
        .sum()
    )

    revenue_risk = (
        subset[
            "expected_revenue_at_risk"
        ]
        .sum()
    )

    profit_risk = (
        subset[
            "expected_profit_at_risk"
        ]
        .sum()
    )


    print(
        f"  {priority}: "
        f"{len(subset):,} customers | "
        f"Revenue: ₹{revenue:,.2f} | "
        f"Customer value: ₹{value:,.2f} | "
        f"Revenue at risk: ₹{revenue_risk:,.2f} | "
        f"Profit at risk: ₹{profit_risk:,.2f}"
    )


# ============================================================
# TOTAL ECONOMIC RISK
# ============================================================

total_revenue_at_risk = (
    df["expected_revenue_at_risk"]
    .sum()
)

total_profit_at_risk = (
    df["expected_profit_at_risk"]
    .sum()
)


print(
    "\n" + "-" * 70
)

print(
    "TOTAL EXPECTED VALUE AT RISK"
)

print(
    f"\nExpected revenue at risk: "
    f"₹{total_revenue_at_risk:,.2f}"
)

print(
    f"Expected profit at risk: "
    f"₹{total_profit_at_risk:,.2f}"
)


# ============================================================
# TOP 10 RETENTION PRIORITIES
# ============================================================

print(
    "\n" + "-" * 70
)

print(
    "TOP 10 RETENTION PRIORITIES"
)

print("-" * 70)


top_columns = [
    "retention_rank",
    "customer_id",
    "customer_segment",
    "location",
    "acquisition_channel",
    "total_revenue",
    "customer_value",
    "expected_revenue_at_risk",
    "expected_profit_at_risk",
    "recency_days",
    "churn_probability_percentage",
    "churn_risk",
    "retention_score",
    "retention_priority",
    "retention_action"
]


print(
    df[
        top_columns
    ]
    .head(10)
    .to_string(
        index=False
    )
)


# ============================================================
# SAVE OUTPUT
# ============================================================

df.to_csv(
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
    "CUSTOMER CHURN SCORING COMPLETE"
)

print(
    "=" * 70
)

print(
    f"\nSaved scored dataset to:"
)

print(
    OUTPUT_FILE
)


print(
    "\nOutput contains:"
)

output_columns = [
    "Churn probability",
    "Churn risk band",
    "Predicted churn",
    "Customer value",
    "Expected revenue at risk",
    "Expected profit at risk",
    "Retention score",
    "Retention priority",
    "Recommended retention action",
    "Retention rank",
    "RFM Recency Score",
    "RFM Frequency Score",
    "RFM Monetary Score",
    "RFM Score",
    "RFM Total Score",
    "RFM Segment"
]

for column in output_columns:

    print(
        f"  - {column}"
    )


print(
    "\nReady for:"
)

print(
    "  - Retention analysis"
)

print(
    "  - Power BI dashboard"
)

print(
    "  - Customer-level targeting"
)

print(
    "  - Business recommendations"
)

print(
    "\nFinal model: Random Forest"
)

print(
    f"Customers scored: {len(df):,}"
)

print(
    "\n" + "=" * 70
)