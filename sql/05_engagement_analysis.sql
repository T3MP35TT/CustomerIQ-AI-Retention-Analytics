-- ============================================================
-- CUSTOMERIQ
-- CUSTOMER ENGAGEMENT ANALYSIS
-- ============================================================


-- ============================================================
-- 1. OVERALL INTERACTION SUMMARY
-- ============================================================

SELECT

    interaction_type,

    COUNT(*) AS interactions,

    COUNT(
        DISTINCT customer_id
    ) AS unique_customers

FROM interactions

GROUP BY
    interaction_type

ORDER BY
    interactions DESC;


-- ============================================================
-- 2. INTERACTION TYPE BY CHANNEL
-- ============================================================

SELECT

    channel,

    interaction_type,

    COUNT(*) AS interactions,

    COUNT(
        DISTINCT customer_id
    ) AS unique_customers

FROM interactions

GROUP BY

    channel,
    interaction_type

ORDER BY
    channel,
    interactions DESC;


-- ============================================================
-- 3. CUSTOMER ENGAGEMENT METRICS
-- ============================================================

SELECT

    customer_id,

    COUNT(*) AS total_interactions,

    COUNT(
        DISTINCT interaction_type
    ) AS interaction_types_used,

    COUNT(
        DISTINCT channel
    ) AS channels_used,

    SUM(
        CASE
            WHEN interaction_type = 'view'
                THEN 1
            ELSE 0
        END
    ) AS views,

    SUM(
        CASE
            WHEN interaction_type = 'click'
                THEN 1
            ELSE 0
        END
    ) AS clicks,

    SUM(
        CASE
            WHEN interaction_type = 'add_to_cart'
                THEN 1
            ELSE 0
        END
    ) AS add_to_carts,

    SUM(
        CASE
            WHEN interaction_type = 'email_open'
                THEN 1
            ELSE 0
        END
    ) AS email_opens

FROM interactions

GROUP BY
    customer_id

ORDER BY
    total_interactions DESC;


-- ============================================================
-- 4. ENGAGEMENT BY CUSTOMER SEGMENT
-- ============================================================

SELECT

    c.customer_segment,

    COUNT(
        DISTINCT c.customer_id
    ) AS customers,

    ROUND(
        AVG(
            COALESCE(e.total_interactions, 0)
        ),
        2
    ) AS avg_interactions_per_customer,

    ROUND(
        AVG(
            COALESCE(e.views, 0)
        ),
        2
    ) AS avg_views,

    ROUND(
        AVG(
            COALESCE(e.clicks, 0)
        ),
        2
    ) AS avg_clicks,

    ROUND(
        AVG(
            COALESCE(e.add_to_carts, 0)
        ),
        2
    ) AS avg_add_to_carts,

    ROUND(
        AVG(
            COALESCE(e.email_opens, 0)
        ),
        2
    ) AS avg_email_opens

FROM customers c

LEFT JOIN (

    SELECT

        customer_id,

        COUNT(*) AS total_interactions,

        SUM(
            CASE
                WHEN interaction_type = 'view'
                    THEN 1
                ELSE 0
            END
        ) AS views,

        SUM(
            CASE
                WHEN interaction_type = 'click'
                    THEN 1
                ELSE 0
            END
        ) AS clicks,

        SUM(
            CASE
                WHEN interaction_type = 'add_to_cart'
                    THEN 1
                ELSE 0
            END
        ) AS add_to_carts,

        SUM(
            CASE
                WHEN interaction_type = 'email_open'
                    THEN 1
                ELSE 0
            END
        ) AS email_opens

    FROM interactions

    GROUP BY customer_id

) e

ON c.customer_id = e.customer_id

GROUP BY
    c.customer_segment

ORDER BY
    avg_interactions_per_customer DESC;


-- ============================================================
-- 5. ENGAGEMENT vs PURCHASE BEHAVIOR
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

        ROUND(
            SUM(revenue),
            2
        ) AS total_revenue

    FROM transactions

    GROUP BY customer_id

)

SELECT

    CASE

        WHEN COALESCE(
            e.total_interactions,
            0
        ) < 20

            THEN 'Low Engagement'

        WHEN COALESCE(
            e.total_interactions,
            0
        ) < 50

            THEN 'Medium Engagement'

        WHEN COALESCE(
            e.total_interactions,
            0
        ) < 100

            THEN 'High Engagement'

        ELSE 'Very High Engagement'

    END AS engagement_band,

    COUNT(
        DISTINCT e.customer_id
    ) AS customers,

    ROUND(
        AVG(
            COALESCE(
                p.total_orders,
                0
            )
        ),
        2
    ) AS avg_orders,

    ROUND(
        AVG(
            COALESCE(
                p.total_revenue,
                0
            )
        ),
        2
    ) AS avg_revenue

