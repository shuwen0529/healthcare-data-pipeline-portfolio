-- Optimized incremental load pattern.
-- Key ideas:
-- 1. Filter new records before joining to dimensions.
-- 2. Select only required columns.
-- 3. Pre-aggregate to the final analytical grain.
-- 4. Use a MERGE pattern to avoid full table rebuilds.

WITH incremental_source AS (
    SELECT
        member_id,
        CAST(activity_date AS DATE) AS activity_date,
        LOWER(TRIM(activity_type)) AS activity_type,
        CAST(amount AS DECIMAL(18, 2)) AS amount
    FROM source_activity
    WHERE activity_date > (
        SELECT COALESCE(MAX(processed_through_date), DATE '1900-01-01')
        FROM pipeline_audit
        WHERE pipeline_name = 'monthly_activity_features'
          AND status = 'SUCCESS'
    )
      AND status = 'valid'
),
monthly_features AS (
    SELECT
        member_id,
        DATE_TRUNC('month', activity_date) AS activity_month,
        activity_type,
        COUNT(*) AS activity_count,
        SUM(amount) AS total_amount
    FROM incremental_source
    GROUP BY member_id, DATE_TRUNC('month', activity_date), activity_type
)
MERGE INTO analytics.monthly_activity_features AS target
USING monthly_features AS source
    ON target.member_id = source.member_id
   AND target.activity_month = source.activity_month
   AND target.activity_type = source.activity_type
WHEN MATCHED THEN UPDATE SET
    activity_count = source.activity_count,
    total_amount = source.total_amount,
    updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN INSERT (
    member_id,
    activity_month,
    activity_type,
    activity_count,
    total_amount,
    updated_at
) VALUES (
    source.member_id,
    source.activity_month,
    source.activity_type,
    source.activity_count,
    source.total_amount,
    CURRENT_TIMESTAMP
);
