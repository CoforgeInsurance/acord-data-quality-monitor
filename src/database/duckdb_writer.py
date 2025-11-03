"""
DuckDB Writer for storing submissions and processing results.
"""

import duckdb
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.models.submission import ACORDSubmission, ProcessingResult


class DuckDBWriter:
    """Write submissions and results to DuckDB for dashboard visualization"""
    
    def __init__(self, db_path: str):
        """
        Initialize DuckDB connection.
        
        Args:
            db_path: Path to DuckDB database file
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if they don't exist"""
        with duckdb.connect(self.db_path) as conn:
            # Submissions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    submission_id VARCHAR PRIMARY KEY,
                    business_name VARCHAR,
                    naics_code VARCHAR,
                    annual_revenue DECIMAL(15,2),
                    employee_count INTEGER,
                    years_in_business INTEGER,
                    business_address VARCHAR,
                    requested_coverage_types VARCHAR,
                    requested_limits VARCHAR,
                    submission_date TIMESTAMP,
                    created_at TIMESTAMP
                )
            """)
            
            # Processing results table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_results (
                    submission_id VARCHAR,
                    quality_score DOUBLE,
                    completeness_score DOUBLE,
                    consistency_score DOUBLE,
                    enrichment_applied BOOLEAN,
                    anomalies_detected VARCHAR,
                    processing_time_ms INTEGER,
                    agent_decisions VARCHAR,
                    processed_at TIMESTAMP,
                    PRIMARY KEY (submission_id, processed_at)
                )
            """)
            
            # Anomalies table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY,
                    submission_id VARCHAR,
                    anomaly_type VARCHAR,
                    confidence_score DOUBLE,
                    severity VARCHAR,
                    explanation VARCHAR,
                    detected_at TIMESTAMP
                )
            """)
    
    async def store_submission(self, submission: ACORDSubmission):
        """Store submission in database"""
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO submissions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                submission.submission_id,
                submission.business_name,
                submission.naics_code,
                float(submission.annual_revenue),
                submission.employee_count,
                submission.years_in_business,
                submission.business_address,
                submission.requested_coverage_types,
                submission.requested_limits,
                submission.submission_date,
                submission.created_at
            ])
    
    async def store_processing_result(self, result: ProcessingResult):
        """Store processing result in database"""
        import json
        
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO processing_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                result.submission_id,
                result.quality_score,
                result.quality_score,  # completeness_score (simplified)
                result.quality_score,  # consistency_score (simplified)
                result.enrichment_applied,
                json.dumps(result.anomalies_detected),
                result.processing_time_ms,
                json.dumps(result.ai_agent_decisions),
                datetime.now()
            ])
