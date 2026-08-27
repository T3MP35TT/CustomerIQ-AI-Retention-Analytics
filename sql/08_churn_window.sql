-- ============================================================
-- 08_churn_window.sql
-- CUSTOMERIQ — CHURN OBSERVATION & PREDICTION WINDOW
-- ============================================================

WITH dataset_range AS (
    SELECT
        MIN(transaction_date) AS first_transaction_date,
        MAX(transaction_date) AS last_transaction_date
    FROM transactions
),

churn_window AS (
    SELECT
        first_transaction_date,
        last_transaction_date,

        -- Historical observation period
        '2024-01-06' AS observation_start_date,
        '2025-12-31' AS observation_end_date,

        -- 90-day future churn window
        '2026-01-01' AS prediction_start_date,
        '2026-03-31' AS prediction_end_date

    FROM dataset_range
)

SELECT
    first_transaction_date,
    last_transaction_date,
    observation_start_date,
    observation_end_date,
    prediction_start_date,
    prediction_end_date,

    CAST(
        julianday(observation_end_date)
        - julianday(observation_start_date)
        + 1
        AS INTEGER
    ) AS observation_days,

    CAST(
        julianday(prediction_end_date)
        - julianday(prediction_start_date)
        + 1
        AS INTEGER
    ) AS prediction_window_days

FROM churn_window;