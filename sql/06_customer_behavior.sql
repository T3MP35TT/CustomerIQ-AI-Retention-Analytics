-- ============================================================
-- CUSTOMERIQ
-- CUSTOMER BEHAVIOR MATRIX
-- ============================================================


-- ============================================================
-- 1. CUSTOMER PURCHASE + ENGAGEMENT PROFILE
-- ============================================================

WITH engagement AS (

    SELECT

        customer_id,

        COUNT(*) AS total_interactions,

        COUNT(
            DISTINCT interaction_type
        ) AS interaction_types,

        COUNT(
            DISTINCT channel
        ) AS channels_used

    FROM interactions

    GROUP BY customer_id

),

purchases AS (

    SELECT

        customer_id,

        COUNT(
            DISTINCT transaction_id
        ) AS total_orders,

        ROUND(
            SUM(revenue),
            2
        ) AS total_revenue,

        MAX(
            transaction_date
        ) AS last_purchase_date

    FROM transactions

    GROUP BY customer_id

),

base AS (

    SELECT

        c.customer_id,

        c.customer_segment,

        c.acquisition_channel,

        c.location,

        COALESCE(
            e.total_interactions,
            0
        ) AS total_interactions,

        COALESCE(
            e.interaction_types,
            0
        ) AS interaction_types,

        COALESCE(
            e.channels_used,
            0
        ) AS channels_used,

        COALESCE(
            p.total_orders,
            0
        ) AS total_orders,

        COALESCE(
            p.total_revenue,
            0
        ) AS total_revenue,

        p.last_purchase_date

    FROM customers c

    LEFT JOIN engagement e
        ON c.customer_id = e.customer_id

    LEFT JOIN purchases p
        ON c.customer_id = p.customer_id

)

SELECT

    *,

    CASE

        WHEN total_interactions = 0
            THEN 'No Engagement'

        WHEN total_interactions < 20
            THEN 'Low Engagement'

        WHEN total_interactions < 50
            THEN 'Medium Engagement'

        WHEN total_interactions < 100
            THEN 'High Engagement'

        ELSE 'Very High Engagement'

    END AS engagement_band,

    CASE

        WHEN total_orders = 0
            THEN 'Non-Purchaser'

        WHEN total_orders = 1
            THEN 'One-Time Buyer'

        ELSE 'Repeat Buyer'

    END AS purchase_status

FROM base

ORDER BY
    total_revenue DESC;


-- ============================================================
-- 2. ENGAGEMENT × PURCHASE MATRIX
-- ============================================================

WITH engagement AS (

    SELECT

        customer_id,

        COUNT(*) AS total_interactions

    FROM interactions

    GROUP BY customer_id

),

purchases AS (

    SELECT

        customer_id,

        COUNT(
            DISTINCT transaction_id
        ) AS total_orders,

        SUM(
            revenue
        ) AS revenue

    FROM transactions

    GROUP BY customer_id

),

customer_profile AS (

    SELECT

        c.customer_id,

        COALESCE(
            e.total_interactions,
            0
        ) AS interactions,

        COALESCE(
            p.total_orders,
            0
        ) AS orders,

        COALESCE(
            p.revenue,
            0
        ) AS revenue

    FROM customers c

    LEFT JOIN engagement e
        ON c.customer_id = e.customer_id

    LEFT JOIN purchases p
        ON c.customer_id = p.customer_id

)

SELECT

    CASE

        WHEN interactions = 0
            THEN 'No Engagement'

        WHEN interactions < 50
            THEN 'Low / Medium Engagement'

        ELSE 'High Engagement'

    END AS engagement_group,

    CASE

        WHEN orders = 0
            THEN 'Non-Purchaser'

        ELSE 'Purchaser'

    END AS purchase_group,

    COUNT(*) AS customers,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue,

    ROUND(
        AVG(orders),
        2
    ) AS average_orders

FROM customer_profile

GROUP BY

    engagement_group,
    purchase_group

ORDER BY

    engagement_group,
    purchase_group;


-- ============================================================
-- 3. HIGH-ENGAGEMENT NON-PURCHASERS
-- ============================================================

WITH engagement AS (

    SELECT

        customer_id,

        COUNT(*) AS total_interactions

    FROM interactions

    GROUP BY customer_id

)

SELECT

    c.customer_id,

    c.customer_segment,

    c.location,

    c.acquisition_channel,

    e.total_interactions

