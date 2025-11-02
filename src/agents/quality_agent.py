"""
AI-GENERATED Quality Assessment Agent

Automatically assesses submission quality using rule-based and ML approaches.
Makes intelligent decisions about data quality and confidence scores.
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.models.submission import ACORDSubmission
from src.validators.quality_validator import SubmissionQualityValidator
from src.utils.contract_loader import ContractLoader


@dataclass
class QualityAssessmentResult:
    """Result of quality assessment"""
    submission_id: str
    quality_score: float
    completeness_score: float
    consistency_score: float
    agent_reasoning: str
    validation_details: Dict[str, Any]
    confidence: float


class QualityAgent:
    """
    AI Agent for intelligent quality assessment.
    
    AI-GENERATED from contracts/streaming_pipeline.yml
    Capabilities:
    - Field completeness scoring
    - Consistency validation
    - Business rule checking
    - Confidence estimation
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize quality assessment agent.
        
        Args:
            config_path: Path to contracts directory
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'contracts'
        
        self.contract_loader = ContractLoader(config_path)
        self.validator = SubmissionQualityValidator(config_path)
        self.contract = self.contract_loader.load_contract('streaming_pipeline.yml')
        
    async def assess_quality(self, submission: ACORDSubmission) -> QualityAssessmentResult:
        """
        Assess submission quality with AI reasoning.
        
        AI Decision Process:
        1. Run all quality validators
        2. Calculate weighted quality score
        3. Determine confidence in assessment
        4. Generate human-readable reasoning
        
        Args:
            submission: ACORDSubmission to assess
            
        Returns:
            QualityAssessmentResult with scores and reasoning
        """
        # Run comprehensive validation
        validation_result = self.validator.validate_submission(submission)
        
        # Extract scores
        quality_score = validation_result['overall_quality_score']
        completeness_score = validation_result['completeness_score']
        consistency_score = validation_result['consistency_score']
        
        # AI Decision: Calculate confidence based on data quality
        confidence = self._calculate_confidence(validation_result)
        
        # AI Decision: Generate reasoning
        reasoning = self._generate_reasoning(validation_result, submission)
        
        return QualityAssessmentResult(
            submission_id=submission.submission_id,
            quality_score=quality_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            agent_reasoning=reasoning,
            validation_details=validation_result,
            confidence=confidence
        )
    
    def _calculate_confidence(self, validation_result: Dict[str, Any]) -> float:
        """
        Calculate confidence in quality assessment.
        
        AI Decision Logic:
        - High confidence (>0.9): All checks passed, no warnings
        - Medium confidence (0.7-0.9): Minor warnings present
        - Low confidence (<0.7): Errors or inconsistencies detected
        """
        summary = validation_result['summary']
        
        # No errors = high confidence
        if summary['errors'] == 0 and summary['warnings'] == 0:
            return 0.95
        
        # Minor warnings = medium confidence
        if summary['errors'] == 0 and summary['warnings'] <= 2:
            return 0.85
        
        # Errors present = lower confidence based on severity
        error_ratio = summary['errors'] / summary['total_checks']
        return max(0.5, 1.0 - error_ratio)
    
    def _generate_reasoning(self, validation_result: Dict[str, Any], submission: ACORDSubmission) -> str:
        """
        Generate human-readable reasoning for quality assessment.
        
        AI Decision: Explain the quality score in business terms.
        """
        summary = validation_result['summary']
        quality_score = validation_result['overall_quality_score']
        
        # Build reasoning based on results
        reasoning_parts = []
        
        # Overall assessment
        if quality_score >= 0.9:
            reasoning_parts.append("High quality submission with excellent data completeness and consistency.")
        elif quality_score >= 0.7:
            reasoning_parts.append("Good quality submission with minor data quality issues.")
        else:
            reasoning_parts.append("Submission requires attention due to data quality concerns.")
        
        # Specific issues
        if summary['errors'] > 0:
            reasoning_parts.append(f"Found {summary['errors']} critical error(s) requiring resolution.")
        
        if summary['warnings'] > 0:
            reasoning_parts.append(f"Identified {summary['warnings']} warning(s) for review.")
        
        # Enrichment opportunity
        if validation_result['enrichment_suggestions']:
            reasoning_parts.append(f"Enrichment available from {len(validation_result['enrichment_suggestions'])} source(s).")
        
        return " ".join(reasoning_parts)
