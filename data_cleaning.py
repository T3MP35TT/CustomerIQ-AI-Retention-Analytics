import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CUSTOMERIQ
# DATA CLEANING & BUSINESS-RULE VALIDATION
# ============================================================

# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
CLEAN_DIR = DATA_DIR / "clean"

CLEAN_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# INPUT FILES
# ------------------------------------------------------------

CUSTOMERS_FILE = DATA_DIR / "customers.csv"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
PRODUCTS_FILE = DATA_DIR / "products.csv"
INTERACTIONS_FILE = DATA_DIR / "interactions.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("CUSTOMERIQ — DATA CLEANING")
print("=" * 70)

print("\nLoading datasets...")

customers = pd.read_csv(
    CUSTOMERS_FILE
)

transactions = pd.read_csv(
    TRANSACTIONS_FILE
)

products = pd.read_csv(
    PRODUCTS_FILE
)

interactions = pd.read_csv(
    INTERACTIONS_FILE
)

print("✓ Customers loaded")
print("✓ Transactions loaded")
print("✓ Products loaded")
print("✓ Interactions loaded")


# ============================================================
# INITIAL RECORD COUNTS
# ============================================================

initial_counts = {
    "customers": len(customers),
    "transactions": len(transactions),
    "products": len(products),
    "interactions": len(interactions)
}


print("\nInitial record counts:")

for dataset, count in initial_counts.items():

    print(
        f"  {dataset:<15} {count:,}"
    )


# ============================================================
# STANDARDIZE COLUMN NAMES
# ============================================================

def standardize_columns(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


customers = standardize_columns(
    customers
)

transactions = standardize_columns(
    transactions
)

products = standardize_columns(
    products
)

interactions = standardize_columns(
    interactions
)


# ============================================================
# REMOVE EXACT DUPLICATES
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATE CHECK")
print("=" * 70)


def remove_duplicates(df, name):

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    print(
        f"{name:<15} duplicates removed: "
        f"{removed:,}"
    )

    return df


customers = remove_duplicates(
    customers,
    "Customers"
)

transactions = remove_duplicates(
    transactions,
    "Transactions"
)

products = remove_duplicates(
    products,
    "Products"
)

interactions = remove_duplicates(
    interactions,
    "Interactions"
)


# ============================================================
# DATE CONVERSION
# ============================================================

print("\n" + "=" * 70)
print("DATE CONVERSION")
print("=" * 70)


customers["signup_date"] = pd.to_datetime(
    customers["signup_date"],
    errors="coerce"
)

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)

products["launch_date"] = pd.to_datetime(
    products["launch_date"],
    errors="coerce"
)

interactions["interaction_timestamp"] = pd.to_datetime(
    interactions["interaction_timestamp"],
    errors="coerce"
)


print("✓ Customer signup dates converted")
print("✓ Transaction dates converted")
print("✓ Product launch dates converted")
print("✓ Interaction timestamps converted")


# ============================================================
# DATE VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("DATE VALIDATION")
print("=" * 70)


date_checks = {

    "customers_invalid_signup_dates":
        customers["signup_date"].isna().sum(),

    "transactions_invalid_dates":
        transactions["transaction_date"].isna().sum(),

    "products_invalid_launch_dates":
        products["launch_date"].isna().sum(),

    "interactions_invalid_timestamps":
        interactions["interaction_timestamp"].isna().sum()
}


for check, count in date_checks.items():

    print(
        f"{check:<40} {count:,}"
    )


# ============================================================
# CUSTOMER VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("CUSTOMER BUSINESS-RULE VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# AGE VALIDATION
# ------------------------------------------------------------

invalid_age = (
    (customers["age"] < 18)
    |
    (customers["age"] > 100)
)


print(
    f"Invalid age records: "
    f"{invalid_age.sum():,}"
)


if invalid_age.sum() > 0:

    customers.loc[
        invalid_age,
        "age"
    ] = np.nan


# ------------------------------------------------------------
# REQUIRED CUSTOMER FIELDS
# ------------------------------------------------------------

customer_required = [
    "customer_id",
    "signup_date"
]


