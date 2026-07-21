"""
Database client and connection management for Campaign Canvas.

This module handles:
- Database connection pooling and lifecycle management
- Schema initialization with proper constraints
- Transaction management with error handling
- Connection validation and health checks
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from src.config import config
from src.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""
    pass


class DatabaseInitError(DatabaseError):
    """Exception raised when database initialization fails."""
    pass


class DatabaseClient:
    """
    Thread-safe database client with connection management and health checks.
    
    Supports:
    - Automatic connection pooling
    - Transaction management
    - Connection validation
    - Graceful error handling
    """
    
    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize database client.
        
        Args:
            db_path: Path to SQLite database file.
                    Defaults to config.DB_PATH
        """
        self.db_path = db_path or config.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized DatabaseClient with path: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with proper configuration.
        
        Returns:
            sqlite3.Connection object
            
        Raises:
            DatabaseConnectionError: If connection fails
        """
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=config.DB_TIMEOUT,
                check_same_thread=config.DB_CHECK_SAME_THREAD,
            )
            
            # Enable foreign keys support
            conn.execute("PRAGMA foreign_keys = ON;")
            
            # Set row factory for dict-like access
            conn.row_factory = sqlite3.Row
            
            # Enable query timeout
            conn.execute(f"PRAGMA query_only = false;")
            
            logger.debug(f"Database connection established to {self.db_path}")
            return conn
            
        except sqlite3.OperationalError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseConnectionError(f"Cannot connect to {self.db_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to database: {e}")
            raise DatabaseConnectionError(f"Unexpected error: {e}")
    
    @contextmanager
    def get_db_session(self):
        """
        Context manager for database sessions with automatic commit/rollback.
        
        Usage:
            with db_client.get_db_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def health_check(self) -> bool:
        """
        Check if database is accessible and healthy.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            with self.get_db_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def init_db(self) -> None:
        """
        Initialize database schema with all required tables and constraints.
        
        Raises:
            DatabaseInitError: If schema initialization fails
        """
        try:
            with self.get_db_session() as conn:
                cursor = conn.cursor()
                
                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys = ON;")
                
                # 1. Table: ad_campaign_metrics
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS ad_campaign_metrics (
                    campaign_id VARCHAR PRIMARY KEY,
                    ad_platform VARCHAR NOT NULL CHECK(
                        ad_platform IN (
                            'google_ads', 'meta_ads', 'linkedin_ads',
                            'tiktok_ads', 'pinterest_ads'
                        )
                    ),
                    spend_usd DECIMAL(10, 2) NOT NULL CHECK(spend_usd >= 0),
                    clicks INTEGER NOT NULL CHECK(clicks >= 0),
                    impressions INTEGER NOT NULL CHECK(impressions >= 0),
                    sync_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                
                # Create index for faster queries
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ad_campaign_metrics_date
                ON ad_campaign_metrics(sync_date);
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ad_campaign_metrics_platform
                ON ad_campaign_metrics(ad_platform);
                """)
                
                # 2. Table: hubspot_signups
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS hubspot_signups (
                    email VARCHAR PRIMARY KEY,
                    utm_campaign VARCHAR,
                    signup_timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (utm_campaign)
                        REFERENCES ad_campaign_metrics(campaign_id)
                        ON DELETE SET NULL
                );
                """)
                
                # Create index for faster lookups
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_hubspot_signups_utm
                ON hubspot_signups(utm_campaign);
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_hubspot_signups_timestamp
                ON hubspot_signups(signup_timestamp);
                """)
                
                # 3. Table: product_activations
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_activations (
                    user_id VARCHAR PRIMARY KEY,
                    email VARCHAR NOT NULL,
                    signup_timestamp TIMESTAMP NOT NULL,
                    activation_timestamp TIMESTAMP,
                    profile_completed BOOLEAN NOT NULL
                        CHECK(profile_completed IN (0, 1)),
                    campaign_run BOOLEAN NOT NULL
                        CHECK(campaign_run IN (0, 1)),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (email)
                        REFERENCES hubspot_signups(email)
                        ON DELETE CASCADE,
                    CHECK (
                        activation_timestamp IS NULL
                        OR signup_timestamp <= activation_timestamp
                    )
                );
                """)
                
                # Create indexes for faster queries
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_product_activations_email
                ON product_activations(email);
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_product_activations_timestamp
                ON product_activations(signup_timestamp);
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_product_activations_activated
                ON product_activations(activation_timestamp);
                """)
                
                logger.info("Database schema initialized successfully")
                
        except sqlite3.DatabaseError as e:
            logger.error(f"Database initialization error: {e}")
            raise DatabaseInitError(f"Failed to initialize database schema: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {e}")
            raise DatabaseInitError(f"Unexpected error: {e}")


# Global database client instance
db_client = DatabaseClient()


def get_connection() -> sqlite3.Connection:
    """Get a database connection (backward compatibility)."""
    return db_client.get_connection()


def init_db() -> None:
    """Initialize database schema (backward compatibility)."""
    db_client.init_db()

