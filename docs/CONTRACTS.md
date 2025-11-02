# Contract Design Patterns

## 🎯 Contract-Driven Development Philosophy

**Core Principle**: Define **what** you want in YAML contracts, let AI generate **how** it's implemented.

## Why YAML Contracts?

### Traditional Approach (Code-First)
```python
# Manual coding - prone to inconsistencies
class Submission:
    def __init__(self):
        self.business_name = None  # What constraints?
        self.revenue = None        # What range is valid?
        self.employees = None      # How does this relate to revenue?
```

**Problems**:
- ❌ No single source of truth
- ❌ Business rules scattered across codebase
- ❌ Hard to maintain consistency
- ❌ Manual coding of repetitive validation logic

### Contract-Driven Approach (YAML-First)

```yaml
# contracts/submission_quality_rules.yml
required_fields:
  basic_info:
    - field: business_name
      nullable: false
      min_length: 3
      max_length: 200
    
    - field: annual_revenue
      type: decimal
      range: [10000, 1000000000]
    
    - field: employee_count
      type: integer
      range: [1, 100000]

consistency_checks:
  - rule_id: "CONS-001"
    name: "Revenue vs. Employee Consistency"
    logic: |
      IF employee_count < 5 THEN annual_revenue < 1000000
```

**Benefits**:
- ✅ Single source of truth
- ✅ Business rules in declarative format
- ✅ AI generates validation code
- ✅ Tests verify contract compliance
- ✅ Easy to evolve and version

## Contract Types

### 1. Quality Rules Contract

**Purpose**: Define data quality validation rules for ACORD submissions.

**Template**:
```yaml
contract_version: "1.0"
contract_type: quality_rules
standard: ACORD_103
description: "Data quality validation rules"
owner: data-engineering-team

required_fields:
  category_name:
    - field: field_name
      acord_path: "XPath/To/Field"
      nullable: false
      type: string|integer|decimal|date
      pattern: "regex_pattern"    # Optional
      range: [min, max]            # Optional
      min_length: N                # Optional
      max_length: N                # Optional
      description: "Field description"

consistency_checks:
  - rule_id: "CONS-XXX"
    name: "Human-readable rule name"
    description: "What this rule checks"
    severity: error|warning|info
    logic: |
      Business logic in plain English
      IF condition THEN expectation
    error_message: "Error message with ${field} placeholders"

quality_thresholds:
  - metric: metric_name
    description: "What this metric measures"
    target: 0.95        # Target value (0.0 to 1.0)
    minimum: 0.80       # Minimum acceptable
    calculation: "Formula for calculation"

enrichment_sources:
  - source: api_name
    api_endpoint: "https://..."
    fields_provided: [field1, field2]
    cost: free|paid
    rate_limit: N_per_month
    confidence_threshold: 0.8
```

**Example**: `contracts/submission_quality_rules.yml`

**AI Generates From This**:
- `src/validators/quality_validator.py` - Implements all validation rules
- Tests for each quality rule

### 2. Data Warehouse Dimension Contract

**Purpose**: Define schema for a dimension table.

**Template**:
```yaml
contract_version: "1.0"
contract_type: data_warehouse_dimension
table: schema.table_name
standard: ACORD_103
description: "Dimension description"
owner: data-engineering-team

schema:
  - name: field_name
    type: VARCHAR(N)|INTEGER|DECIMAL(M,N)|TIMESTAMP|BOOLEAN
    nullable: true|false
    primary_key: true|false      # Optional
    foreign_key: parent.table.field  # Optional
    source: "ACORD/XPath" OR "Function()"
    quality_rule: contract_file.section.field  # Optional
    description: "Field description"

quality_rules:
  - no_duplicates: [field1, field2]
  - no_nulls: [field1, field2]
  - referential_integrity:
      parent: parent_table
      key: foreign_key_field

sla:
  freshness: N_hours|N_minutes
  completeness: 0.95    # % of records complete
  reliability: 0.999    # Uptime guarantee
```

**Example**: `contracts/dim_submission.yml`

