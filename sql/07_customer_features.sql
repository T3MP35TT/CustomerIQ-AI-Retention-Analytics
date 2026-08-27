-- ============================================================
-- CUSTOMERIQ
-- 07 - CUSTOMER FEATURES
--
-- PURPOSE:
-- Build customer-level historical features for CustomerIQ
-- analytics using the complete available transaction history.
--
-- DATA COVERAGE:
-- 2024-01-06 → 2026-03-31
--
-- NOTE:
-- This file is NOT the churn-model dataset.
-- Churn-specific observation/prediction windows are handled
-- separately in 09_churn_dataset.sql.
-- ============================================================


-- ============================================================
-- QUERY 1
-- CUSTOMER-LEVEL FEATURES
-- ============================================================

WITH purchase_features AS (

    SELECT

        t.customer_id,

        COUNT(
            DISTINCT t.transaction_id
        ) AS total_orders,

        SUM(
            t.quantity
        ) AS total_units,

        ROUND(
            SUM(t.revenue),
            2
        ) AS total_revenue,

        ROUND(
            SUM(
                t.quantity * p.cost
            ),
            2
        ) AS total_cost,

        ROUND(
            SUM(t.revenue)
            -
            SUM(
                t.quantity * p.cost
            ),
            2
        ) AS gross_profit,

        ROUND(

            (
                SUM(t.revenue)
                -
                SUM(
                    t.quantity * p.cost
                )
            )
            /
            NULLIF(
                SUM(t.revenue),
                0
            )
            * 100,

            2

        ) AS gross_margin_percentage,

        ROUND(

            SUM(t.revenue)
            /
            NULLIF(
                COUNT(
                    DISTINCT t.transaction_id
                ),
                0
            ),

            2

        ) AS average_order_value,

        MIN(
            t.transaction_date
        ) AS first_purchase_date,

        MAX(
            t.transaction_date
        ) AS last_purchase_date

    FROM transactions t

    JOIN products p

        ON t.product_id = p.product_id

    GROUP BY

        t.customer_id
),


-- ============================================================
-- CUSTOMER ENGAGEMENT FEATURES
-- ============================================================

engagement_features AS (

    SELECT

        i.customer_id,

        COUNT(*) AS total_interactions,

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
        ) AS interaction_types_used

    FROM interactions i

    GROUP BY

        i.customer_id
)


-- ============================================================
-- FINAL CUSTOMER FEATURE TABLE
-- ============================================================

SELECT

    c.customer_id,

    -- Customer profile

    c.customer_segment,

    c.acquisition_channel,

    c.location,

    c.age,

    c.gender,


    -- Purchase behavior

    COALESCE(
        p.total_orders,
        0
    ) AS total_orders,

    COALESCE(
        p.total_units,
        0
    ) AS total_units,

    COALESCE(
        p.total_revenue,
        0
    ) AS total_revenue,

    COALESCE(
        p.total_cost,
        0
    ) AS total_cost,

    COALESCE(
        p.gross_profit,
        0
    ) AS gross_profit,

    COALESCE(
        p.gross_margin_percentage,
        0
    ) AS gross_margin_percentage,

    COALESCE(
        p.average_order_value,
        0
    ) AS average_order_value,


    -- Purchase dates

    p.first_purchase_date,

    p.last_purchase_date,


    -- Recency

    CASE

        WHEN p.last_purchase_date IS NOT NULL

        THEN CAST(

            julianday(
                '2026-03-31'
            )
            -
            julianday(
                p.last_purchase_date
            )

            AS INTEGER

        )

        ELSE NULL

    END AS recency_days,


    -- Customer lifespan

    CASE

        WHEN
            p.first_purchase_date IS NOT NULL
            AND
            p.last_purchase_date IS NOT NULL

        THEN CAST(

            julianday(
                p.last_purchase_date
            )
            -
            julianday(
                p.first_purchase_date
            )

            AS INTEGER

        )

        ELSE NULL

    END AS customer_lifespan_days,


    -- Engagement

    COALESCE(
        e.total_interactions,
        0
    ) AS total_interactions,

    COALESCE(
        e.views,
        0
    ) AS views,

    COALESCE(
        e.clicks,
        0
    ) AS clicks,

    COALESCE(
        e.add_to_carts,
        0
    ) AS add_to_carts,

    COALESCE(
        e.email_opens,
        0
    ) AS email_opens,

    COALESCE(
        e.channels_used,
        0
    ) AS channels_used,

    COALESCE(
        e.interaction_types_used,
        0
    ) AS interaction_types_used,


    -- Engagement availability flag

    CASE

        WHEN e.customer_id IS NOT NULL
        THEN 1

        ELSE 0

    END AS has_interaction_history,


    -- ========================================================
    -- DERIVED PURCHASE METRICS
    -- ========================================================

    CASE

        WHEN
            p.customer_id IS NOT NULL
            AND
            (
                julianday(
                    p.last_purchase_date
                )
                -
                julianday(
                    p.first_purchase_date
                )
            ) > 0

        THEN ROUND(

            p.total_orders
            /
            (
                (
                    julianday(
                        p.last_purchase_date
                    )
                    -
                    julianday(
                        p.first_purchase_date
                    )
                )
                /
                365.25
            ),

            2

        )

        ELSE NULL

    END AS annualized_order_frequency,


    -- ========================================================
    -- DERIVED ENGAGEMENT METRICS
    -- ========================================================

    CASE

        WHEN
            COALESCE(e.views, 0) > 0

        THEN ROUND(

            e.clicks * 1.0
            /
            e.views,

            4

        )

        ELSE 0

    END AS click_rate,


    CASE

        WHEN
            COALESCE(e.views, 0) > 0

        THEN ROUND(

            e.add_to_carts * 1.0
            /
            e.views,

            4

        )

        ELSE 0

    END AS add_to_cart_rate,


    CASE

        WHEN
            COALESCE(e.total_interactions, 0) > 0

        THEN ROUND(

            e.email_opens * 1.0
            /
            e.total_interactions,

            4

        )

        ELSE 0

    END AS email_open_share


