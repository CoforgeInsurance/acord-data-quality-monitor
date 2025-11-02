"""
Example: Using the ACORD Data Quality Monitor

This example demonstrates the complete workflow:
1. Parse ACORD 103 XML file
2. Validate data quality
3. Review validation results
4. Handle quality issues
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.acord_parser import ACORDParser
from src.validators.quality_validator import SubmissionQualityValidator
from decimal import Decimal
import json


def example_1_parse_complete_submission():
    """Example 1: Parse a complete ACORD submission"""
    print("=" * 60)
    print("Example 1: Parse Complete ACORD Submission")
    print("=" * 60)
    
    # Initialize parser
    parser = ACORDParser()
    
    # Parse complete submission
    xml_file = Path('data/sample_acord/complete_submission_001.xml')
    submission = parser.parse_xml(xml_file)
    
    # Display parsed data
    print(f"\n✅ Successfully parsed: {xml_file.name}")
    print(f"\nSubmission Details:")
    print(f"  Business Name: {submission.business_name}")
    print(f"  NAICS Code: {submission.naics_code}")
    print(f"  Annual Revenue: ${submission.annual_revenue:,.2f}")
    print(f"  Employees: {submission.employee_count}")
    print(f"  Years in Business: {submission.years_in_business}")
    print(f"  Coverage Types: {submission.requested_coverage_types}")
    print(f"  Coverage Limits: {submission.requested_limits}")
    print(f"  Submission Date: {submission.submission_date}")
    
    return submission


def example_2_validate_quality(submission):
    """Example 2: Validate data quality"""
    print("\n" + "=" * 60)
    print("Example 2: Validate Data Quality")
    print("=" * 60)
    
    # Initialize validator
    validator = SubmissionQualityValidator()
    
    # Run validation
    report = validator.validate_submission(submission)
    
    # Display quality scores
    print(f"\n📊 Quality Scores:")
    print(f"  Completeness: {report['completeness_score']:.0%}")
    print(f"  Consistency: {report['consistency_score']:.0%}")
    print(f"  Overall Quality: {report['overall_quality_score']:.0%}")
    
    # Display validation summary
    summary = report['summary']
    print(f"\n📋 Validation Summary:")
    print(f"  Total Checks: {summary['total_checks']}")
    print(f"  Passed: {summary['passed_checks']}")
    print(f"  Failed: {summary['failed_checks']}")
    print(f"  Errors: {summary['errors']}")
    print(f"  Warnings: {summary['warnings']}")
    
    # Show failed validations
    failed_validations = [r for r in report['validation_results'] if not r.passed]
    if failed_validations:
        print(f"\n⚠️  Failed Validations:")
        for result in failed_validations:
            print(f"  - [{result.severity.value.upper()}] {result.rule_name}")
            print(f"    {result.error_message}")
    else:
        print(f"\n✅ All validations passed!")
    
    return report


def example_3_handle_incomplete_submission():
    """Example 3: Handle incomplete submission"""
    print("\n" + "=" * 60)
    print("Example 3: Handle Incomplete Submission")
    print("=" * 60)
    
    parser = ACORDParser()
    xml_file = Path('data/sample_acord/incomplete_submission_001.xml')
    
    print(f"\nAttempting to parse: {xml_file.name}")
    print(f"(This file is missing: business_name, naics_code)")
    
    try:
        submission = parser.parse_xml(xml_file)
        print(f"✅ Parsed successfully (but may fail validation)")
    except ValueError as e:
        print(f"❌ Parser error: {e}")
        print(f"\nThis demonstrates contract enforcement:")
        print(f"  - Parser requires fields marked as 'nullable: false'")
        print(f"  - Fails fast on missing required data")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def example_4_handle_anomalous_submission():
    """Example 4: Detect anomalous data"""
    print("\n" + "=" * 60)
    print("Example 4: Detect Anomalous Data")
    print("=" * 60)
    
    parser = ACORDParser()
    validator = SubmissionQualityValidator()
    
    xml_file = Path('data/sample_acord/anomalous_submission_001.xml')
    print(f"\nParsing: {xml_file.name}")
    print(f"(This file has revenue/employee mismatch: 3 employees, $50M revenue)")
    
    try:
        submission = parser.parse_xml(xml_file)
        print(f"✅ Parsed successfully")
        
        # Validate
        report = validator.validate_submission(submission)
        
        print(f"\n📊 Quality Analysis:")
        print(f"  Completeness: {report['completeness_score']:.0%}")
        print(f"  Consistency: {report['consistency_score']:.0%}")
        print(f"  Overall Quality: {report['overall_quality_score']:.0%}")
        
        # Show consistency violations
        consistency_failures = [
            r for r in report['validation_results']
            if not r.passed and 'CONS' in r.rule_id
        ]
        
        if consistency_failures:
            print(f"\n⚠️  Consistency Issues Detected:")
            for result in consistency_failures:
                print(f"  - [{result.rule_id}] {result.rule_name}")
                print(f"    Severity: {result.severity.value}")
                print(f"    {result.error_message}")
        
        # Show enrichment suggestions
        if report['enrichment_suggestions']:
            print(f"\n💡 Enrichment Suggestions:")
            for suggestion in report['enrichment_suggestions']:
                print(f"  - {suggestion['source']}: {', '.join(suggestion['fields_provided'])}")
                print(f"    API: {suggestion['api_endpoint']}")
                print(f"    Cost: {suggestion['cost']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_5_batch_processing():
    """Example 5: Batch process multiple submissions"""
    print("\n" + "=" * 60)
    print("Example 5: Batch Processing")
    print("=" * 60)
    
    parser = ACORDParser()
    validator = SubmissionQualityValidator()
    
    # Get all complete submission files
    sample_dir = Path('data/sample_acord')
    xml_files = sorted(sample_dir.glob('complete_*.xml'))
    
    print(f"\nProcessing {len(xml_files)} submissions...")
    
    results = []
    for xml_file in xml_files:
        try:
            submission = parser.parse_xml(xml_file)
            report = validator.validate_submission(submission)
            
            results.append({
                'file': xml_file.name,
                'business_name': submission.business_name,
                'quality_score': report['overall_quality_score'],
                'passed_checks': report['summary']['passed_checks'],
                'failed_checks': report['summary']['failed_checks']
            })
        except Exception as e:
            results.append({
                'file': xml_file.name,
                'error': str(e)
            })
    
    # Display results table
    print(f"\n📊 Batch Processing Results:")
    print(f"\n{'File':<30} {'Business Name':<25} {'Quality':<10} {'Passed':<8} {'Failed':<8}")
    print("-" * 90)
    
    for result in results:
        if 'error' in result:
            print(f"{result['file']:<30} ERROR: {result['error']}")
        else:
            print(f"{result['file']:<30} {result['business_name']:<25} "
                  f"{result['quality_score']:.0%}      {result['passed_checks']:<8} {result['failed_checks']:<8}")


def main():
    """Run all examples"""
    print("\n")
    print("=" * 60)
    print("ACORD Data Quality Monitor - Usage Examples")
    print("=" * 60)
    
    # Example 1: Parse complete submission
    submission = example_1_parse_complete_submission()
    
    # Example 2: Validate quality
    if submission:
        report = example_2_validate_quality(submission)
    
    # Example 3: Handle incomplete submission
    example_3_handle_incomplete_submission()
    
    # Example 4: Detect anomalies
    example_4_handle_anomalous_submission()
    
    # Example 5: Batch processing
    example_5_batch_processing()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
    print("\nNext Steps:")
    print("  1. Review the generated validation reports")
    print("  2. Integrate parser and validator into your pipeline")
    print("  3. Run dbt models: cd dbt_project && dbt run")
    print("  4. View metrics: cat docs/METRICS.md")
    print("  5. Regenerate code: Delete AI-generated files, regenerate from contracts")
    print("")


if __name__ == '__main__':
    main()
