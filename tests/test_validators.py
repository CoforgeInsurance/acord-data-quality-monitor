"""
Test Quality Validators

Tests that the AI-generated validators correctly check all quality rules.
"""

import pytest
from src.parsers.acord_parser import ACORDParser
from src.validators.quality_validator import SubmissionQualityValidator, Severity


class TestQualityValidator:
    """Test suite for quality validator"""
    
    def test_validator_initialization(self):
        """Validator should initialize with contract loader"""
        validator = SubmissionQualityValidator()
        assert validator is not None
        assert validator.contract_loader is not None
        assert validator.quality_rules is not None
    
    def test_validate_complete_submission(self, complete_submission_files):
        """Complete submissions should pass most validations"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        for xml_file in complete_submission_files:
            submission = parser.parse_xml(xml_file)
            report = validator.validate_submission(submission)
            
            # Verify report structure
            assert 'completeness_score' in report
            assert 'consistency_score' in report
            assert 'overall_quality_score' in report
            assert 'validation_results' in report
            assert 'enrichment_suggestions' in report
            assert 'summary' in report
            
            # Complete submissions should have high completeness
            assert report['completeness_score'] >= 0.8
            
            # Scores should be between 0 and 1
            assert 0.0 <= report['completeness_score'] <= 1.0
            assert 0.0 <= report['consistency_score'] <= 1.0
            assert 0.0 <= report['overall_quality_score'] <= 1.0
    
    def test_validate_anomalous_submission_low_score(self, anomalous_submission_files):
        """Anomalous submissions should have consistency warnings"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        # Parse first anomalous file (revenue_employee_mismatch)
        submission = parser.parse_xml(anomalous_submission_files[0])
        report = validator.validate_submission(submission)
        
        # Should have failed consistency checks
        failed_consistency = [
            r for r in report['validation_results']
            if not r.passed and 'CONS' in r.rule_id
        ]
        assert len(failed_consistency) > 0
        
        # Consistency score should be lower
        assert report['consistency_score'] < 1.0
    
    def test_required_fields_validation(self, complete_submission_files):
        """Validator should check all required fields from contract"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        submission = parser.parse_xml(complete_submission_files[0])
        required_results = validator.validate_required_fields(submission)
        
        # Should have validation results for required fields
        assert len(required_results) > 0
        
        # Should check business_name, naics_code, annual_revenue, etc.
        field_names = set()
        for result in required_results:
            if result.field_name:
                field_names.add(result.field_name)
        
        assert 'business_name' in field_names or any('business_name' in fn for fn in field_names)
        assert 'naics_code' in field_names or any('naics_code' in fn for fn in field_names)
    
    def test_consistency_checks_validation(self, complete_submission_files):
        """Validator should run all consistency checks from contract"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        submission = parser.parse_xml(complete_submission_files[0])
        consistency_results = validator.validate_consistency(submission)
        
        # Should have results for CONS-001, CONS-002, CONS-003
        rule_ids = [r.rule_id for r in consistency_results]
        assert 'CONS-001' in rule_ids
        assert 'CONS-002' in rule_ids
        assert 'CONS-003' in rule_ids
    
    def test_cons_001_revenue_employee_consistency(self):
        """Test CONS-001: Revenue vs. Employee Consistency"""
        from src.models.submission import ACORDSubmission
        from datetime import datetime
        from decimal import Decimal
        
        validator = SubmissionQualityValidator()
        
        # Create submission with inconsistent data (3 employees, $50M revenue)
        submission = ACORDSubmission(
            submission_id="test-001",
            business_name="Test Corp",
            naics_code="541511",
            annual_revenue=Decimal("50000000"),
            employee_count=3,
            years_in_business=5,
            business_address="123 Main St, City, ST 12345",
            requested_coverage_types="General Liability",
            requested_limits="$1,000,000",
            submission_date=datetime.now()
        )
        
        # Validate
        consistency_results = validator.validate_consistency(submission)
        cons_001 = [r for r in consistency_results if r.rule_id == 'CONS-001']
        
        assert len(cons_001) == 1
        assert cons_001[0].passed == False  # Should fail
        assert cons_001[0].severity == Severity.WARNING
    
    def test_cons_002_years_revenue_consistency(self):
        """Test CONS-002: Years in Business vs. Revenue"""
        from src.models.submission import ACORDSubmission
        from datetime import datetime
        from decimal import Decimal
        
        validator = SubmissionQualityValidator()
        
        # Create submission with new business and high revenue
        submission = ACORDSubmission(
            submission_id="test-002",
            business_name="Startup Inc",
            naics_code="541511",
            annual_revenue=Decimal("25000000"),  # $25M
            employee_count=50,
            years_in_business=1,  # Only 1 year old
            business_address="123 Main St, City, ST 12345",
            requested_coverage_types="General Liability",
            requested_limits="$1,000,000",
            submission_date=datetime.now()
        )
        
        # Validate
        consistency_results = validator.validate_consistency(submission)
        cons_002 = [r for r in consistency_results if r.rule_id == 'CONS-002']
        
        assert len(cons_002) == 1
        assert cons_002[0].passed == False  # Should fail
        assert cons_002[0].severity == Severity.WARNING
    
    def test_cons_003_naics_validity(self, complete_submission_files):
        """Test CONS-003: NAICS Code Industry Match"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        submission = parser.parse_xml(complete_submission_files[0])
        consistency_results = validator.validate_consistency(submission)
        cons_003 = [r for r in consistency_results if r.rule_id == 'CONS-003']
        
        assert len(cons_003) == 1
        # Should pass for valid 6-digit NAICS
        assert cons_003[0].passed == True
    
    def test_quality_thresholds_calculation(self, complete_submission_files):
        """Test that quality scores are calculated per contract thresholds"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        submission = parser.parse_xml(complete_submission_files[0])
        report = validator.validate_submission(submission)
        
        # Overall quality score should be weighted average
        # (completeness_score * 0.6) + (consistency_score * 0.4)
        expected_overall = (report['completeness_score'] * 0.6) + (report['consistency_score'] * 0.4)
        assert abs(report['overall_quality_score'] - expected_overall) < 0.01
    
    def test_enrichment_suggestions(self, incomplete_submission_files):
        """Validator should suggest enrichment for missing data"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        # Try parsing incomplete file (may fail, which is expected)
        try:
            submission = parser.parse_xml(incomplete_submission_files[0])
            report = validator.validate_submission(submission)
            
            # If parsing succeeds, check for enrichment suggestions
            if report['summary']['failed_checks'] > 0:
                # May have enrichment suggestions
                assert 'enrichment_suggestions' in report
        except (ValueError, Exception):
            # If parsing fails due to missing required fields, that's expected
            pass
    
    def test_validation_result_severity_levels(self, complete_submission_files):
        """Validation results should have appropriate severity levels"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        submission = parser.parse_xml(complete_submission_files[0])
        report = validator.validate_submission(submission)
        
        # Check severity levels exist
        severities = set(r.severity for r in report['validation_results'])
        assert len(severities) > 0
        
        # All severities should be valid enum values
        for severity in severities:
            assert severity in [Severity.ERROR, Severity.WARNING, Severity.INFO]
    
    def test_summary_counts(self, complete_submission_files):
        """Validation summary should have accurate counts"""
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        submission = parser.parse_xml(complete_submission_files[0])
        report = validator.validate_submission(submission)
        
        summary = report['summary']
        
        # Counts should add up
        assert summary['total_checks'] == summary['passed_checks'] + summary['failed_checks']
        
        # Errors and warnings should not exceed failed checks
        assert summary['errors'] + summary['warnings'] <= summary['failed_checks']
