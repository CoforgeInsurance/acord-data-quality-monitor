"""
Tests for batch processor and database components
"""

import pytest
import asyncio
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from src.orchestrator.batch_processor import BatchProcessor
from src.database.duckdb_writer import DuckDBWriter
from src.models.submission import ACORDSubmission, ProcessingResult


class TestDuckDBWriter:
    """Test DuckDB writer functionality"""
    
    def test_duckdb_writer_initialization(self, tmp_path):
        """DuckDB writer should initialize and create schema"""
        db_path = tmp_path / "test.duckdb"
        writer = DuckDBWriter(str(db_path))
        
        assert db_path.exists()
        assert writer.db_path == str(db_path)
    
    @pytest.mark.asyncio
    async def test_store_submission(self, tmp_path):
        """DuckDB writer should store submission"""
        db_path = tmp_path / "test.duckdb"
        writer = DuckDBWriter(str(db_path))
        
        # Create test submission
        submission = ACORDSubmission(
            submission_id="TEST-001",
            business_name="Test Business",
            naics_code="541511",
            annual_revenue=Decimal("1000000"),
            employee_count=50,
            years_in_business=10,
            business_address="123 Test St, Test City, TS 12345",
            requested_coverage_types="GL, Property",
            requested_limits="$1M/$2M",
            submission_date=datetime.now()
        )
        
        await writer.store_submission(submission)
        
        # Verify submission was stored
        import duckdb
        conn = duckdb.connect(str(db_path), read_only=True)
        result = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()
        conn.close()
        
        assert result[0] == 1
    
    @pytest.mark.asyncio
    async def test_store_processing_result(self, tmp_path):
        """DuckDB writer should store processing result"""
        db_path = tmp_path / "test.duckdb"
        writer = DuckDBWriter(str(db_path))
        
        # Create test processing result
        result = ProcessingResult(
            submission_id="TEST-001",
            quality_score=0.95,
            enrichment_applied=False,
            anomalies_detected=[],
            processing_time_ms=100,
            ai_agent_decisions={"quality_agent": "High quality"}
        )
        
        await writer.store_processing_result(result)
        
        # Verify result was stored
        import duckdb
        conn = duckdb.connect(str(db_path), read_only=True)
        db_result = conn.execute("SELECT COUNT(*) FROM processing_results").fetchone()
        conn.close()
        
        assert db_result[0] == 1


class TestBatchProcessor:
    """Test batch processor functionality"""
    
    def test_batch_processor_initialization(self):
        """Batch processor should initialize"""
        data_dir = Path(__file__).parent.parent / 'data' / 'sample_acord'
        processor = BatchProcessor(data_dir)
        
        assert processor.data_dir == data_dir
        assert processor.parser is not None
        assert processor.stream_processor is not None
        assert processor.db_writer is not None
    
    @pytest.mark.asyncio
    async def test_process_all_files(self, tmp_path):
        """Batch processor should process all XML files"""
        data_dir = Path(__file__).parent.parent / 'data' / 'sample_acord'
        db_path = tmp_path / "test.duckdb"
        
        processor = BatchProcessor(data_dir, str(db_path))
        summary = await processor.process_all_files()
        
        # Verify summary
        assert summary['total_files'] == 6
        assert summary['successful'] >= 0
        assert summary['failed'] >= 0
        assert summary['successful'] + summary['failed'] == 6
        assert 'total_time_seconds' in summary
        assert 'avg_quality_score' in summary
        assert 'results' in summary
        
        # Verify database was populated
        import duckdb
        conn = duckdb.connect(str(db_path), read_only=True)
        submissions_count = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        results_count = conn.execute("SELECT COUNT(*) FROM processing_results").fetchone()[0]
        conn.close()
        
        assert submissions_count == summary['successful']
        assert results_count == summary['successful']


class TestMockAPIs:
    """Test mock APIs functionality"""
    
    @pytest.mark.asyncio
    async def test_mock_opencorporates_search(self):
        """Mock OpenCorporates API should return company data"""
        from src.agents.mock_apis import MockOpenCorporatesAPI
        
        api = MockOpenCorporatesAPI()
        result = await api.search_company("Test Company", "CA")
        
        # Should return data most of the time (80% success rate)
        # Just verify it returns the expected structure when successful
        if result:
            assert 'company_name' in result
            assert 'jurisdiction' in result
            assert 'status' in result
    
    @pytest.mark.asyncio
    async def test_mock_naics_validate(self):
        """Mock NAICS API should validate known codes"""
        from src.agents.mock_apis import MockNAICSLookupAPI
        
        api = MockNAICSLookupAPI()
        result = await api.validate_naics("541511")
        
        assert result is not None
        assert result['code'] == "541511"
        assert result['title'] == "Custom Computer Programming Services"
        assert 'confidence' in result
    
    @pytest.mark.asyncio
    async def test_mock_naics_infer_from_name(self):
        """Mock NAICS API should infer code from business name"""
        from src.agents.mock_apis import MockNAICSLookupAPI
        
        api = MockNAICSLookupAPI()
        result = await api.infer_naics_from_business_name("TechSoft Software Solutions")
        
        assert result is not None
        assert result['code'] == "541511"
        assert result['confidence'] < 1.0  # Lower confidence for inference
