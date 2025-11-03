"""
Test ACORD Parser

Tests that the AI-generated parser correctly extracts fields from ACORD XML files.
"""

import pytest
from pathlib import Path
from src.parsers.acord_parser import ACORDParser
from src.models.submission import ACORDSubmission
from pydantic import ValidationError


class TestACORDParser:
    """Test suite for ACORD parser"""
    
    def test_parser_initialization(self):
        """Parser should initialize with contract loader"""
        parser = ACORDParser()
        assert parser is not None
        assert parser.contract_loader is not None
        assert parser.dim_submission_contract is not None
        assert parser.quality_rules_contract is not None
    
    def test_parse_complete_submission(self, complete_submission_files):
        """Parser should successfully parse complete submissions"""
        parser = ACORDParser()
        
        for xml_file in complete_submission_files:
            submission = parser.parse_xml(xml_file)
            
            # Verify it's an ACORDSubmission instance
            assert isinstance(submission, ACORDSubmission)
            
            # Verify all required fields are present
            assert submission.submission_id is not None
            assert submission.business_name is not None
            assert submission.naics_code is not None
            assert submission.annual_revenue is not None
            assert submission.employee_count is not None
            assert submission.years_in_business is not None
            assert submission.business_address is not None
            assert submission.requested_coverage_types is not None
            assert submission.requested_limits is not None
            assert submission.submission_date is not None
            assert submission.created_at is not None
    
    def test_parse_incomplete_submission_uses_placeholders(self, incomplete_submission_files):
        """Parser should use placeholder values for incomplete submissions to allow processing"""
        parser = ACORDParser()
        
        for xml_file in incomplete_submission_files:
            # Parser should succeed with placeholders
            submission = parser.parse_xml(xml_file)
            assert isinstance(submission, ACORDSubmission)
            
            # Verify placeholders are used for missing fields
            # At least one placeholder should be present
            has_placeholder = (
                submission.business_name == "UNKNOWN_BUSINESS" or
                submission.naics_code == "000000" or
                submission.annual_revenue == 10000 or
                submission.employee_count == 1 or
                submission.years_in_business == 0 or
                submission.business_address == "UNKNOWN_ADDRESS" or
                submission.requested_coverage_types == "UNKNOWN_COVERAGE" or
                submission.requested_limits == "UNKNOWN_LIMITS"
            )
            assert has_placeholder, f"Expected placeholders for incomplete submission {xml_file.name}"
    
    def test_parse_anomalous_submission(self, anomalous_submission_files):
        """Parser should parse anomalous submissions but validation will catch issues"""
        parser = ACORDParser()
        
        # Parser extracts data even if it's anomalous
        # Validator will catch the issues
        for xml_file in anomalous_submission_files:
            try:
                submission = parser.parse_xml(xml_file)
                assert isinstance(submission, ACORDSubmission)
            except (ValueError, ValidationError):
                # Some anomalies might fail at parse time (e.g., invalid NAICS format)
                pass
    
    def test_extract_field_business_name(self, complete_submission_files):
        """Parser should extract business name correctly"""
        parser = ACORDParser()
        submission = parser.parse_xml(complete_submission_files[0])
        
        assert len(submission.business_name) >= 3
        assert len(submission.business_name) <= 200
    
    def test_extract_field_naics_code(self, complete_submission_files):
        """Parser should extract NAICS code correctly"""
        parser = ACORDParser()
        submission = parser.parse_xml(complete_submission_files[0])
        
        # Should be 6 digits
        assert len(submission.naics_code) == 6
        assert submission.naics_code.isdigit()
    
    def test_extract_field_annual_revenue(self, complete_submission_files):
        """Parser should extract annual revenue as Decimal"""
        parser = ACORDParser()
        submission = parser.parse_xml(complete_submission_files[0])
        
        assert submission.annual_revenue >= 10000
        assert submission.annual_revenue <= 1000000000
    
    def test_extract_field_employee_count(self, complete_submission_files):
        """Parser should extract employee count as integer"""
        parser = ACORDParser()
        submission = parser.parse_xml(complete_submission_files[0])
        
        assert isinstance(submission.employee_count, int)
        assert submission.employee_count >= 1
        assert submission.employee_count <= 100000
    
    def test_extract_field_address(self, complete_submission_files):
        """Parser should combine address fields correctly"""
        parser = ACORDParser()
        submission = parser.parse_xml(complete_submission_files[0])
        
        # Address should contain multiple parts
        assert len(submission.business_address) > 0
        assert ',' in submission.business_address  # Should have comma separators
    
    def test_parse_multiple_files(self, complete_submission_files):
        """Parser should handle parsing multiple files"""
        parser = ACORDParser()
        submissions = parser.parse_multiple(complete_submission_files)
        
        assert len(submissions) == len(complete_submission_files)
        assert all(isinstance(s, ACORDSubmission) for s in submissions)
    
    def test_parse_nonexistent_file(self):
        """Parser should raise FileNotFoundError for missing file"""
        parser = ACORDParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_xml(Path('/nonexistent/file.xml'))
    
    def test_datetime_parsing(self, complete_submission_files):
        """Parser should correctly parse datetime fields"""
        parser = ACORDParser()
        submission = parser.parse_xml(complete_submission_files[0])
        
        from datetime import datetime
        assert isinstance(submission.submission_date, datetime)
        assert isinstance(submission.created_at, datetime)