for column in customer_required:

    missing = customers[column].isna().sum()

    print(
        f"Missing {column}: "
        f"{missing:,}"
    )


# ============================================================
# TRANSACTION VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("TRANSACTION BUSINESS-RULE VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# QUANTITY
# ------------------------------------------------------------

invalid_quantity = (
    transactions["quantity"] <= 0
)


print(
    f"Invalid quantity records: "
    f"{invalid_quantity.sum():,}"
)


# ------------------------------------------------------------
# PRICE
# ------------------------------------------------------------

invalid_price = (
    transactions["price"] < 0
)


print(
    f"Invalid transaction price records: "
    f"{invalid_price.sum():,}"
)


# ------------------------------------------------------------
# DISCOUNT
# ------------------------------------------------------------

invalid_discount = (
    (transactions["discount"] < 0)
    |
    (transactions["discount"] > 1)
)


print(
    f"Invalid discount records: "
    f"{invalid_discount.sum():,}"
)


# ------------------------------------------------------------
# REMOVE INVALID TRANSACTIONS
# ------------------------------------------------------------

transaction_invalid_mask = (
    invalid_quantity
    |
    invalid_price
    |
    invalid_discount
)


invalid_transaction_count = (
    transaction_invalid_mask.sum()
)


if invalid_transaction_count > 0:

    transactions = transactions[
        ~transaction_invalid_mask
    ].copy()


print(
    f"Invalid transaction records removed: "
    f"{invalid_transaction_count:,}"
)


# ============================================================
# PRODUCT VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("PRODUCT BUSINESS-RULE VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# PRODUCT PRICE
# ------------------------------------------------------------

invalid_product_price = (
    products["price"] < 0
)


print(
    f"Invalid product prices: "
    f"{invalid_product_price.sum():,}"
)


# ------------------------------------------------------------
# PRODUCT COST
# ------------------------------------------------------------

invalid_product_cost = (
    products["cost"] < 0
)


print(
    f"Invalid product costs: "
    f"{invalid_product_cost.sum():,}"
)


# ------------------------------------------------------------
# COST GREATER THAN PRICE
# ------------------------------------------------------------

cost_above_price = (
    products["cost"]
    > products["price"]
)


print(
    f"Products where cost > price: "
    f"{cost_above_price.sum():,}"
)


# ============================================================
# PRODUCT DERIVED METRICS
# ============================================================

products["gross_margin"] = (
    products["price"]
    - products["cost"]
)


products["margin_percentage"] = np.where(
    products["price"] > 0,
    (
        products["gross_margin"]
        /
        products["price"]
        * 100
    ),
    0
)


# ============================================================
# TRANSACTION BUSINESS VALIDATION
# CUSTOMER SIGNUP DATE
# ============================================================

print("\n" + "=" * 70)
print("TRANSACTION DATE vs CUSTOMER SIGNUP")
print("=" * 70)


transaction_customer_check = transactions[
    [
        "transaction_id",
        "customer_id",
        "transaction_date"
    ]
].merge(
    customers[
        [
            "customer_id",
            "signup_date"
        ]
    ],
    on="customer_id",
    how="left"
)


transaction_before_signup = (
    transaction_customer_check[
        "transaction_date"
    ]
    <
    transaction_customer_check[
        "signup_date"
    ]
)


invalid_before_signup = (
    transaction_before_signup.sum()
)


print(
    f"Transactions before customer signup: "
    f"{invalid_before_signup:,}"
)


# ------------------------------------------------------------
# REMOVE TRANSACTIONS BEFORE SIGNUP
# ------------------------------------------------------------

if invalid_before_signup > 0:

    invalid_ids = transaction_customer_check.loc[
        transaction_before_signup,
        "transaction_id"
    ]

    transactions = transactions[
        ~transactions[
            "transaction_id"
        ].isin(invalid_ids)
    ].copy()


# ============================================================
# TRANSACTION DATE vs PRODUCT LAUNCH
# ============================================================

print("\n" + "=" * 70)
print("TRANSACTION DATE vs PRODUCT LAUNCH")
print("=" * 70)


