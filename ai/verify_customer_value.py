from customeriq_ai import load_customer_data


# ============================================================
# CUSTOMERIQ — VERIFY HIGH-RISK CUSTOMER VALUE
# ============================================================

df = load_customer_data()


print("\n" + "=" * 60)
print("CUSTOMERIQ — HIGH-RISK CUSTOMER VALUE VERIFICATION")
print("=" * 60)


# ============================================================
# DATASET OVERVIEW
# ============================================================

print("\nTOTAL CUSTOMERS")
print(len(df))


print("\nCHURN RISK DISTRIBUTION")

print(
    df["churn_risk"]
    .value_counts(dropna=False)
    .to_string()
)


# ============================================================
# HIGH-RISK CUSTOMERS
# ============================================================

high_risk = df[
    df["churn_risk"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "high risk"
].copy()


print("\nHIGH-RISK CUSTOMERS")
print(len(high_risk))


# ============================================================
# CUSTOMER VALUE STATISTICS
# ============================================================

print("\nHIGH-RISK CUSTOMER VALUE STATISTICS")

print(
    high_risk["customer_value"]
    .describe()
    .to_string()
)


# ============================================================
# AVERAGE
# ============================================================

average_value = (
    high_risk["customer_value"]
    .mean()
)


print("\nAVERAGE CUSTOMER VALUE OF HIGH-RISK CUSTOMERS")

print(
    f"₹{average_value:,.2f}"
)


# ============================================================
# MEDIAN
# ============================================================

median_value = (
    high_risk["customer_value"]
    .median()
)


print("\nMEDIAN CUSTOMER VALUE OF HIGH-RISK CUSTOMERS")

print(
    f"₹{median_value:,.2f}"
)


# ============================================================
# MINIMUM / MAXIMUM
# ============================================================

minimum_value = (
    high_risk["customer_value"]
    .min()
)

maximum_value = (
    high_risk["customer_value"]
    .max()
)


print("\nMINIMUM HIGH-RISK CUSTOMER VALUE")

print(
    f"₹{minimum_value:,.2f}"
)


print("\nMAXIMUM HIGH-RISK CUSTOMER VALUE")

print(
    f"₹{maximum_value:,.2f}"
)


# ============================================================
# TOP 20 HIGH-RISK CUSTOMERS BY VALUE
# ============================================================

print(
    "\nTOP 20 HIGH-RISK CUSTOMERS BY CUSTOMER VALUE"
)


top_value = (
    high_risk[
        [
            "customer_id",
            "customer_value",
            "churn_probability_percentage",
            "expected_revenue_at_risk"
        ]
    ]
    .sort_values(
        "customer_value",
        ascending=False
    )
    .head(20)
)


print(
    top_value.to_string(
        index=False
    )
)


# ============================================================
# BOTTOM 20
# ============================================================

print(
    "\nBOTTOM 20 HIGH-RISK CUSTOMERS BY CUSTOMER VALUE"
)


bottom_value = (
    high_risk[
        [
            "customer_id",
            "customer_value",
            "churn_probability_percentage",
            "expected_revenue_at_risk"
        ]
    ]
    .sort_values(
        "customer_value",
        ascending=True
    )
    .head(20)
)


print(
    bottom_value.to_string(
        index=False
    )
)


# ============================================================
# CROSS-CHECK AGAINST EXPECTED REVENUE AT RISK
# ============================================================

print(
    "\nHIGH-RISK CUSTOMERS — REVENUE EXPOSURE"
)


print(
    f"Total customer value: "
    f"₹{high_risk['customer_value'].sum():,.2f}"
)


print(
    f"Total expected revenue at risk: "
    f"₹{high_risk['expected_revenue_at_risk'].sum():,.2f}"
)


# ============================================================
# FINAL
# ============================================================

print(
    "\n" + "=" * 60
)

print(
    "VERIFICATION COMPLETE"
)

print(
    "=" * 60
)