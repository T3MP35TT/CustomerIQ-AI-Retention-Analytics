import pandas as pd
from pathlib import Path


# ============================================================
# CUSTOMERIQ — DATA AUDIT
# ============================================================

DATA_DIR = Path("data")


FILES = {
    "customers": "customers.csv",
    "transactions": "transactions.csv",
    "products": "products.csv",
    "interactions": "interactions.csv"
}


def audit_dataset(name, filename):

    print("\n" + "=" * 70)
    print(f"{name.upper()} DATASET")
    print("=" * 70)

    file_path = DATA_DIR / filename

    df = pd.read_csv(file_path)

    print(f"\nRows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]:,}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")

    missing = df.isna().sum()

    missing = missing[
        missing > 0
    ]

    if len(missing) == 0:
        print("  No missing values")
    else:
        for column, count in missing.items():

            percentage = (
                count
                / len(df)
                * 100
            )

            print(
                f"  - {column}: "
                f"{count:,} "
                f"({percentage:.2f}%)"
            )

    print("\nDuplicate Rows:")

    duplicates = df.duplicated().sum()

    print(
        f"  {duplicates:,}"
    )

    return df


# ============================================================
# RUN AUDIT
# ============================================================

datasets = {}

for name, filename in FILES.items():

    datasets[name] = audit_dataset(
        name,
        filename
    )


# ============================================================
# PRIMARY KEY CHECKS
# ============================================================

print("\n" + "=" * 70)
print("PRIMARY KEY VALIDATION")
print("=" * 70)


key_checks = {

    "customers": "customer_id",

    "transactions": "transaction_id",

    "products": "product_id",

    "interactions": "interaction_id"
}


for table, key in key_checks.items():

    df = datasets[table]

    duplicate_keys = (
        df[key]
        .duplicated()
        .sum()
    )

    null_keys = (
        df[key]
        .isna()
        .sum()
    )

    print(
        f"\n{table}:"
    )

    print(
        f"  {key} duplicate values: "
        f"{duplicate_keys:,}"
    )

    print(
        f"  {key} missing values: "
        f"{null_keys:,}"
    )


# ============================================================
# RELATIONSHIP VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("FOREIGN KEY VALIDATION")
print("=" * 70)


customers = datasets["customers"]
transactions = datasets["transactions"]
products = datasets["products"]
interactions = datasets["interactions"]


# Transactions → Customers

invalid_transaction_customers = (
    ~transactions["customer_id"]
    .isin(customers["customer_id"])
).sum()


print(
    "\nTransactions → Customers:"
)

print(
    f"  Invalid customer IDs: "
    f"{invalid_transaction_customers:,}"
)


# Transactions → Products

invalid_transaction_products = (
    ~transactions["product_id"]
    .isin(products["product_id"])
).sum()


print(
    "\nTransactions → Products:"
)

print(
    f"  Invalid product IDs: "
    f"{invalid_transaction_products:,}"
)


# Interactions → Customers

invalid_interaction_customers = (
    ~interactions["customer_id"]
    .isin(customers["customer_id"])
).sum()


print(
    "\nInteractions → Customers:"
)

print(
    f"  Invalid customer IDs: "
    f"{invalid_interaction_customers:,}"
)


# Interactions → Products
#
# Missing product_id values are allowed here
# because some interaction types may not be
# product-specific.

interaction_product_check = interactions[
    interactions["product_id"].notna()
]

invalid_interaction_products = (
    ~interaction_product_check["product_id"]
    .isin(products["product_id"])
).sum()


print(
    "\nInteractions → Products:"
)

print(
    f"  Invalid non-null product IDs: "
    f"{invalid_interaction_products:,}"
)


# ============================================================
# INTERACTION TYPE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("INTERACTION TYPE ANALYSIS")
print("=" * 70)


interaction_summary = (
    interactions[
        "interaction_type"
    ]
    .value_counts()
)


print(
    interaction_summary
)


print("\nMissing product_id by interaction type:")


missing_product_summary = (
    interactions
    .assign(
        Product_ID_Missing=
        interactions["product_id"].isna()
    )
    .groupby("interaction_type")[
        "Product_ID_Missing"
    ]
    .agg(
        Total_Interactions="count",
        Missing_Product_ID="sum"
    )
)


missing_product_summary[
    "Missing_Percentage"
] = (
    missing_product_summary[
        "Missing_Product_ID"
    ]
    /
    missing_product_summary[
        "Total_Interactions"
    ]
    * 100
)


print(
    missing_product_summary
)


# ============================================================
# DATE RANGE CHECK
# ============================================================

print("\n" + "=" * 70)
print("DATE RANGE")
print("=" * 70)


transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
)

customers["signup_date"] = pd.to_datetime(
    customers["signup_date"]
)

products["launch_date"] = pd.to_datetime(
    products["launch_date"]
)

interactions["interaction_timestamp"] = pd.to_datetime(
    interactions["interaction_timestamp"]
)


print(
    "\nCustomer signup:"
)

print(
    customers["signup_date"].min(),
    "→",
    customers["signup_date"].max()
)


print(
    "\nTransactions:"
)

print(
    transactions["transaction_date"].min(),
    "→",
    transactions["transaction_date"].max()
)


print(
    "\nProducts:"
)

print(
    products["launch_date"].min(),
    "→",
    products["launch_date"].max()
)


print(
    "\nInteractions:"
)

print(
    interactions["interaction_timestamp"].min(),
    "→",
    interactions["interaction_timestamp"].max()
)


print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)