# ACORD Data Quality Monitor - Project Kickoff

## ✅ Repository Created

**Repository**: https://github.com/CoforgeInsurance/acord-data-quality-monitor

**Description**: AI-Agentic Data Quality Monitor for ACORD Insurance Submissions - Automated validation, enrichment, and compliance checking with 90% AI-generated code from YAML contracts

**Topics**: insurance, acord, data-quality, ai-agentic, insurtech, pnc-specialty, dbt, great-expectations, python

---

## 🎯 Project Overview

Building a **Specialty Underwriting Data Quality Monitor** that:
- Ingests ACORD 103/125/126 submissions (XML/JSON)
- Validates data quality using contract-driven rules
- Auto-detects incomplete/inconsistent data
- Suggests enrichment from free APIs (LinkedIn, OpenCorporates, NAICS)
- Auto-populates missing fields
- **90% AI-generated code** from YAML contracts

---

## 📅 3-Week Plan

### Week 1: Foundation & Data Contracts

#### Day 1-2: Project Structure & Sample Data
- [ ] Clone repository locally
- [ ] Set up Python project structure
- [ ] Generate synthetic ACORD 103 XML samples (10-20 submissions)
  - Mix of complete, incomplete, and anomalous data
  - Include commercial auto, GL, property submissions
- [ ] Create initial `contracts/` directory

#### Day 3-4: Define Data Contracts
- [ ] Create `contracts/submission_quality_rules.yml`
  - Required fields (business name, NAICS, revenue, employees)
  - Field validation rules (ranges, patterns, types)
  - Consistency checks (revenue vs employees, payroll vs revenue)
  - ACORD 103 schema mappings
- [ ] Create `contracts/dim_submission.yml`
  - Data warehouse dimension contract
  - Field definitions with ACORD mappings
- [ ] Create `contracts/fact_quality_check.yml`
  - Quality check results fact table

#### Day 5-7: Tech Stack Setup
- [ ] Set up Python environment (requirements.txt)
  - xmltodict (ACORD XML parsing)
  - pydantic (data validation)
  - great-expectations (data quality)
  - duckdb (embedded database)
  - streamlit (dashboard)
- [ ] Set up dbt project
  - dbt-duckdb adapter
  - Initial profiles.yml
- [ ] GitHub Actions workflow (basic CI/CD)

---

### Week 2: AI Generation & Core Pipeline

#### Day 8-9: ACORD Parser (AI-Generated)
- [ ] Prompt AI to generate ACORD 103 parser from contract
  - Input: YAML contract with ACORD mappings
  - Output: Python parser class
- [ ] Generate Pydantic models from schema contract
- [ ] Test parser with sample XML files
- [ ] Validate AI-generated code

#### Day 10-11: Quality Validators (AI-Generated)
- [ ] Prompt AI to generate Great Expectations suite from quality rules contract
  - Input: `submission_quality_rules.yml`
  - Output: `great_expectations/expectations/submission_suite.json`
- [ ] Generate custom validators for insurance-specific rules
  - Revenue vs. employees consistency
  - Payroll vs. revenue ratio
  - NAICS code validation
- [ ] Test validators against sample data

#### Day 12-13: dbt Models (AI-Generated)
- [ ] Prompt AI to generate dbt models from data contracts
  - `models/staging/stg_submissions.sql`
  - `models/warehouse/dim_submission.sql`
  - `models/warehouse/fact_quality_check.sql`
- [ ] Generate dbt tests from quality rules
  - Schema tests (not_null, unique)
  - Custom SQL tests (business rules)
- [ ] Run dbt pipeline on sample data

#### Day 14: Enrichment Integrations (AI-Generated)
- [ ] Prompt AI to generate API integration code
  - OpenCorporates API (business verification)
  - NAICS lookup service (industry classification)
  - LinkedIn Company API (employee count, revenue estimates)
- [ ] Create enrichment orchestration logic
- [ ] Test enrichment with real APIs (free tier)

