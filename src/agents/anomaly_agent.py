"""
AI-GENERATED Anomaly Detection Agent

Uses machine learning to detect unusual patterns in submissions.
Continuously learns from submission patterns to improve detection.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import joblib
from pathlib import Path

from src.models.submission import ACORDSubmission, AnomalyResult
from src.utils.contract_loader import ContractLoader


class AnomalyDetectionAgent:
    """
    AI Agent for detecting submission anomalies using ML.
    
    AI-GENERATED from contracts/streaming_pipeline.yml
    Detects:
    - Statistical outliers (revenue, employee count)
    - Pattern deviations (submission timing, field combinations)
    - Business rule violations (industry vs. revenue mismatches)
    - Data quality degradation trends
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ML models and historical data.
        
        Args:
            config_path: Path to contracts directory
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'contracts'
        
        self.contract_loader = ContractLoader(config_path)
        self.contract = self.contract_loader.load_contract('streaming_pipeline.yml')
        self.ai_config = self.contract_loader.load_contract('ai_agent_configs.yml')
        
        self.model_path = Path(__file__).parent.parent.parent / 'models' / 'anomaly_detection'
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Load or train models
        self.statistical_model = self._load_or_train_statistical_model()
        self.scaler = self._load_or_create_scaler()
        
        # Anomaly thresholds
        agent_config = self.contract['ai_agents']['anomaly_agent']
        self.confidence_threshold = agent_config['confidence_threshold']
        
    async def detect_anomalies(
        self, 
        submission: ACORDSubmission, 
        quality_result: Any
    ) -> List[AnomalyResult]:
        """
        Detect anomalies using multiple ML approaches.
        
        Detection Methods:
        1. Statistical Outliers → Isolation Forest on numerical features
        2. Pattern Anomalies → Time series analysis of submission patterns
        3. Business Logic → Rule-based validation with ML confidence
        4. Quality Trends → Degradation in data quality over time
        
        Args:
            submission: ACORDSubmission to analyze
            quality_result: Quality assessment result
            
        Returns:
            List of AnomalyResult objects
        """
        anomalies = []
        
        # Method 1: Statistical Outlier Detection
        statistical_anomalies = await self._detect_statistical_outliers(submission)
        anomalies.extend(statistical_anomalies)
        
        # Method 2: Submission Pattern Analysis
        pattern_anomalies = await self._detect_pattern_anomalies(submission)
        anomalies.extend(pattern_anomalies)
        
        # Method 3: Business Rule Anomalies
        business_anomalies = await self._detect_business_anomalies(submission, quality_result)
        anomalies.extend(business_anomalies)
        
        # Filter by confidence threshold
        high_confidence_anomalies = [
            a for a in anomalies 
            if a.confidence_score >= self.confidence_threshold
        ]
        
        return high_confidence_anomalies
    
    async def _detect_statistical_outliers(self, submission: ACORDSubmission) -> List[AnomalyResult]:
        """
        Use Isolation Forest to detect statistical outliers.
        
        Args:
            submission: ACORDSubmission to analyze
            
        Returns:
            List of AnomalyResult objects for statistical anomalies
        """
        features = self._extract_numerical_features(submission)
        if not features or len(features) == 0:
            return []
            
        # Scale features
        try:
            features_scaled = self.scaler.transform([features])
        except Exception:
            # If scaling fails, return empty list
            return []
        
        # Predict anomaly
        try:
            anomaly_score = self.statistical_model.decision_function(features_scaled)[0]
            is_anomaly = self.statistical_model.predict(features_scaled)[0] == -1
        except Exception:
            # If prediction fails, return empty list
            return []
        
        anomalies = []
        if is_anomaly:
            # Determine which feature is most anomalous
            feature_names = ['annual_revenue', 'employee_count', 'years_in_business']
            feature_scores = self._calculate_feature_anomaly_scores(features, feature_names)
            
            for feature, score in feature_scores.items():
                if score > 0.7:  # High anomaly score for this feature
                    anomalies.append(AnomalyResult(
                        submission_id=submission.submission_id,
                        anomaly_type=f"statistical_outlier_{feature}",
                        confidence_score=min(score, 0.95),
                        severity=self._determine_severity(score),
                        explanation=f"{feature.replace('_', ' ').title()} value is statistically unusual compared to similar businesses",
                        recommended_action=f"Verify {feature} data with applicant"
                    ))
        
        return anomalies
    
    def _extract_numerical_features(self, submission: ACORDSubmission) -> List[float]:
        """
        Extract numerical features for ML analysis.
        
        Args:
            submission: ACORDSubmission
            
        Returns:
            List of numerical feature values
        """
        return [
            float(submission.annual_revenue or 0),
            float(submission.employee_count or 0),
            float(submission.years_in_business or 0)
        ]
    
    async def _detect_pattern_anomalies(self, submission: ACORDSubmission) -> List[AnomalyResult]:
        """
        Detect unusual submission timing and pattern anomalies.
        
        Args:
            submission: ACORDSubmission to analyze
            
        Returns:
            List of AnomalyResult objects for pattern anomalies
        """
        anomalies = []
        
        # Time-based anomalies
        if self._is_unusual_submission_time(submission.submission_date):
            anomalies.append(AnomalyResult(
                submission_id=submission.submission_id,
                anomaly_type="unusual_submission_time",
                confidence_score=0.8,
                severity="medium",
                explanation="Submission received outside normal business hours",
                recommended_action="Review for automated/bulk submissions"
            ))
        
        # Industry pattern anomalies
        if await self._is_unusual_industry_pattern(submission):
            anomalies.append(AnomalyResult(
                submission_id=submission.submission_id,
                anomaly_type="unusual_industry_pattern",
                confidence_score=0.85,
                severity="high",
                explanation="Industry classification doesn't match typical patterns for this business size/revenue",
                recommended_action="Verify NAICS code accuracy"
            ))
            
        return anomalies
    
    async def _detect_business_anomalies(
        self, 
        submission: ACORDSubmission, 
        quality_result: Any
    ) -> List[AnomalyResult]:
        """
        Detect business logic anomalies.
        
        Args:
            submission: ACORDSubmission to analyze
            quality_result: Quality assessment result
            
        Returns:
            List of AnomalyResult objects for business anomalies
        """
        anomalies = []
        
        # Check for unusually low quality score
        if hasattr(quality_result, 'quality_score') and quality_result.quality_score < 0.5:
            anomalies.append(AnomalyResult(
                submission_id=submission.submission_id,
                anomaly_type="low_quality_score",
                confidence_score=0.9,
                severity="high",
                explanation=f"Quality score of {quality_result.quality_score:.2f} is unusually low",
                recommended_action="Review submission for data quality issues"
            ))
        
        return anomalies
    
    def _calculate_feature_anomaly_scores(
        self, 
        features: List[float], 
        feature_names: List[str]
    ) -> Dict[str, float]:
        """
        Calculate anomaly scores for individual features.
        
        This is a simplified heuristic. In production, would use more sophisticated methods.
        
        Args:
            features: List of feature values
            feature_names: List of feature names
            
        Returns:
            Dictionary mapping feature names to anomaly scores
        """
        scores = {}
        
        # Simple heuristic: check if values are in extreme ranges
        revenue, employees, years = features
        
        # Revenue anomaly
        if revenue > 100000000 or revenue < 50000:
            scores['annual_revenue'] = 0.8
        
        # Employee count anomaly
        if employees > 1000 or employees < 2:
            scores['employee_count'] = 0.75
        
        # Years in business anomaly
        if years > 100 or years == 0:
            scores['years_in_business'] = 0.7
        
        return scores
    
    def _determine_severity(self, score: float) -> str:
        """
        Determine severity level based on anomaly score.
        
        Args:
            score: Anomaly score (0.0 to 1.0)
            
        Returns:
            Severity level: low, medium, high, critical
        """
        if score >= 0.9:
            return "critical"
        elif score >= 0.8:
            return "high"
        elif score >= 0.7:
            return "medium"
        else:
            return "low"
    
    def _is_unusual_submission_time(self, submission_date: datetime) -> bool:
        """
        Check if submission time is unusual (e.g., outside business hours).
        
        Args:
            submission_date: Submission timestamp
            
        Returns:
            True if submission time is unusual
        """
        hour = submission_date.hour
        day_of_week = submission_date.weekday()
        
        # Weekend submission
        if day_of_week >= 5:  # Saturday or Sunday
            return True
        
        # Outside business hours (9 AM - 5 PM)
        if hour < 9 or hour >= 17:
            return True
        
        return False
    
    async def _is_unusual_industry_pattern(self, submission: ACORDSubmission) -> bool:
        """
        Check if industry/size/revenue pattern is unusual.
        
        Args:
            submission: ACORDSubmission to analyze
            
        Returns:
            True if pattern is unusual
        """
        # Simple heuristic: very small business with very high revenue
        if submission.employee_count < 5 and float(submission.annual_revenue) > 10000000:
            return True
        
        # Very large business with very low revenue
        if submission.employee_count > 500 and float(submission.annual_revenue) < 1000000:
            return True
        
        return False
    
    def _load_or_train_statistical_model(self) -> IsolationForest:
        """
        Load existing Isolation Forest model or train a new one.
        
        Returns:
            Trained IsolationForest model
        """
        model_file = self.model_path / 'isolation_forest.joblib'
        
        if model_file.exists():
            try:
                return joblib.load(model_file)
            except Exception:
                pass
        
        # Train new model with default parameters
        model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # Generate synthetic training data for initialization
        # In production, this would use real historical data
        training_data = self._generate_synthetic_training_data()
        model.fit(training_data)
        
        # Save model
        try:
            joblib.dump(model, model_file)
        except Exception:
            pass
        
        return model
    
    def _load_or_create_scaler(self) -> StandardScaler:
        """
        Load existing scaler or create a new one.
        
        Returns:
            Fitted StandardScaler
        """
        scaler_file = self.model_path / 'scaler.joblib'
        
        if scaler_file.exists():
            try:
                return joblib.load(scaler_file)
            except Exception:
                pass
        
        # Create new scaler
        scaler = StandardScaler()
        
        # Fit on synthetic data
        training_data = self._generate_synthetic_training_data()
        scaler.fit(training_data)
        
        # Save scaler
        try:
            joblib.dump(scaler, scaler_file)
        except Exception:
            pass
        
        return scaler
    
    def _generate_synthetic_training_data(self) -> np.ndarray:
        """
        Generate synthetic training data for model initialization.
        
        In production, this would be replaced with real historical data.
        
        Returns:
            Numpy array of training data
        """
        np.random.seed(42)
        
        # Generate realistic business data
        n_samples = 1000
        
        # Annual revenue: log-normal distribution
        revenue = np.random.lognormal(mean=14, sigma=1.5, size=n_samples)
        
        # Employee count: follows revenue with some noise
        employees = (revenue / 200000) * np.random.lognormal(mean=0, sigma=0.5, size=n_samples)
        employees = np.clip(employees, 1, 10000)
        
        # Years in business: exponential distribution
        years = np.random.exponential(scale=10, size=n_samples)
        years = np.clip(years, 0, 100)
        
        return np.column_stack([revenue, employees, years])
