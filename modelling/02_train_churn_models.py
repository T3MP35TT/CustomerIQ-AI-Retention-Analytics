import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate
)

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)


# ============================================================
# CUSTOMERIQ
# CHURN MODELLING — MODEL TRAINING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "churn_modeling_dataset.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_FILE = (
    MODEL_DIR
    / "customeriq_churn_model.joblib"
)

METADATA_FILE = (
    MODEL_DIR
    / "customeriq_churn_model_metadata.joblib"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    DATA_FILE
)


print("=" * 70)
print("CUSTOMERIQ — CHURN MODEL TRAINING")
print("=" * 70)

print(
    f"\nDataset:\n{DATA_FILE}"
)

print(
    f"\nRows: {len(df):,}"
)


# ============================================================
# TARGET
# ============================================================

target = "churned"

y = df[target]


# ============================================================
# INITIAL FEATURE SET
# ============================================================

initial_feature_columns = [

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


X_initial = df[
    initial_feature_columns
].copy()


# ============================================================
# FEATURE REDUCTION
# ============================================================
#
# Several features contain highly overlapping information.
#
# Financial redundancy:
#   total_revenue
#   net_revenue
#   total_cost
#   gross_profit
#
# Transaction volume redundancy:
#   total_orders
#   total_units
#
# Engagement redundancy:
#   total_interactions
#   views
#   clicks
#   add_to_carts
#   email_opens
#
# We retain representative business features and remove
# redundant variables to improve model interpretability,
# especially for Logistic Regression.
# ============================================================

removed_features = [

    "total_units",
    "net_revenue",
    "total_cost",
    "gross_profit",

    "views",
    "clicks",
    "add_to_carts",
    "email_opens",

    "has_interaction_history"
]


X = X_initial.drop(
    columns=removed_features
)


print("\n" + "=" * 70)
print("FEATURE REDUCTION")
print("=" * 70)

print(
    "\nFeatures removed because they are redundant, "
    "derived, or constant:"
)

for feature in removed_features:

    print(
        f"  - {feature}"
    )


print(
    f"\nInitial features: "
    f"{len(initial_feature_columns)}"
)

print(
    f"Final model features: "
    f"{len(X.columns)}"
)


# ============================================================
# FINAL MODEL FEATURES
# ============================================================

print("\n" + "-" * 70)
print("FINAL MODEL FEATURES")
print("-" * 70)

for feature in X.columns:

    print(
        f"  - {feature}"
    )


# ============================================================
# FEATURE TYPES
# ============================================================
#
# Use pandas type helpers rather than checking only for
# dtype == "object".
#
# This handles normal strings, pandas StringDtype,
# categorical columns, and object columns correctly.
# ============================================================

categorical_features = [

    column
    for column in X.columns

    if (
        pd.api.types.is_string_dtype(
            X[column]
        )

        or pd.api.types.is_object_dtype(
            X[column]
        )

        or isinstance(
            X[column].dtype,
            pd.CategoricalDtype
        )
    )
]


numerical_features = [

    column
    for column in X.columns

    if column not in categorical_features
]


print(
    f"\nCategorical features: "
    f"{len(categorical_features)}"
)

for feature in categorical_features:

    print(
        f"  - {feature}"
    )


print(
    f"\nNumerical features: "
    f"{len(numerical_features)}"
)

for feature in numerical_features:

    print(
        f"  - {feature}"
    )


print(
    f"\nTotal model features: "
    f"{len(X.columns)}"
)


# ============================================================
# FINAL FEATURE CORRELATION AUDIT
# ============================================================

print("\n" + "=" * 70)
print("FINAL FEATURE CORRELATION AUDIT")
print("=" * 70)


if len(numerical_features) > 1:

    correlation_matrix = X[
        numerical_features
    ].corr()


    high_correlations = []


    for i in range(
        len(numerical_features)
    ):

        for j in range(
            i + 1,
            len(numerical_features)
        ):

            feature_a = numerical_features[i]

            feature_b = numerical_features[j]

            correlation = correlation_matrix.loc[
                feature_a,
                feature_b
            ]


            if abs(correlation) >= 0.85:

                high_correlations.append(
                    (
                        feature_a,
                        feature_b,
                        correlation
                    )
                )


    if high_correlations:

        print(
            "\nRemaining highly correlated numerical features "
            "(absolute correlation >= 0.85):"
        )


        for (
            feature_a,
            feature_b,
            correlation
        ) in high_correlations:

            print(
                f"  {feature_a} <-> "
                f"{feature_b}: "
                f"{correlation:.3f}"
            )


    else:

        print(
            "\nNo remaining numerical feature pairs "
            "have absolute correlation >= 0.85."
        )


else:

    print(
        "\nNot enough numerical features "
        "for correlation audit."
    )


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


print("\n" + "=" * 70)
print("TRAIN / TEST SPLIT")
print("=" * 70)

print(
    f"\nTraining customers: "
    f"{len(X_train):,}"
)

print(
    f"Testing customers: "
    f"{len(X_test):,}"
)

print(
    f"\nTraining churn rate: "
    f"{y_train.mean() * 100:.2f}%"
)

print(
    f"Testing churn rate: "
    f"{y_test.mean() * 100:.2f}%"
)


# ============================================================
# PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline(

    steps=[

        (
            "imputer",

            SimpleImputer(
                strategy="median"
            )
        ),

        (
            "scaler",

            StandardScaler()
        )
    ]
)