---

### Week 3: Dashboard, Testing & Demo Prep

#### Day 15-16: Streamlit Dashboard (AI-Generated)
- [ ] Prompt AI to generate Streamlit dashboard from requirements
  - Upload ACORD submission interface
  - Quality check results display
  - Enrichment suggestions panel
  - Completeness score visualization
  - Field-by-field validation status
- [ ] Add interactive elements
  - "Apply Enrichment" button
  - Export quality report
- [ ] Style and polish UI

#### Day 17: Pipeline Regeneration Testing
- [ ] Delete generated code (parser, validators, dbt models)
- [ ] Re-prompt AI with same contracts
- [ ] Compare original vs. regenerated code
- [ ] Measure regeneration accuracy (target: 90%+)
- [ ] Document regeneration process

#### Day 18-19: Documentation & Metrics
- [ ] Create comprehensive README.md
  - Project philosophy (AI-agentic approach)
  - Architecture diagram
  - Quick start guide
  - Data contract examples
- [ ] Create METRICS.md
  - Data Contract Coverage: 100%
  - Quality Test Coverage: 100%
  - Pipeline Regeneration Safety: 90%+
  - ACORD Compliance: 100%
  - Auto-Enrichment Success Rate
- [ ] Create DEMO.md (demo script)
- [ ] Add badges (build status, coverage, etc.)

#### Day 20-21: Demo Recording & Polish
- [ ] Record demo video (5-7 minutes)
  - Show messy ACORD submission
  - AI validates and flags issues
  - AI suggests enrichment
  - One-click auto-populate
  - Contract change → AI regenerates code
- [ ] Polish GitHub repo
  - Clean commit history
  - Add screenshots
  - Create GitHub Pages site (optional)
- [ ] Prepare presentation slides

---

## 🛠️ Tech Stack (All Free Tier)

### Data Storage
- **DuckDB**: Embedded database (no server needed)
- **File System**: ACORD XML/JSON files

### Data Transformation
- **dbt-core**: SQL transformations
- **dbt-duckdb**: DuckDB adapter

### Data Quality
- **Great Expectations**: Quality validation framework
- **Pydantic**: Python data validation

### APIs (Free Tier)
- **OpenCorporates API**: Business verification (500 calls/month free)
- **NAICS Association**: Industry classification lookup (free)
- **LinkedIn Company API**: Limited free tier or public data scraping

### Dashboard
- **Streamlit**: Python-based web app
- **Streamlit Community Cloud**: Free hosting

### Orchestration
- **GitHub Actions**: CI/CD pipeline (free for public repos)
- **Python scripts**: Local orchestration

### AI Code Generation
- **GitHub Copilot**: Code generation assistant
- **ChatGPT/Claude**: Contract-to-code generation

---

## 📁 Proposed Repository Structure

```
acord-data-quality-monitor/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Build, test, quality checks
│       └── regeneration-test.yml     # Test AI regeneration
├── contracts/
│   ├── submission_quality_rules.yml  # Quality validation rules
│   ├── dim_submission.yml            # Submission dimension contract
│   ├── fact_quality_check.yml        # Quality check fact contract
│   └── enrichment_sources.yml        # API integration specs
├── data/
│   ├── sample_acord/                 # Sample ACORD XML files
│   │   ├── complete_submission.xml
│   │   ├── incomplete_submission.xml
│   │   └── anomalous_submission.xml
│   └── seeds/                        # Reference data (NAICS codes, etc.)
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_submissions.sql
│   │   └── warehouse/
│   │       ├── dim_submission.sql
│   │       └── fact_quality_check.sql
│   ├── tests/                        # Custom dbt tests
│   └── dbt_project.yml
├── great_expectations/
│   ├── expectations/
│   │   └── submission_suite.json     # AI-generated from contract
│   └── checkpoints/
│       └── submission_checkpoint.yml
├── src/
│   ├── parsers/
│   │   └── acord_parser.py          # AI-generated ACORD XML parser
│   ├── validators/
│   │   └── quality_validator.py     # AI-generated validators
│   ├── enrichment/
│   │   ├── opencorporates.py        # AI-generated API integration
│   │   ├── naics_lookup.py
│   │   └── linkedin_scraper.py
│   └── models/
│       └── submission.py            # Pydantic models
├── dashboard/
│   └── app.py                       # Streamlit dashboard (AI-generated)
├── tests/
│   ├── test_parser.py
│   ├── test_validators.py
│   └── test_regeneration.py         # Regeneration safety tests
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO.md                      # Demo script
│   └── METRICS.md                   # AI-agentic metrics
├── scripts/
│   ├── generate_sample_data.py      # Create ACORD samples
│   └── run_pipeline.py              # Orchestration script
├── .gitignore
├── README.md
├── requirements.txt
└── pyproject.toml
```

