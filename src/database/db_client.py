import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "marketing.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))

def init_db():
    """Initializes the database schema matching the PRD specifications.

    ad_campaign_metrics uses a composite PRIMARY KEY (campaign_id, sync_date)
    so that each calendar day for a campaign is stored as a separate row,
    preserving the full daily time-series of ad performance data.
    A UNIQUE index on campaign_id alone is also created so that
    hubspot_signups.utm_campaign can reference it via a foreign key.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys support in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Table: ad_campaign_metrics
    #    Composite PK (campaign_id, sync_date) ensures one row per campaign per day,
    #    enabling daily time-series queries (trend charts, day-over-day deltas, etc.).
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ad_campaign_metrics (
        campaign_id VARCHAR NOT NULL,
        sync_date   DATE    NOT NULL,
        ad_platform VARCHAR CHECK(ad_platform IN ('google_ads', 'meta_ads', 'linkedin_ads', 'tiktok_ads', 'pinterest_ads')),
        spend_usd   DECIMAL(10, 2) NOT NULL CHECK(spend_usd >= 0),
        clicks      INTEGER        NOT NULL CHECK(clicks >= 0),
        impressions INTEGER        NOT NULL CHECK(impressions >= 0),
        PRIMARY KEY (campaign_id, sync_date)
    );
    """)

    # Unique index on campaign_id so hubspot_signups.utm_campaign can FK-reference it.
    # SQLite FK references must point to a PRIMARY KEY or a UNIQUE column/index.
    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uix_adcm_campaign_id
    ON ad_campaign_metrics (campaign_id);
    """)

    # Index to accelerate date-range and platform queries
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_acm_sync_date
        ON ad_campaign_metrics (sync_date);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_acm_platform
        ON ad_campaign_metrics (ad_platform, sync_date);
    """)
    
    # 2. Table: hubspot_signups
    #    utm_campaign FK references the unique campaign_id index on ad_campaign_metrics.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hubspot_signups (
        email            VARCHAR   PRIMARY KEY,
        utm_campaign     VARCHAR,
        signup_timestamp TIMESTAMP NOT NULL,
        FOREIGN KEY (utm_campaign) REFERENCES ad_campaign_metrics(campaign_id)
    );
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_hs_utm_campaign
        ON hubspot_signups (utm_campaign);
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
