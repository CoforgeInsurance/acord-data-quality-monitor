# ACORD Data Quality Monitor

> **AI-Agentic Data Quality Monitor for ACORD Insurance Submissions**  
> Automated validation, enrichment, and compliance checking with 90% AI-generated code from YAML contracts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![ACORD Standards](https://img.shields.io/badge/ACORD-103-green.svg)](https://www.acord.org/standards-architecture/acord-forms/ACORD-103)

## 🎯 Overview

This project demonstrates **contract-driven development** for insurance data engineering, where:
- **Human Role (20%)**: Define YAML contracts (data schemas, quality rules, business logic)
- **AI Role (80%)**: Generate parsers, validators, tests, pipelines, and dashboards from contracts

### Key Features

- ✅ **ACORD 103 Parsing**: Automated ingestion of commercial insurance submissions
- ✅ **Quality Validation**: 10+ insurance-specific data quality rules
- ✅ **Auto-Enrichment**: Suggests missing data from free APIs (OpenCorporates, NAICS)
- ✅ **Contract-Driven**: 90%+ code AI-generated from YAML specifications
- ✅ **Regeneration Safety**: Delete code, regenerate from contracts, tests still pass

## 🏗️ Architecture

```
ACORD XML → Parser → Validator → dbt Pipeline → DuckDB → Dashboard
              ↑          ↑            ↑
         AI-Generated from YAML Contracts
```

**Core Principle**: If it's not in the contract, it can't be regenerated.

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/CoforgeInsurance/acord-data-quality-monitor.git
cd acord-data-quality-monitor

# Install dependencies
pip install -r requirements.txt

# Generate sample ACORD data
python scripts/generate_sample_data.py

# Run quality validation
python -m src.main --validate data/sample_acord/complete_submission_001.xml

# Run tests
pytest tests/ -v
```

## 📋 Project Status

**Phase 1: Foundation** (In Progress - See [Issue #1](https://github.com/CoforgeInsurance/acord-data-quality-monitor/issues/1))

- [ ] Project structure
- [ ] YAML data contracts
- [ ] Sample ACORD 103 XML files
- [ ] AI-generated ACORD parser
- [ ] AI-generated quality validators
- [ ] dbt pipeline
- [ ] Test suite
- [ ] CI/CD workflows
- [ ] Documentation

## 🎓 AI-Agentic Development Principles

### 1. Contracts First
All code generation starts from YAML contracts:

```yaml
# contracts/submission_quality_rules.yml
required_fields:
  basic_info:
    - field: business_name
      acord_path: "CommercialSubmission/Applicant/BusinessInfo/BusinessName"
      nullable: false
      min_length: 3
```

### 2. AI-Generated Code
From contracts, AI generates:
- `src/parsers/acord_parser.py` - ACORD XML parser
- `src/validators/quality_validator.py` - Quality validators
- `dbt_project/models/` - SQL transformations

### 3. Test Contract Compliance
Tests verify generated code matches contracts:

```python
def test_parser_implements_all_contract_fields():
    """Parser must extract ALL fields defined in dim_submission.yml"""
    # Ensures regeneration safety
```

### 4. Regeneration Safety
**Key Metric**: Can you delete code and regenerate it from contracts?
- Target: 90%+ of codebase regenerable

## 📊 Metrics

Track these AI-agentic metrics:

| Metric | Target | Current |
|--------|--------|---------|
| Data Contract Coverage | 100% | TBD |
| Quality Test Coverage | 100% | TBD |
| Code AI-Generation % | 90%+ | TBD |
| Pipeline Regeneration Safety | >90% | TBD |
| ACORD Compliance | 100% | TBD |

## 🛠️ Tech Stack

- **Python 3.11+**: Core language
- **dbt-core**: SQL transformations
- **DuckDB**: Embedded database
- **Great Expectations**: Data quality framework
- **Pydantic**: Data validation
- **Streamlit**: Dashboard (coming soon)
- **GitHub Actions**: CI/CD

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Contracts Guide](docs/CONTRACTS.md) - How to write YAML contracts
- [Metrics](docs/METRICS.md) - AI-agentic metrics tracking
- [AI-Agentic Data Engineering](https://github.com/CoforgeInsurance/cid-ai-guide/blob/main/AGENTIC-DATA-ENGINEERING.md) - Philosophy and principles

## 🤝 Contributing

This project follows **AI-agentic development principles**:

1. **Update contracts first** (YAML files in `contracts/`)
2. **Regenerate code** using AI assistants (GitHub Copilot, ChatGPT, Claude)
3. **Run contract compliance tests** (`pytest tests/test_contract_compliance.py`)
4. **Verify regeneration** (delete generated code, regenerate, tests pass)

## 📖 Related Resources

- [ACORD Standards](https://www.acord.org/standards-architecture/acord-data-standards)
- [ACORD 103 Documentation](https://www.acord.org/standards-architecture/acord-forms/ACORD-103)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)
- [Great Expectations](https://docs.greatexpectations.io/)

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙋 Questions?

- **Issues**: [GitHub Issues](https://github.com/CoforgeInsurance/acord-data-quality-monitor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CoforgeInsurance/acord-data-quality-monitor/discussions)
- **Reference Project**: [CI/CD AI Guide](https://github.com/CoforgeInsurance/cid-ai-guide)

---

**Built with AI-Agentic Development Principles**  
*Where humans define contracts (YAML) and AI generates code (90%+)*
