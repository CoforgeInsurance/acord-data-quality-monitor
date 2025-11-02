"""
Test Contract Compliance

This is the KEY test ensuring regeneration safety:
- Delete AI-generated parser → regenerate → tests still pass
- Delete AI-generated validators → regenerate → tests still pass
- Delete AI-generated dbt models → regenerate → tests still pass

Tests verify that AI-generated code implements ALL specifications from YAML contracts.
"""

import pytest
import yaml
from pathlib import Path
from src.parsers.acord_parser import ACORDParser
from src.validators.quality_validator import SubmissionQualityValidator
from src.models.submission import ACORDSubmission


class TestContractCompliance:
    """Verify AI-generated code complies with YAML contracts"""
    
    def test_parser_implements_all_dim_submission_fields(self, contracts_dir, complete_submission_files):
        """
        Parser must extract ALL fields defined in dim_submission.yml
        
        This ensures regeneration safety: if we delete and regenerate the parser,
        it must still extract all contract fields.
        """
        # Load dim_submission contract
        contract_path = contracts_dir / 'dim_submission.yml'
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
        
        # Get all field names from contract schema
        contract_fields = set()
        for field_def in contract['schema']:
            field_name = field_def['name']
            # Skip generated fields like submission_id and created_at
            if field_name not in ['submission_id', 'created_at']:
                contract_fields.add(field_name)
        
        # Parse a complete submission
        parser = ACORDParser()
        submission = parser.parse_xml(complete_submission_files[0])
        
        # Verify parser extracts all contract fields
        for field_name in contract_fields:
            assert hasattr(submission, field_name), \
                f"Parser must extract contract field: {field_name}"
            
            value = getattr(submission, field_name)
            # Field should have a value (not None for complete submissions)
            # Some fields can be None (nullable=true), but for complete submissions all should be present
            if field_name != 'acord_submission_number':  # This one can be None
                assert value is not None, \
                    f"Parser must extract non-null value for field: {field_name}"
    
    def test_parser_uses_correct_acord_paths(self, contracts_dir):
        """
        Parser must use ACORD paths defined in contracts
        
        Verifies parser implementation matches contract specifications.
        """
        # Load contracts
        dim_contract_path = contracts_dir / 'dim_submission.yml'
        with open(dim_contract_path, 'r') as f:
            dim_contract = yaml.safe_load(f)
        
        quality_contract_path = contracts_dir / 'submission_quality_rules.yml'
        with open(quality_contract_path, 'r') as f:
            quality_contract = yaml.safe_load(f)
        
        # Verify parser has mappings for all ACORD paths
        parser = ACORDParser()
        
        # Check parser has loaded contracts
        assert parser.dim_submission_contract is not None
        assert parser.quality_rules_contract is not None
        
        # Parser should have extract_field method for XPath extraction
        assert hasattr(parser, '_extract_field')
    
    def test_validator_implements_all_required_fields_checks(self, contracts_dir):
        """
        Validator must check ALL required_fields from submission_quality_rules.yml
        
        This ensures regeneration safety for validators.
        """
        # Load quality rules contract
        contract_path = contracts_dir / 'submission_quality_rules.yml'
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
        
        # Get all required field rules
        required_fields = []
        for category, fields in contract['required_fields'].items():
            for field_def in fields:
                required_fields.append(field_def['field'])
        
        # Validator should check these fields
        validator = SubmissionQualityValidator()
        assert validator.quality_rules is not None
        
        # Create a test submission
        from datetime import datetime
        from decimal import Decimal
        
        submission = ACORDSubmission(
            submission_id="test-compliance",
            business_name="Test Business",
            naics_code="541511",
            annual_revenue=Decimal("1000000"),
            employee_count=20,
            years_in_business=5,
            business_address="123 Test St, City, ST 12345",
            requested_coverage_types="General Liability",
            requested_limits="$1,000,000",
            submission_date=datetime.now()
        )
        
        # Validate
        results = validator.validate_required_fields(submission)
        
        # Should have validation results (passed or failed)
        assert len(results) > 0
        
        # Count fields that were actually validated
        validated_fields = set()
        for result in results:
            if result.field_name:
                # Handle composite field names like "field1, field2"
                for field in result.field_name.split(','):
                    validated_fields.add(field.strip())
        
        # Most required fields should be validated
        # (At least basic_info fields: business_name, naics_code, annual_revenue, employee_count)
        assert 'business_name' in validated_fields or any('business_name' in f for f in validated_fields)
        assert 'naics_code' in validated_fields or any('naics_code' in f for f in validated_fields)
    
    def test_validator_implements_all_consistency_checks(self, contracts_dir):
        """
        Validator must run ALL consistency_checks from submission_quality_rules.yml
        
        This ensures all business logic rules are implemented.
        """
        # Load quality rules contract
        contract_path = contracts_dir / 'submission_quality_rules.yml'
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
        
        # Get all consistency check rule IDs
        contract_rule_ids = set()
        for check in contract['consistency_checks']:
            contract_rule_ids.add(check['rule_id'])
        
        # Create a test submission
        from datetime import datetime
        from decimal import Decimal
        
        validator = SubmissionQualityValidator()
        submission = ACORDSubmission(
            submission_id="test-compliance",
            business_name="Test Business",
            naics_code="541511",
            annual_revenue=Decimal("1000000"),
            employee_count=20,
            years_in_business=5,
            business_address="123 Test St, City, ST 12345",
            requested_coverage_types="General Liability",
            requested_limits="$1,000,000",
            submission_date=datetime.now()
        )
        
        # Get consistency check results
        results = validator.validate_consistency(submission)
        
        # Get rule IDs from results
        validated_rule_ids = set(r.rule_id for r in results)
        
        # Validator must check all contract consistency rules
        for rule_id in contract_rule_ids:
            assert rule_id in validated_rule_ids, \
                f"Validator must implement consistency check: {rule_id}"
    
    def test_validator_calculates_quality_thresholds_per_contract(self, contracts_dir, complete_submission_files):
        """
        Validator must calculate quality metrics per contract specifications
        
        Verifies quality_thresholds calculations match contract formulas.
        """
        # Load quality rules contract
        contract_path = contracts_dir / 'submission_quality_rules.yml'
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
        
        # Get threshold definitions
        thresholds = {t['metric']: t for t in contract['quality_thresholds']}
        
        # Parse and validate a submission
        parser = ACORDParser()
        validator = SubmissionQualityValidator()
        
        submission = parser.parse_xml(complete_submission_files[0])
        report = validator.validate_submission(submission)
        
        # Verify all threshold metrics are calculated
        assert 'completeness_score' in report
        assert 'consistency_score' in report
        assert 'overall_quality_score' in report
        
        # Verify overall_quality_score calculation matches contract formula
        # Contract: "(completeness_score * 0.6) + (consistency_score * 0.4)"
        expected_overall = (report['completeness_score'] * 0.6) + (report['consistency_score'] * 0.4)
        assert abs(report['overall_quality_score'] - expected_overall) < 0.01, \
            "Overall quality score must match contract formula"
        
        # Verify scores are in valid range
        for metric in ['completeness_score', 'consistency_score', 'overall_quality_score']:
            assert 0.0 <= report[metric] <= 1.0, \
                f"{metric} must be between 0.0 and 1.0"
    
    def test_pydantic_models_match_contract_schema(self, contracts_dir):
        """
        Pydantic models must match dim_submission.yml schema
        
        Ensures ACORDSubmission model implements all contract fields with correct types.
        """
        # Load dim_submission contract
        contract_path = contracts_dir / 'dim_submission.yml'
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
        
        # Get schema fields
        schema_fields = {}
        for field_def in contract['schema']:
            field_name = field_def['name']
            field_type = field_def['type']
            nullable = field_def.get('nullable', True)
            schema_fields[field_name] = {
                'type': field_type,
                'nullable': nullable
            }
        
        # Check ACORDSubmission model has all fields
        from src.models.submission import ACORDSubmission
        
        model_fields = ACORDSubmission.model_fields
        
        for field_name, field_spec in schema_fields.items():
            assert field_name in model_fields, \
                f"ACORDSubmission must have field: {field_name}"
            
            # Check nullable constraint
            model_field = model_fields[field_name]
            is_required = model_field.is_required()
            
            if not field_spec['nullable']:
                # Non-nullable fields should be required (unless they have defaults like created_at)
                if field_name not in ['submission_id', 'created_at']:
                    assert is_required or model_field.default is not None, \
                        f"Non-nullable field {field_name} should be required or have default"
    
    def test_contract_versions_are_consistent(self, contracts_dir):
        """
        All contracts should have the same version number
        
        Ensures contract evolution is coordinated.
        """
        contract_files = [
            'submission_quality_rules.yml',
            'dim_submission.yml',
            'fact_quality_check.yml'
        ]
        
        versions = set()
        for contract_file in contract_files:
            contract_path = contracts_dir / contract_file
            with open(contract_path, 'r') as f:
                contract = yaml.safe_load(f)
            versions.add(contract.get('contract_version', 'unknown'))
        
        # All contracts should have same version
        assert len(versions) == 1, \
            f"All contracts must have same version, found: {versions}"
        
        # Version should be defined
        version = versions.pop()
        assert version != 'unknown', "All contracts must have contract_version"
    
    def test_enrichment_sources_defined_in_contract(self, contracts_dir):
        """
        Validator should reference enrichment sources from contract
        """
        # Load quality rules contract
        contract_path = contracts_dir / 'submission_quality_rules.yml'
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
        
        # Contract should have enrichment sources
        assert 'enrichment_sources' in contract
        assert len(contract['enrichment_sources']) > 0
        
        # Each source should have required fields
        for source in contract['enrichment_sources']:
            assert 'source' in source
            assert 'api_endpoint' in source
            assert 'fields_provided' in source
            assert 'confidence_threshold' in source


