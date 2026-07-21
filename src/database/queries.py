"""
Database queries module with type safety and comprehensive query abstractions.

Provides:
- Typed query builders
- Connection pooling
- Query result validation
- Performance optimization with prepared statements
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import sqlite3

from src.database.db_client import db_client, DatabaseError
from src.logging_config import get_logger
from src.config import config

logger = get_logger(__name__)


class QueryBuilder:
    """
    Safe query builder with parameterized queries to prevent SQL injection.
    """
    
    @staticmethod
    def get_campaign_metrics(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        limit: int = config.MAX_ROWS_PER_QUERY,
    ) -> Tuple[str, List[Any]]:
        """Build query for campaign metrics."""
        query = "SELECT * FROM ad_campaign_metrics WHERE 1=1"
        params: List[Any] = []
        
        if start_date:
            query += " AND sync_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND sync_date <= ?"
            params.append(end_date)
        
        if platforms:
            placeholders = ",".join("?" * len(platforms))
            query += f" AND ad_platform IN ({placeholders})"
            params.extend(platforms)
        
        query += " ORDER BY sync_date DESC LIMIT ?"
        params.append(limit)
        
        return query, params
    
    @staticmethod
    def get_signups(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        campaign_id: Optional[str] = None,
        limit: int = config.MAX_ROWS_PER_QUERY,
    ) -> Tuple[str, List[Any]]:
        """Build query for signups."""
        query = "SELECT * FROM hubspot_signups WHERE 1=1"
        params: List[Any] = []
        
        if start_date:
            query += " AND DATE(signup_timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(signup_timestamp) <= ?"
            params.append(end_date)
        
        if campaign_id:
            query += " AND utm_campaign = ?"
            params.append(campaign_id)
        
        query += " ORDER BY signup_timestamp DESC LIMIT ?"
        params.append(limit)
        
        return query, params
    
    @staticmethod
    def get_activations(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        activated_only: bool = False,
        limit: int = config.MAX_ROWS_PER_QUERY,
    ) -> Tuple[str, List[Any]]:
        """Build query for activations."""
        query = "SELECT * FROM product_activations WHERE 1=1"
        params: List[Any] = []
        
        if start_date:
            query += " AND DATE(signup_timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(signup_timestamp) <= ?"
            params.append(end_date)
        
        if activated_only:
            query += " AND activation_timestamp IS NOT NULL"
        
        query += " ORDER BY signup_timestamp DESC LIMIT ?"
        params.append(limit)
        
        return query, params
    
    @staticmethod
    def get_funnel_stats(
        campaign_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[str, List[Any]]:
        """Build query for funnel statistics."""
        query = """
        SELECT
            COALESCE(acm.campaign_id, 'unknown') as campaign_id,
            acm.ad_platform,
            SUM(acm.impressions) as total_impressions,
            SUM(acm.clicks) as total_clicks,
            COUNT(DISTINCT hs.email) as total_signups,
            COUNT(DISTINCT CASE WHEN pa.profile_completed = 1 THEN pa.user_id END) as profile_completed,
            COUNT(DISTINCT CASE WHEN pa.campaign_run = 1 THEN pa.user_id END) as campaign_run,
            COUNT(DISTINCT CASE WHEN pa.activation_timestamp IS NOT NULL THEN pa.user_id END) as activated,
            SUM(acm.spend_usd) as total_spend
        FROM ad_campaign_metrics acm
        LEFT JOIN hubspot_signups hs ON acm.campaign_id = hs.utm_campaign
        LEFT JOIN product_activations pa ON hs.email = pa.email
        WHERE 1=1
        """
        params: List[Any] = []
        
        if campaign_id:
            query += " AND acm.campaign_id = ?"
            params.append(campaign_id)
        
        if start_date:
            query += " AND DATE(acm.sync_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(acm.sync_date) <= ?"
            params.append(end_date)
        
        query += " GROUP BY acm.campaign_id, acm.ad_platform"
        
        return query, params


class DatabaseQueries:
    """Database query executor with error handling."""
    
    @staticmethod
    def execute_query(
        query: str,
        params: List[Any],
        fetch_one: bool = False,
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        Execute a parameterized query safely.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: If True, return single row, otherwise return all rows
        
        Returns:
            Query result(s) or None
            
        Raises:
            DatabaseError: If query execution fails
        """
        try:
            with db_client.get_db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None
                else:
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except sqlite3.DatabaseError as e:
            logger.error(f"Database query error: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    @staticmethod
    def get_campaign_metrics(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        platforms: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get campaign metrics with optional filtering."""
        query, params = QueryBuilder.get_campaign_metrics(
            start_date, end_date, platforms
        )
        result = DatabaseQueries.execute_query(query, params)
        return result if result else []
    
    @staticmethod
    def get_signups(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get signup records with optional filtering."""
        query, params = QueryBuilder.get_signups(
            start_date, end_date, campaign_id
        )
        result = DatabaseQueries.execute_query(query, params)
        return result if result else []
    
    @staticmethod
    def get_activations(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        activated_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get activation records with optional filtering."""
        query, params = QueryBuilder.get_activations(
            start_date, end_date, activated_only
        )
        result = DatabaseQueries.execute_query(query, params)
        return result if result else []
    
    @staticmethod
    def get_funnel_statistics(
        campaign_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get funnel statistics with optional filtering."""
        query, params = QueryBuilder.get_funnel_stats(
            campaign_id, start_date, end_date
        )
        result = DatabaseQueries.execute_query(query, params)
        return result if result else []
    
    @staticmethod
    def get_campaign_count() -> int:
        """Get total number of campaigns."""
        query = "SELECT COUNT(*) as count FROM ad_campaign_metrics"
        result = DatabaseQueries.execute_query(query, [], fetch_one=True)
        return result.get("count", 0) if result else 0
    
    @staticmethod
    def get_signup_count() -> int:
        """Get total number of signups."""
        query = "SELECT COUNT(*) as count FROM hubspot_signups"
        result = DatabaseQueries.execute_query(query, [], fetch_one=True)
        return result.get("count", 0) if result else 0
    
    @staticmethod
    def get_activation_count() -> int:
        """Get total number of activations."""
        query = "SELECT COUNT(*) as count FROM product_activations WHERE activation_timestamp IS NOT NULL"
        result = DatabaseQueries.execute_query(query, [], fetch_one=True)
        return result.get("count", 0) if result else 0
    
    @staticmethod
    def get_date_range() -> Tuple[Optional[str], Optional[str]]:
        """Get date range of data in the database."""
        query = """
        SELECT
            MIN(sync_date) as min_date,
            MAX(sync_date) as max_date
        FROM ad_campaign_metrics
        """
        result = DatabaseQueries.execute_query(query, [], fetch_one=True)
        
        if result:
            return (result.get("min_date"), result.get("max_date"))
        
        return (None, None)

