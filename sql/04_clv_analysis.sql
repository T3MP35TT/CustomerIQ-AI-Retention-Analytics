-- ============================================================
-- CUSTOMERIQ
-- CUSTOMER LIFETIME VALUE & PROFITABILITY ANALYSIS
-- ============================================================


-- ============================================================
-- 1. CUSTOMER REVENUE & PROFIT
-- ============================================================

WITH customer_value AS (

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
                t.quantity
                * p.cost
            ),
            2
        ) AS total_cost,

        ROUND(
            SUM(t.revenue)
            -
            SUM(
                t.quantity
                * p.cost
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
        ) AS gross_margin_percentage

    FROM transactions t

    JOIN products p
        ON t.product_id = p.product_id

    GROUP BY
        t.customer_id
)

SELECT *

FROM customer_value

ORDER BY gross_profit DESC;


-- ============================================================
-- 2. CUSTOMER LIFESPAN
-- ============================================================

WITH customer_lifespan AS (

    SELECT

        t.customer_id,

        MIN(
            t.transaction_date
        ) AS first_purchase_date,

        MAX(
            t.transaction_date
        ) AS last_purchase_date,

        CAST(

            julianday(
                MAX(t.transaction_date)
            )
            -
            julianday(
                MIN(t.transaction_date)
            )

            AS INTEGER

        ) AS customer_lifespan_days

    FROM transactions t

    GROUP BY
        t.customer_id
)

SELECT *

FROM customer_lifespan

ORDER BY customer_lifespan_days DESC;


-- ============================================================
-- 3. CUSTOMER VALUE PROFILE
-- ============================================================