transaction_product_check = transactions[
    [
        "transaction_id",
        "product_id",
        "transaction_date"
    ]
].merge(
    products[
        [
            "product_id",
            "launch_date"
        ]
    ],
    on="product_id",
    how="left"
)


transaction_before_launch = (
    transaction_product_check[
        "transaction_date"
    ]
    <
    transaction_product_check[
        "launch_date"
    ]
)


invalid_before_launch = (
    transaction_before_launch.sum()
)


print(
    f"Transactions before product launch: "
    f"{invalid_before_launch:,}"
)


# ------------------------------------------------------------
# FLAG TRANSACTIONS BEFORE PRODUCT LAUNCH
# ------------------------------------------------------------
#
# These records are retained because approximately 28.8%
# of transactions occur before the recorded product launch
# date. Automatically deleting such a large portion of the
# dataset could remove valid business activity if launch_date
# has a different business definition.
#

transactions = transactions.merge(
    products[
        [
            "product_id",
            "launch_date"
        ]
    ],
    on="product_id",
    how="left"
)

transactions["transaction_before_product_launch"] = (
    transactions["transaction_date"]
    <
    transactions["launch_date"]
).astype(int)

invalid_before_launch = (
    transactions[
        "transaction_before_product_launch"
    ].sum()
)

print(
    f"Transactions before recorded product launch: "
    f"{invalid_before_launch:,}"
)

print(
    "✓ Records retained and flagged for investigation"
)

# ============================================================
# TRANSACTION DERIVED METRICS
# ============================================================

print("\n" + "=" * 70)
print("TRANSACTION METRICS")
print("=" * 70)


# Revenue before discount

transactions["gross_revenue"] = (
    transactions["quantity"]
    *
    transactions["price"]
)


# Discount amount

transactions["discount_amount"] = (
    transactions["gross_revenue"]
    *
    transactions["discount"]
)


# Net revenue

transactions["revenue"] = (
    transactions["gross_revenue"]
    -
    transactions["discount_amount"]
)


print("✓ Gross revenue calculated")
print("✓ Discount amount calculated")
print("✓ Net revenue calculated")


# ============================================================
# INTERACTION VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("INTERACTION BUSINESS-RULE VALIDATION")
print("=" * 70)


valid_interaction_types = {
    "view",
    "click",
    "add_to_cart",
    "email_open"
}


invalid_interaction_type = ~(
    interactions[
        "interaction_type"
    ].isin(
        valid_interaction_types
    )
)


print(
    f"Invalid interaction types: "
    f"{invalid_interaction_type.sum():,}"
)


if invalid_interaction_type.sum() > 0:

    interactions = interactions[
        ~invalid_interaction_type
    ].copy()


# ============================================================
# INTERACTION CHANNEL VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("INTERACTION CHANNEL VALIDATION")
print("=" * 70)


interaction_channels = (
    interactions[
        "channel"
    ]
    .dropna()
    .unique()
)


print(
    "Channels found:"
)

for channel in sorted(
    interaction_channels
):

    print(
        f"  - {channel}"
    )


# ============================================================
# INTERACTION PRODUCT ID VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("INTERACTION PRODUCT VALIDATION")
print("=" * 70)


# Missing product_id values are preserved.
#
# They are not automatically treated as errors because
# approximately 30% of every interaction type contains
# missing product IDs.
#
# We only validate product IDs that are actually present.

non_null_interactions = interactions[
    interactions["product_id"].notna()
]


invalid_interaction_products = ~(
    non_null_interactions[
        "product_id"
    ].isin(
        products["product_id"]
    )
)


invalid_interaction_product_count = (
    invalid_interaction_products.sum()
)


print(
    "Missing product_id records: "
    f"{interactions['product_id'].isna().sum():,}"
)


print(
    "Invalid non-null product IDs: "
    f"{invalid_interaction_product_count:,}"
)


if invalid_interaction_product_count > 0:

    invalid_product_ids = (
        non_null_interactions.loc[
            invalid_interaction_products,
            "interaction_id"
        ]
    )

    interactions = interactions[
        ~interactions[
            "interaction_id"
        ].isin(
            invalid_product_ids
        )
    ].copy()