FROM customers c

JOIN engagement e
    ON c.customer_id = e.customer_id

LEFT JOIN transactions t
    ON c.customer_id = t.customer_id

WHERE

    e.total_interactions >= 50

    AND t.customer_id IS NULL

GROUP BY

    c.customer_id,

    c.customer_segment,

    c.location,

    c.acquisition_channel,

    e.total_interactions

ORDER BY
    e.total_interactions DESC;


-- ============================================================
-- 4. PURCHASERS WITH LOW ENGAGEMENT
-- ============================================================

WITH engagement AS (

    SELECT

        customer_id,

        COUNT(*) AS total_interactions

    FROM interactions

    GROUP BY customer_id

),

purchases AS (

    SELECT

        customer_id,

        COUNT(
            DISTINCT transaction_id
        ) AS orders,

        SUM(
            revenue
        ) AS revenue

    FROM transactions

    GROUP BY customer_id

)

SELECT

    p.customer_id,

    c.customer_segment,

    c.location,

    c.acquisition_channel,

    COALESCE(
        e.total_interactions,
        0
    ) AS interactions,

    p.orders,

    ROUND(
        p.revenue,
        2
    ) AS revenue

FROM purchases p

JOIN customers c
    ON p.customer_id = c.customer_id

LEFT JOIN engagement e
    ON p.customer_id = e.customer_id

WHERE

    COALESCE(
        e.total_interactions,
        0
    ) < 20

ORDER BY
    p.revenue DESC;


-- ============================================================
-- 5. HIGH-VALUE CUSTOMERS WITH DECLINING RECENCY
-- ============================================================

WITH customer_metrics AS (

    SELECT

        customer_id,

        COUNT(
            DISTINCT transaction_id
        ) AS orders,

        SUM(
            revenue
        ) AS revenue,

        MAX(
            transaction_date
        ) AS last_purchase_date

    FROM transactions

    GROUP BY customer_id

),

analysis_date AS (

    SELECT
        MAX(transaction_date) AS latest_date

    FROM transactions

)

SELECT

    cm.customer_id,

    c.customer_segment,

    c.location,

    c.acquisition_channel,

    cm.orders,

    ROUND(
        cm.revenue,
        2
    ) AS revenue,

    CAST(

        julianday(
            a.latest_date
        )
        -
        julianday(
            cm.last_purchase_date
        )

        AS INTEGER

    ) AS recency_days

FROM customer_metrics cm

JOIN customers c
    ON cm.customer_id = c.customer_id

CROSS JOIN analysis_date a

WHERE

    cm.revenue >= 100000

    AND

    julianday(
        a.latest_date
    )
    -
    julianday(
        cm.last_purchase_date
    ) >= 60

ORDER BY
    cm.revenue DESC;


-- ============================================================
-- 6. CUSTOMER BEHAVIOR SUMMARY
-- ============================================================

WITH engagement AS (

    SELECT

        customer_id,

        COUNT(*) AS interactions

    FROM interactions

    GROUP BY customer_id

),

purchases AS (

    SELECT

        customer_id,

        COUNT(
            DISTINCT transaction_id
        ) AS orders,

        SUM(
            revenue
        ) AS revenue

    FROM transactions

    GROUP BY customer_id

),

profiles AS (

    SELECT

        c.customer_id,

        COALESCE(
            e.interactions,
            0
        ) AS interactions,

        COALESCE(
            p.orders,
            0
        ) AS orders,

        COALESCE(
            p.revenue,
            0
        ) AS revenue

    FROM customers c

    LEFT JOIN engagement e
        ON c.customer_id = e.customer_id

    LEFT JOIN purchases p
        ON c.customer_id = p.customer_id

)

SELECT

    CASE

        WHEN interactions >= 50
             AND orders > 0

            THEN 'Engaged Purchasers'

        WHEN interactions >= 50
             AND orders = 0

            THEN 'Engaged Non-Purchasers'

        WHEN interactions < 50
             AND orders > 0

            THEN 'Low-Engagement Purchasers'

        ELSE 'Low-Activity Customers'

    END AS customer_behavior_group,

    COUNT(*) AS customers,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue,

    ROUND(
        AVG(orders),
        2
    ) AS average_orders,

    ROUND(
        AVG(interactions),
        2
    ) AS average_interactions

FROM profiles

GROUP BY
    customer_behavior_group

ORDER BY
    revenue DESC;