WITH customer_metrics AS (

    SELECT

        t.customer_id,

        COUNT(
            DISTINCT t.transaction_id
        ) AS total_orders,

        SUM(
            t.quantity
        ) AS total_units,

        SUM(
            t.revenue
        ) AS total_revenue,

        SUM(
            t.quantity * p.cost
        ) AS total_cost,

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

customer_value AS (

    SELECT

        *,

        total_revenue
        -
        total_cost
        AS gross_profit,

        CAST(

            julianday(
                last_purchase_date
            )
            -
            julianday(
                first_purchase_date
            )

            AS INTEGER

        ) AS lifespan_days

    FROM customer_metrics
)

SELECT

    customer_id,

    total_orders,

    total_units,

    ROUND(
        total_revenue,
        2
    ) AS total_revenue,

    ROUND(
        total_cost,
        2
    ) AS total_cost,

    ROUND(
        gross_profit,
        2
    ) AS gross_profit,

    ROUND(

        gross_profit
        /
        NULLIF(
            total_revenue,
            0
        )
        * 100,

        2

    ) AS gross_margin_percentage,

    first_purchase_date,

    last_purchase_date,

    lifespan_days,

    ROUND(

        total_revenue
        /
        NULLIF(
            total_orders,
            0
        ),

        2

    ) AS average_order_value

FROM customer_value

ORDER BY gross_profit DESC;


-- ============================================================
-- 4. ANNUALIZED CUSTOMER VALUE
-- ============================================================
--
-- This is an observed-value-based estimate.
-- It should NOT be interpreted as guaranteed future CLV.
--
-- For customers with a lifespan shorter than one year,
-- we use one year as the minimum denominator to avoid
-- extreme annualization.
-- ============================================================

WITH customer_metrics AS (

    SELECT

        t.customer_id,

        SUM(
            t.revenue
        ) AS total_revenue,

        SUM(
            t.quantity * p.cost
        ) AS total_cost,

        COUNT(
            DISTINCT t.transaction_id
        ) AS total_orders,

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

customer_value AS (

    SELECT

        *,

        total_revenue
        -
        total_cost
        AS gross_profit,

        CASE

            WHEN
                julianday(
                    last_purchase_date
                )
                -
                julianday(
                    first_purchase_date
                )
                < 365

            THEN 365

            ELSE

                julianday(
                    last_purchase_date
                )
                -
                julianday(
                    first_purchase_date
                )

        END AS annualization_days

    FROM customer_metrics
)

SELECT

    customer_id,

    ROUND(
        total_revenue,
        2
    ) AS total_revenue,

    ROUND(
        gross_profit,
        2
    ) AS gross_profit,

    total_orders,

    ROUND(

        gross_profit
        /
        annualization_days
        * 365,

        2

    ) AS annualized_profit_value

FROM customer_value

ORDER BY annualized_profit_value DESC;


-- ============================================================
-- 5. CUSTOMER PROFITABILITY SEGMENTS
-- ============================================================

WITH customer_profit AS (

    SELECT

        t.customer_id,

        SUM(
            t.revenue
        ) AS revenue,

        SUM(
            t.quantity * p.cost
        ) AS cost,

        SUM(
            t.revenue
        )
        -
        SUM(
            t.quantity * p.cost
        ) AS profit

    FROM transactions t

    JOIN products p
        ON t.product_id = p.product_id

    GROUP BY
        t.customer_id
)

SELECT

    CASE

        WHEN profit >= 1000000
            THEN 'Very High Value'

        WHEN profit >= 500000
            THEN 'High Value'

        WHEN profit >= 100000
            THEN 'Medium Value'

        WHEN profit >= 25000
            THEN 'Low Value'

        ELSE 'Very Low Value'

    END AS profitability_segment,

    COUNT(*) AS customers,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue,

    ROUND(
        SUM(profit),
        2
    ) AS gross_profit,

    ROUND(
        AVG(profit),
        2
    ) AS average_profit_per_customer

FROM customer_profit

GROUP BY profitability_segment

ORDER BY
    MIN(profit);


-- ============================================================
-- 6. CUSTOMER VALUE BY ACQUISITION CHANNEL
-- ============================================================

SELECT

    c.acquisition_channel,

    COUNT(
        DISTINCT t.customer_id
    ) AS purchasing_customers,

    ROUND(
        SUM(t.revenue),
        2
    ) AS revenue,

    ROUND(
        SUM(
            t.revenue
            -
            (
                t.quantity * p.cost
            )
        ),
        2
    ) AS gross_profit,

    ROUND(

        SUM(
            t.revenue
            -
            (
                t.quantity * p.cost
            )
        )
        /
        NULLIF(
            COUNT(DISTINCT t.customer_id),
            0
        ),

        2

    ) AS profit_per_customer

FROM transactions t

JOIN customers c
    ON t.customer_id = c.customer_id

JOIN products p
    ON t.product_id = p.product_id

GROUP BY
    c.acquisition_channel

ORDER BY
    profit_per_customer DESC;


-- ============================================================
-- 7. CUSTOMER VALUE BY ORIGINAL SEGMENT
-- ============================================================

SELECT

    c.customer_segment,

    COUNT(
        DISTINCT t.customer_id
    ) AS purchasing_customers,

    ROUND(
        SUM(t.revenue),
        2
    ) AS revenue,

    ROUND(

        SUM(
            t.revenue
            -
            (
                t.quantity * p.cost
            )
        ),

        2

    ) AS gross_profit,

    ROUND(

        SUM(
            t.revenue
            -
            (
                t.quantity * p.cost
            )
        )
        /
        NULLIF(
            COUNT(DISTINCT t.customer_id),
            0
        ),

        2

    ) AS profit_per_customer

FROM transactions t

JOIN customers c
    ON t.customer_id = c.customer_id

JOIN products p
    ON t.product_id = p.product_id

GROUP BY
    c.customer_segment

ORDER BY
    gross_profit DESC;


-- ============================================================
-- 8. TOP 20 CUSTOMERS BY GROSS PROFIT
-- ============================================================

SELECT

    c.customer_id,

    c.customer_segment,

    c.location,

    c.acquisition_channel,

    COUNT(
        DISTINCT t.transaction_id
    ) AS orders,

    ROUND(
        SUM(t.revenue),
        2
    ) AS revenue,

    ROUND(

        SUM(
            t.revenue
            -
            (
                t.quantity * p.cost
            )
        ),

        2

    ) AS gross_profit

FROM customers c

JOIN transactions t
    ON c.customer_id = t.customer_id

JOIN products p
    ON t.product_id = p.product_id

GROUP BY

    c.customer_id,

    c.customer_segment,

    c.location,

    c.acquisition_channel

ORDER BY
    gross_profit DESC

LIMIT 20;