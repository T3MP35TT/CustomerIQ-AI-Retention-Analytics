-- ============================================================
-- 09_churn_dataset.sql
-- CUSTOMERIQ — CHURN DATASET
-- ============================================================
--
-- Observation period:
-- 2024-01-06 → 2025-12-31
--
-- Prediction window:
-- 2026-01-01 → 2026-03-31
--
-- Churn definition:
-- No purchase during the 90-day prediction window = churned
--
-- IMPORTANT:
-- Every statement in this file is SELECT-only so that the
-- existing run_sql.py can execute every statement safely.
-- ============================================================


-- ============================================================
-- QUERY 1 — OBSERVATION / PREDICTION WINDOW
-- ============================================================

SELECT

    MIN(transaction_date)
        AS first_transaction_date,

    MAX(transaction_date)
        AS last_transaction_date,

    '2024-01-06'
        AS observation_start_date,

    '2025-12-31'
        AS observation_end_date,

    '2026-01-01'
        AS prediction_start_date,

    '2026-03-31'
        AS prediction_end_date,

    CAST(
        julianday('2025-12-31')
        - julianday('2024-01-06')
        + 1
        AS INTEGER
    ) AS observation_days,

    CAST(
        julianday('2026-03-31')
        - julianday('2026-01-01')
        + 1
        AS INTEGER
    ) AS prediction_window_days

FROM transactions;


-- ============================================================
-- QUERY 2 — HISTORICAL TRANSACTION FEATURES
-- ============================================================

SELECT

    c.customer_id,
    c.customer_segment,
    c.acquisition_channel,
    c.location,
    c.age,
    c.gender,

    COUNT(t.transaction_id)
        AS total_orders,

    COALESCE(
        SUM(t.quantity),
        0
    ) AS total_units,

    COALESCE(
        SUM(t.gross_revenue),
        0
    ) AS total_revenue,

    COALESCE(
        SUM(
            t.gross_revenue
            * (1 - COALESCE(t.discount, 0))
        ),
        0
    ) AS net_revenue,

    COALESCE(
        SUM(
            t.quantity * p.cost
        ),
        0
    ) AS total_cost,

    COALESCE(
        SUM(
            (
                t.gross_revenue
                * (1 - COALESCE(t.discount, 0))
            )
            - (t.quantity * p.cost)
        ),
        0
    ) AS gross_profit,

    CASE
        WHEN SUM(
            t.gross_revenue
            * (1 - COALESCE(t.discount, 0))
        ) > 0

        THEN ROUND(
            SUM(
                (
                    t.gross_revenue
                    * (1 - COALESCE(t.discount, 0))
                )
                - (t.quantity * p.cost)
            )
            * 100.0
            /
            SUM(
                t.gross_revenue
                * (1 - COALESCE(t.discount, 0))
            ),
            2
        )

        ELSE 0
    END AS gross_margin_percentage,

    CASE
        WHEN COUNT(t.transaction_id) > 0

        THEN ROUND(
            SUM(
                t.gross_revenue
                * (1 - COALESCE(t.discount, 0))
            )
            / COUNT(t.transaction_id),
            2
        )

        ELSE 0
    END AS average_order_value,

    MIN(t.transaction_date)
        AS first_purchase_date,

    MAX(t.transaction_date)
        AS last_purchase_date,

    CASE
        WHEN MAX(t.transaction_date) IS NOT NULL

        THEN CAST(
            julianday('2025-12-31')
            - julianday(MAX(t.transaction_date))
            AS INTEGER
        )

        ELSE NULL
    END AS recency_days,

    CASE
        WHEN MIN(t.transaction_date) IS NOT NULL

        THEN CAST(
            julianday(MAX(t.transaction_date))
            - julianday(MIN(t.transaction_date))
            AS INTEGER
        )

        ELSE NULL
    END AS customer_lifespan_days

FROM customers c

LEFT JOIN transactions t
    ON c.customer_id = t.customer_id

    AND t.transaction_date >= '2024-01-06'
    AND t.transaction_date <= '2025-12-31'

LEFT JOIN products p
    ON t.product_id = p.product_id

GROUP BY
    c.customer_id,
    c.customer_segment,
    c.acquisition_channel,
    c.location,
    c.age,
    c.gender