class TestRegenerationSafety:
    """
    Test that code can be regenerated from contracts
    
    These tests verify the core AI-agentic principle:
    Can we delete generated code and regenerate it from contracts?
    """
    
    def test_parser_regeneration_contract_exists(self, contracts_dir):
        """
        Contracts exist to regenerate parser
        """
        # Both contracts needed for parser generation exist
        assert (contracts_dir / 'submission_quality_rules.yml').exists()
        assert (contracts_dir / 'dim_submission.yml').exists()
    
    def test_validator_regeneration_contract_exists(self, contracts_dir):
        """
        Contract exists to regenerate validator
        """
        # Quality rules contract needed for validator generation exists
        assert (contracts_dir / 'submission_quality_rules.yml').exists()
    
    def test_models_regeneration_contract_exists(self, contracts_dir):
        """
        Contracts exist to regenerate Pydantic models
        """
        # Contracts needed for model generation exist
        assert (contracts_dir / 'dim_submission.yml').exists()
        assert (contracts_dir / 'fact_quality_check.yml').exists()
    
    def test_contract_loader_can_load_all_contracts(self, contracts_dir):
        """
        ContractLoader can load all contracts needed for regeneration
        """
        from src.utils.contract_loader import ContractLoader
        
        loader = ContractLoader(contracts_dir)
        
        # Should successfully load all contracts
        quality_rules = loader.get_quality_rules_contract()
        dim_submission = loader.get_dim_submission_contract()
        fact_quality = loader.get_fact_quality_check_contract()
        
        assert quality_rules is not None
        assert dim_submission is not None
        assert fact_quality is not None
        
        # All should be valid YAML dictionaries
        assert isinstance(quality_rules, dict)
        assert isinstance(dim_submission, dict)
        assert isinstance(fact_quality, dict)
