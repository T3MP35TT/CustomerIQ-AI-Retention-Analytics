-- ============================================================
-- CUSTOMERIQ
-- SALES & REVENUE ANALYSIS
-- ============================================================


-- ============================================================
-- 1. OVERALL BUSINESS KPIs
-- ============================================================

SELECT
    COUNT(DISTINCT transaction_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS purchasing_customers,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS average_order_value
FROM transactions;


-- ============================================================
-- 2. MONTHLY REVENUE
-- ============================================================

SELECT
    transaction_month,
    COUNT(DISTINCT transaction_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(revenue), 2) AS revenue
FROM transactions
GROUP BY transaction_month
ORDER BY transaction_month;


-- ============================================================
-- 3. MONTHLY REVENUE GROWTH
-- ============================================================

WITH monthly_revenue AS (

    SELECT
        transaction_month,
        SUM(revenue) AS revenue

    FROM transactions

    GROUP BY transaction_month
),

revenue_growth AS (

    SELECT

        transaction_month,

        revenue,

        LAG(revenue) OVER (
            ORDER BY transaction_month
        ) AS previous_month_revenue

    FROM monthly_revenue
)

SELECT

    transaction_month,

    ROUND(revenue, 2) AS revenue,

    ROUND(
        previous_month_revenue,
        2
    ) AS previous_month_revenue,

    ROUND(
        (
            revenue
            - previous_month_revenue
        )
        /
        NULLIF(
            previous_month_revenue,
            0
        )
        * 100,
        2
    ) AS revenue_growth_percentage

FROM revenue_growth

ORDER BY transaction_month;


-- ============================================================
-- 4. REVENUE BY CUSTOMER SEGMENT
-- ============================================================

SELECT

    c.customer_segment,

    COUNT(
        DISTINCT t.customer_id
    ) AS customers,

    COUNT(
        DISTINCT t.transaction_id
    ) AS orders,

    ROUND(
        SUM(t.revenue),
        2
    ) AS revenue,

    ROUND(
        AVG(t.revenue),
        2
    ) AS average_order_value

FROM transactions t

JOIN customers c
    ON t.customer_id = c.customer_id

GROUP BY
    c.customer_segment

ORDER BY
    revenue DESC;


-- ============================================================
-- 5. REVENUE BY ACQUISITION CHANNEL
-- ============================================================

SELECT

    c.acquisition_channel,

    COUNT(
        DISTINCT c.customer_id
    ) AS customers,

    COUNT(
        DISTINCT t.transaction_id
    ) AS orders,

    ROUND(
        SUM(t.revenue),
        2
    ) AS revenue,

    ROUND(
        SUM(t.revenue)
        /
        NULLIF(
            COUNT(DISTINCT c.customer_id),
            0
        ),
        2
    ) AS revenue_per_customer

FROM customers c

LEFT JOIN transactions t
    ON c.customer_id = t.customer_id

GROUP BY
    c.acquisition_channel

ORDER BY
    revenue DESC;


-- ============================================================
-- 6. REVENUE BY LOCATION
-- ============================================================

SELECT

    c.location,

    COUNT(
        DISTINCT c.customer_id
    ) AS customers,

    COUNT(
        DISTINCT t.transaction_id
    ) AS orders,

    ROUND(
        SUM(t.revenue),
        2
    ) AS revenue

FROM customers c

LEFT JOIN transactions t
    ON c.customer_id = t.customer_id

GROUP BY
    c.location

ORDER BY
    revenue DESC;


-- ============================================================
-- 7. DISCOUNT IMPACT
-- ============================================================

SELECT

    CASE

        WHEN discount = 0
            THEN 'No Discount'

        WHEN discount <= 0.10
            THEN '0–10%'

        WHEN discount <= 0.20
            THEN '10–20%'

        WHEN discount <= 0.30
            THEN '20–30%'

        ELSE '30%+'

    END AS discount_band,

    COUNT(
        DISTINCT transaction_id
    ) AS orders,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue,

    ROUND(
        AVG(revenue),
        2
    ) AS average_order_value

FROM transactions

GROUP BY
    discount_band

ORDER BY
    MIN(discount);


-- ============================================================
-- 8. YEARLY PERFORMANCE
-- ============================================================

SELECT

    transaction_year,

    COUNT(
        DISTINCT transaction_id
    ) AS orders,

    COUNT(
        DISTINCT customer_id
    ) AS customers,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue

FROM transactions

GROUP BY
    transaction_year

ORDER BY
    transaction_year;


-- ============================================================
-- 9. TRANSACTIONS FLAGGED BEFORE PRODUCT LAUNCH
-- ============================================================

SELECT

    transaction_before_product_launch,

    COUNT(*) AS transactions,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue

FROM transactions

GROUP BY
    transaction_before_product_launch

ORDER BY
    transaction_before_product_launch;