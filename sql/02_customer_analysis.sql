-- ============================================================
-- 2. CUSTOMER RECENCY
-- ============================================================

WITH customer_last_purchase AS (

    SELECT
        customer_id,
        MAX(transaction_date) AS last_purchase_date

    FROM transactions

    GROUP BY customer_id
),

analysis_date AS (

    SELECT
        MAX(transaction_date) AS latest_transaction_date

    FROM transactions
)

SELECT

    clp.customer_id,

    c.customer_segment,

    c.acquisition_channel,

    c.location,

    clp.total_orders,

    clp.total_spend,

    clp.last_purchase_date,

    CAST(
        julianday(
            a.latest_transaction_date
        )
        -
        julianday(
            clp.last_purchase_date
        )
        AS INTEGER
    ) AS recency_days

FROM (

    SELECT

        customer_id,

        COUNT(
            DISTINCT transaction_id
        ) AS total_orders,

        ROUND(
            SUM(revenue),
            2
        ) AS total_spend,

        MAX(
            transaction_date
        ) AS last_purchase_date

    FROM transactions

    GROUP BY customer_id

) AS clp

JOIN customers AS c
    ON clp.customer_id = c.customer_id

CROSS JOIN analysis_date AS a

ORDER BY recency_days DESC;