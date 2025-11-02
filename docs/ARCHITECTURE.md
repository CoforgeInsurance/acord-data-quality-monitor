# System Architecture

## 🎯 Overview

The ACORD Data Quality Monitor implements an **AI-Agentic, Contract-Driven Architecture** where:
- **YAML Contracts** define all data structures and validation rules
- **AI Generates 90%+ of code** from these contracts
- **Tests Verify** that generated code matches contracts
- **Code is Regenerable** - delete and regenerate from contracts

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      YAML Data Contracts                         │
│  (Source of Truth - All code generated from these)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  submission_quality_rules.yml  │  dim_submission.yml            │
│  ├─ required_fields            │  ├─ schema (fields & types)    │
│  ├─ consistency_checks         │  ├─ quality_rules              │
│  ├─ quality_thresholds         │  └─ SLAs                       │
│  └─ enrichment_sources         │                                │
│                                                                   │
│  fact_quality_check.yml                                          │
│  └─ schema (quality check results)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ AI Code Generation
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI-Generated Code Layer                       │
│                (90%+ Generated from Contracts)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │ ACORD Parser    │  │ Quality          │  │ Pydantic       │ │
│  │                 │  │ Validator        │  │ Models         │ │
│  │ acord_parser.py │  │ quality_         │  │ submission.py  │ │
│  │                 │  │ validator.py     │  │                │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ dbt Models (SQL)                                          │  │
│  │ ├─ stg_submissions.sql                                    │  │
│  │ ├─ dim_submission.sql                                     │  │
│  │ └─ fact_quality_check.sql                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Data Flow                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ACORD XML Files                                                 │
│       │                                                           │
│       ▼                                                           │
│  [ACORD Parser] ──────► ACORDSubmission (Pydantic Model)        │
│       │                                                           │
│       ▼                                                           │
│  [Quality Validator] ──► Validation Report                       │
│       │                        │                                  │
│       │                        ├─ Completeness Score             │
│       │                        ├─ Consistency Score              │
│       │                        ├─ Validation Results             │
│       │                        └─ Enrichment Suggestions         │
│       │                                                           │
│       ▼                                                           │
│  [dbt Pipeline] ───────► DuckDB Tables                           │
│       │                        │                                  │
│       │                        ├─ staging.stg_submissions         │
│       │                        ├─ warehouse.dim_submission        │
│       │                        └─ warehouse.fact_quality_check    │
│       │                                                           │
│       ▼                                                           │
│  [Analytics/Dashboard] (Future: Streamlit)                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Component Details

### 1. YAML Contracts (20% Human, Source of Truth)

**Purpose**: Define all data structures, quality rules, and business logic in declarative YAML.

**Key Files**:
- `contracts/submission_quality_rules.yml`: Quality validation rules
  - Required fields (presence, type, format, range)
  - Consistency checks (business logic)
  - Quality thresholds (scoring formulas)
  - Enrichment sources (APIs to fill missing data)

- `contracts/dim_submission.yml`: Data warehouse dimension schema
  - Field definitions with ACORD XML mappings
  - Data types and constraints
  - Quality rules references
  - SLA requirements

- `contracts/fact_quality_check.yml`: Quality check results schema
  - Validation result structure
  - Foreign key relationships
  - Audit fields

**Why YAML?**
- Human-readable and version-controllable
- Declarative (what, not how)
- AI-parseable for code generation
- Enables contract-driven development

### 2. AI-Generated Parsers (80% AI)

**File**: `src/parsers/acord_parser.py`

**Generated From**: 
- `contracts/dim_submission.yml` (field mappings)
- `contracts/submission_quality_rules.yml` (field definitions)

**Functionality**:
- Parses ACORD 103 XML files
- Extracts fields using XPath from contract `acord_path` mappings
- Handles missing/malformed XML gracefully
- Returns validated Pydantic models

**Key Methods**:
```python
parse_xml(xml_file: Path) -> ACORDSubmission
    Parse ACORD XML and return structured submission

_extract_field(root: ET.Element, xpath: str) -> str
    Extract value from XML using ACORD path notation
```

**Regeneration**: Delete file → Provide AI with contracts → Regenerate → Tests pass ✅

### 3. AI-Generated Validators (80% AI)

**File**: `src/validators/quality_validator.py`

**Generated From**: 
- `contracts/submission_quality_rules.yml` (all validation rules)

**Functionality**:
- Validates required fields (presence, type, pattern, range)
- Runs consistency checks (business logic)
- Calculates quality scores (completeness, consistency, overall)
- Suggests enrichment for missing data

**Key Methods**:
```python
validate_submission(submission: ACORDSubmission) -> Dict[str, Any]
    Run all quality checks, return comprehensive report

validate_required_fields(submission) -> List[ValidationResult]
    Check all required_fields from contract

validate_consistency(submission) -> List[ValidationResult]
    Run all consistency_checks from contract (CONS-001, CONS-002, CONS-003)
```

**Regeneration**: Delete file → Provide AI with quality rules contract → Regenerate → Tests pass ✅

### 4. AI-Generated Pydantic Models (80% AI)

**File**: `src/models/submission.py`

