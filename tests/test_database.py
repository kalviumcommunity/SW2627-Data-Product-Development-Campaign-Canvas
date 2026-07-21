"""
Unit tests for database module.
"""

import pytest
from src.database.db_client import (
    DatabaseClient,
    DatabaseConnectionError,
    DatabaseInitError,
)
from tests.fixtures import test_db_path, test_db_connection, TestDataFactory


class TestDatabaseClient:
    """Test database client."""
    
    def test_database_client_initialization(self, test_db_path):
        """Test database client initialization."""
        client = DatabaseClient(test_db_path)
        assert client.db_path == test_db_path
    
    def test_get_connection(self, test_db_path):
        """Test getting a database connection."""
        client = DatabaseClient(test_db_path)
        conn = client.get_connection()
        
        assert conn is not None
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result is not None
        
        conn.close()
    
    def test_database_initialization(self, test_db_path):
        """Test database schema initialization."""
        client = DatabaseClient(test_db_path)
        client.init_db()
        
        conn = client.get_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ad_campaign_metrics'"
        )
        assert cursor.fetchone() is not None
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='hubspot_signups'"
        )
        assert cursor.fetchone() is not None
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='product_activations'"
        )
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_health_check(self, test_db_path):
        """Test database health check."""
        client = DatabaseClient(test_db_path)
        client.init_db()
        
        assert client.health_check() is True
    
    def test_context_manager(self, test_db_path):
        """Test database session context manager."""
        client = DatabaseClient(test_db_path)
        client.init_db()
        
        with client.get_db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            assert cursor.fetchone() is not None


class TestDatabaseQueries:
    """Test database queries."""
    
    @pytest.mark.unit
    def test_query_builder_campaigns(self):
        """Test campaign query builder."""
        from src.database.queries import QueryBuilder
        
        query, params = QueryBuilder.get_campaign_metrics(
            start_date="2024-01-01",
            end_date="2024-01-31",
            platforms=["google_ads", "meta_ads"],
        )
        
        assert "WHERE 1=1" in query
        assert "sync_date" in query
        assert "ad_platform IN" in query
        assert len(params) == 5  # start_date, end_date, platform1, platform2, limit
    
    @pytest.mark.unit
    def test_query_builder_signups(self):
        """Test signup query builder."""
        from src.database.queries import QueryBuilder
        
        query, params = QueryBuilder.get_signups(
            campaign_id="c_google_brand"
        )
        
        assert "hubspot_signups" in query
        assert "utm_campaign" in query