categorical_pipeline = Pipeline(

    steps=[

        (
            "imputer",

            SimpleImputer(
                strategy="most_frequent"
            )
        ),

        (
            "encoder",

            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


preprocessor = ColumnTransformer(

    transformers=[

        (
            "numeric",

            numeric_pipeline,

            numerical_features
        ),

        (
            "categorical",

            categorical_pipeline,

            categorical_features
        )
    ]
)


# ============================================================
# MODELS
# ============================================================

models = {

    "Logistic Regression":

        LogisticRegression(

            max_iter=2000,

            class_weight="balanced",

            random_state=42
        ),


    "Random Forest":

        RandomForestClassifier(

            n_estimators=400,

            max_depth=None,

            min_samples_leaf=2,

            class_weight="balanced",

            random_state=42,

            n_jobs=-1
        ),


    "Gradient Boosting":

        GradientBoostingClassifier(

            n_estimators=200,

            learning_rate=0.05,

            max_depth=3,

            random_state=42
        )
}


# ============================================================
# HOLDOUT TEST EVALUATION
# ============================================================

holdout_results = []


print("\n" + "=" * 70)
print("HOLDOUT TEST EVALUATION")
print("=" * 70)


for model_name, model in models.items():

    print("\n" + "-" * 70)

    print(
        f"TRAINING: {model_name}"
    )

    print("-" * 70)


    pipeline = Pipeline(

        steps=[

            (
                "preprocessor",

                preprocessor
            ),

            (
                "model",

                model
            )
        ]
    )


    pipeline.fit(
        X_train,
        y_train
    )


    predictions = pipeline.predict(
        X_test
    )


    probabilities = pipeline.predict_proba(
        X_test
    )[:, 1]


    accuracy = accuracy_score(
        y_test,
        predictions
    )


    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )


    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )


    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )


    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )


    pr_auc = average_precision_score(
        y_test,
        probabilities
    )


    matrix = confusion_matrix(
        y_test,
        predictions
    )


    holdout_results.append(

        {

            "model":
                model_name,

            "accuracy":
                accuracy,

            "precision":
                precision,

            "recall":
                recall,

            "f1":
                f1,

            "roc_auc":
                roc_auc,

            "pr_auc":
                pr_auc
        }
    )


    print(
        f"\nAccuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1 Score : {f1:.4f}"
    )

    print(
        f"ROC-AUC  : {roc_auc:.4f}"
    )

    print(
        f"PR-AUC   : {pr_auc:.4f}"
    )

    print(
        "\nConfusion Matrix:"
    )

    print(
        matrix
    )


# ============================================================
# HOLDOUT MODEL COMPARISON
# ============================================================

holdout_df = pd.DataFrame(
    holdout_results
)


