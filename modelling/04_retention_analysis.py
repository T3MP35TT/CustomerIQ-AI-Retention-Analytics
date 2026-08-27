import pandas as pd
import numpy as np

from pathlib import Path


# ============================================================
# CUSTOMERIQ
# RETENTION ANALYSIS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "churn_scored_customers.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)


print("=" * 70)
print("CUSTOMERIQ — RETENTION ANALYSIS")
print("=" * 70)

print(
    f"\nDataset:\n{DATA_FILE}"
)

print(
    f"\nCustomers: {len(df):,}"
)


# ============================================================
# VALIDATION
# ============================================================

required_columns = [
    "customer_id",
    "customer_segment",
    "acquisition_channel",
    "location",
    "total_orders",
    "total_revenue",
    "gross_profit",
    "recency_days",
    "churn_probability",
    "churn_risk",
    "predicted_churn",
    "customer_value",
    "expected_revenue_at_risk",
    "expected_profit_at_risk",
    "retention_score",
    "retention_priority",
    "retention_action",
    "retention_rank",
    "rfm_segment",
    "rfm_total_score"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print("\nERROR: Required columns missing:")

    for column in missing_columns:
        print(f"  - {column}")

    raise ValueError(
        "Scored dataset is missing required columns."
    )


print(
    "\nAll required columns are available."
)


# ============================================================
# BASIC MODEL / SCORING SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("1. CHURN OVERVIEW")
print("=" * 70)


total_customers = len(df)

predicted_churners = int(
    df["predicted_churn"].sum()
)

predicted_churn_rate = (
    predicted_churners
    / total_customers
    * 100
)


print(
    f"\nTotal customers: "
    f"{total_customers:,}"
)

print(
    f"Predicted churners: "
    f"{predicted_churners:,}"
)

print(
    f"Predicted churn rate: "
    f"{predicted_churn_rate:.2f}%"
)


# ============================================================
# 2. RISK DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("2. CHURN RISK DISTRIBUTION")
print("=" * 70)


risk_summary = (
    df
    .groupby("churn_risk")
    .agg(
        customers=(
            "customer_id",
            "count"
        ),

        revenue=(
            "total_revenue",
            "sum"
        ),

        customer_value=(
            "customer_value",
            "sum"
        ),

        expected_revenue_at_risk=(
            "expected_revenue_at_risk",
            "sum"
        ),

        expected_profit_at_risk=(
            "expected_profit_at_risk",
            "sum"
        ),

        avg_churn_probability=(
            "churn_probability",
            "mean"
        )
    )
    .reset_index()
)


risk_summary["customer_percentage"] = (
    risk_summary["customers"]
    / total_customers
    * 100
)


risk_summary["avg_churn_probability"] = (
    risk_summary["avg_churn_probability"]
    * 100
)


risk_summary = risk_summary.sort_values(
    "expected_revenue_at_risk",
    ascending=False
)


print(
    risk_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 3. RETENTION PRIORITY
# ============================================================

print("\n" + "=" * 70)
print("3. RETENTION PRIORITY")
print("=" * 70)


priority_summary = (
    df
    .groupby("retention_priority")
    .agg(
        customers=(
            "customer_id",
            "count"
        ),

        revenue=(
            "total_revenue",
            "sum"
        ),

        customer_value=(
            "customer_value",
            "sum"
        ),

        expected_revenue_at_risk=(
            "expected_revenue_at_risk",
            "sum"
        ),

        expected_profit_at_risk=(
            "expected_profit_at_risk",
            "sum"
        ),

        avg_churn_probability=(
            "churn_probability",
            "mean"
        ),

        avg_retention_score=(
            "retention_score",
            "mean"
        )
    )
    .reset_index()
)


priority_summary["customer_percentage"] = (
    priority_summary["customers"]
    / total_customers
    * 100
)


priority_summary["avg_churn_probability"] = (
    priority_summary["avg_churn_probability"]
    * 100
)


priority_summary = priority_summary.sort_values(
    "expected_revenue_at_risk",
    ascending=False
)


print(
    priority_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 4. RFM SEGMENT ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("4. RFM SEGMENT ANALYSIS")
print("=" * 70)


rfm_summary = (
    df
    .groupby("rfm_segment")
    .agg(
        customers=(
            "customer_id",
            "count"
        ),

        revenue=(
            "total_revenue",
            "sum"
        ),

        customer_value=(
            "customer_value",
            "sum"
        ),

        expected_revenue_at_risk=(
            "expected_revenue_at_risk",
            "sum"
        ),

        expected_profit_at_risk=(
            "expected_profit_at_risk",
            "sum"
        ),

        avg_churn_probability=(
            "churn_probability",
            "mean"
        ),

        avg_recency_days=(
            "recency_days",
            "mean"
        ),

        avg_orders=(
            "total_orders",
            "mean"
        )
    )
    .reset_index()
)


rfm_summary["customer_percentage"] = (
    rfm_summary["customers"]
    / total_customers
    * 100
)


rfm_summary["avg_churn_probability"] = (
    rfm_summary["avg_churn_probability"]
    * 100
)


rfm_summary = rfm_summary.sort_values(
    "expected_revenue_at_risk",
    ascending=False
)


print(
    rfm_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 5. RFM × CHURN RISK
# ============================================================

print("\n" + "=" * 70)
print("5. RFM × CHURN RISK")
print("=" * 70)


rfm_risk = (
    df
    .groupby(
        [
            "rfm_segment",
            "churn_risk"
        ]
    )
    .agg(
        customers=(
            "customer_id",
            "count"
        ),

        revenue=(
            "total_revenue",
            "sum"
        ),

        expected_revenue_at_risk=(
            "expected_revenue_at_risk",
            "sum"
        ),

        expected_profit_at_risk=(
            "expected_profit_at_risk",
            "sum"
        ),

        avg_churn_probability=(
            "churn_probability",
            "mean"
        )
    )
    .reset_index()
)


rfm_risk["avg_churn_probability"] = (
    rfm_risk["avg_churn_probability"]
    * 100
)


rfm_risk = rfm_risk.sort_values(
    "expected_revenue_at_risk",
    ascending=False
)


print(
    rfm_risk
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 6. ACQUISITION CHANNEL ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("6. ACQUISITION CHANNEL ANALYSIS")
print("=" * 70)


channel_summary = (
    df
    .groupby("acquisition_channel")
    .agg(
        customers=(
            "customer_id",
            "count"
        ),

        revenue=(
            "total_revenue",
            "sum"
        ),

        customer_value=(
            "customer_value",
            "sum"
        ),

        expected_revenue_at_risk=(
            "expected_revenue_at_risk",
            "sum"
        ),

        expected_profit_at_risk=(
            "expected_profit_at_risk",
            "sum"
        ),

        avg_churn_probability=(
            "churn_probability",
            "mean"
        ),

        predicted_churners=(
            "predicted_churn",
            "sum"
        )
    )
    .reset_index()
)


channel_summary["churn_rate"] = (
    channel_summary["predicted_churners"]
    / channel_summary["customers"]
    * 100
)


channel_summary["avg_churn_probability"] = (
    channel_summary["avg_churn_probability"]
    * 100
)


channel_summary = channel_summary.sort_values(
    "expected_revenue_at_risk",
    ascending=False
)


print(
    channel_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 7. LOCATION ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("7. LOCATION ANALYSIS")
print("=" * 70)


location_summary = (
    df
    .groupby("location")
    .agg(
        customers=(
            "customer_id",
            "count"
        ),

        revenue=(
            "total_revenue",
            "sum"
        ),

        customer_value=(
            "customer_value",
            "sum"
        ),

        expected_revenue_at_risk=(
            "expected_revenue_at_risk",
            "sum"
        ),

        expected_profit_at_risk=(
            "expected_profit_at_risk",
            "sum"
        ),

        avg_churn_probability=(
            "churn_probability",
            "mean"
        ),

        predicted_churners=(
            "predicted_churn",
            "sum"
        )
    )
    .reset_index()
)


location_summary["churn_rate"] = (
    location_summary["predicted_churners"]
    / location_summary["customers"]
    * 100
)


location_summary["avg_churn_probability"] = (
    location_summary["avg_churn_probability"]
    * 100
)


location_summary = location_summary.sort_values(
    "expected_revenue_at_risk",
    ascending=False
)


print(
    location_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 8. CUSTOMER SEGMENT ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("8. CUSTOMER SEGMENT ANALYSIS")
print("=" * 70)


segment_summary = (
    df
    .groupby("customer_segment")
    .agg(
        customers=(
            "customer_id",
            "count"
        ),

        revenue=(
            "total_revenue",
            "sum"
        ),

        customer_value=(
            "customer_value",
            "sum"
        ),

        expected_revenue_at_risk=(
            "expected_revenue_at_risk",
            "sum"
        ),

        expected_profit_at_risk=(
            "expected_profit_at_risk",
            "sum"
        ),

        avg_churn_probability=(
            "churn_probability",
            "mean"
        ),

        predicted_churners=(
            "predicted_churn",
            "sum"
        )
    )
    .reset_index()
)


segment_summary["churn_rate"] = (
    segment_summary["predicted_churners"]
    / segment_summary["customers"]
    * 100
)


segment_summary["avg_churn_probability"] = (
    segment_summary["avg_churn_probability"]
    * 100
)


segment_summary = segment_summary.sort_values(
    "expected_revenue_at_risk",
    ascending=False
)


print(
    segment_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 9. HIGH-VALUE AT-RISK CUSTOMERS
# ============================================================

print("\n" + "=" * 70)
print("9. HIGH-VALUE AT-RISK CUSTOMERS")
print("=" * 70)


high_value_risk = (
    df[
        (
            df["churn_probability"] >= 0.50
        )
        &
        (
            df["customer_value"] > 0
        )
    ]
    .sort_values(
        "expected_revenue_at_risk",
        ascending=False
    )
)


print(
    f"\nHigh-risk customers: "
    f"{len(high_value_risk):,}"
)


print(
    f"Revenue at risk: ₹"
    f"{high_value_risk['expected_revenue_at_risk'].sum():,.2f}"
)


print(
    f"Profit at risk: ₹"
    f"{high_value_risk['expected_profit_at_risk'].sum():,.2f}"
)


print(
    "\nTop 20 high-value at-risk customers:"
)


top_columns = [
    "customer_id",
    "customer_segment",
    "location",
    "acquisition_channel",
    "rfm_segment",
    "total_revenue",
    "customer_value",
    "expected_revenue_at_risk",
    "expected_profit_at_risk",
    "recency_days",
    "churn_probability",
    "retention_score",
    "retention_priority"
]


print(
    high_value_risk[
        top_columns
    ]
    .head(20)
    .round(3)
    .to_string(index=False)
)


# ============================================================
# 10. TOP RETENTION TARGETS
# ============================================================

print("\n" + "=" * 70)
print("10. TOP RETENTION TARGETS")
print("=" * 70)


top_targets = (
    df
    .sort_values(
        [
            "retention_score",
            "expected_revenue_at_risk"
        ],
        ascending=False
    )
    .head(25)
)


print(
    top_targets[
        [
            "retention_rank",
            "customer_id",
            "rfm_segment",
            "churn_risk",
            "retention_priority",
            "total_revenue",
            "expected_revenue_at_risk",
            "expected_profit_at_risk",
            "recency_days",
            "retention_action"
        ]
    ]
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 11. TOTAL VALUE AT RISK
# ============================================================

print("\n" + "=" * 70)
print("11. TOTAL EXPECTED VALUE AT RISK")
print("=" * 70)


total_revenue_at_risk = (
    df["expected_revenue_at_risk"]
    .sum()
)


total_profit_at_risk = (
    df["expected_profit_at_risk"]
    .sum()
)


total_customer_value = (
    df["customer_value"]
    .sum()
)


print(
    f"\nTotal customer value: "
    f"₹{total_customer_value:,.2f}"
)


print(
    f"Expected revenue at risk: "
    f"₹{total_revenue_at_risk:,.2f}"
)


print(
    f"Expected profit at risk: "
    f"₹{total_profit_at_risk:,.2f}"
)


# ============================================================
# 12. CONCENTRATION OF RISK
# ============================================================

print("\n" + "=" * 70)
print("12. RISK CONCENTRATION")
print("=" * 70)


top_10_risk = (
    df
    .sort_values(
        "expected_revenue_at_risk",
        ascending=False
    )
    .head(10)
)


top_25_risk = (
    df
    .sort_values(
        "expected_revenue_at_risk",
        ascending=False
    )
    .head(25)
)


top_10_share = (
    top_10_risk[
        "expected_revenue_at_risk"
    ].sum()
    / total_revenue_at_risk
    * 100
)


top_25_share = (
    top_25_risk[
        "expected_revenue_at_risk"
    ].sum()
    / total_revenue_at_risk
    * 100
)


print(
    f"\nTop 10 customers account for "
    f"{top_10_share:.2f}% of expected revenue at risk."
)


print(
    f"Top 25 customers account for "
    f"{top_25_share:.2f}% of expected revenue at risk."
)


# ============================================================
# 13. EXPORT ANALYSIS TABLES
# ============================================================

print("\n" + "=" * 70)
print("EXPORTING RETENTION ANALYSIS")
print("=" * 70)


exports = {

    "retention_risk_summary.csv":
        risk_summary,

    "retention_priority_summary.csv":
        priority_summary,

    "retention_rfm_summary.csv":
        rfm_summary,

    "retention_rfm_risk.csv":
        rfm_risk,

    "retention_channel_summary.csv":
        channel_summary,

    "retention_location_summary.csv":
        location_summary,

    "retention_segment_summary.csv":
        segment_summary,

    "retention_top_targets.csv":
        top_targets,

    "retention_high_value_risk.csv":
        high_value_risk
}


for filename, table in exports.items():

    output_file = (
        OUTPUT_DIR
        / filename
    )

    table.to_csv(
        output_file,
        index=False
    )

    print(
        f"Saved: {output_file}"
    )


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("RETENTION ANALYSIS COMPLETE")
print("=" * 70)

print(
    "\nAnalysis includes:"
)

print(
    "  - Churn risk distribution"
)

print(
    "  - Retention priority analysis"
)

print(
    "  - RFM segment analysis"
)

print(
    "  - RFM × churn risk"
)

print(
    "  - Acquisition channel analysis"
)

print(
    "  - Location analysis"
)

print(
    "  - Customer segment analysis"
)

print(
    "  - High-value at-risk customers"
)

print(
    "  - Top retention targets"
)

print(
    "  - Expected revenue/profit at risk"
)

print(
    "  - Risk concentration"
)

print(
    "\nReady for Power BI retention dashboard."
)

print(
    "=" * 70
)