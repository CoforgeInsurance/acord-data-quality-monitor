"""
AI-GENERATED Quality Validator from YAML Contracts

This file is AUTO-GENERATED from contracts/submission_quality_rules.yml
DO NOT EDIT MANUALLY - Regenerate using AI from contract specifications
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from decimal import Decimal
import re
import uuid
from datetime import datetime

from src.models.submission import ACORDSubmission, QualityCheckResult
from src.utils.contract_loader import ContractLoader


class Severity(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    rule_id: str
    rule_name: str
    passed: bool
    severity: Severity
    error_message: Optional[str]
    field_name: Optional[str]
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    
    def to_quality_check_result(self, submission_id: str, rule_category: str) -> QualityCheckResult:
        """Convert to QualityCheckResult Pydantic model"""
        return QualityCheckResult(
            quality_check_id=str(uuid.uuid4()),
            submission_id=submission_id,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            rule_category=rule_category,
            severity=self.severity.value,
            passed=self.passed,
            expected_value=self.expected_value,
            actual_value=self.actual_value,
            error_message=self.error_message,
            field_name=self.field_name,
            check_timestamp=datetime.now()
        )


class SubmissionQualityValidator:
    """
    Validate ACORD submissions against quality rules contract.
    
    AI-GENERATED from contracts/submission_quality_rules.yml
    Implements all required_fields and consistency_checks from contract.
    """
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """
        Initialize validator with quality rules contract.
        
        Args:
            contracts_dir: Path to contracts directory
        """
        self.contract_loader = ContractLoader(contracts_dir)
        self.quality_rules = self.contract_loader.get_quality_rules_contract()
    
    def validate_submission(self, submission: ACORDSubmission) -> Dict[str, Any]:
        """
        Run all quality checks and return comprehensive report.
        
        Args:
            submission: ACORDSubmission to validate
        
        Returns:
            Dictionary with:
            - completeness_score: float (0.0 to 1.0)
            - consistency_score: float (0.0 to 1.0)
            - overall_quality_score: float (0.0 to 1.0)
            - validation_results: List[ValidationResult]
            - enrichment_suggestions: List[Dict]
            - summary: Dict with counts and metrics
        """
        # Run required fields validation
        required_results = self.validate_required_fields(submission)
        
        # Run consistency checks
        consistency_results = self.validate_consistency(submission)
        
        # Combine all results
        all_results = required_results + consistency_results
        
        # Calculate metrics
        total_checks = len(all_results)
        passed_checks = sum(1 for r in all_results if r.passed)
        
        # Calculate completeness score (required fields)
        total_required = len(required_results)
        passed_required = sum(1 for r in required_results if r.passed)
        completeness_score = passed_required / total_required if total_required > 0 else 1.0
        
        # Calculate consistency score (consistency checks)
        total_consistency = len(consistency_results)
        passed_consistency = sum(1 for r in consistency_results if r.passed)
        consistency_score = passed_consistency / total_consistency if total_consistency > 0 else 1.0
        
        # Calculate overall quality score (weighted average from contract)
        # From contract: (completeness_score * 0.6) + (consistency_score * 0.4)
        overall_quality_score = (completeness_score * 0.6) + (consistency_score * 0.4)
        
        # Get enrichment suggestions for failed validations
        enrichment_suggestions = self._get_enrichment_suggestions(all_results)
        
        # Build summary
        summary = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'errors': sum(1 for r in all_results if not r.passed and r.severity == Severity.ERROR),
            'warnings': sum(1 for r in all_results if not r.passed and r.severity == Severity.WARNING),
        }
        
        return {
            'completeness_score': round(completeness_score, 2),
            'consistency_score': round(consistency_score, 2),
            'overall_quality_score': round(overall_quality_score, 2),
            'validation_results': all_results,
            'enrichment_suggestions': enrichment_suggestions,
            'summary': summary
        }
    
    def validate_required_fields(self, submission: ACORDSubmission) -> List[ValidationResult]:
        """
        Check all required fields from contract.
        
        AI-GENERATED from submission_quality_rules.yml required_fields section.
        
        Args:
            submission: ACORDSubmission to validate
        
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        # Get required fields from contract
        required_fields = self.quality_rules.get('required_fields', {})
        
        # Validate basic_info fields
        basic_info = required_fields.get('basic_info', [])
        
        for field_def in basic_info:
            field_name = field_def['field']
            
            # Get actual value from submission
            actual_value = getattr(submission, field_name, None)
            
            # Check if field is null
            if field_def.get('nullable', True) == False and actual_value is None:
                results.append(ValidationResult(
                    rule_id=f"REQ-{field_name.upper()}",
                    rule_name=f"Required Field: {field_def.get('description', field_name)}",
                    passed=False,
                    severity=Severity.ERROR,
                    error_message=f"{field_name} is required but missing",
                    field_name=field_name,
                    expected_value="Not null",
                    actual_value="null"
                ))
                continue
            
            # Skip further validation if field is None and nullable
            if actual_value is None:
                continue
            
            # Validate pattern (e.g., NAICS code)
            if 'pattern' in field_def:
                pattern = field_def['pattern']
                if not re.match(pattern, str(actual_value)):
                    results.append(ValidationResult(
                        rule_id=f"REQ-{field_name.upper()}-PATTERN",
                        rule_name=f"Pattern Validation: {field_name}",
                        passed=False,
                        severity=Severity.ERROR,
                        error_message=f"{field_name} does not match required pattern {pattern}",
                        field_name=field_name,
                        expected_value=f"Pattern: {pattern}",
                        actual_value=str(actual_value)
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id=f"REQ-{field_name.upper()}-PATTERN",
                        rule_name=f"Pattern Validation: {field_name}",
                        passed=True,
                        severity=Severity.INFO,
                        error_message=None,
                        field_name=field_name
                    ))
            
            # Validate min/max length
            if 'min_length' in field_def or 'max_length' in field_def:
                actual_len = len(str(actual_value))
                min_len = field_def.get('min_length', 0)
                max_len = field_def.get('max_length', float('inf'))
                
                if actual_len < min_len or actual_len > max_len:
                    results.append(ValidationResult(
                        rule_id=f"REQ-{field_name.upper()}-LENGTH",
                        rule_name=f"Length Validation: {field_name}",
                        passed=False,
                        severity=Severity.ERROR,
                        error_message=f"{field_name} length {actual_len} not in range [{min_len}, {max_len}]",
                        field_name=field_name,
                        expected_value=f"Length in [{min_len}, {max_len}]",
                        actual_value=f"Length: {actual_len}"
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id=f"REQ-{field_name.upper()}-LENGTH",
                        rule_name=f"Length Validation: {field_name}",
                        passed=True,
                        severity=Severity.INFO,
                        error_message=None,
                        field_name=field_name
                    ))
            
            # Validate range (for numeric fields)
            if 'range' in field_def:
                min_val, max_val = field_def['range']
                numeric_val = float(actual_value)
                
                if numeric_val < min_val or numeric_val > max_val:
                    results.append(ValidationResult(
                        rule_id=f"REQ-{field_name.upper()}-RANGE",
                        rule_name=f"Range Validation: {field_name}",
                        passed=False,
                        severity=Severity.ERROR,
                        error_message=f"{field_name} value {numeric_val} not in range [{min_val}, {max_val}]",
                        field_name=field_name,
                        expected_value=f"[{min_val}, {max_val}]",
                        actual_value=str(numeric_val)
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id=f"REQ-{field_name.upper()}-RANGE",
                        rule_name=f"Range Validation: {field_name}",
                        passed=True,
                        severity=Severity.INFO,
                        error_message=None,
                        field_name=field_name
                    ))
        
        # Validate coverage_info fields
        coverage_info = required_fields.get('coverage_info', [])
        
        for field_def in coverage_info:
            field_name = field_def['field']
            actual_value = getattr(submission, field_name, None)
            
            if field_def.get('nullable', True) == False and actual_value is None:
                results.append(ValidationResult(
                    rule_id=f"REQ-{field_name.upper()}",
                    rule_name=f"Required Field: {field_def.get('description', field_name)}",
                    passed=False,
                    severity=Severity.ERROR,
                    error_message=f"{field_name} is required but missing",
                    field_name=field_name,
                    expected_value="Not null",
                    actual_value="null"
                ))
            else:
                results.append(ValidationResult(
                    rule_id=f"REQ-{field_name.upper()}",
                    rule_name=f"Required Field: {field_def.get('description', field_name)}",
                    passed=True,
                    severity=Severity.INFO,
                    error_message=None,
                    field_name=field_name
                ))
        
        return results
    
    def validate_consistency(self, submission: ACORDSubmission) -> List[ValidationResult]:
        """
        Run all consistency checks from contract.
        
        AI-GENERATED from submission_quality_rules.yml consistency_checks section.
        
        Args:
            submission: ACORDSubmission to validate
        
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        # Get consistency checks from contract
        consistency_checks = self.quality_rules.get('consistency_checks', [])
        
        for check in consistency_checks:
            rule_id = check['rule_id']
            rule_name = check['name']
            severity_str = check['severity']
            severity = Severity.WARNING if severity_str == 'warning' else Severity.ERROR
            
            # CONS-001: Revenue vs. Employee Consistency
            if rule_id == 'CONS-001':
                passed = self._check_revenue_employee_consistency(submission)
                error_msg = None if passed else check['error_message'].replace(
                    '${annual_revenue}', str(submission.annual_revenue)
                ).replace(
                    '${employee_count}', str(submission.employee_count)
                )
                
                results.append(ValidationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    passed=passed,
                    severity=severity,
                    error_message=error_msg,
                    field_name='annual_revenue, employee_count',
                    expected_value='Revenue proportional to employees',
                    actual_value=f"Revenue: {submission.annual_revenue}, Employees: {submission.employee_count}"
                ))
            
            # CONS-002: Years in Business vs. Revenue
            elif rule_id == 'CONS-002':
                passed = self._check_years_revenue_consistency(submission)
                error_msg = None if passed else check['error_message'].replace(
                    '${years_in_business}', str(submission.years_in_business)
                ).replace(
                    '${annual_revenue}', str(submission.annual_revenue)
                )
                
                results.append(ValidationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    passed=passed,
                    severity=severity,
                    error_message=error_msg,
                    field_name='years_in_business, annual_revenue',
                    expected_value='New businesses (<2 years) should have revenue <$5M',
                    actual_value=f"Years: {submission.years_in_business}, Revenue: {submission.annual_revenue}"
                ))
            
            # CONS-003: NAICS Code Industry Match
            elif rule_id == 'CONS-003':
                passed = self._check_naics_validity(submission)
                error_msg = None if passed else check['error_message'].replace(
                    '${naics_code}', submission.naics_code
                )
                
                results.append(ValidationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    passed=passed,
                    severity=severity,
                    error_message=error_msg,
                    field_name='naics_code',
                    expected_value='Valid 6-digit NAICS code',
                    actual_value=submission.naics_code
                ))
        
        return results
    
    def _check_revenue_employee_consistency(self, submission: ACORDSubmission) -> bool:
        """
        Check if revenue is proportional to employee count.
        
        From contract logic:
        IF employee_count < 5 THEN annual_revenue < 1000000
        IF employee_count BETWEEN 5 AND 50 THEN annual_revenue BETWEEN 500000 AND 50000000
        IF employee_count > 100 THEN annual_revenue > 5000000
        """
        revenue = float(submission.annual_revenue)
        employees = submission.employee_count
        
        if employees < 5:
            return revenue < 1000000
        elif 5 <= employees <= 50:
            return 500000 <= revenue <= 50000000
        elif employees > 100:
            return revenue > 5000000
        
        # For employees between 50 and 100, we don't have specific rules, so pass
        return True
    
    def _check_years_revenue_consistency(self, submission: ACORDSubmission) -> bool:
        """
        Check if new businesses have reasonable revenue.
        
        From contract logic:
        IF years_in_business < 2 THEN annual_revenue < 5000000
        """
        if submission.years_in_business < 2:
            return float(submission.annual_revenue) < 5000000
        return True
    
    def _check_naics_validity(self, submission: ACORDSubmission) -> bool:
        """
        Validate NAICS code format (basic check).
        More sophisticated validation would check against reference table.
        """
        # Basic format check (6 digits)
        return re.match(r'^\d{6}$', submission.naics_code) is not None
    
    def _get_enrichment_suggestions(self, validation_results: List[ValidationResult]) -> List[Dict[str, Any]]:
        """
        Get enrichment suggestions for failed validations.
        
        Based on enrichment_sources from contract.
        """
        suggestions = []
        
        # Get enrichment sources from contract
        enrichment_sources = self.quality_rules.get('enrichment_sources', [])
        
        # Check which fields failed and suggest enrichment
        failed_fields = set()
        for result in validation_results:
            if not result.passed and result.field_name:
                failed_fields.add(result.field_name)
        
        for source in enrichment_sources:
            source_name = source['source']
            fields_provided = source['fields_provided']
            
            # Check if this source can help with any failed fields
            relevant_fields = [f for f in fields_provided if f in failed_fields]
            
            if relevant_fields:
                suggestions.append({
                    'source': source_name,
                    'api_endpoint': source['api_endpoint'],
                    'fields_provided': relevant_fields,
                    'cost': source['cost'],
                    'confidence_threshold': source['confidence_threshold']
                })
        
        return suggestions
