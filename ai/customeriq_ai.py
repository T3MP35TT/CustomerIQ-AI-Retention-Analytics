import pandas as pd
from pathlib import Path


# ============================================================
# CUSTOMERIQ — DATA LOADER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "churn_scored_customers.csv"
)


def load_customer_data():
    """
    Load the CustomerIQ scored customer dataset.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"CustomerIQ scored dataset not found:\n{DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    return df


def get_dataset_summary(df):
    """
    Return high-level CustomerIQ metrics.
    """

    total_customers = len(df)

    predicted_churners = int(
        df["predicted_churn"].sum()
    )

    predicted_churn_rate = (
        predicted_churners / total_customers
        if total_customers > 0
        else 0
    )

    expected_revenue_at_risk = df[
        "expected_revenue_at_risk"
    ].sum()

    expected_profit_at_risk = df[
        "expected_profit_at_risk"
    ].sum()

    return {
        "total_customers": total_customers,
        "predicted_churners": predicted_churners,
        "predicted_churn_rate": predicted_churn_rate,
        "expected_revenue_at_risk": expected_revenue_at_risk,
        "expected_profit_at_risk": expected_profit_at_risk,
    }


if __name__ == "__main__":

    df = load_customer_data()

    summary = get_dataset_summary(df)

    print("\n" + "=" * 60)
    print("CUSTOMERIQ — DATA TEST")
    print("=" * 60)

    print(f"\nCustomers: {summary['total_customers']:,}")
    print(
        f"Predicted churners: "
        f"{summary['predicted_churners']:,}"
    )
    print(
        f"Predicted churn rate: "
        f"{summary['predicted_churn_rate']:.2%}"
    )
    print(
        f"Expected revenue at risk: "
        f"₹{summary['expected_revenue_at_risk']:,.2f}"
    )
    print(
        f"Expected profit at risk: "
        f"₹{summary['expected_profit_at_risk']:,.2f}"
    )

    print("\nCustomerIQ data loaded successfully.")