-- AI-GENERATED from contracts/dim_submission.yml
-- Staging layer: Raw ACORD submissions → structured format

{{ config(
    materialized='view',
    schema='staging'
) }}

WITH source AS (
    -- In production, this would read from ods.raw_submissions
    -- For now, we'll create a stub that demonstrates the contract mapping
    SELECT
        gen_random_uuid()::VARCHAR as raw_submission_id,
        'SUB-' || substr(md5(random()::text), 1, 8) as acord_submission_number,
        'Sample Business Inc' as business_name,
        '541511' as naics_code,
        1000000.00 as annual_revenue,
        25 as employee_count,
        5 as years_in_business,
        '123 Main St, City, ST 12345' as business_address,
        'General Liability, Property' as requested_coverage_types,
        '$1,000,000/$2,000,000' as requested_limits,
        CURRENT_TIMESTAMP as submission_date
    LIMIT 0  -- No actual data, just schema definition
),

parsed AS (
    -- AI-GENERATED field mappings from dim_submission.yml
    SELECT
        raw_submission_id::VARCHAR(50) as submission_id,
        acord_submission_number::VARCHAR(50) as acord_submission_number,
        business_name::VARCHAR(200) as business_name,
        naics_code::VARCHAR(10) as naics_code,
        annual_revenue::DECIMAL(15,2) as annual_revenue,
        employee_count::INTEGER as employee_count,
        years_in_business::INTEGER as years_in_business,
        business_address::VARCHAR(500) as business_address,
        requested_coverage_types::VARCHAR(200) as requested_coverage_types,
        requested_limits::VARCHAR(200) as requested_limits,
        submission_date::TIMESTAMP as submission_date,
        CURRENT_TIMESTAMP as created_at
    FROM source
)

SELECT * FROM parsed