holdout_df = holdout_df.sort_values(

    by="pr_auc",

    ascending=False
)


print("\n" + "=" * 70)
print("MODEL COMPARISON — HOLDOUT TEST")
print("=" * 70)


print(

    holdout_df

    .round(4)

    .to_string(
        index=False
    )
)


# ============================================================
# 5-FOLD STRATIFIED CROSS-VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("5-FOLD STRATIFIED CROSS-VALIDATION")
print("=" * 70)


print(
    "\nEvaluating model stability across "
    "5 stratified folds..."
)


cv = StratifiedKFold(

    n_splits=5,

    shuffle=True,

    random_state=42
)


scoring = {

    "accuracy":
        "accuracy",

    "precision":
        "precision",

    "recall":
        "recall",

    "f1":
        "f1",

    "roc_auc":
        "roc_auc",

    "pr_auc":
        "average_precision"
}


cv_results = []


for model_name, model in models.items():

    print("\n" + "-" * 70)

    print(
        f"CROSS-VALIDATING: {model_name}"
    )

    print("-" * 70)


    pipeline = Pipeline(

        steps=[

            (
                "preprocessor",

                preprocessor
            ),

            (
                "model",

                model
            )
        ]
    )


    scores = cross_validate(

        pipeline,

        X,

        y,

        cv=cv,

        scoring=scoring,

        n_jobs=-1
    )


    accuracy_mean = scores[
        "test_accuracy"
    ].mean()


    accuracy_std = scores[
        "test_accuracy"
    ].std()


    precision_mean = scores[
        "test_precision"
    ].mean()


    precision_std = scores[
        "test_precision"
    ].std()


    recall_mean = scores[
        "test_recall"
    ].mean()


    recall_std = scores[
        "test_recall"
    ].std()


    f1_mean = scores[
        "test_f1"
    ].mean()


    f1_std = scores[
        "test_f1"
    ].std()


    roc_auc_mean = scores[
        "test_roc_auc"
    ].mean()


    roc_auc_std = scores[
        "test_roc_auc"
    ].std()


    pr_auc_mean = scores[
        "test_pr_auc"
    ].mean()


    pr_auc_std = scores[
        "test_pr_auc"
    ].std()


    cv_results.append(

        {

            "model":
                model_name,

            "accuracy_mean":
                accuracy_mean,

            "accuracy_std":
                accuracy_std,

            "precision_mean":
                precision_mean,

            "precision_std":
                precision_std,

            "recall_mean":
                recall_mean,

            "recall_std":
                recall_std,

            "f1_mean":
                f1_mean,

            "f1_std":
                f1_std,

            "roc_auc_mean":
                roc_auc_mean,

            "roc_auc_std":
                roc_auc_std,

            "pr_auc_mean":
                pr_auc_mean,

            "pr_auc_std":
                pr_auc_std
        }
    )


    print(
        f"\nAccuracy : "
        f"{accuracy_mean:.4f} +/- "
        f"{accuracy_std:.4f}"
    )

    print(
        f"Precision: "
        f"{precision_mean:.4f} +/- "
        f"{precision_std:.4f}"
    )

    print(
        f"Recall   : "
        f"{recall_mean:.4f} +/- "
        f"{recall_std:.4f}"
    )

    print(
        f"F1 Score : "
        f"{f1_mean:.4f} +/- "
        f"{f1_std:.4f}"
    )

    print(
        f"ROC-AUC  : "
        f"{roc_auc_mean:.4f} +/- "
        f"{roc_auc_std:.4f}"
    )

    print(
        f"PR-AUC   : "
        f"{pr_auc_mean:.4f} +/- "
        f"{pr_auc_std:.4f}"
    )


# ============================================================
# CV MODEL COMPARISON
# ============================================================

cv_df = pd.DataFrame(
    cv_results
)


cv_df = cv_df.sort_values(

    by="pr_auc_mean",

    ascending=False
)


print("\n" + "=" * 70)
print("MODEL COMPARISON — 5-FOLD CROSS-VALIDATION")
print("=" * 70)


display_columns = [

    "model",

    "accuracy_mean",

    "precision_mean",

    "recall_mean",

    "f1_mean",

    "roc_auc_mean",

    "pr_auc_mean"
]