HAVING
    COUNT(t.transaction_id) > 0

ORDER BY
    total_revenue DESC;


-- ============================================================
-- QUERY 3 — HISTORICAL INTERACTION FEATURES
-- ============================================================

SELECT

    c.customer_id,

    COUNT(i.interaction_id)
        AS total_interactions,

    SUM(
        CASE
            WHEN i.interaction_type = 'view'
            THEN 1
            ELSE 0
        END
    ) AS views,

    SUM(
        CASE
            WHEN i.interaction_type = 'click'
            THEN 1
            ELSE 0
        END
    ) AS clicks,

    SUM(
        CASE
            WHEN i.interaction_type = 'add_to_cart'
            THEN 1
            ELSE 0
        END
    ) AS add_to_carts,

    SUM(
        CASE
            WHEN i.interaction_type = 'email_open'
            THEN 1
            ELSE 0
        END
    ) AS email_opens,

    COUNT(
        DISTINCT i.channel
    ) AS channels_used,

    COUNT(
        DISTINCT i.interaction_type
    ) AS interaction_types_used,

    CASE
        WHEN COUNT(i.interaction_id) > 0
        THEN 1
        ELSE 0
    END AS has_interaction_history

FROM customers c

LEFT JOIN interactions i
    ON c.customer_id = i.customer_id

    AND i.interaction_timestamp >= '2024-01-06'
    AND i.interaction_timestamp < '2026-01-01'

GROUP BY
    c.customer_id

ORDER BY
    total_interactions DESC;


-- ============================================================
-- QUERY 4 — FUTURE PURCHASE DATA
-- ============================================================

SELECT

    c.customer_id,

    COUNT(t.transaction_id)
        AS future_orders,

    COALESCE(
        SUM(
            t.gross_revenue
            * (1 - COALESCE(t.discount, 0))
        ),
        0
    ) AS future_revenue

FROM customers c

LEFT JOIN transactions t
    ON c.customer_id = t.customer_id

    AND t.transaction_date >= '2026-01-01'
    AND t.transaction_date <= '2026-03-31'

GROUP BY
    c.customer_id

ORDER BY
    future_orders DESC;


-- ============================================================
-- QUERY 5 — FINAL CHURN DATASET
-- ============================================================

WITH historical_features AS (

    SELECT

        c.customer_id,
        c.customer_segment,
        c.acquisition_channel,
        c.location,
        c.age,
        c.gender,

        COUNT(t.transaction_id)
            AS total_orders,

        COALESCE(
            SUM(t.quantity),
            0
        ) AS total_units,

        COALESCE(
            SUM(t.gross_revenue),
            0
        ) AS total_revenue,

        COALESCE(
            SUM(
                t.gross_revenue
                * (1 - COALESCE(t.discount, 0))
            ),
            0
        ) AS net_revenue,

        COALESCE(
            SUM(
                t.quantity * p.cost
            ),
            0
        ) AS total_cost,

        COALESCE(
            SUM(
                (
                    t.gross_revenue
                    * (1 - COALESCE(t.discount, 0))
                )
                - (t.quantity * p.cost)
            ),
            0
        ) AS gross_profit,

        CASE
            WHEN SUM(
                t.gross_revenue
                * (1 - COALESCE(t.discount, 0))
            ) > 0

            THEN ROUND(
                SUM(
                    (
                        t.gross_revenue
                        * (1 - COALESCE(t.discount, 0))
                    )
                    - (t.quantity * p.cost)
                )
                * 100.0
                /
                SUM(
                    t.gross_revenue
                    * (1 - COALESCE(t.discount, 0))
                ),
                2
            )

            ELSE 0
        END AS gross_margin_percentage,

        CASE
            WHEN COUNT(t.transaction_id) > 0

            THEN ROUND(
                SUM(
                    t.gross_revenue
                    * (1 - COALESCE(t.discount, 0))
                )
                / COUNT(t.transaction_id),
                2
            )

            ELSE 0
        END AS average_order_value,

        MIN(t.transaction_date)
            AS first_purchase_date,

        MAX(t.transaction_date)
            AS last_purchase_date,

        CAST(
            julianday('2025-12-31')
            - julianday(MAX(t.transaction_date))
            AS INTEGER
        ) AS recency_days,

        CAST(
            julianday(MAX(t.transaction_date))
            - julianday(MIN(t.transaction_date))
            AS INTEGER
        ) AS customer_lifespan_days

    FROM customers c

    LEFT JOIN transactions t
        ON c.customer_id = t.customer_id

        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    LEFT JOIN products p
        ON t.product_id = p.product_id

    GROUP BY
        c.customer_id,
        c.customer_segment,
        c.acquisition_channel,
        c.location,
        c.age,
        c.gender

    HAVING
        COUNT(t.transaction_id) > 0
),