---

## 🎬 Demo Script Preview

### Act 1: The Problem (30 seconds)
- Show messy ACORD 103 submission XML
- Missing: annual_revenue, employee_count
- Anomaly: Business claims 2 employees, $50M revenue
- "Manual review takes 15 minutes per submission"

### Act 2: AI Validation (1 minute)
- Upload submission to Streamlit app
- AI runs quality checks from YAML contract
- Dashboard shows:
  - ❌ Revenue: Missing (required)
  - ❌ Employee count: Missing (required)
  - ⚠️ Consistency check: Failed (missing data)
  - Overall completeness: 60%

### Act 3: AI Enrichment (1 minute)
- AI suggests enrichment sources:
  - OpenCorporates: Found business entity
  - LinkedIn: 250 employees, $18M revenue
- Click "Apply Suggestions"
- Fields auto-populated
- New completeness: 95%

### Act 4: Contract Changes (2 minutes)
- Open `contracts/submission_quality_rules.yml`
- Add new rule: `prior_claims_required: true`
- Show AI regenerating validator code
- Run tests → all pass
- "No manual coding required"

### Act 5: The Philosophy (1 minute)
- Show metrics:
  - 90% of code AI-generated from contracts
  - 100% data contract coverage
  - 100% quality test coverage
  - Pipeline regenerable in < 5 minutes
- "This is AI-Agentic Development"

---

## 🎯 Success Metrics

### Technical Metrics
- **Data Contract Coverage**: 100% (all entities have YAML contracts)
- **Quality Test Coverage**: 100% (every contract rule = automated test)
- **ACORD Compliance**: 100% (validates against ACORD 103 XSD)
- **Pipeline Regeneration Safety**: 90%+ (AI can rebuild from contracts)
- **Auto-Enrichment Success**: 75%+ (fields successfully auto-populated)
- **Code AI-Generation %**: 90%+ (lines of AI-generated code / total lines)

### Business Metrics
- **Quality Review Time**: Target 70% reduction (15 min → 5 min)
- **Submission Completeness**: Target 85%+ (currently ~60%)
- **False Positive Rate**: < 5% (valid submissions flagged incorrectly)
- **Enrichment Accuracy**: > 90% (auto-populated fields are correct)

---

## 🚀 Next Immediate Actions

1. **Clone the repository locally**
   ```bash
   git clone https://github.com/CoforgeInsurance/acord-data-quality-monitor.git
   cd acord-data-quality-monitor
   ```

2. **Create initial project structure**
   - Set up directory structure
   - Create initial README.md
   - Add .gitignore (Python, dbt, data files)

3. **Generate sample ACORD data**
   - Use AI to create 10-15 ACORD 103 XML samples
   - Mix of complete, incomplete, anomalous submissions

4. **Define first data contract**
   - Start with `contracts/submission_quality_rules.yml`
   - Document required fields, validation rules, ACORD mappings

**Ready to proceed?** Let me know and we can start with creating the initial project structure and first contract! 🎯