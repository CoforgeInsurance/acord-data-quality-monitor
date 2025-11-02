"""
Example Usage of AI-Powered Real-Time Data Quality Monitoring

This script demonstrates how to use the AI agents and streaming processor
to analyze ACORD insurance submissions in real-time.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from src.models.submission import ACORDSubmission
from src.agents.quality_agent import QualityAgent
from src.agents.enrichment_agent import EnrichmentAgent
from src.agents.anomaly_agent import AnomalyDetectionAgent
from src.streaming.submission_stream_processor import SubmissionStreamProcessor


def create_sample_submission(submission_id: str) -> ACORDSubmission:
    """Create a sample ACORD submission for testing"""
    return ACORDSubmission(
        submission_id=submission_id,
        acord_submission_number=f"ACORD-{submission_id}",
        business_name="ABC Manufacturing Inc",
        naics_code="333200",
        annual_revenue=Decimal("2500000"),
        employee_count=35,
        years_in_business=12,
        business_address="456 Industrial Park Dr, Manufacturing City, ST 54321",
        requested_coverage_types="General Liability, Property, Workers Compensation",
        requested_limits="$2M / $4M",
        submission_date=datetime.now()
    )


async def example_quality_agent():
    """Example: Using the Quality Agent"""
    print("\n" + "="*80)
    print("Example 1: Quality Agent")
    print("="*80)
    
    # Create agent
    quality_agent = QualityAgent()
    
    # Create submission
    submission = create_sample_submission("DEMO-001")
    
    # Assess quality
    print(f"\nAssessing quality for submission: {submission.submission_id}")
    result = await quality_agent.assess_quality(submission)
    
    # Display results
    print(f"\n✅ Quality Assessment Results:")
    print(f"   Overall Quality Score:    {result.quality_score:.2f}")
    print(f"   Completeness Score:       {result.completeness_score:.2f}")
    print(f"   Consistency Score:        {result.consistency_score:.2f}")
    print(f"   Agent Confidence:         {result.confidence:.2f}")
    print(f"\n📝 Agent Reasoning:")
    print(f"   {result.agent_reasoning}")


async def example_enrichment_agent():
    """Example: Using the Enrichment Agent"""
    print("\n" + "="*80)
    print("Example 2: Enrichment Agent")
    print("="*80)
    
    # Create agent
    enrichment_agent = EnrichmentAgent()
    
    # Create submission
    submission = create_sample_submission("DEMO-002")
    
    # Attempt enrichment
    print(f"\nAttempting enrichment for submission: {submission.submission_id}")
    enriched = await enrichment_agent.enrich_submission(submission)
    
    # Display results
    print(f"\n📊 Enrichment Results:")
    if enriched:
        print(f"   ✅ Enrichment applied")
    else:
        print(f"   ℹ️  No enrichment needed (submission is complete)")
    
    print(f"\n📝 Decision Log:")
    for decision in enrichment_agent.last_decision_log:
        print(f"   - {decision}")


async def example_anomaly_agent():
    """Example: Using the Anomaly Detection Agent"""
    print("\n" + "="*80)
    print("Example 3: Anomaly Detection Agent")
    print("="*80)
    
    # Create agent
    anomaly_agent = AnomalyDetectionAgent()
    
    # Create an unusual submission (very high revenue, few employees)
    anomalous_submission = ACORDSubmission(
        submission_id="DEMO-003",
        acord_submission_number="ACORD-DEMO-003",
        business_name="Unusual Business Corp",
        naics_code="541519",
        annual_revenue=Decimal("50000000"),  # Very high revenue
        employee_count=3,  # Very few employees
        years_in_business=1,  # New business
        business_address="789 Anomaly Ave, Unusual Town, ST 99999",
        requested_coverage_types="General Liability",
        requested_limits="$10M / $20M",
        submission_date=datetime(2024, 1, 1, 2, 30)  # 2:30 AM
    )
    
    # Mock quality result
    class MockQualityResult:
        quality_score = 0.7
    
    # Detect anomalies
    print(f"\nDetecting anomalies for submission: {anomalous_submission.submission_id}")
    anomalies = await anomaly_agent.detect_anomalies(anomalous_submission, MockQualityResult())
    
    # Display results
    print(f"\n⚠️  Anomalies Detected: {len(anomalies)}")
    for i, anomaly in enumerate(anomalies, 1):
        print(f"\n   Anomaly {i}:")
        print(f"   - Type:        {anomaly.anomaly_type}")
        print(f"   - Severity:    {anomaly.severity.upper()}")
        print(f"   - Confidence:  {anomaly.confidence_score:.2f}")
        print(f"   - Explanation: {anomaly.explanation}")
        print(f"   - Action:      {anomaly.recommended_action}")


async def example_stream_processor():
    """Example: Using the Submission Stream Processor"""
    print("\n" + "="*80)
    print("Example 4: Real-Time Stream Processor")
    print("="*80)
    
    # Create processor
    processor = SubmissionStreamProcessor()
    
    # Create submission
    submission = create_sample_submission("DEMO-004")
    
    # Process submission
    print(f"\nProcessing submission through AI agent pipeline: {submission.submission_id}")
    result = await processor.process_submission_stream(submission)
    
    # Display results
    print(f"\n🚀 Processing Results:")
    print(f"   Submission ID:         {result.submission_id}")
    print(f"   Quality Score:         {result.quality_score:.2f}")
    print(f"   Enrichment Applied:    {result.enrichment_applied}")
    print(f"   Anomalies Detected:    {len(result.anomalies_detected)}")
    print(f"   Processing Time:       {result.processing_time_ms}ms")
    
    print(f"\n🤖 AI Agent Decisions:")
    print(f"\n   Quality Agent:")
    print(f"   {result.ai_agent_decisions.get('quality_agent', 'N/A')}")
    
    print(f"\n   Enrichment Agent:")
    enrichment_log = result.ai_agent_decisions.get('enrichment_agent', [])
    if enrichment_log:
        for log in enrichment_log:
            print(f"   - {log}")
    else:
        print(f"   - No enrichment decisions")
    
    print(f"\n   Anomaly Agent:")
    anomaly_decisions = result.ai_agent_decisions.get('anomaly_agent', [])
    if anomaly_decisions:
        for decision in anomaly_decisions:
            print(f"   - {decision}")
    else:
        print(f"   - No anomalies detected")


async def example_batch_processing():
    """Example: Batch Processing Multiple Submissions"""
    print("\n" + "="*80)
    print("Example 5: Batch Processing")
    print("="*80)
    
    # Create processor
    processor = SubmissionStreamProcessor()
    
    # Create multiple submissions
    submissions = [
        create_sample_submission(f"BATCH-{i:03d}")
        for i in range(1, 6)
    ]
    
    # Process batch
    print(f"\nProcessing batch of {len(submissions)} submissions...")
    results = await processor.process_batch(submissions)
    
    # Display summary
    print(f"\n📊 Batch Processing Summary:")
    print(f"   Total Submissions:     {len(results)}")
    print(f"   Avg Quality Score:     {sum(r.quality_score for r in results) / len(results):.2f}")
    print(f"   Enrichments Applied:   {sum(1 for r in results if r.enrichment_applied)}")
    print(f"   Total Anomalies:       {sum(len(r.anomalies_detected) for r in results)}")
    print(f"   Avg Processing Time:   {sum(r.processing_time_ms for r in results) / len(results):.0f}ms")
    
    # Show individual results
    print(f"\n📋 Individual Results:")
    for result in results:
        print(f"   {result.submission_id}: Quality={result.quality_score:.2f}, "
              f"Time={result.processing_time_ms}ms, Anomalies={len(result.anomalies_detected)}")


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("🤖 AI-Powered ACORD Data Quality Monitor - Usage Examples")
    print("="*80)
    
    # Run examples
    await example_quality_agent()
    await example_enrichment_agent()
    await example_anomaly_agent()
    await example_stream_processor()
    await example_batch_processing()
    
    print("\n" + "="*80)
    print("✅ All examples completed successfully!")
    print("="*80)
    print("\n💡 Next Steps:")
    print("   1. Run the real-time dashboard: streamlit run src/dashboard/realtime_monitor.py")
    print("   2. Process actual ACORD XML files from data/sample_acord/")
    print("   3. Customize AI agent configurations in contracts/ai_agent_configs.yml")
    print("   4. Monitor agent performance and retrain models as needed")
    print("\n")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
