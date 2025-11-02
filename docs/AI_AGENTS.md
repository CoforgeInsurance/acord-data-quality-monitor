# AI-Powered Real-Time Data Quality Monitoring

## 🎯 Overview

This document describes the AI-powered capabilities that enable real-time data quality monitoring, intelligent enrichment, and anomaly detection for ACORD insurance submissions.

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Real-Time Submissions                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           Submission Stream Processor                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Stage 1: Quality Assessment (Quality Agent)              │  │
│  │  ↓                                                         │  │
│  │  Stage 2: Data Enrichment (Enrichment Agent)              │  │
│  │  ↓                                                         │  │
│  │  Stage 3: Anomaly Detection (Anomaly Agent)               │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Processing Results → Dashboard + DuckDB + Alerts               │
└─────────────────────────────────────────────────────────────────┘
```

## 🤖 AI Agents

### 1. Quality Agent

**Purpose**: Intelligently assess submission quality using rule-based and ML approaches.

**Location**: `src/agents/quality_agent.py`

**Capabilities**:
- Field completeness scoring
- Consistency validation
- Business rule checking
- Confidence estimation

**Usage**:
```python
from src.agents.quality_agent import QualityAgent

# Initialize agent
quality_agent = QualityAgent()

# Assess submission
result = await quality_agent.assess_quality(submission)

# Access results
print(f"Quality Score: {result.quality_score}")
print(f"Reasoning: {result.agent_reasoning}")
print(f"Confidence: {result.confidence}")
```

**Output**:
```python
QualityAssessmentResult(
    submission_id="SUB-001",
    quality_score=0.87,
    completeness_score=0.92,
    consistency_score=0.80,
    agent_reasoning="Good quality submission with minor data quality issues.",
    validation_details={...},
    confidence=0.85
)
```

### 2. Enrichment Agent

**Purpose**: Automatically enrich incomplete submissions using external APIs.

**Location**: `src/agents/enrichment_agent.py`

**Capabilities**:
- Missing data detection
- External API integration
- Data confidence scoring
- Cost optimization

**Decision Logic**:
- Identifies missing critical fields
- Ranks enrichment opportunities by value/cost ratio
- Selects optimal APIs within budget ($0.10/submission)
- Validates enriched data quality

**Usage**:
```python
from src.agents.enrichment_agent import EnrichmentAgent

# Initialize agent
enrichment_agent = EnrichmentAgent()

# Attempt enrichment
enriched = await enrichment_agent.enrich_submission(submission)

# Check decision log
for decision in enrichment_agent.last_decision_log:
    print(decision)
```

**External APIs** (configured in `contracts/ai_agent_configs.yml`):
- **OpenCorporates**: Business name lookup (cost: $0.02/request)
- **NAICS Lookup**: Industry classification (cost: $0.01/request)

### 3. Anomaly Detection Agent

**Purpose**: Detect unusual patterns in submissions using machine learning.

**Location**: `src/agents/anomaly_agent.py`

**Capabilities**:
- Statistical outlier detection (Isolation Forest)
- Pattern anomaly detection
- Business rule violations
- Time-based anomaly detection

**Detection Methods**:

1. **Statistical Outliers**: Isolation Forest on numerical features
   - Annual revenue
   - Employee count
   - Years in business

2. **Pattern Anomalies**:
   - Unusual submission times (weekends, after hours)
   - Industry/size/revenue mismatches

3. **Business Logic**:
   - Unusually low quality scores
   - Field combinations that don't make sense

**Usage**:
```python
from src.agents.anomaly_agent import AnomalyDetectionAgent

# Initialize agent
anomaly_agent = AnomalyDetectionAgent()

# Detect anomalies
anomalies = await anomaly_agent.detect_anomalies(submission, quality_result)

# Review anomalies
for anomaly in anomalies:
    print(f"{anomaly.anomaly_type}: {anomaly.explanation}")
    print(f"Severity: {anomaly.severity}, Confidence: {anomaly.confidence_score}")
```

**Anomaly Types**:
- `statistical_outlier_*`: Numerical values outside normal range
- `unusual_submission_time`: Submitted outside business hours
- `unusual_industry_pattern`: Industry/size/revenue mismatch
- `low_quality_score`: Quality score below threshold

## 🚀 Submission Stream Processor

**Purpose**: Orchestrate AI agents in a real-time processing pipeline.

**Location**: `src/streaming/submission_stream_processor.py`

**Processing Workflow**:

1. **Quality Assessment**: Initial quality evaluation
2. **Enrichment** (conditional): Apply if quality_score < 0.8
3. **Re-assessment**: Re-evaluate quality after enrichment
4. **Anomaly Detection**: Scan for unusual patterns
5. **Result Storage**: Save to DuckDB and update dashboard

**Usage**:
```python
from src.streaming.submission_stream_processor import SubmissionStreamProcessor

# Initialize processor
processor = SubmissionStreamProcessor()

# Process single submission
result = await processor.process_submission_stream(submission)

