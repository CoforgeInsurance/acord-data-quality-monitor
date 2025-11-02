-- AI-GENERATED from contracts/fact_quality_check.yml
-- Warehouse fact: Quality check results for each submission

{{ config(
    materialized='table',
    schema='warehouse'
) }}

WITH submissions AS (
    SELECT * FROM {{ ref('dim_submission') }}
),

-- Stub for quality check results
-- In production, this would be populated by the Python quality validator
quality_checks AS (
    SELECT
        gen_random_uuid()::VARCHAR(50) as quality_check_id,
        submission_id,
        'REQ-BUSINESS_NAME' as rule_id,
        'Required Field: Business Name' as rule_name,
        'required_field' as rule_category,
        'error' as severity,
        true as passed,
        'Not null' as expected_value,
        business_name as actual_value,
        NULL as error_message,
        'business_name' as field_name,
        CURRENT_TIMESTAMP as check_timestamp
    FROM submissions
    LIMIT 0  -- No actual data, just schema definition
)

SELECT * FROM quality_checks