historical_interactions AS (

    SELECT

        c.customer_id,

        COUNT(i.interaction_id)
            AS total_interactions,

        SUM(
            CASE
                WHEN i.interaction_type = 'view'
                THEN 1
                ELSE 0
            END
        ) AS views,

        SUM(
            CASE
                WHEN i.interaction_type = 'click'
                THEN 1
                ELSE 0
            END
        ) AS clicks,

        SUM(
            CASE
                WHEN i.interaction_type = 'add_to_cart'
                THEN 1
                ELSE 0
            END
        ) AS add_to_carts,

        SUM(
            CASE
                WHEN i.interaction_type = 'email_open'
                THEN 1
                ELSE 0
            END
        ) AS email_opens,

        COUNT(DISTINCT i.channel)
            AS channels_used,

        COUNT(DISTINCT i.interaction_type)
            AS interaction_types_used

    FROM customers c

    LEFT JOIN interactions i
        ON c.customer_id = i.customer_id

        AND i.interaction_timestamp >= '2024-01-06'
        AND i.interaction_timestamp < '2026-01-01'

    GROUP BY
        c.customer_id
),

future_purchases AS (

    SELECT

        c.customer_id,

        COUNT(t.transaction_id)
            AS future_orders,

        COALESCE(
            SUM(
                t.gross_revenue
                * (1 - COALESCE(t.discount, 0))
            ),
            0
        ) AS future_revenue

    FROM customers c

    LEFT JOIN transactions t
        ON c.customer_id = t.customer_id

        AND t.transaction_date >= '2026-01-01'
        AND t.transaction_date <= '2026-03-31'

    GROUP BY
        c.customer_id
)

SELECT

    h.customer_id,

    h.customer_segment,
    h.acquisition_channel,
    h.location,
    h.age,
    h.gender,

    h.total_orders,
    h.total_units,
    h.total_revenue,
    h.net_revenue,
    h.total_cost,
    h.gross_profit,
    h.gross_margin_percentage,
    h.average_order_value,

    h.first_purchase_date,
    h.last_purchase_date,
    h.recency_days,
    h.customer_lifespan_days,

    COALESCE(i.total_interactions, 0)
        AS total_interactions,

    COALESCE(i.views, 0)
        AS views,

    COALESCE(i.clicks, 0)
        AS clicks,

    COALESCE(i.add_to_carts, 0)
        AS add_to_carts,

    COALESCE(i.email_opens, 0)
        AS email_opens,

    COALESCE(i.channels_used, 0)
        AS channels_used,

    COALESCE(i.interaction_types_used, 0)
        AS interaction_types_used,

    CASE
        WHEN COALESCE(i.total_interactions, 0) > 0
        THEN 1
        ELSE 0
    END AS has_interaction_history,

    CASE
        WHEN h.customer_lifespan_days > 0

        THEN ROUND(
            h.total_orders * 365.0
            / h.customer_lifespan_days,
            2
        )

        ELSE h.total_orders
    END AS annualized_order_frequency,

    CASE
        WHEN COALESCE(i.total_interactions, 0) > 0

        THEN ROUND(
            COALESCE(i.clicks, 0) * 1.0
            / i.total_interactions,
            4
        )

        ELSE 0
    END AS click_rate,

    CASE
        WHEN COALESCE(i.total_interactions, 0) > 0

        THEN ROUND(
            COALESCE(i.add_to_carts, 0) * 1.0
            / i.total_interactions,
            4
        )

        ELSE 0
    END AS add_to_cart_rate,

    CASE
        WHEN COALESCE(i.total_interactions, 0) > 0

        THEN ROUND(
            COALESCE(i.email_opens, 0) * 1.0
            / i.total_interactions,
            4
        )

        ELSE 0
    END AS email_open_share,

    f.future_orders,
    f.future_revenue,

    CASE
        WHEN f.future_orders = 0
        THEN 1
        ELSE 0
    END AS churned