# ============================================================
# INTERACTION TIME FEATURES
# ============================================================

interactions["interaction_date"] = (
    interactions[
        "interaction_timestamp"
    ].dt.date
)


interactions["interaction_hour"] = (
    interactions[
        "interaction_timestamp"
    ].dt.hour
)


interactions["interaction_month"] = (
    interactions[
        "interaction_timestamp"
    ].dt.to_period("M")
    .astype(str)
)


# ============================================================
# CUSTOMER TIME FEATURES
# ============================================================

customers["signup_year"] = (
    customers[
        "signup_date"
    ].dt.year
)


customers["signup_month"] = (
    customers[
        "signup_date"
    ].dt.to_period("M")
    .astype(str)
)


# ============================================================
# TRANSACTION TIME FEATURES
# ============================================================

transactions["transaction_year"] = (
    transactions[
        "transaction_date"
    ].dt.year
)


transactions["transaction_month"] = (
    transactions[
        "transaction_date"
    ].dt.to_period("M")
    .astype(str)
)


# ============================================================
# FINAL FOREIGN KEY VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("FINAL RELATIONSHIP VALIDATION")
print("=" * 70)


invalid_customer_transactions = (
    ~transactions[
        "customer_id"
    ].isin(
        customers[
            "customer_id"
        ]
    )
).sum()


invalid_product_transactions = (
    ~transactions[
        "product_id"
    ].isin(
        products[
            "product_id"
        ]
    )
).sum()


invalid_customer_interactions = (
    ~interactions[
        "customer_id"
    ].isin(
        customers[
            "customer_id"
        ]
    )
).sum()


non_null_interactions = interactions[
    interactions["product_id"].notna()
]


invalid_product_interactions = (
    ~non_null_interactions[
        "product_id"
    ].isin(
        products[
            "product_id"
        ]
    )
).sum()


print(
    f"Transaction → Customer invalid: "
    f"{invalid_customer_transactions:,}"
)

print(
    f"Transaction → Product invalid: "
    f"{invalid_product_transactions:,}"
)

print(
    f"Interaction → Customer invalid: "
    f"{invalid_customer_interactions:,}"
)

print(
    f"Interaction → Product invalid: "
    f"{invalid_product_interactions:,}"
)


# ============================================================
# FINAL DATA QUALITY SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL DATA QUALITY SUMMARY")
print("=" * 70)


final_datasets = {
    "customers": customers,
    "transactions": transactions,
    "products": products,
    "interactions": interactions
}


for name, df in final_datasets.items():

    print(
        f"\n{name.upper()}"
    )

    print(
        f"  Rows: "
        f"{len(df):,}"
    )

    print(
        f"  Columns: "
        f"{len(df.columns):,}"
    )

    print(
        f"  Duplicate rows: "
        f"{df.duplicated().sum():,}"
    )

    print(
        f"  Total missing values: "
        f"{df.isna().sum().sum():,}"
    )


# ============================================================
# SAVE CLEAN DATASETS
# ============================================================

print("\n" + "=" * 70)
print("SAVING CLEAN DATA")
print("=" * 70)


customers.to_csv(
    CLEAN_DIR / "customers_clean.csv",
    index=False
)

transactions.to_csv(
    CLEAN_DIR / "transactions_clean.csv",
    index=False
)

products.to_csv(
    CLEAN_DIR / "products_clean.csv",
    index=False
)

interactions.to_csv(
    CLEAN_DIR / "interactions_clean.csv",
    index=False
)


print(
    "\n✓ customers_clean.csv"
)

print(
    "✓ transactions_clean.csv"
)

print(
    "✓ products_clean.csv"
)

print(
    "✓ interactions_clean.csv"
)


# ============================================================
# FINAL COUNTS
# ============================================================

print("\n" + "=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)


for name, df in final_datasets.items():

    original = initial_counts[name]

    final = len(df)

    removed = original - final

    print(
        f"{name:<15} "
        f"Original: {original:>8,} | "
        f"Final: {final:>8,} | "
        f"Removed: {removed:>8,}"
    )


print("\nClean datasets saved to:")

print(
    CLEAN_DIR
)

print("\n" + "=" * 70)