# Process batch
results = await processor.process_batch(submissions)
```

**Performance SLAs** (from `contracts/streaming_pipeline.yml`):
- Max processing time: 10,000ms (10 seconds)
- Max queue size: 1,000 submissions
- Availability: 99.9%
- Error rate threshold: 1%

## 📊 Real-Time Dashboard

**Purpose**: Monitor AI agent performance and data quality in real-time.

**Location**: `src/dashboard/realtime_monitor.py`

**Launch Dashboard**:
```bash
streamlit run src/dashboard/realtime_monitor.py
```

**Dashboard Features**:
- **Key Metrics**: Submissions today, avg quality score, enrichment rate, anomalies
- **Quality Distribution**: Histogram of quality scores
- **Processing Times**: Line chart of processing performance
- **AI Agent Performance**: Individual agent metrics
- **Recent Submissions**: Table of recent processing results

## 📋 Configuration Contracts

### Streaming Pipeline Contract

**File**: `contracts/streaming_pipeline.yml`

Defines:
- Input sources and polling configuration
- Processing pipeline stages
- AI agent specifications
- Performance SLAs

### AI Agent Configuration Contract

**File**: `contracts/ai_agent_configs.yml`

Defines:
- ML model configurations
- External API specifications
- Performance monitoring metrics
- Alerting thresholds

## 🧪 Testing

### Run AI Agent Tests

```bash
# All tests
pytest tests/test_ai_agents.py -v

# Specific test class
pytest tests/test_ai_agents.py::TestQualityAgent -v

# Specific test
pytest tests/test_ai_agents.py::TestQualityAgent::test_assess_high_quality_submission -v
```

### Test Coverage

- Quality Agent: 23 tests
- Enrichment Agent: Testing decision logic and cost optimization
- Anomaly Agent: Statistical and pattern detection tests
- Stream Processor: Integration and batch processing tests

## 📈 Performance Metrics

### Agent Performance Metrics (from contracts)

**Quality Agent**:
- Target accuracy: 90%
- Measurement window: 24 hours

**Enrichment Agent**:
- Target quality improvement: 15%
- Max cost per submission: $0.10
- Min confidence threshold: 0.7

**Anomaly Agent**:
- Target precision: 80%
- Confidence threshold: 0.7
- Retraining schedule: Daily

## 🔄 Example Workflows

### Example 1: Process Single Submission

```python
import asyncio
from src.streaming.submission_stream_processor import SubmissionStreamProcessor
from src.models.submission import ACORDSubmission
from decimal import Decimal
from datetime import datetime

async def process_submission():
    # Create submission
    submission = ACORDSubmission(
        submission_id="SUB-001",
        business_name="Example Corp",
        naics_code="541512",
        annual_revenue=Decimal("2500000"),
        employee_count=35,
        years_in_business=12,
        business_address="123 Main St, City, ST 12345",
        requested_coverage_types="GL, Property",
        requested_limits="$2M / $4M",
        submission_date=datetime.now()
    )
    
    # Process
    processor = SubmissionStreamProcessor()
    result = await processor.process_submission_stream(submission)
    
    # Display results
    print(f"Quality Score: {result.quality_score}")
    print(f"Anomalies: {result.anomalies_detected}")
    print(f"Processing Time: {result.processing_time_ms}ms")

asyncio.run(process_submission())
```

### Example 2: Batch Processing

```python
async def process_batch():
    processor = SubmissionStreamProcessor()
    
    # Load submissions
    submissions = [...]  # Load from XML files
    
    # Process concurrently
    results = await processor.process_batch(submissions)
    
    # Analyze results
    avg_quality = sum(r.quality_score for r in results) / len(results)
    total_anomalies = sum(len(r.anomalies_detected) for r in results)
    
    print(f"Processed {len(results)} submissions")
    print(f"Average quality: {avg_quality:.2f}")
    print(f"Total anomalies: {total_anomalies}")

asyncio.run(process_batch())
```

## 🔐 Security Considerations

1. **API Keys**: Store external API keys in environment variables, not in code
2. **Cost Controls**: Respect cost budgets to prevent runaway API expenses
3. **Data Privacy**: Ensure submission data is handled according to privacy policies
4. **Model Security**: Regularly retrain models on recent data to prevent drift

## 🚧 Future Enhancements

1. **Real API Integration**: Connect to actual external APIs
2. **Model Retraining**: Automated model retraining pipeline
3. **Advanced ML**: Deep learning for quality assessment
4. **Real-time Alerts**: Slack/email notifications for critical anomalies
5. **A/B Testing**: Compare different AI agent configurations
6. **Explainable AI**: More detailed reasoning for agent decisions

## 📚 Related Documentation

- [Architecture](ARCHITECTURE.md) - Overall system design
- [Contracts Guide](CONTRACTS.md) - YAML contract specifications
- [Metrics](METRICS.md) - Performance metrics and KPIs

## 🤝 Contributing

When adding new AI capabilities:

1. Define behavior in YAML contracts first
2. Implement AI agent with decision logging
3. Add comprehensive tests
4. Update this documentation
5. Verify contract compliance