**AI Generates From This**:
- `src/models/submission.py` - Pydantic model with all fields
- `dbt_project/models/warehouse/dim_submission.sql` - dbt transformation
- Field-level tests in dbt schema.yml

### 3. Data Warehouse Fact Contract

**Purpose**: Define schema for a fact table.

**Template**:
```yaml
contract_version: "1.0"
contract_type: data_warehouse_fact
table: schema.table_name
description: "Fact table description"
owner: data-engineering-team

schema:
  - name: field_name
    type: VARCHAR(N)|INTEGER|DECIMAL(M,N)|TIMESTAMP|BOOLEAN
    nullable: true|false
    primary_key: true|false
    foreign_key: dimension.table.field  # Links to dimension
    source: "Source description"
    description: "Field description"

quality_rules:
  - no_duplicates: [field1]
  - no_nulls: [field1, field2]
  - referential_integrity:
      parent: dimension_table
      key: foreign_key_field

sla:
  freshness: N_hours
  completeness: 0.99
  reliability: 0.999
```

**Example**: `contracts/fact_quality_check.yml`

**AI Generates From This**:
- `src/models/submission.py` - Pydantic model for fact records
- `dbt_project/models/warehouse/fact_quality_check.sql` - dbt transformation
- Referential integrity tests

## Contract Design Best Practices

### 1. Start with Business Requirements

```yaml
# ❌ BAD: Technical-first
required_fields:
  - field: col1
    type: string

# ✅ GOOD: Business-first
required_fields:
  basic_info:
    - field: business_name
      description: "Legal business name for insurance submission"
      nullable: false
      min_length: 3
      max_length: 200
```

### 2. Be Explicit About Constraints

```yaml
# ❌ BAD: Implicit constraints
- field: annual_revenue
  type: decimal

# ✅ GOOD: Explicit constraints
- field: annual_revenue
  type: decimal
  range: [10000, 1000000000]  # $10K to $1B
  description: "Annual revenue in USD, must be realistic for business size"
```

### 3. Link to Business Logic

```yaml
# ✅ GOOD: Reference quality rules in schema
schema:
  - name: business_name
    type: VARCHAR(200)
    nullable: false
    source: "ACORD/Applicant/BusinessInfo/BusinessName"
    quality_rule: submission_quality_rules.required_fields.basic_info.business_name
    description: "Legal business name"
```

### 4. Document Consistency Rules

```yaml
# ✅ GOOD: Clear business logic
consistency_checks:
  - rule_id: "CONS-001"
    name: "Revenue vs. Employee Consistency"
    description: "Revenue should be proportional to employee count"
    severity: warning
    logic: |
      Small companies (< 5 employees) should have < $1M revenue
      Medium companies (5-50 employees) should have $500K-$50M revenue
      Large companies (> 100 employees) should have > $5M revenue
    error_message: "Revenue of ${annual_revenue} inconsistent with ${employee_count} employees"
```

### 5. Version Your Contracts

```yaml
contract_version: "1.0"

# When making breaking changes:
# 1. Increment to "2.0"
# 2. Document migration path in contracts/CHANGELOG.md
# 3. Update all related contracts to same version
# 4. Regenerate all code from new contracts
# 5. Run full test suite
```

## Contract Evolution

### Adding a New Field

**Step 1**: Update quality rules contract
```yaml
# contracts/submission_quality_rules.yml
required_fields:
  basic_info:
    - field: ein_number
      acord_path: "CommercialSubmission/Applicant/BusinessInfo/EIN"
      nullable: false
      pattern: '^\d{2}-\d{7}$'
      description: "Employer Identification Number (XX-XXXXXXX)"
```

**Step 2**: Update dimension contract
```yaml
# contracts/dim_submission.yml
schema:
  - name: ein_number
    type: VARCHAR(10)
    nullable: false
    source: "ACORD/Applicant/BusinessInfo/EIN"
    quality_rule: submission_quality_rules.required_fields.basic_info.ein_number
    description: "Employer Identification Number"
```

**Step 3**: Regenerate code
```bash
# AI regenerates parser with new field extraction
# AI regenerates validator with new validation rule
# AI regenerates Pydantic model with new field
# AI regenerates dbt model with new column
```

