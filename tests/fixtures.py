"""
Test utilities and fixtures for Campaign Canvas.

Provides:
- Test data factories
- Mock database fixtures
- Common test utilities
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import string

import pytest


class TestDataFactory:
    """Factory for generating test data."""
    
    @staticmethod
    def random_campaign_id() -> str:
        """Generate a random campaign ID."""
        campaigns = [
            "c_google_brand", "c_google_nonbrand", "c_meta_prospect",
            "c_meta_retarget", "c_youtube_awareness", "c_display_remarketing"
        ]
        return random.choice(campaigns)
    
    @staticmethod
    def random_email() -> str:
        """Generate a random email for testing."""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"test_{random_str}@example.com"
    
    @staticmethod
    def random_platform() -> str:
        """Generate a random ad platform."""
        platforms = ["google_ads", "meta_ads", "linkedin_ads", "tiktok_ads", "pinterest_ads"]
        return random.choice(platforms)
    
    @staticmethod
    def create_campaign_metrics(
        campaign_id: str,
        spend_usd: float = 100.0,
        clicks: int = 50,
        impressions: int = 1000,
        sync_date: str = None,
    ) -> Dict[str, Any]:
        """Create a campaign metrics record."""
        if sync_date is None:
            sync_date = datetime.now().strftime("%Y-%m-%d")
        
        return {
            "campaign_id": campaign_id,
            "ad_platform": TestDataFactory.random_platform(),
            "spend_usd": spend_usd,
            "clicks": clicks,
            "impressions": impressions,
            "sync_date": sync_date,
        }
    
    @staticmethod
    def create_signup(
        email: str = None,
        utm_campaign: str = None,
        signup_timestamp: str = None,
    ) -> Dict[str, Any]:
        """Create a signup record."""
        if email is None:
            email = TestDataFactory.random_email()
        if utm_campaign is None:
            utm_campaign = TestDataFactory.random_campaign_id()
        if signup_timestamp is None:
            signup_timestamp = datetime.now().isoformat()
        
        return {
            "email": email,
            "utm_campaign": utm_campaign,
            "signup_timestamp": signup_timestamp,
        }
    
    @staticmethod
    def create_activation(
        user_id: str = None,
        email: str = None,
        signup_timestamp: str = None,
        activation_timestamp: str = None,
        profile_completed: int = 1,
        campaign_run: int = 1,
    ) -> Dict[str, Any]:
        """Create an activation record."""
        if user_id is None:
            user_id = f"usr_{random.randint(1000, 9999)}"
        if email is None:
            email = TestDataFactory.random_email()
        if signup_timestamp is None:
            signup_timestamp = datetime.now().isoformat()
        if activation_timestamp is None:
            activation_timestamp = (
                datetime.now() + timedelta(hours=random.randint(1, 168))
            ).isoformat()
        
        return {
            "user_id": user_id,
            "email": email,
            "signup_timestamp": signup_timestamp,
            "activation_timestamp": activation_timestamp,
            "profile_completed": profile_completed,
            "campaign_run": campaign_run,
        }


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Create a temporary test database."""
    db_path = tmp_path / "test.db"
    return db_path


@pytest.fixture
def test_db_connection(test_db_path: Path) -> sqlite3.Connection:
    """Create a test database connection with schema."""
    conn = sqlite3.connect(str(test_db_path))
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create tables
    cursor.execute("""
    CREATE TABLE ad_campaign_metrics (
        campaign_id VARCHAR PRIMARY KEY,
        ad_platform VARCHAR,
        spend_usd DECIMAL(10, 2),
        clicks INTEGER,
        impressions INTEGER,
        sync_date DATE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE hubspot_signups (
        email VARCHAR PRIMARY KEY,
        utm_campaign VARCHAR,
        signup_timestamp TIMESTAMP,
        FOREIGN KEY (utm_campaign) REFERENCES ad_campaign_metrics(campaign_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE product_activations (
        user_id VARCHAR PRIMARY KEY,
        email VARCHAR NOT NULL,
        signup_timestamp TIMESTAMP,
        activation_timestamp TIMESTAMP,
        profile_completed BOOLEAN,
        campaign_run BOOLEAN,
        FOREIGN KEY (email) REFERENCES hubspot_signups(email)
    );
    """)
    
    conn.commit()
    return conn


def insert_test_data(
    connection: sqlite3.Connection,
    table: str,
    data: List[Dict[str, Any]],
) -> None:
    """Insert test data into database."""
    if not data:
        return
    
    cursor = connection.cursor()
    columns = list(data[0].keys())
    placeholders = ",".join(["?"] * len(columns))
    column_names = ",".join(columns)
    
    query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
    
    for row in data:
        values = [row.get(col) for col in columns]
        cursor.execute(query, values)
    
    connection.commit()