FROM historical_features h

LEFT JOIN historical_interactions i
    ON h.customer_id = i.customer_id

LEFT JOIN future_purchases f
    ON h.customer_id = f.customer_id

ORDER BY
    h.total_revenue DESC;


-- ============================================================
-- QUERY 6 — CHURN DISTRIBUTION
-- ============================================================

WITH churn_data AS (

    SELECT

        c.customer_id,

        COUNT(t.transaction_id)
            AS total_orders,

        CASE
            WHEN COUNT(f.transaction_id) = 0
            THEN 1
            ELSE 0
        END AS churned

    FROM customers c

    LEFT JOIN transactions t
        ON c.customer_id = t.customer_id
        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    LEFT JOIN transactions f
        ON c.customer_id = f.customer_id
        AND f.transaction_date >= '2026-01-01'
        AND f.transaction_date <= '2026-03-31'

    GROUP BY
        c.customer_id

    HAVING
        COUNT(t.transaction_id) > 0
)

SELECT

    churned,

    COUNT(*) AS customers,

    ROUND(
        COUNT(*) * 100.0
        / (SELECT COUNT(*) FROM churn_data),
        2
    ) AS percentage

FROM churn_data

GROUP BY
    churned

ORDER BY
    churned;


-- ============================================================
-- QUERY 7 — CHURN SUMMARY
-- ============================================================

WITH churn_data AS (

    SELECT

        c.customer_id,

        CASE
            WHEN COUNT(f.transaction_id) = 0
            THEN 1
            ELSE 0
        END AS churned

    FROM customers c

    LEFT JOIN transactions t
        ON c.customer_id = t.customer_id
        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    LEFT JOIN transactions f
        ON c.customer_id = f.customer_id
        AND f.transaction_date >= '2026-01-01'
        AND f.transaction_date <= '2026-03-31'

    GROUP BY
        c.customer_id

    HAVING
        COUNT(t.transaction_id) > 0
)

SELECT

    COUNT(*) AS observation_customers,

    SUM(
        CASE
            WHEN churned = 1
            THEN 1
            ELSE 0
        END
    ) AS churned_customers,

    SUM(
        CASE
            WHEN churned = 0
            THEN 1
            ELSE 0
        END
    ) AS retained_customers,

    ROUND(
        AVG(churned) * 100,
        2
    ) AS churn_rate_percentage

FROM churn_data;


-- ============================================================
-- QUERY 8 — NULL VALIDATION
-- ============================================================

WITH churn_data AS (

    SELECT

        c.customer_id,

        COUNT(t.transaction_id)
            AS total_orders,

        COALESCE(
            SUM(t.gross_revenue),
            0
        ) AS total_revenue,

        COALESCE(
            SUM(
                (
                    t.gross_revenue
                    * (1 - COALESCE(t.discount, 0))
                )
                - (t.quantity * p.cost)
            ),
            0
        ) AS gross_profit,

        MIN(t.transaction_date)
            AS first_purchase_date,

        MAX(t.transaction_date)
            AS last_purchase_date

    FROM customers c

    LEFT JOIN transactions t
        ON c.customer_id = t.customer_id
        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    LEFT JOIN products p
        ON t.product_id = p.product_id

    GROUP BY
        c.customer_id

    HAVING
        COUNT(t.transaction_id) > 0
)

SELECT

    COUNT(*) AS customers,

    SUM(
        CASE
            WHEN total_orders IS NULL
            THEN 1
            ELSE 0
        END
    ) AS null_orders,

    SUM(
        CASE
            WHEN total_revenue IS NULL
            THEN 1
            ELSE 0
        END
    ) AS null_revenue,

    SUM(
        CASE
            WHEN gross_profit IS NULL
            THEN 1
            ELSE 0
        END
    ) AS null_profit,

    SUM(
        CASE
            WHEN first_purchase_date IS NULL
            THEN 1
            ELSE 0
        END
    ) AS null_first_purchase,

    SUM(
        CASE
            WHEN last_purchase_date IS NULL
            THEN 1
            ELSE 0
        END
    ) AS null_last_purchase

