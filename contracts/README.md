# YAML Data Contracts

This directory contains the **source of truth** for all data structures and validation rules in the ACORD Data Quality Monitor.

## 🎯 Philosophy

**Contracts First**: All code generation starts from these YAML contracts. If it's not in the contract, it can't be regenerated.

## 📋 Contracts

### Quality Rules Contract
**File**: `submission_quality_rules.yml`

Defines data quality validation rules for ACORD 103 submissions:
- **Required Fields**: Must be present and valid
- **Consistency Checks**: Business logic rules (e.g., revenue vs. employees)
- **Quality Thresholds**: Completeness, consistency, overall quality scores
- **Enrichment Sources**: APIs to fetch missing data
- **ACORD Compliance**: Standard version and validation settings

### Data Warehouse Dimension Contract
**File**: `dim_submission.yml`

Schema for submission dimension table:
- Maps ACORD XML paths to database columns
- Links to quality rules
- Defines data types, constraints, SLAs
- One row per insurance submission

### Data Warehouse Fact Contract
**File**: `fact_quality_check.yml`

Schema for quality check results:
- One row per validation rule per submission
- Tracks pass/fail status, error messages
- Links to submission dimension
- Enables quality metric reporting

## 🔄 How AI Uses These Contracts

### Parser Generation
From `submission_quality_rules.yml` and `dim_submission.yml`:
```python
# AI generates src/parsers/acord_parser.py
class ACORDParser:
    def parse_xml(self, xml_file):
        # Extracts fields using acord_path from contracts
        business_name = extract_field(xml, "CommercialSubmission/Applicant/BusinessInfo/BusinessName")
        # ... more fields from contract
```

### Validator Generation
From `submission_quality_rules.yml`:
```python
# AI generates src/validators/quality_validator.py
class SubmissionQualityValidator:
    def validate_required_fields(self, submission):
        # Checks all required_fields from contract
        # Validates patterns, ranges, types
    
    def validate_consistency(self, submission):
        # Runs all consistency_checks from contract
        # CONS-001, CONS-002, CONS-003, etc.
```

### dbt Model Generation
From `dim_submission.yml`:
```sql
-- AI generates dbt_project/models/warehouse/dim_submission.sql
SELECT
    submission_id,
    business_name,
    naics_code,
    annual_revenue::DECIMAL(15,2) as annual_revenue,
    -- ... more fields from contract schema
FROM staging.stg_submissions
```

## ✅ Contract Validation

Run validation to ensure contracts are well-formed:

```bash
python scripts/validate_contracts.py
```

Checks:
- YAML syntax is valid
- Required fields are present
- Data types are supported
- References between contracts are valid

## 📝 Adding New Quality Rules

1. **Edit contract**: Add rule to `submission_quality_rules.yml`
2. **Regenerate code**: Use AI to update `quality_validator.py`
3. **Test**: Run `pytest tests/test_contract_compliance.py`
4. **Verify**: Delete validator, regenerate, tests still pass ✅

## 🔗 Contract Evolution

**Version**: `1.0`

When breaking changes are needed:
1. Increment `contract_version` to `2.0`
2. Update all AI-generated code
3. Maintain backward compatibility in dbt models
4. Document migration path

## 📚 References

- [Contract Design Patterns](../docs/CONTRACTS.md)
- [Architecture Overview](../docs/ARCHITECTURE.md)
- [AI-Agentic Development Guide](https://github.com/CoforgeInsurance/cid-ai-guide/blob/main/AGENTIC-DATA-ENGINEERING.md)