FROM engagement e

LEFT JOIN purchases p
    ON e.customer_id = p.customer_id

GROUP BY engagement_band

ORDER BY
    MIN(e.total_interactions);


-- ============================================================
-- 6. ENGAGEMENT AND REVENUE
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

        SUM(revenue) AS revenue

    FROM transactions

    GROUP BY customer_id

)

SELECT

    CASE

        WHEN e.total_interactions < 20
            THEN 'Low Engagement'

        WHEN e.total_interactions < 50
            THEN 'Medium Engagement'

        WHEN e.total_interactions < 100
            THEN 'High Engagement'

        ELSE 'Very High Engagement'

    END AS engagement_band,

    COUNT(
        DISTINCT e.customer_id
    ) AS customers,

    ROUND(
        SUM(
            COALESCE(
                p.revenue,
                0
            )
        ),
        2
    ) AS total_revenue,

    ROUND(
        AVG(
            COALESCE(
                p.revenue,
                0
            )
        ),
        2
    ) AS revenue_per_customer

FROM engagement e

LEFT JOIN purchases p
    ON e.customer_id = p.customer_id

GROUP BY engagement_band

ORDER BY
    MIN(e.total_interactions);


-- ============================================================
-- 7. CHANNEL ENGAGEMENT
-- ============================================================

SELECT

    channel,

    COUNT(*) AS interactions,

    COUNT(
        DISTINCT customer_id
    ) AS customers,

    ROUND(

        COUNT(*)
        * 1.0
        /
        COUNT(
            DISTINCT customer_id
        ),

        2

    ) AS interactions_per_customer

FROM interactions

GROUP BY channel

ORDER BY
    interactions_per_customer DESC;


-- ============================================================
-- 8. MONTHLY ENGAGEMENT
-- ============================================================

SELECT

    interaction_month,

    COUNT(*) AS interactions,

    COUNT(
        DISTINCT customer_id
    ) AS active_customers

FROM interactions

GROUP BY
    interaction_month

ORDER BY
    interaction_month;


-- ============================================================
-- 9. ENGAGEMENT OF RFM SEGMENTS
-- ============================================================

WITH customer_rfm AS (

    SELECT

        customer_id,

        CAST(

            julianday(
                (
                    SELECT
                        MAX(transaction_date)
                    FROM transactions
                )
            )
            -
            julianday(
                MAX(transaction_date)
            )

            AS INTEGER

        ) AS recency,

        COUNT(
            DISTINCT transaction_id
        ) AS frequency,

        SUM(
            revenue
        ) AS monetary

    FROM transactions

    GROUP BY customer_id

),

rfm_scores AS (

    SELECT

        *,

        NTILE(5) OVER (
            ORDER BY recency DESC
        ) AS recency_score,

        NTILE(5) OVER (
            ORDER BY frequency
        ) AS frequency_score,

        NTILE(5) OVER (
            ORDER BY monetary
        ) AS monetary_score

    FROM customer_rfm

),

rfm_segments AS (

    SELECT

        customer_id,

        CASE

            WHEN recency_score >= 4
                 AND frequency_score >= 4
                 AND monetary_score >= 4
                THEN 'Champions'

            WHEN recency_score >= 3
                 AND frequency_score >= 4
                THEN 'Loyal Customers'

            WHEN recency_score >= 4
                 AND frequency_score <= 3
                 AND monetary_score >= 3
                THEN 'Potential Loyalists'

            WHEN recency_score <= 2
                 AND frequency_score >= 3
                 AND monetary_score >= 3
                THEN 'At Risk'

            WHEN recency_score <= 2
                 AND frequency_score <= 2
                THEN 'Lost Customers'

            WHEN recency_score >= 4
                 AND frequency_score <= 2
                THEN 'New / Promising'

            ELSE 'Needs Attention'

        END AS rfm_segment

    FROM rfm_scores
),

engagement AS (

    SELECT

        customer_id,

        COUNT(*) AS total_interactions

    FROM interactions

    GROUP BY customer_id

)

SELECT

    r.rfm_segment,

    COUNT(
        DISTINCT r.customer_id
    ) AS customers,

    ROUND(
        AVG(
            COALESCE(
                e.total_interactions,
                0
            )
        ),
        2
    ) AS avg_interactions,

    ROUND(
        MAX(
            COALESCE(
                e.total_interactions,
                0
            )
        ),
        2
    ) AS max_interactions

FROM rfm_segments r

LEFT JOIN engagement e
    ON r.customer_id = e.customer_id

GROUP BY
    r.rfm_segment

ORDER BY
    avg_interactions DESC;