FROM customers c

LEFT JOIN purchase_features p

    ON c.customer_id = p.customer_id

LEFT JOIN engagement_features e

    ON c.customer_id = e.customer_id

ORDER BY

    total_revenue DESC;


-- ============================================================
-- QUERY 2
-- CUSTOMER POPULATION SUMMARY
-- ============================================================

WITH purchase_customers AS (

    SELECT DISTINCT

        customer_id

    FROM transactions

),

repeat_customers AS (

    SELECT

        customer_id

    FROM transactions

    GROUP BY

        customer_id

    HAVING COUNT(
        DISTINCT transaction_id
    ) > 1

),

engaged_customers AS (

    SELECT DISTINCT

        customer_id

    FROM interactions

)

SELECT

    COUNT(DISTINCT c.customer_id)
        AS total_customers,

    COUNT(DISTINCT p.customer_id)
        AS purchasing_customers,

    COUNT(DISTINCT r.customer_id)
        AS repeat_customers,

    COUNT(DISTINCT e.customer_id)
        AS engaged_customers,

    COUNT(DISTINCT c.customer_id)
        -
        COUNT(DISTINCT e.customer_id)
        AS no_engagement_customers,

    ROUND(

        COALESCE(
            (
                SELECT AVG(order_count)
                FROM (
                    SELECT
                        customer_id,
                        COUNT(
                            DISTINCT transaction_id
                        ) AS order_count
                    FROM transactions
                    GROUP BY customer_id
                )
            ),
            0
        ),

        2

    ) AS average_orders,

    ROUND(

        COALESCE(
            (
                SELECT AVG(customer_revenue)
                FROM (
                    SELECT
                        customer_id,
                        SUM(revenue)
                            AS customer_revenue
                    FROM transactions
                    GROUP BY customer_id
                )
            ),
            0
        ),

        2

    ) AS average_revenue,

    ROUND(

        COALESCE(
            (
                SELECT AVG(customer_profit)
                FROM (
                    SELECT
                        t.customer_id,

                        SUM(
                            t.revenue
                            -
                            (
                                t.quantity * p.cost
                            )
                        ) AS customer_profit

                    FROM transactions t

                    JOIN products p

                        ON t.product_id =
                           p.product_id

                    GROUP BY
                        t.customer_id
                )
            ),
            0
        ),

        2

    ) AS average_profit,

    ROUND(

        COALESCE(
            (
                SELECT AVG(interaction_count)
                FROM (
                    SELECT
                        customer_id,
                        COUNT(*) AS interaction_count
                    FROM interactions
                    GROUP BY customer_id
                )
            ),
            0
        ),

        2

    ) AS average_interactions

FROM customers c

LEFT JOIN purchase_customers p

    ON c.customer_id = p.customer_id

LEFT JOIN repeat_customers r

    ON c.customer_id = r.customer_id

LEFT JOIN engaged_customers e

    ON c.customer_id = e.customer_id;


-- ============================================================
-- QUERY 3
-- HIGH-VALUE CUSTOMER / PROFITABILITY CHECK
-- ============================================================

WITH customer_profitability AS (

    SELECT

        t.customer_id,

        COUNT(
            DISTINCT t.transaction_id
        ) AS total_orders,

        ROUND(
            SUM(t.revenue),
            2
        ) AS total_revenue,

        ROUND(

            SUM(t.revenue)
            -
            SUM(
                t.quantity * p.cost
            ),

            2

        ) AS gross_profit

    FROM transactions t

    JOIN products p

        ON t.product_id = p.product_id

    GROUP BY

        t.customer_id
)

SELECT

    c.customer_id,

    c.customer_segment,

    c.location,

    c.acquisition_channel,

    cp.total_orders,

    cp.total_revenue,

    cp.gross_profit,

    CAST(

        julianday(
            '2026-03-31'
        )
        -
        julianday(
            cp_last.last_purchase_date
        )

        AS INTEGER

    ) AS recency_days

FROM customers c

JOIN customer_profitability cp

    ON c.customer_id = cp.customer_id

JOIN (

    SELECT

        customer_id,

        MAX(transaction_date)
            AS last_purchase_date

    FROM transactions

    GROUP BY customer_id

) cp_last

    ON c.customer_id = cp_last.customer_id

ORDER BY

    cp.gross_profit DESC

LIMIT 10;