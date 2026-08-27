-- ============================================================
-- 10_export_churn_dataset.sql
-- CUSTOMERIQ — CHURN MODEL EXPORT DATASET
-- ============================================================
--
-- Purpose:
-- Export the final customer-level dataset for churn modeling.
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
-- This query is SELECT-only and returns only customers with
-- at least one purchase during the observation period.
--
-- All model features are calculated using observation-period
-- data only. Future transactions are used ONLY to create the
-- churn target and future_revenue/future_orders.
-- ============================================================


WITH historical_features AS (

    SELECT

        c.customer_id,
        c.customer_segment,
        c.acquisition_channel,
        c.location,
        c.age,
        c.gender,

        -- ----------------------------------------------------
        -- TRANSACTION FEATURES
        -- ----------------------------------------------------

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


        -- ----------------------------------------------------
        -- CUSTOMER TENURE / RECENCY
        -- ----------------------------------------------------

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


    -- Only customers who actually purchased during
    -- the observation period are eligible for churn modeling.

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


-- ============================================================
-- FINAL EXPORT
-- ============================================================

SELECT

    -- --------------------------------------------------------
    -- CUSTOMER INFORMATION
    -- --------------------------------------------------------

    h.customer_id,
    h.customer_segment,
    h.acquisition_channel,
    h.location,
    h.age,
    h.gender,


    -- --------------------------------------------------------
    -- HISTORICAL PURCHASE FEATURES
    -- --------------------------------------------------------

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


    -- --------------------------------------------------------
    -- HISTORICAL ENGAGEMENT FEATURES
    -- --------------------------------------------------------

    COALESCE(
        i.total_interactions,
        0
    ) AS total_interactions,

    COALESCE(
        i.views,
        0
    ) AS views,

    COALESCE(
        i.clicks,
        0
    ) AS clicks,

    COALESCE(
        i.add_to_carts,
        0
    ) AS add_to_carts,

    COALESCE(
        i.email_opens,
        0
    ) AS email_opens,

    COALESCE(
        i.channels_used,
        0
    ) AS channels_used,

    COALESCE(
        i.interaction_types_used,
        0
    ) AS interaction_types_used,


    CASE
        WHEN COALESCE(i.total_interactions, 0) > 0
        THEN 1
        ELSE 0
    END AS has_interaction_history,


    -- --------------------------------------------------------
    -- DERIVED BEHAVIOR FEATURES
    -- --------------------------------------------------------

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


    -- --------------------------------------------------------
    -- FUTURE OUTCOMES
    --
    -- These are included for supervised-learning target
    -- creation / validation.
    -- --------------------------------------------------------

    COALESCE(
        f.future_orders,
        0
    ) AS future_orders,

    COALESCE(
        f.future_revenue,
        0
    ) AS future_revenue,


    -- --------------------------------------------------------
    -- CHURN TARGET
    --
    -- 1 = no purchase in prediction window
    -- 0 = at least one purchase in prediction window
    -- --------------------------------------------------------

    CASE
        WHEN COALESCE(f.future_orders, 0) = 0
        THEN 1
        ELSE 0
    END AS churned


FROM historical_features h

LEFT JOIN historical_interactions i
    ON h.customer_id = i.customer_id

LEFT JOIN future_purchases f
    ON h.customer_id = f.customer_id


ORDER BY
    h.customer_id;