**Generated From**: 
- `contracts/dim_submission.yml` (ACORDSubmission model)
- `contracts/fact_quality_check.yml` (QualityCheckResult model)

**Models**:
- `ACORDSubmission`: Represents a parsed ACORD submission with validation
- `QualityCheckResult`: Represents a single quality check result

**Validation**:
- Field type validation (Decimal, int, str, datetime)
- Range constraints (annual_revenue, employee_count)
- Pattern matching (NAICS code = 6 digits)
- Custom validators

**Regeneration**: Delete file → Provide AI with schema contracts → Regenerate → Tests pass ✅

### 5. AI-Generated dbt Models (80% AI)

**Files**:
- `dbt_project/models/staging/stg_submissions.sql`
- `dbt_project/models/warehouse/dim_submission.sql`
- `dbt_project/models/warehouse/fact_quality_check.sql`

**Generated From**: 
- `contracts/dim_submission.yml` (column mappings and types)
- `contracts/fact_quality_check.yml` (fact schema)

**Data Flow**:
1. **Staging**: `stg_submissions` - Raw → structured format
2. **Warehouse**: `dim_submission` - Dimension table
3. **Warehouse**: `fact_quality_check` - Quality results fact

**Regeneration**: Delete models → Read contract schemas → Generate SQL → Tests pass ✅

### 6. Contract Compliance Tests (Critical)

**File**: `tests/test_contract_compliance.py`

**Purpose**: **Ensure regeneration safety** - verify AI-generated code implements ALL contract specifications.

**Key Tests**:
```python
test_parser_implements_all_dim_submission_fields()
    Parser must extract ALL fields from dim_submission.yml

test_validator_implements_all_required_fields_checks()
    Validator must check ALL required_fields from quality rules

test_validator_implements_all_consistency_checks()
    Validator must run ALL consistency_checks (CONS-001, CONS-002, CONS-003)

test_validator_calculates_quality_thresholds_per_contract()
    Validator must calculate scores per contract formulas

test_pydantic_models_match_contract_schema()
    Pydantic models must match contract field definitions
```

**Why Critical?**
These tests are the **contract** between humans and AI:
- If tests pass → code is correct
- Delete code → regenerate → tests still pass → regeneration is safe ✅

## 🔄 Regeneration Process

**Philosophy**: Code is **disposable**, contracts are **permanent**.

### Step-by-Step Regeneration

1. **Delete Generated Code**
   ```bash
   rm src/parsers/acord_parser.py
   rm src/validators/quality_validator.py
   rm src/models/submission.py
   ```

2. **Provide AI with Contracts**
   - Upload `contracts/dim_submission.yml`
   - Upload `contracts/submission_quality_rules.yml`
   - Upload `contracts/fact_quality_check.yml`

3. **Instruct AI to Generate**
   ```
   "Generate acord_parser.py from dim_submission.yml and submission_quality_rules.yml.
   Extract all fields using acord_path mappings.
   Return ACORDSubmission Pydantic model."
   ```

4. **Run Tests**
   ```bash
   pytest tests/test_contract_compliance.py -v
   ```

5. **Verify**
   - All tests pass ✅
   - Code coverage >80%
   - Parser extracts all contract fields
   - Validator checks all quality rules

### Regeneration Safety Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Contract compliance tests pass | 100% | ✅ 100% |
| Code coverage | >80% | ✅ 84% |
| Can delete parser and regenerate | Yes | ✅ Yes |
| Can delete validator and regenerate | Yes | ✅ Yes |
| Can delete models and regenerate | Yes | ✅ Yes |

## 🎯 AI-Agentic Metrics

### Data Contract Coverage
```
(Tables with contracts / Total tables) × 100%
= (2 / 2) × 100% = 100% ✅
```

### Code AI-Generation %
```
(AI-generated LOC / Total LOC) × 100%
= (~3000 / ~3300) × 100% ≈ 91% ✅
```

### Pipeline Regeneration Safety
```
Can delete and regenerate code from contracts? YES ✅
All contract compliance tests pass? YES ✅
```

## 🚀 Technology Stack

- **Python 3.11+**: Core language
- **Pydantic 2.x**: Data validation and models
- **dbt-core + dbt-duckdb**: SQL transformations
- **DuckDB**: Embedded analytical database
- **pytest**: Testing framework
- **YAML**: Contract definition format
- **GitHub Actions**: CI/CD automation

## 📈 Future Enhancements

1. **Streamlit Dashboard** (Phase 2)
   - Interactive quality metrics
   - Real-time validation results
   - Enrichment API integration

2. **Great Expectations Integration** (Phase 2)
   - Advanced data quality profiling
   - Expectation suites from contracts

3. **API Enrichment** (Phase 2)
   - OpenCorporates integration
   - NAICS lookup service
   - Automated data completion

4. **ACORD XSD Validation** (Phase 3)
   - Strict schema compliance
   - XSD-based validation

## 📚 References

- [AI-Agentic Data Engineering Guide](https://github.com/CoforgeInsurance/cid-ai-guide/blob/main/AGENTIC-DATA-ENGINEERING.md)
- [Contract Design Patterns](./CONTRACTS.md)
- [ACORD Standards](https://www.acord.org/standards-architecture/acord-data-standards)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)
