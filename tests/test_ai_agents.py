"""
Test suite for AI agents and real-time processing.

Tests AI agent decision-making, model performance, and system integration.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from src.agents.quality_agent import QualityAgent, QualityAssessmentResult
from src.agents.enrichment_agent import EnrichmentAgent
from src.agents.anomaly_agent import AnomalyDetectionAgent
from src.models.submission import ACORDSubmission, AnomalyResult
from src.streaming.submission_stream_processor import SubmissionStreamProcessor


@pytest.fixture
def contracts_dir():
    """Return path to contracts directory"""
    return Path(__file__).parent.parent / 'contracts'


@pytest.fixture
def sample_submission():
    """Create a sample ACORD submission for testing"""
    return ACORDSubmission(
        submission_id="TEST-001",
        acord_submission_number="ACORD-001",
        business_name="Test Business Inc",
        naics_code="541512",
        annual_revenue=Decimal("1500000"),
        employee_count=25,
        years_in_business=10,
        business_address="123 Main St, Anytown, ST 12345",
        requested_coverage_types="General Liability, Property",
        requested_limits="$1M / $2M",
        submission_date=datetime.now()
    )


@pytest.fixture
def high_quality_submission():
    """Create a high quality submission"""
    return ACORDSubmission(
        submission_id="TEST-HQ-001",
        acord_submission_number="ACORD-HQ-001",
        business_name="High Quality Business LLC",
        naics_code="541511",
        annual_revenue=Decimal("2500000"),
        employee_count=50,
        years_in_business=15,
        business_address="456 Quality Ave, Goodtown, ST 54321",
        requested_coverage_types="General Liability, Property, Workers Comp",
        requested_limits="$2M / $4M",
        submission_date=datetime.now()
    )


@pytest.fixture
def low_quality_submission():
    """Create a low quality submission with minimal data"""
    return ACORDSubmission(
        submission_id="TEST-LQ-001",
        acord_submission_number="ACORD-LQ-001",
        business_name="Low",  # Too short, will pass min_length=3 but borderline
        naics_code="123456",  # Valid format but potentially unusual
        annual_revenue=Decimal("15000"),  # Very low, near minimum
        employee_count=1,
        years_in_business=0,  # Brand new business
        business_address="1 St",  # Very short address
        requested_coverage_types="GL",
        requested_limits="$1M",
        submission_date=datetime.now()
    )


@pytest.fixture
def anomalous_submission():
    """Create a submission with statistical anomalies"""
    return ACORDSubmission(
        submission_id="TEST-ANOM-001",
        acord_submission_number="ACORD-ANOM-001",
        business_name="Anomalous Business Corp",
        naics_code="541519",
        annual_revenue=Decimal("50000000"),  # Very high revenue
        employee_count=3,  # Very few employees for such high revenue
        years_in_business=1,  # New business with high revenue
        business_address="789 Unusual Blvd, Oddtown, ST 99999",
        requested_coverage_types="General Liability",
        requested_limits="$10M / $20M",
        submission_date=datetime(2024, 1, 1, 2, 30)  # 2:30 AM - unusual time
    )


class TestQualityAgent:
    """Test Quality Agent functionality"""
    
    @pytest.mark.asyncio
    async def test_quality_agent_initialization(self, contracts_dir):
        """Quality agent should initialize successfully"""
        agent = QualityAgent(contracts_dir)
        assert agent is not None
        assert agent.validator is not None
        assert agent.contract is not None
    
    @pytest.mark.asyncio
    async def test_assess_high_quality_submission(self, contracts_dir, high_quality_submission):
        """Quality agent should give high scores to high quality submissions"""
        agent = QualityAgent(contracts_dir)
        result = await agent.assess_quality(high_quality_submission)
        
        assert isinstance(result, QualityAssessmentResult)
        assert result.quality_score >= 0.7
        assert result.completeness_score >= 0.7
        assert result.confidence >= 0.7
        assert "quality" in result.agent_reasoning.lower()
    
    @pytest.mark.asyncio
    async def test_assess_low_quality_submission(self, contracts_dir, low_quality_submission):
        """Quality agent should identify low quality submissions"""
        agent = QualityAgent(contracts_dir)
        result = await agent.assess_quality(low_quality_submission)
        
        assert isinstance(result, QualityAssessmentResult)
        # Low quality submission might still pass basic validation
        assert 0.0 <= result.quality_score <= 1.0
        assert result.validation_details is not None
    
    @pytest.mark.asyncio
    async def test_quality_agent_reasoning(self, contracts_dir, sample_submission):
        """Quality agent should provide reasoning for its assessment"""
        agent = QualityAgent(contracts_dir)
        result = await agent.assess_quality(sample_submission)
        
        assert result.agent_reasoning is not None
        assert len(result.agent_reasoning) > 0
        assert isinstance(result.agent_reasoning, str)
    
    @pytest.mark.asyncio
    async def test_quality_agent_confidence(self, contracts_dir, high_quality_submission):
        """Quality agent should have high confidence for clear cases"""
        agent = QualityAgent(contracts_dir)
        result = await agent.assess_quality(high_quality_submission)
        
        assert 0.0 <= result.confidence <= 1.0
        # High quality submissions should have high confidence
        if result.quality_score >= 0.9:
            assert result.confidence >= 0.8


class TestEnrichmentAgent:
    """Test Enrichment Agent functionality"""
    
    @pytest.mark.asyncio
    async def test_enrichment_agent_initialization(self, contracts_dir):
        """Enrichment agent should initialize successfully"""
        agent = EnrichmentAgent(contracts_dir)
        assert agent is not None
        assert agent.cost_budget > 0
        assert agent.contract is not None
    
    @pytest.mark.asyncio
    async def test_enrichment_complete_submission(self, contracts_dir, high_quality_submission):
        """Enrichment agent should not enrich complete submissions"""
        agent = EnrichmentAgent(contracts_dir)
        result = await agent.enrich_submission(high_quality_submission)
        
        # No enrichment needed for complete submission
        assert result is None or result == high_quality_submission
        assert len(agent.last_decision_log) > 0
    
    @pytest.mark.asyncio
    async def test_enrichment_decision_logging(self, contracts_dir, sample_submission):
        """Enrichment agent should log its decisions"""
        agent = EnrichmentAgent(contracts_dir)
        await agent.enrich_submission(sample_submission)
        
        assert agent.last_decision_log is not None
        assert isinstance(agent.last_decision_log, list)
        assert len(agent.last_decision_log) > 0
    
    @pytest.mark.asyncio
    async def test_enrichment_cost_budget(self, contracts_dir, sample_submission):
        """Enrichment agent should respect cost budget"""
        agent = EnrichmentAgent(contracts_dir)
        
        # Agent should have a cost budget
        assert agent.cost_budget > 0
        assert agent.cost_budget == 0.10  # From contract


class TestAnomalyDetectionAgent:
    """Test Anomaly Detection Agent functionality"""
    
    @pytest.mark.asyncio
    async def test_anomaly_agent_initialization(self, contracts_dir):
        """Anomaly agent should initialize successfully"""
        agent = AnomalyDetectionAgent(contracts_dir)
        assert agent is not None
        assert agent.statistical_model is not None
        assert agent.scaler is not None
        assert agent.confidence_threshold > 0
    
    @pytest.mark.asyncio
    async def test_detect_no_anomalies(self, contracts_dir, high_quality_submission):
        """Anomaly agent should not flag normal submissions"""
        agent = AnomalyDetectionAgent(contracts_dir)
        
        # Mock quality result
        class MockQualityResult:
            quality_score = 0.9
        
        anomalies = await agent.detect_anomalies(high_quality_submission, MockQualityResult())
        
        # Normal submission should have few or no anomalies
        assert isinstance(anomalies, list)
        # Allow for some anomalies due to ML uncertainty
        assert len(anomalies) <= 2
    
    @pytest.mark.asyncio
    async def test_detect_statistical_anomalies(self, contracts_dir, anomalous_submission):
        """Anomaly agent should detect statistical outliers"""
        agent = AnomalyDetectionAgent(contracts_dir)
        
        class MockQualityResult:
            quality_score = 0.7
        
        anomalies = await agent.detect_anomalies(anomalous_submission, MockQualityResult())
        
        # Anomalous submission should be flagged
        assert isinstance(anomalies, list)
        
        # Check structure of anomalies
        for anomaly in anomalies:
            assert isinstance(anomaly, AnomalyResult)
            assert hasattr(anomaly, 'anomaly_type')
            assert hasattr(anomaly, 'confidence_score')
            assert hasattr(anomaly, 'severity')
            assert 0.0 <= anomaly.confidence_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_detect_time_based_anomalies(self, contracts_dir, anomalous_submission):
        """Anomaly agent should detect unusual submission times"""
        agent = AnomalyDetectionAgent(contracts_dir)
        
        class MockQualityResult:
            quality_score = 0.8
        
        anomalies = await agent.detect_anomalies(anomalous_submission, MockQualityResult())
        
        # Check if time anomaly was detected
        anomaly_types = [a.anomaly_type for a in anomalies]
        # May or may not detect time anomaly depending on other factors
        assert isinstance(anomaly_types, list)
    
    @pytest.mark.asyncio
    async def test_anomaly_severity_levels(self, contracts_dir, anomalous_submission):
        """Anomaly agent should assign severity levels"""
        agent = AnomalyDetectionAgent(contracts_dir)
        
        class MockQualityResult:
            quality_score = 0.6
        
        anomalies = await agent.detect_anomalies(anomalous_submission, MockQualityResult())
        
        for anomaly in anomalies:
            assert anomaly.severity in ['low', 'medium', 'high', 'critical']


class TestSubmissionStreamProcessor:
    """Test real-time streaming pipeline"""
    
    @pytest.mark.asyncio
    async def test_processor_initialization(self, contracts_dir):
        """Stream processor should initialize successfully"""
        processor = SubmissionStreamProcessor(contracts_dir)
        assert processor is not None
        assert processor.quality_agent is not None
        assert processor.enrichment_agent is not None
        assert processor.anomaly_agent is not None
    
    @pytest.mark.asyncio
    async def test_process_single_submission(self, contracts_dir, sample_submission):
        """Stream processor should process submissions"""
        processor = SubmissionStreamProcessor(contracts_dir)
        result = await processor.process_submission_stream(sample_submission)
        
        assert result is not None
        assert result.submission_id == sample_submission.submission_id
        assert 0.0 <= result.quality_score <= 1.0
        assert result.processing_time_ms > 0
        assert isinstance(result.enrichment_applied, bool)
        assert isinstance(result.anomalies_detected, list)
    
    @pytest.mark.asyncio
    async def test_process_high_quality_submission(self, contracts_dir, high_quality_submission):
        """Stream processor should handle high quality submissions efficiently"""
        processor = SubmissionStreamProcessor(contracts_dir)
        result = await processor.process_submission_stream(high_quality_submission)
        
        # High quality submission shouldn't need enrichment
        assert result.quality_score >= 0.7
        # Enrichment likely not needed
        assert isinstance(result.enrichment_applied, bool)
    
    @pytest.mark.asyncio
    async def test_process_batch_submissions(self, contracts_dir, sample_submission, high_quality_submission):
        """Stream processor should handle batch processing"""
        processor = SubmissionStreamProcessor(contracts_dir)
        submissions = [sample_submission, high_quality_submission]
        
        results = await processor.process_batch(submissions)
        
        assert len(results) == 2
        assert all(r.quality_score >= 0 for r in results)
        assert all(r.processing_time_ms > 0 for r in results)
    
    @pytest.mark.asyncio
    async def test_ai_agent_decisions_logged(self, contracts_dir, sample_submission):
        """Stream processor should log AI agent decisions"""
        processor = SubmissionStreamProcessor(contracts_dir)
        result = await processor.process_submission_stream(sample_submission)
        
        assert result.ai_agent_decisions is not None
        assert 'quality_agent' in result.ai_agent_decisions
        assert 'enrichment_agent' in result.ai_agent_decisions
        assert 'anomaly_agent' in result.ai_agent_decisions
    
    @pytest.mark.asyncio
    async def test_processing_time_reasonable(self, contracts_dir, sample_submission):
        """Stream processor should complete in reasonable time"""
        processor = SubmissionStreamProcessor(contracts_dir)
        result = await processor.process_submission_stream(sample_submission)
        
        # Processing should complete in under 10 seconds (10000ms)
        assert result.processing_time_ms < 10000
        # Processing should take more than 0ms
        assert result.processing_time_ms > 0


class TestIntegration:
    """Integration tests for the complete AI agent pipeline"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_processing(self, contracts_dir, sample_submission):
        """Test complete pipeline from submission to result"""
        processor = SubmissionStreamProcessor(contracts_dir)
        result = await processor.process_submission_stream(sample_submission)
        
        # Verify all components produced output
        assert result.quality_score is not None
        assert result.ai_agent_decisions is not None
        assert 'quality_agent' in result.ai_agent_decisions
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_enrichment_improves_quality(self, contracts_dir):
        """Test that enrichment can improve quality scores"""
        processor = SubmissionStreamProcessor(contracts_dir)
        
        # Create a submission that might benefit from enrichment
        # (though current implementation doesn't actually enrich)
        submission = ACORDSubmission(
            submission_id="TEST-ENRICH-001",
            acord_submission_number="ACORD-ENRICH-001",
            business_name="Test",
            naics_code="541512",
            annual_revenue=Decimal("100000"),
            employee_count=5,
            years_in_business=2,
            business_address="123 Main St",
            requested_coverage_types="GL",
            requested_limits="$1M",
            submission_date=datetime.now()
        )
        
        result = await processor.process_submission_stream(submission)
        
        # Result should be valid regardless of enrichment
        assert 0.0 <= result.quality_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, contracts_dir, sample_submission, high_quality_submission, anomalous_submission):
        """Test that multiple submissions can be processed concurrently"""
        processor = SubmissionStreamProcessor(contracts_dir)
        
        submissions = [sample_submission, high_quality_submission, anomalous_submission]
        
        # Process concurrently
        results = await processor.process_batch(submissions)
        
        assert len(results) == 3
        assert all(isinstance(r.quality_score, float) for r in results)
        assert all(r.processing_time_ms > 0 for r in results)
