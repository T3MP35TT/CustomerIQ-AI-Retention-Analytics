-- ============================================================
-- CUSTOMERIQ
-- RFM CUSTOMER SEGMENTATION
-- ============================================================


-- ============================================================
-- 1. CALCULATE RAW RFM METRICS
-- ============================================================

WITH analysis_date AS (

    SELECT
        MAX(transaction_date) AS snapshot_date

    FROM transactions
),

customer_rfm AS (

    SELECT

        t.customer_id,

        CAST(
            julianday(
                a.snapshot_date
            )
            -
            julianday(
                MAX(t.transaction_date)
            )
            AS INTEGER
        ) AS recency,

        COUNT(
            DISTINCT t.transaction_id
        ) AS frequency,

        ROUND(
            SUM(t.revenue),
            2
        ) AS monetary

    FROM transactions t

    CROSS JOIN analysis_date a

    GROUP BY
        t.customer_id
)

SELECT *

FROM customer_rfm

ORDER BY monetary DESC;


-- ============================================================
-- 2. ASSIGN RFM SCORES
-- ============================================================

WITH analysis_date AS (

    SELECT
        MAX(transaction_date) AS snapshot_date

    FROM transactions
),

customer_rfm AS (

    SELECT

        t.customer_id,

        CAST(
            julianday(
                a.snapshot_date
            )
            -
            julianday(
                MAX(t.transaction_date)
            )
            AS INTEGER
        ) AS recency,

        COUNT(
            DISTINCT t.transaction_id
        ) AS frequency,

        ROUND(
            SUM(t.revenue),
            2
        ) AS monetary

    FROM transactions t

    CROSS JOIN analysis_date a

    GROUP BY
        t.customer_id
),

rfm_scores AS (

    SELECT

        customer_id,

        recency,

        frequency,

        monetary,

        -- Lower recency is better
        NTILE(5) OVER (
            ORDER BY recency DESC
        ) AS recency_score,

        -- Higher frequency is better
        NTILE(5) OVER (
            ORDER BY frequency
        ) AS frequency_score,

        -- Higher monetary value is better
        NTILE(5) OVER (
            ORDER BY monetary
        ) AS monetary_score

    FROM customer_rfm
)

SELECT *

FROM rfm_scores

ORDER BY
    recency_score DESC,
    frequency_score DESC,
    monetary_score DESC;


-- ============================================================
-- 3. CREATE RFM SEGMENTS
-- ============================================================

WITH analysis_date AS (

    SELECT
        MAX(transaction_date) AS snapshot_date

    FROM transactions
),

customer_rfm AS (

    SELECT

        t.customer_id,

        CAST(
            julianday(
                a.snapshot_date
            )
            -
            julianday(
                MAX(t.transaction_date)
            )
            AS INTEGER
        ) AS recency,

        COUNT(
            DISTINCT t.transaction_id
        ) AS frequency,

        ROUND(
            SUM(t.revenue),
            2
        ) AS monetary

    FROM transactions t

    CROSS JOIN analysis_date a

    GROUP BY
        t.customer_id
),

rfm_scores AS (

    SELECT

        customer_id,

        recency,

        frequency,

        monetary,

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

segmented AS (

    SELECT

        *,

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
)

SELECT *

FROM segmented

ORDER BY
    monetary DESC;


-- ============================================================
-- 4. RFM SEGMENT SUMMARY
-- ============================================================

WITH analysis_date AS (

    SELECT
        MAX(transaction_date) AS snapshot_date

    FROM transactions
),

customer_rfm AS (

    SELECT

        t.customer_id,

        CAST(
            julianday(
                a.snapshot_date
            )
            -
            julianday(
                MAX(t.transaction_date)
            )
            AS INTEGER
        ) AS recency,

        COUNT(
            DISTINCT t.transaction_id
        ) AS frequency,

        ROUND(
            SUM(t.revenue),
            2
        ) AS monetary

    FROM transactions t

    CROSS JOIN analysis_date a

    GROUP BY
        t.customer_id
),

rfm_scores AS (

    SELECT

        customer_id,

        recency,

        frequency,

        monetary,

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

segmented AS (

    SELECT

        *,

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
)

SELECT

    rfm_segment,

    COUNT(*) AS customers,

    ROUND(
        SUM(monetary),
        2
    ) AS revenue,

    ROUND(
        AVG(monetary),
        2
    ) AS average_customer_value,

    ROUND(
        AVG(frequency),
        2
    ) AS average_frequency,

    ROUND(
        AVG(recency),
        2
    ) AS average_recency_days

FROM segmented

GROUP BY rfm_segment

ORDER BY revenue DESC;