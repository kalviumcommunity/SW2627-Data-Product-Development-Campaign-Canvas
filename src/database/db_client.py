import sqlite3
from pathlib import Path

from src.database.queries import (
    CREATE_INDEX_ACM_PLATFORM,
    CREATE_INDEX_ACM_SYNC_DATE,
    CREATE_INDEX_ADCM_CAMPAIGN_ID,
    CREATE_INDEX_HS_EMAIL,
    CREATE_INDEX_HS_UTM_CAMPAIGN,
    CREATE_INDEX_PA_EMAIL,
    CREATE_INDEX_PA_TIMESTAMPS,
    CREATE_TABLE_AD_CAMPAIGN_METRICS,
    CREATE_TABLE_HUBSPOT_SIGNUPS,
    CREATE_TABLE_PRODUCT_ACTIVATIONS,
    PRAGMA_FOREIGN_KEYS_ON,
)

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "marketing.db"


def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with foreign keys enabled.

    SQLite disables foreign key enforcement by default and resets the setting
    on every new connection. Enabling it here ensures all callers automatically
    get constraint validation without having to remember to set the pragma.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(PRAGMA_FOREIGN_KEYS_ON)
    return conn


def init_db(drop_existing: bool = False):
    """Initializes the database schema matching the PRD specifications.

    ad_campaign_metrics uses a composite PRIMARY KEY (campaign_id, sync_date)
    so that each calendar day for a campaign is stored as a separate row,
    preserving the full daily time-series of ad performance data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if drop_existing:
        cursor.execute("DROP TABLE IF EXISTS product_activations;")
        cursor.execute("DROP TABLE IF EXISTS hubspot_signups;")
        cursor.execute("DROP TABLE IF EXISTS ad_campaign_metrics;")

    cursor.execute(CREATE_TABLE_AD_CAMPAIGN_METRICS)
    cursor.execute(CREATE_INDEX_ADCM_CAMPAIGN_ID)
    cursor.execute(CREATE_INDEX_ACM_SYNC_DATE)
    cursor.execute(CREATE_INDEX_ACM_PLATFORM)

    cursor.execute(CREATE_TABLE_HUBSPOT_SIGNUPS)
    cursor.execute(CREATE_INDEX_HS_UTM_CAMPAIGN)
    cursor.execute(CREATE_INDEX_HS_EMAIL)  # Speeds up JOIN on hubspot_signups.email

    cursor.execute(CREATE_TABLE_PRODUCT_ACTIVATIONS)
    cursor.execute(CREATE_INDEX_PA_EMAIL)  # Speeds up JOIN on product_activations.email
    cursor.execute(CREATE_INDEX_PA_TIMESTAMPS)  # Speeds up time-window activation queries

    conn.commit()
    conn.close()
    print("Database schema successfully initialized!")


if __name__ == "__main__":
    init_db()