FROM churn_data;


-- ============================================================
-- QUERY 9 — TARGET VALIDATION
-- ============================================================

WITH churn_data AS (

    SELECT

        c.customer_id,

        CASE
            WHEN COUNT(f.transaction_id) = 0
            THEN 1
            ELSE 0
        END AS churned

    FROM customers c

    LEFT JOIN transactions t
        ON c.customer_id = t.customer_id
        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    LEFT JOIN transactions f
        ON c.customer_id = f.customer_id
        AND f.transaction_date >= '2026-01-01'
        AND f.transaction_date <= '2026-03-31'

    GROUP BY
        c.customer_id

    HAVING
        COUNT(t.transaction_id) > 0
)

SELECT

    MIN(churned)
        AS minimum_target,

    MAX(churned)
        AS maximum_target,

    COUNT(DISTINCT churned)
        AS distinct_target_values

FROM churn_data;


-- ============================================================
-- QUERY 10 — FUTURE TARGET VALIDATION
-- ============================================================

WITH historical_customers AS (

    SELECT

        c.customer_id

    FROM customers c

    INNER JOIN transactions t
        ON c.customer_id = t.customer_id

        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    GROUP BY
        c.customer_id
),

future_data AS (

    SELECT

        h.customer_id,

        COUNT(t.transaction_id)
            AS future_orders,

        COALESCE(
            SUM(
                t.gross_revenue
                * (1 - COALESCE(t.discount, 0))
            ),
            0
        ) AS future_revenue

    FROM historical_customers h

    LEFT JOIN transactions t
        ON h.customer_id = t.customer_id

        AND t.transaction_date >= '2026-01-01'
        AND t.transaction_date <= '2026-03-31'

    GROUP BY
        h.customer_id
)

SELECT

    COUNT(*) AS customers,

    SUM(
        CASE
            WHEN future_orders < 0
            THEN 1
            ELSE 0
        END
    ) AS invalid_future_orders,

    SUM(
        CASE
            WHEN future_revenue < 0
            THEN 1
            ELSE 0
        END
    ) AS invalid_future_revenue

FROM future_data;


-- ============================================================
-- QUERY 11 — LEAKAGE VALIDATION
-- ============================================================

WITH historical_customers AS (

    SELECT

        c.customer_id,

        MIN(t.transaction_date)
            AS first_purchase_date,

        MAX(t.transaction_date)
            AS last_purchase_date

    FROM customers c

    INNER JOIN transactions t
        ON c.customer_id = t.customer_id

        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    GROUP BY
        c.customer_id
)

SELECT

    COUNT(*) AS customers,

    SUM(
        CASE
            WHEN last_purchase_date > '2025-12-31'
            THEN 1
            ELSE 0
        END
    ) AS features_after_observation_end,

    SUM(
        CASE
            WHEN first_purchase_date > '2025-12-31'
            THEN 1
            ELSE 0
        END
    ) AS first_purchase_after_observation_end

FROM historical_customers;


-- ============================================================
-- QUERY 12 — HISTORICAL CUSTOMER COUNT
-- ============================================================

SELECT

    COUNT(DISTINCT t.customer_id)
        AS observation_customers,

    COUNT(DISTINCT t.customer_id)
        AS purchasing_customers

FROM transactions t

WHERE t.transaction_date >= '2024-01-06'
  AND t.transaction_date <= '2025-12-31';


-- ============================================================
-- QUERY 13 — CHURN BY CUSTOMER SEGMENT
-- ============================================================

WITH historical_customers AS (

    SELECT

        c.customer_id,
        c.customer_segment,

        COUNT(t.transaction_id)
            AS historical_orders

    FROM customers c

    INNER JOIN transactions t
        ON c.customer_id = t.customer_id

        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    GROUP BY
        c.customer_id,
        c.customer_segment
),