**Step 4**: Verify
```bash
pytest tests/test_contract_compliance.py -v
# ✅ Tests verify new field is extracted and validated
```

### Adding a New Consistency Check

**Step 1**: Update quality rules contract
```yaml
consistency_checks:
  - rule_id: "CONS-004"
    name: "EIN Format Validation"
    description: "EIN must be valid IRS format"
    severity: error
    logic: |
      EIN must match pattern XX-XXXXXXX where X is digit
      First two digits cannot be 00, 07-09, 17-19, 28-29, etc.
    error_message: "Invalid EIN format: ${ein_number}"
```

**Step 2**: AI regenerates validator
```python
# AI adds to src/validators/quality_validator.py
def validate_consistency(self, submission):
    # ... existing checks ...
    
    # CONS-004: EIN Format Validation
    if rule_id == 'CONS-004':
        passed = self._check_ein_validity(submission)
        # ... validation logic
```

**Step 3**: Verify
```bash
pytest tests/test_contract_compliance.py::test_validator_implements_all_consistency_checks
# ✅ Test verifies CONS-004 is implemented
```

## How AI Uses Contracts

### Parser Generation

**Input**: `dim_submission.yml` + `submission_quality_rules.yml`

**AI Prompt**:
```
Generate acord_parser.py that:
1. Reads contracts/dim_submission.yml to get field mappings
2. For each field in schema, use `source` as XPath to extract from XML
3. Returns ACORDSubmission Pydantic model
4. Handles missing fields per `nullable` constraint
```

**Output**: `src/parsers/acord_parser.py`

### Validator Generation

**Input**: `submission_quality_rules.yml`

**AI Prompt**:
```
Generate quality_validator.py that:
1. Reads contracts/submission_quality_rules.yml
2. For each required_field, validate: nullable, type, pattern, range, length
3. For each consistency_check, implement business logic as Python function
4. Calculate quality scores per quality_thresholds formulas
5. Return validation report with all results
```

**Output**: `src/validators/quality_validator.py`

### dbt Model Generation

**Input**: `dim_submission.yml`

**AI Prompt**:
```
Generate dim_submission.sql that:
1. Reads contracts/dim_submission.yml schema
2. For each field, create SQL column with appropriate type casting
3. Add dbt tests for no_nulls, unique, referential_integrity
4. Document columns in schema.yml
```

**Output**: `dbt_project/models/warehouse/dim_submission.sql`

## Contract Validation

### Automated Validation

```bash
python scripts/validate_contracts.py
```

**Checks**:
- ✅ YAML syntax is valid
- ✅ Required top-level fields present (contract_version, contract_type, description, owner)
- ✅ Contract-type-specific fields present
- ✅ All field definitions have required attributes
- ✅ References between contracts are valid
- ✅ All contracts have same version number

### CI/CD Integration

```yaml
# .github/workflows/contract-validation.yml
- name: Validate contracts
  run: python scripts/validate_contracts.py

- name: Check version consistency
  run: |
    # Verify all contracts have same version
```

## Metrics

### Contract Coverage

```
Data Contract Coverage = (Tables with contracts / Total tables) × 100%
Target: 100%
Current: 100% ✅ (2/2 tables)
```

### AI Generation Ratio

```
Code AI-Generation % = (AI-generated LOC / Total LOC) × 100%
Target: 90%+
Current: 91% ✅
```

### Regeneration Safety

```
Can delete code and regenerate from contracts? YES ✅
All contract compliance tests pass? YES ✅
Pipeline Regeneration Safety: PASS ✅
```

## Summary

**Contracts are permanent, code is disposable.**

1. **Define requirements** in YAML contracts (20% human effort)
2. **AI generates code** from contracts (80% AI effort)
3. **Tests verify** code matches contracts (automated)
4. **Delete and regenerate** anytime (proven safe)

This approach:
- ✅ Reduces manual coding by 90%+
- ✅ Ensures consistency across codebase
- ✅ Makes evolution safe and traceable
- ✅ Enables true contract-driven development
