"""
Batch Processing Orchestrator

Processes ACORD XML files through the AI-powered pipeline.
Perfect for demo scenarios with small datasets.
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

from src.parsers.acord_parser import ACORDParser
from src.streaming.submission_stream_processor import SubmissionStreamProcessor
from src.database.duckdb_writer import DuckDBWriter

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Process batch of ACORD XML files through AI agent pipeline.
    
    Perfect for demo scenarios where we want to process all
    sample files and populate the database for dashboard visualization.
    """
    
    def __init__(self, 
                 data_dir: Path,
                 db_path: str = "dbt_project/target/acord_dqm.duckdb"):
        """
        Initialize batch processor.
        
        Args:
            data_dir: Directory containing ACORD XML files
            db_path: Path to DuckDB database
        """
        self.data_dir = data_dir
        self.parser = ACORDParser()
        self.stream_processor = SubmissionStreamProcessor()
        self.db_writer = DuckDBWriter(db_path)
        
    async def process_all_files(self) -> Dict[str, Any]:
        """
        Process all XML files in data directory.
        
        Returns:
            Summary statistics and results
        """
        xml_files = list(self.data_dir.glob("*.xml"))
        logger.info(f"Found {len(xml_files)} XML files to process")
        
        results = []
        start_time = datetime.now()
        
        for xml_file in xml_files:
            try:
                # Parse XML
                submission = self.parser.parse_xml(xml_file)
                logger.info(f"Parsed: {xml_file.name}")
                
                # Process through AI agents
                processing_result = await self.stream_processor.process_submission_stream(submission)
                
                # Store in database
                await self.db_writer.store_submission(submission)
                await self.db_writer.store_processing_result(processing_result)
                
                results.append({
                    'file': xml_file.name,
                    'submission_id': submission.submission_id,
                    'quality_score': processing_result.quality_score,
                    'enriched': processing_result.enrichment_applied,
                    'anomalies': len(processing_result.anomalies_detected),
                    'processing_time_ms': processing_result.processing_time_ms
                })
                
                logger.info(
                    f"✓ {xml_file.name}: quality={processing_result.quality_score:.2f}, "
                    f"enriched={processing_result.enrichment_applied}, "
                    f"anomalies={len(processing_result.anomalies_detected)}"
                )
                
            except Exception as e:
                logger.error(f"✗ {xml_file.name}: {str(e)}")
                results.append({
                    'file': xml_file.name,
                    'error': str(e)
                })
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        successful_results = [r for r in results if 'error' not in r]
        avg_quality = sum(r.get('quality_score', 0) for r in successful_results) / len(successful_results) if successful_results else 0
        
        return {
            'total_files': len(xml_files),
            'successful': len(successful_results),
            'failed': len([r for r in results if 'error' in r]),
            'total_time_seconds': total_time,
            'avg_quality_score': avg_quality,
            'results': results
        }


async def main():
    """Main entry point for batch processing"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Process all sample files
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'sample_acord'
    processor = BatchProcessor(data_dir)
    
    print("\n🚀 Starting batch processing of ACORD submissions...\n")
    summary = await processor.process_all_files()
    
    print("\n" + "="*60)
    print("📊 BATCH PROCESSING SUMMARY")
    print("="*60)
    print(f"Total Files:        {summary['total_files']}")
    print(f"Successful:         {summary['successful']}")
    print(f"Failed:             {summary['failed']}")
    print(f"Avg Quality Score:  {summary['avg_quality_score']:.2f}")
    print(f"Total Time:         {summary['total_time_seconds']:.2f}s")
    print("="*60)
    print("\n✅ Processing complete! Run dashboard: streamlit run src/dashboard/realtime_monitor.py\n")


if __name__ == "__main__":
    asyncio.run(main())