churn_data AS (

    SELECT

        h.customer_id,
        h.customer_segment,

        CASE
            WHEN COUNT(f.transaction_id) = 0
            THEN 1
            ELSE 0
        END AS churned

    FROM historical_customers h

    LEFT JOIN transactions f
        ON h.customer_id = f.customer_id

        AND f.transaction_date >= '2026-01-01'
        AND f.transaction_date <= '2026-03-31'

    GROUP BY
        h.customer_id,
        h.customer_segment
)

SELECT

    customer_segment,

    COUNT(*) AS customers,

    SUM(churned)
        AS churned_customers,

    COUNT(*) - SUM(churned)
        AS retained_customers,

    ROUND(
        AVG(churned) * 100,
        2
    ) AS churn_rate_percentage

FROM churn_data

GROUP BY
    customer_segment

ORDER BY
    churn_rate_percentage DESC;


-- ============================================================
-- QUERY 14 — CHURN BY ACQUISITION CHANNEL
-- ============================================================

WITH historical_customers AS (

    SELECT

        c.customer_id,
        c.acquisition_channel,

        COUNT(t.transaction_id)
            AS historical_orders

    FROM customers c

    INNER JOIN transactions t
        ON c.customer_id = t.customer_id

        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    GROUP BY
        c.customer_id,
        c.acquisition_channel
),

churn_data AS (

    SELECT

        h.customer_id,
        h.acquisition_channel,

        CASE
            WHEN COUNT(f.transaction_id) = 0
            THEN 1
            ELSE 0
        END AS churned

    FROM historical_customers h

    LEFT JOIN transactions f
        ON h.customer_id = f.customer_id

        AND f.transaction_date >= '2026-01-01'
        AND f.transaction_date <= '2026-03-31'

    GROUP BY
        h.customer_id,
        h.acquisition_channel
)

SELECT

    acquisition_channel,

    COUNT(*) AS customers,

    SUM(churned)
        AS churned_customers,

    COUNT(*) - SUM(churned)
        AS retained_customers,

    ROUND(
        AVG(churned) * 100,
        2
    ) AS churn_rate_percentage

FROM churn_data

GROUP BY
    acquisition_channel

ORDER BY
    churn_rate_percentage DESC;


-- ============================================================
-- QUERY 15 — CHURN BY RECENCY BAND
-- ============================================================

WITH historical_customers AS (

    SELECT

        c.customer_id,

        CASE
            WHEN julianday('2025-12-31')
                 - julianday(MAX(t.transaction_date)) <= 30
                THEN '0–30 Days'

            WHEN julianday('2025-12-31')
                 - julianday(MAX(t.transaction_date)) <= 60
                THEN '31–60 Days'

            WHEN julianday('2025-12-31')
                 - julianday(MAX(t.transaction_date)) <= 90
                THEN '61–90 Days'

            WHEN julianday('2025-12-31')
                 - julianday(MAX(t.transaction_date)) <= 180
                THEN '91–180 Days'

            ELSE '180+ Days'
        END AS recency_band

    FROM customers c

    INNER JOIN transactions t
        ON c.customer_id = t.customer_id

        AND t.transaction_date >= '2024-01-06'
        AND t.transaction_date <= '2025-12-31'

    GROUP BY
        c.customer_id
),

churn_data AS (

    SELECT

        h.customer_id,
        h.recency_band,

        CASE
            WHEN COUNT(f.transaction_id) = 0
            THEN 1
            ELSE 0
        END AS churned

    FROM historical_customers h

    LEFT JOIN transactions f
        ON h.customer_id = f.customer_id

        AND f.transaction_date >= '2026-01-01'
        AND f.transaction_date <= '2026-03-31'

    GROUP BY
        h.customer_id,
        h.recency_band
)

SELECT

    recency_band,

    COUNT(*) AS customers,

    SUM(churned)
        AS churned_customers,

    COUNT(*) - SUM(churned)
        AS retained_customers,

    ROUND(
        AVG(churned) * 100,
        2
    ) AS churn_rate_percentage

FROM churn_data

GROUP BY
    recency_band

ORDER BY
    CASE recency_band
        WHEN '0–30 Days' THEN 1
        WHEN '31–60 Days' THEN 2
        WHEN '61–90 Days' THEN 3
        WHEN '91–180 Days' THEN 4
        WHEN '180+ Days' THEN 5
    END;