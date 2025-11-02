-- AI-GENERATED from contracts/dim_submission.yml
-- Warehouse dimension: One row per insurance submission

{{ config(
    materialized='table',
    schema='warehouse'
) }}

WITH staging AS (
    SELECT * FROM {{ ref('stg_submissions') }}
),

final AS (
    -- AI-GENERATED field mappings from dim_submission.yml schema
    SELECT
        submission_id,
        acord_submission_number,
        business_name,
        naics_code,
        annual_revenue,
        employee_count,
        years_in_business,
        business_address,
        requested_coverage_types,
        requested_limits,
        submission_date,
        created_at
    FROM staging
)

SELECT * FROM final
