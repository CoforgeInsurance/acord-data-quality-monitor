"""
AI-GENERATED Pydantic Models from YAML Contracts

This file is AUTO-GENERATED from contracts/dim_submission.yml
DO NOT EDIT MANUALLY - Regenerate using AI from contract specifications
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import re


class ACORDSubmission(BaseModel):
    """
    Pydantic model for ACORD submission data.
    
    AI-GENERATED from contracts/dim_submission.yml
    Represents a commercial insurance submission with quality validation.
    """
    
    submission_id: str = Field(
        ...,
        description="Unique identifier for submission",
        max_length=50
    )
    
    acord_submission_number: Optional[str] = Field(
        None,
        description="ACORD submission reference number",
        max_length=50
    )
    
    business_name: str = Field(
        ...,
        description="Legal business name",
        min_length=3,
        max_length=200
    )
    
    naics_code: str = Field(
        ...,
        description="6-digit NAICS industry classification code",
        max_length=10
    )
    
    annual_revenue: Decimal = Field(
        ...,
        description="Annual revenue in USD",
        ge=10000,
        le=1000000000
    )
    
    employee_count: int = Field(
        ...,
        description="Total number of employees",
        ge=1,
        le=100000
    )
    
    years_in_business: int = Field(
        ...,
        description="Number of years in operation",
        ge=0,
        le=200
    )
    
    business_address: str = Field(
        ...,
        description="Primary business address",
        max_length=500
    )
    
    requested_coverage_types: str = Field(
        ...,
        description="Types of coverage requested (GL, Property, Auto, etc.)",
        max_length=200
    )
    
    requested_limits: str = Field(
        ...,
        description="Coverage limits requested",
        max_length=200
    )
    
    submission_date: datetime = Field(
        ...,
        description="When submission was received"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="ETL timestamp"
    )
    
    @field_validator('naics_code')
    @classmethod
    def validate_naics_code(cls, v: str) -> str:
        """Validate NAICS code format (6 digits)"""
        if not re.match(r'^\d{6}$', v):
            raise ValueError(f"NAICS code must be 6 digits, got: {v}")
        return v
    
    @field_validator('business_name')
    @classmethod
    def validate_business_name(cls, v: str) -> str:
        """Validate business name is not empty after stripping whitespace"""
        if not v.strip():
            raise ValueError("Business name cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic model configuration"""
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True


class QualityCheckResult(BaseModel):
    """
    Pydantic model for quality check results.
    
    AI-GENERATED from contracts/fact_quality_check.yml
    Represents validation results for a single quality rule.
    """
    
    quality_check_id: str = Field(
        ...,
        description="Unique identifier for quality check",
        max_length=50
    )
    
    submission_id: str = Field(
        ...,
        description="Reference to submission dimension",
        max_length=50
    )
    
    rule_id: str = Field(
        ...,
        description="Quality rule identifier (e.g., CONS-001)",
        max_length=50
    )
    
    rule_name: str = Field(
        ...,
        description="Human-readable rule name",
        max_length=200
    )
    
    rule_category: str = Field(
        ...,
        description="Category: required_field, consistency_check, threshold",
        max_length=50
    )
    
    severity: str = Field(
        ...,
        description="error, warning, info",
        max_length=20
    )
    
    passed: bool = Field(
        ...,
        description="Did the validation pass?"
    )
    
    expected_value: Optional[str] = Field(
        None,
        description="Expected value or range",
        max_length=500
    )
    
    actual_value: Optional[str] = Field(
        None,
        description="Actual value found",
        max_length=500
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Detailed error message if failed"
    )
    
    field_name: Optional[str] = Field(
        None,
        description="Field name that was validated",
        max_length=100
    )
    
    check_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When validation was performed"
    )
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity is one of allowed values"""
        allowed = ['error', 'warning', 'info']
        if v.lower() not in allowed:
            raise ValueError(f"Severity must be one of {allowed}, got: {v}")
        return v.lower()
    
    @field_validator('rule_category')
    @classmethod
    def validate_rule_category(cls, v: str) -> str:
        """Validate rule category is one of allowed values"""
        allowed = ['required_field', 'consistency_check', 'threshold']
        if v.lower() not in allowed:
            raise ValueError(f"Rule category must be one of {allowed}, got: {v}")
        return v.lower()
    
    class Config:
        """Pydantic model configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True


class ProcessingResult(BaseModel):
    """
    Result of AI-powered submission processing.
    
    AI-GENERATED from contracts/streaming_pipeline.yml
    Represents the output of the real-time processing pipeline.
    """
    
    submission_id: str = Field(
        ...,
        description="Unique identifier for submission"
    )
    
    quality_score: float = Field(
        ...,
        description="Overall quality score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    enrichment_applied: bool = Field(
        default=False,
        description="Whether data enrichment was applied"
    )
    
    anomalies_detected: List[str] = Field(
        default_factory=list,
        description="List of detected anomaly types"
    )
    
    processing_time_ms: int = Field(
        ...,
        description="Processing time in milliseconds",
        ge=0
    )
    
    ai_agent_decisions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Decisions made by AI agents during processing"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When processing was completed"
    )
    
    class Config:
        """Pydantic model configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnomalyResult(BaseModel):
    """
    Result of anomaly detection.
    
    AI-GENERATED from contracts/ai_agent_configs.yml
    """
    
    submission_id: str = Field(
        ...,
        description="Submission identifier"
    )
    
    anomaly_type: str = Field(
        ...,
        description="Type of anomaly detected"
    )
    
    confidence_score: float = Field(
        ...,
        description="Confidence in anomaly detection (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    severity: str = Field(
        ...,
        description="Severity level: low, medium, high, critical"
    )
    
    explanation: str = Field(
        ...,
        description="Human-readable explanation of the anomaly"
    )
    
    recommended_action: str = Field(
        ...,
        description="Recommended action to address the anomaly"
    )
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity is one of allowed values"""
        allowed = ['low', 'medium', 'high', 'critical']
        if v.lower() not in allowed:
            raise ValueError(f"Severity must be one of {allowed}, got: {v}")
        return v.lower()


class EnrichmentDecision(BaseModel):
    """
    AI agent decision about data enrichment.
    
    AI-GENERATED from contracts/ai_agent_configs.yml
    """
    
    field_name: str = Field(
        ...,
        description="Field to be enriched"
    )
    
    api_source: str = Field(
        ...,
        description="API source for enrichment"
    )
    
    confidence_score: float = Field(
        ...,
        description="Confidence in enrichment (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    cost_estimate: float = Field(
        ...,
        description="Estimated cost of API call",
        ge=0.0
    )
    
    reasoning: str = Field(
        ...,
        description="Explanation of why this enrichment is recommended"
    )
    
    enriched_value: Optional[Any] = Field(
        None,
        description="The enriched value (set after API call)"
    )
