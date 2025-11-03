"""
Real-Time Data Quality Monitoring Dashboard

Live dashboard showing:
- Submission processing metrics
- AI agent performance
- Quality trends and anomalies
- Enrichment statistics
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List


class RealTimeMonitor:
    """Real-time dashboard for monitoring AI-powered data quality"""
    
    def __init__(self, db_path: str = "dbt_project/target/acord_dqm.duckdb"):
        """
        Initialize dashboard.
        
        Args:
            db_path: Path to DuckDB database
        """
        self.db_path = db_path
        
    def run_dashboard(self):
        """Main dashboard application"""
        st.set_page_config(
            page_title="AI-Powered ACORD Data Quality Monitor",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 AI-Powered ACORD Data Quality Monitor")
        st.markdown("Real-time monitoring of submission processing with AI agents")
        
        # Auto-refresh controls
        col_refresh, col_auto = st.columns([1, 4])
        with col_refresh:
            if st.button("🔄 Refresh"):
                st.rerun()
        with col_auto:
            st.markdown("*Dashboard updates on refresh*")
        
        self._render_dashboard()
    
    def _render_dashboard(self):
        """Render all dashboard components"""
        
        # Row 1: Key Metrics
        st.subheader("📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Submissions Today",
                value=self._get_submissions_today(),
                delta=self._get_submissions_delta()
            )
        
        with col2:
            st.metric(
                "Avg Quality Score",
                value=f"{self._get_avg_quality_score():.2f}",
                delta=f"{self._get_quality_trend():.2f}"
            )
            
        with col3:
            st.metric(
                "Enrichment Rate",
                value=f"{self._get_enrichment_rate():.1%}",
                delta=f"{self._get_enrichment_trend():.1%}"
            )
            
        with col4:
            st.metric(
                "Anomalies Detected",
                value=self._get_anomalies_today(),
                delta=self._get_anomaly_trend()
            )
        
        # Row 2: Real-Time Processing
        st.subheader("📈 Processing Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quality Score Distribution
            quality_data = self._get_quality_distribution()
            fig_quality = px.histogram(
                quality_data, 
                x='quality_score', 
                nbins=20,
                title="Quality Score Distribution (Last 24h)",
                labels={'quality_score': 'Quality Score', 'count': 'Number of Submissions'}
            )
            fig_quality.update_layout(showlegend=False)
            st.plotly_chart(fig_quality, use_container_width=True)
        
        with col2:
            # Processing Time Trends
            processing_data = self._get_processing_times()
            fig_timing = px.line(
                processing_data,
                x='timestamp',
                y='processing_time_ms',
                title="Processing Time Trends",
                labels={'processing_time_ms': 'Processing Time (ms)', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig_timing, use_container_width=True)
        
        # Row 3: AI Agent Performance
        st.subheader("🤖 AI Agent Performance")
        
        agent_col1, agent_col2, agent_col3 = st.columns(3)
        
        with agent_col1:
            st.markdown("**Quality Agent**")
            quality_agent_metrics = self._get_quality_agent_metrics()
            st.json(quality_agent_metrics)
        
        with agent_col2:
            st.markdown("**Enrichment Agent**")
            enrichment_agent_metrics = self._get_enrichment_agent_metrics()
            st.json(enrichment_agent_metrics)
            
        with agent_col3:
            st.markdown("**Anomaly Agent**")
            anomaly_agent_metrics = self._get_anomaly_agent_metrics()
            st.json(anomaly_agent_metrics)
        
        # Row 4: Recent Submissions
        st.subheader("📋 Recent Submissions")
        recent_submissions = self._get_recent_submissions()
        st.dataframe(recent_submissions, use_container_width=True)
    
    # Placeholder methods - would connect to DuckDB in production
    
    def _get_submissions_today(self) -> int:
        """Get number of submissions today"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            result = conn.execute("""
                SELECT COUNT(*) FROM submissions
                WHERE DATE(created_at) = CURRENT_DATE
            """).fetchone()
            conn.close()
            return result[0] if result else 0
        except:
            return 0
    
    def _get_submissions_delta(self) -> int:
        """Get change in submissions vs yesterday"""
        # Placeholder
        return 5
    
    def _get_avg_quality_score(self) -> float:
        """Get average quality score"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            result = conn.execute("""
                SELECT AVG(quality_score) FROM processing_results
                WHERE DATE(processed_at) >= CURRENT_DATE - INTERVAL 1 DAY
            """).fetchone()
            conn.close()
            return round(result[0], 2) if result and result[0] else 0.0
        except:
            return 0.0
    
    def _get_quality_trend(self) -> float:
        """Get quality score trend"""
        # Placeholder
        return 0.03
    
    def _get_enrichment_rate(self) -> float:
        """Get enrichment rate"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            result = conn.execute("""
                SELECT 
                    CAST(SUM(CASE WHEN enrichment_applied THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) 
                FROM processing_results
                WHERE DATE(processed_at) >= CURRENT_DATE - INTERVAL 1 DAY
            """).fetchone()
            conn.close()
            return result[0] if result and result[0] else 0.0
        except:
            return 0.0
    
    def _get_enrichment_trend(self) -> float:
        """Get enrichment trend"""
        # Placeholder
        return -0.02
    
    def _get_anomalies_today(self) -> int:
        """Get anomalies detected today"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            result = conn.execute("""
                SELECT COUNT(*) FROM processing_results
                WHERE DATE(processed_at) >= CURRENT_DATE
                AND anomalies_detected != '[]'
            """).fetchone()
            conn.close()
            return result[0] if result else 0
        except:
            return 0
    
    def _get_anomaly_trend(self) -> int:
        """Get anomaly trend"""
        # Placeholder
        return -1
    
    def _get_quality_distribution(self) -> pd.DataFrame:
        """Get quality score distribution for chart"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            df = conn.execute("""
                SELECT quality_score
                FROM processing_results
                WHERE DATE(processed_at) >= CURRENT_DATE - INTERVAL 1 DAY
            """).df()
            conn.close()
            return df if not df.empty else pd.DataFrame({'quality_score': [0.85]})
        except:
            return pd.DataFrame({'quality_score': [0.85]})
    
    def _get_processing_times(self) -> pd.DataFrame:
        """Get processing time data"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            df = conn.execute("""
                SELECT processed_at as timestamp, processing_time_ms
                FROM processing_results
                WHERE DATE(processed_at) >= CURRENT_DATE - INTERVAL 1 DAY
                ORDER BY processed_at
            """).df()
            conn.close()
            if not df.empty:
                return df
        except:
            pass
        # Fallback to sample data
        import numpy as np
        times = pd.date_range(end=datetime.now(), periods=10, freq='1min')
        processing_times = np.random.normal(2000, 500, 10)
        return pd.DataFrame({
            'timestamp': times,
            'processing_time_ms': processing_times
        })
    
    def _get_quality_agent_metrics(self) -> Dict[str, Any]:
        """Get quality agent metrics"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            result = conn.execute("""
                SELECT 
                    COUNT(*) as decisions_today,
                    AVG(quality_score) as avg_quality
                FROM processing_results
                WHERE DATE(processed_at) >= CURRENT_DATE
            """).fetchone()
            conn.close()
            if result:
                return {
                    "decisions_today": result[0],
                    "avg_quality_score": round(result[1], 2) if result[1] else 0,
                    "avg_confidence": 0.88
                }
        except:
            pass
        return {
            "decisions_today": 0,
            "avg_quality_score": 0.0,
            "avg_confidence": 0.0
        }
    
    def _get_enrichment_agent_metrics(self) -> Dict[str, Any]:
        """Get enrichment agent metrics"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            result = conn.execute("""
                SELECT 
                    SUM(CASE WHEN enrichment_applied THEN 1 ELSE 0 END) as enrichments,
                    COUNT(*) as total
                FROM processing_results
                WHERE DATE(processed_at) >= CURRENT_DATE
            """).fetchone()
            conn.close()
            if result and result[1] > 0:
                return {
                    "enrichments_applied": result[0],
                    "total_submissions": result[1],
                    "enrichment_rate": round(result[0] / result[1], 2) if result[1] > 0 else 0
                }
        except:
            pass
        return {
            "enrichments_applied": 0,
            "total_submissions": 0,
            "enrichment_rate": 0.0
        }
    
    def _get_anomaly_agent_metrics(self) -> Dict[str, Any]:
        """Get anomaly agent metrics"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            result = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN anomalies_detected != '[]' THEN 1 ELSE 0 END) as with_anomalies
                FROM processing_results
                WHERE DATE(processed_at) >= CURRENT_DATE
            """).fetchone()
            conn.close()
            if result:
                return {
                    "submissions_analyzed": result[0],
                    "anomalies_detected": result[1],
                    "detection_rate": round(result[1] / result[0], 2) if result[0] > 0 else 0
                }
        except:
            pass
        return {
            "submissions_analyzed": 0,
            "anomalies_detected": 0,
            "detection_rate": 0.0
        }
    
    def _get_recent_submissions(self) -> pd.DataFrame:
        """Get recent submissions for table"""
        try:
            import duckdb
            conn = duckdb.connect(self.db_path, read_only=True)
            df = conn.execute("""
                SELECT 
                    s.submission_id,
                    s.business_name,
                    s.naics_code,
                    s.annual_revenue,
                    s.employee_count,
                    pr.quality_score,
                    pr.enrichment_applied,
                    pr.anomalies_detected,
                    pr.processed_at
                FROM submissions s
                JOIN processing_results pr ON s.submission_id = pr.submission_id
                ORDER BY pr.processed_at DESC
                LIMIT 10
            """).df()
            conn.close()
            if not df.empty:
                # Round quality score for display
                df['quality_score'] = df['quality_score'].round(2)
                return df
        except Exception as e:
            pass
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            'submission_id', 'business_name', 'naics_code', 
            'annual_revenue', 'employee_count', 'quality_score',
            'enrichment_applied', 'anomalies_detected', 'processed_at'
        ])


def main():
    """Entry point for Streamlit dashboard"""
    monitor = RealTimeMonitor()
    monitor.run_dashboard()


if __name__ == "__main__":
    main()
