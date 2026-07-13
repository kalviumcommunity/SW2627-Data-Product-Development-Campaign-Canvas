import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "marketing.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))

def init_db():
    """Initializes the database schema matching the PRD specifications."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys support in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Table: ad_campaign_metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ad_campaign_metrics (
        campaign_id VARCHAR PRIMARY KEY,
        ad_platform VARCHAR CHECK(ad_platform IN ('google_ads', 'meta_ads')),
        spend_usd DECIMAL(10, 2) NOT NULL CHECK(spend_usd >= 0),
        clicks INTEGER NOT NULL CHECK(clicks >= 0),
        impressions INTEGER NOT NULL CHECK(impressions >= 0),
        sync_date DATE NOT NULL
    );
    """)
    
    # 2. Table: hubspot_signups
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hubspot_signups (
        email VARCHAR PRIMARY KEY,
        utm_campaign VARCHAR,
        signup_timestamp TIMESTAMP NOT NULL,
        FOREIGN KEY (utm_campaign) REFERENCES ad_campaign_metrics(campaign_id)
    );
    """)
    
    # 3. Table: product_activations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_activations (
        user_id VARCHAR PRIMARY KEY,
        email VARCHAR NOT NULL,
        signup_timestamp TIMESTAMP NOT NULL,
        activation_timestamp TIMESTAMP,
        profile_completed BOOLEAN NOT NULL CHECK(profile_completed IN (0, 1)),
        campaign_run BOOLEAN NOT NULL CHECK(campaign_run IN (0, 1)),
        FOREIGN KEY (email) REFERENCES hubspot_signups(email),
        CHECK (activation_timestamp IS NULL OR signup_timestamp <= activation_timestamp)
    );
    """)
    
    conn.commit()
    conn.close()
    print("Database schema successfully initialized!")

if __name__ == "__main__":
    init_db()
