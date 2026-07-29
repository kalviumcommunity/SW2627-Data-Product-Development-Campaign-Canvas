import sys
import pytest
import pandas as pd
import sqlite3
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.database.db_client import init_db, get_connection
from src.database.queries import CAMPAIGN_OVERVIEW_QUERY
from src.utils.campaigns import load_campaign_data, calculate_revenue, add_marketing_dimensions
from src.etl_pipeline import run_etl


def test_etl_and_campaign_query_date_grouping():
    """Test that the ETL and SQL query produce accurate date-level signups and activations without duplication."""
    run_etl()
    conn = get_connection()
    df = pd.read_sql_query(CAMPAIGN_OVERVIEW_QUERY, conn)
    conn.close()

    assert not df.empty
    assert "date" in df.columns
    assert "campaign_id" in df.columns
    assert "signups" in df.columns
    assert "activations_7d" in df.columns

    # Verify that total signups match raw table count
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM hubspot_signups WHERE utm_campaign IS NOT NULL")
    raw_signup_count = cursor.fetchone()[0]
    conn.close()

    assert df["signups"].sum() == raw_signup_count


def test_load_campaign_data_returns_dataframe():
    """Test load_campaign_data returns valid DataFrame and boolean flag."""
    df, is_demo = load_campaign_data()
    assert isinstance(df, pd.DataFrame)
    assert isinstance(is_demo, bool)
    assert "revenue" in df.columns
    assert "campaign_name" in df.columns


def test_add_marketing_dimensions():
    """Test marketing channel dimension mapping for various campaign types."""
    sample_df = pd.DataFrame({
        "campaign_id": ["c_google_brand", "c_youtube_awareness", "c_display_remarketing", "c_meta_prospect"],
        "campaign_name": ["Search - Brand", "YouTube - Awareness", "Display - Remarketing", "Paid Social - Prospecting"],
        "ad_platform": ["google_ads", "google_ads", "google_ads", "meta_ads"]
    })

    enriched = add_marketing_dimensions(sample_df)
    assert "channel" in enriched.columns
    channels = enriched["channel"].tolist()
    assert "Search" in channels
    assert "Video" in channels
    assert "Display" in channels
    assert "Social" in channels
