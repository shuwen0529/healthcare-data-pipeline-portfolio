-- Create a member-level analytical dataset from standardized source tables.
-- The same pattern can be applied to claims, survey, or administrative datasets.

WITH eligible_activity AS (
    SELECT
        a.member_id,
        m.region,
        a.activity_date,
        LOWER(TRIM(a.activity_type)) AS activity_type,
        CAST(a.amount AS DECIMAL(18, 2)) AS amount
    FROM standardized_activity a
    INNER JOIN standardized_members m
        ON a.member_id = m.member_id
    WHERE a.activity_date BETWEEN m.coverage_start AND m.coverage_end
),
member_features AS (
    SELECT
        member_id,
        region,
        COUNT(*) AS total_activity_count,
        SUM(amount) AS total_amount,
        SUM(CASE WHEN activity_type = 'rx' THEN 1 ELSE 0 END) AS rx_count,
        SUM(CASE WHEN activity_type = 'lab' THEN 1 ELSE 0 END) AS lab_count,
        MAX(activity_date) AS last_activity_date
    FROM eligible_activity
    GROUP BY member_id, region
)
SELECT *
FROM member_features;
