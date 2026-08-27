import pandas as pd
from pathlib import Path


# ============================================================
# CUSTOMERIQ
# CHURN MODELING — EDA & DATA VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "churn_modeling_dataset.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    DATA_FILE
)


print("=" * 70)
print("CUSTOMERIQ — CHURN MODELING EDA")
print("=" * 70)

print(
    f"\nDataset:\n{DATA_FILE}"
)


# ============================================================
# DATASET OVERVIEW
# ============================================================

print("\n" + "-" * 70)
print("DATASET OVERVIEW")
print("-" * 70)

print(
    f"\nRows: {len(df):,}"
)

print(
    f"Columns: {len(df.columns):,}"
)

print(
    f"Memory usage: "
    f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
)


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

print("\n" + "-" * 70)
print("TARGET DISTRIBUTION")
print("-" * 70)

target_distribution = (
    df["churned"]
    .value_counts()
    .sort_index()
)

for value, count in target_distribution.items():

    percentage = (
        count
        / len(df)
        * 100
    )

    label = (
        "Retained"
        if value == 0
        else "Churned"
    )

    print(
        f"{label:<10}: "
        f"{count:>5,} "
        f"({percentage:>6.2f}%)"
    )


# ============================================================
# MISSING VALUES
# ============================================================

print("\n" + "-" * 70)
print("MISSING VALUES")
print("-" * 70)

missing = (
    df.isna()
    .sum()
)

missing = (
    missing[missing > 0]
    .sort_values(ascending=False)
)

if missing.empty:

    print(
        "\nNo missing values found."
    )

else:

    print(
        missing
    )


# ============================================================
# DUPLICATES
# ============================================================

print("\n" + "-" * 70)
print("DUPLICATE CHECK")
print("-" * 70)

print(
    f"\nDuplicate rows: "
    f"{df.duplicated().sum():,}"
)

print(
    f"Duplicate customer IDs: "
    f"{df['customer_id'].duplicated().sum():,}"
)


# ============================================================
# DATA TYPES
# ============================================================

print("\n" + "-" * 70)
print("DATA TYPES")
print("-" * 70)

print(
    df.dtypes
)


# ============================================================
# NUMERICAL SUMMARY
# ============================================================

print("\n" + "-" * 70)
print("NUMERICAL FEATURE SUMMARY")
print("-" * 70)

numeric_columns = (
    df.select_dtypes(
        include="number"
    )
    .columns
)

print(
    df[numeric_columns]
    .describe()
    .round(2)
    .to_string()
)


# ============================================================
# CATEGORICAL DISTRIBUTIONS
# ============================================================

print("\n" + "-" * 70)
print("CATEGORICAL FEATURES")
print("-" * 70)

categorical_columns = [
    "customer_segment",
    "acquisition_channel",
    "location",
    "gender"
]

for column in categorical_columns:

    print(
        f"\n{column}:"
    )

    print(
        df[column]
        .value_counts()
        .to_string()
    )


# ============================================================
# CHURN BY CATEGORICAL FEATURES
# ============================================================

print("\n" + "-" * 70)
print("CHURN RATE BY CATEGORICAL FEATURES")
print("-" * 70)

for column in categorical_columns:

    churn_summary = (
        df.groupby(column)["churned"]
        .agg(
            customers="count",
            churned="sum",
            churn_rate="mean"
        )
        .sort_values(
            "churn_rate",
            ascending=False
        )
    )

    churn_summary["churn_rate"] *= 100

    print(
        f"\n{column}:"
    )

    print(
        churn_summary
        .round(2)
        .to_string()
    )


# ============================================================
# NUMERICAL FEATURES — CHURN COMPARISON
# ============================================================

print("\n" + "-" * 70)
print("NUMERICAL FEATURES — RETAINED VS CHURNED")
print("-" * 70)

comparison_columns = [
    "age",
    "total_orders",
    "total_units",
    "total_revenue",
    "net_revenue",
    "total_cost",
    "gross_profit",
    "gross_margin_percentage",
    "average_order_value",
    "recency_days",
    "customer_lifespan_days",
    "total_interactions",
    "views",
    "clicks",
    "add_to_carts",
    "email_opens",
    "channels_used",
    "interaction_types_used",
    "annualized_order_frequency",
    "click_rate",
    "add_to_cart_rate",
    "email_open_share"
]

comparison = (
    df.groupby("churned")[comparison_columns]
    .mean()
    .T
)

comparison.columns = [
    "Retained",
    "Churned"
]

comparison["Difference"] = (
    comparison["Churned"]
    - comparison["Retained"]
)

print(
    comparison
    .round(2)
    .to_string()
)


# ============================================================
# FEATURE CORRELATION WITH TARGET
# ============================================================

print("\n" + "-" * 70)
print("NUMERICAL FEATURE CORRELATION WITH CHURN")
print("-" * 70)

correlation = (
    df[comparison_columns + ["churned"]]
    .corr()["churned"]
    .drop("churned")
    .sort_values()
)

print(
    correlation
    .round(4)
    .to_string()
)


# ============================================================
# MODELING FEATURE LIST
# ============================================================

feature_columns = [
    "customer_segment",
    "acquisition_channel",
    "location",
    "age",
    "gender",
    "total_orders",
    "total_units",
    "total_revenue",
    "net_revenue",
    "total_cost",
    "gross_profit",
    "gross_margin_percentage",
    "average_order_value",
    "recency_days",
    "customer_lifespan_days",
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
    "email_open_share"
]


ignored_columns = [
    "customer_id",
    "first_purchase_date",
    "last_purchase_date",
    "future_orders",
    "future_revenue",
    "churned"
]


print("\n" + "-" * 70)
print("MODELING FEATURES")
print("-" * 70)

print(
    f"\nPredictive features: "
    f"{len(feature_columns)}"
)

for column in feature_columns:

    print(
        f"  ✓ {column}"
    )


print("\n" + "-" * 70)
print("IGNORED COLUMNS")
print("-" * 70)

for column in ignored_columns:

    print(
        f"  - {column}"
    )


# ============================================================
# FINAL FEATURE VALIDATION
# ============================================================

missing_features = [
    column
    for column in feature_columns
    if column not in df.columns
]

if missing_features:

    raise ValueError(
        "Missing modeling features: "
        + ", ".join(missing_features)
    )


unexpected_target_in_features = (
    "churned" in feature_columns
    or "future_orders" in feature_columns
    or "future_revenue" in feature_columns
)

if unexpected_target_in_features:

    raise ValueError(
        "Target leakage detected in modeling features."
    )


print("\n" + "=" * 70)
print("EDA COMPLETE")
print("=" * 70)

print(
    "\nDataset is ready for preprocessing and model training."
)