print(

    cv_df[
        display_columns
    ]

    .round(4)

    .to_string(
        index=False
    )
)


# ============================================================
# BEST MODEL
# ============================================================

best_row = cv_df.iloc[0]


best_model_name = best_row[
    "model"
]


print("\n" + "=" * 70)
print("BEST MODEL")
print("=" * 70)


print(
    f"\nModel: "
    f"{best_model_name}"
)


print(
    f"Mean PR-AUC: "
    f"{best_row['pr_auc_mean']:.4f}"
)


print(
    f"Mean ROC-AUC: "
    f"{best_row['roc_auc_mean']:.4f}"
)


print(
    f"Mean F1: "
    f"{best_row['f1_mean']:.4f}"
)


print(
    f"Mean Recall: "
    f"{best_row['recall_mean']:.4f}"
)


print(
    f"Mean Precision: "
    f"{best_row['precision_mean']:.4f}"
)


# ============================================================
# FINAL MODEL
# ============================================================

print("\n" + "=" * 70)
print("FINAL MODEL")
print("=" * 70)


print(
    "\nTraining final model on all available "
    "observation customers..."
)


final_model = Pipeline(

    steps=[

        (
            "preprocessor",

            preprocessor
        ),

        (
            "model",

            models[
                best_model_name
            ]
        )
    ]
)


final_model.fit(
    X,
    y
)


print(
    f"\nFinal model: "
    f"{best_model_name}"
)


print(
    f"Training customers: "
    f"{len(X):,}"
)


# ============================================================
# SAVE FINAL MODEL
# ============================================================

joblib.dump(

    final_model,

    MODEL_FILE
)


print(
    "\nSaved final model to:"
)

print(
    MODEL_FILE
)


# ============================================================
# SAVE MODEL METADATA
# ============================================================

metadata = {

    "model_name":
        best_model_name,

    "target":
        target,

    "training_rows":
        len(X),

    "features":
        list(X.columns),

    "categorical_features":
        categorical_features,

    "numerical_features":
        numerical_features,

    "removed_features":
        removed_features,

    "selection_metric":
        "PR-AUC",

    "cv_folds":
        5,

    "cv_pr_auc":
        float(
            best_row[
                "pr_auc_mean"
            ]
        ),

    "cv_roc_auc":
        float(
            best_row[
                "roc_auc_mean"
            ]
        ),

    "cv_f1":
        float(
            best_row[
                "f1_mean"
            ]
        ),

    "cv_recall":
        float(
            best_row[
                "recall_mean"
            ]
        ),

    "cv_precision":
        float(
            best_row[
                "precision_mean"
            ]
        )
}


joblib.dump(

    metadata,

    METADATA_FILE
)


# ============================================================
# FINAL FEATURE SET
# ============================================================

print("\n" + "=" * 70)
print("FINAL FEATURE SET")
print("=" * 70)


print(
    f"\nCategorical features: "
    f"{len(categorical_features)}"
)


for feature in categorical_features:

    print(
        f"  - {feature}"
    )


print(
    f"\nNumerical features: "
    f"{len(numerical_features)}"
)


for feature in numerical_features:

    print(
        f"  - {feature}"
    )


print(
    "\nExcluded features:"
)


for feature in removed_features:

    print(
        f"  - {feature}"
    )


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("MODEL TRAINING & VALIDATION COMPLETE")
print("=" * 70)


print(
    "\nModels were evaluated using:"
)

print(
    "  - Stratified 80/20 train-test split"
)

print(
    "  - 5-fold stratified cross-validation"
)

print(
    "  - Feature redundancy audit"
)

print(
    "  - Observation-window features only"
)


print(
    "\nPrimary model selection metric: PR-AUC."
)


print(
    "Recall is also important because missed churners "
    "represent customers the retention team failed to identify."
)


print(
    f"\nFinal selected model:"
)


print(
    f"  {best_model_name}"
)


print(
    f"\nFinal model was trained on "
    f"{len(X):,} observation customers."
)


print(
    "\nReady for customer churn scoring."
)