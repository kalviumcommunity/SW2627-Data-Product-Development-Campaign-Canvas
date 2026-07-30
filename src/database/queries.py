"""Reusable SQL query strings and dynamic query helpers for CampaignCanvas."""

from __future__ import annotations

import re
from typing import Final

# ── Pragma Directives ────────────────────────────────────────────────────────
PRAGMA_FOREIGN_KEYS_ON: Final = "PRAGMA foreign_keys = ON;"
PRAGMA_FOREIGN_KEYS_OFF: Final = "PRAGMA foreign_keys = OFF;"

# ── Table Purge Queries ──────────────────────────────────────────────────────
DELETE_PRODUCT_ACTIVATIONS: Final = "DELETE FROM product_activations;"
DELETE_HUBSPOT_SIGNUPS: Final = "DELETE FROM hubspot_signups;"
DELETE_AD_CAMPAIGN_METRICS: Final = "DELETE FROM ad_campaign_metrics;"

# ── Default Workspace Queries ────────────────────────────────────────────────
# NOTE: This query targets the in-memory SQLite `campaigns` view that
# sql_workspace.py builds from the loaded DataFrame — it does NOT reference
# the on-disk SQLite `ad_campaign_metrics` table.  The `campaigns` view has
# columns: date, campaign, channel, platform, region, device, impressions,
# clicks, visits, signups, conversions, spend, revenue.
SQL_WORKSPACE_DEFAULT_QUERY: Final = """SELECT
    channel,
    SUM(spend)       AS total_spend,
    SUM(revenue)     AS total_revenue,
    ROUND(SUM(revenue) * 1.0 / NULLIF(SUM(spend), 0), 2) AS roas,
    SUM(clicks)      AS total_clicks,
    SUM(impressions) AS total_impressions,
    ROUND(SUM(clicks) * 100.0 / NULLIF(SUM(impressions), 0), 2) AS ctr_pct,
    ROUND(SUM(spend) * 1.0 / NULLIF(SUM(clicks), 0), 2) AS cpc
FROM campaigns
GROUP BY channel
HAVING SUM(spend) > 0
ORDER BY total_revenue DESC;"""


# ── Campaign Overview & Activation Aggregations ─────────────────────────────
CAMPAIGN_OVERVIEW_QUERY: Final = """WITH campaign_signups AS (
    SELECT 
        utm_campaign,
        COUNT(*) AS signups
    FROM hubspot_signups
    WHERE utm_campaign IS NOT NULL
    GROUP BY utm_campaign
),
campaign_activations AS (
    SELECT 
        h.utm_campaign,
        SUM(p.profile_completed) AS profile_completed,
        SUM(p.campaign_run) AS campaign_run,
        SUM(CASE 
            WHEN p.profile_completed = 1 
                 AND p.campaign_run = 1 
                 AND (julianday(p.activation_timestamp) - julianday(p.signup_timestamp)) <= 7.0 
            THEN 1 ELSE 0 
        END) AS activations_7d
    FROM hubspot_signups h
    JOIN product_activations p ON h.email = p.email
    WHERE h.utm_campaign IS NOT NULL
    GROUP BY h.utm_campaign
)
SELECT 
    a.sync_date AS date,
    a.campaign_id,
    a.ad_platform,
    a.spend_usd,
    a.clicks,
    a.impressions,
    COALESCE(s.signups, 0) AS signups,
    COALESCE(c.profile_completed, 0) AS profile_completed,
    COALESCE(c.campaign_run, 0) AS campaign_run,
    COALESCE(c.activations_7d, 0) AS activations_7d
FROM ad_campaign_metrics a
LEFT JOIN campaign_signups s ON a.campaign_id = s.utm_campaign
LEFT JOIN campaign_activations c ON a.campaign_id = c.utm_campaign
ORDER BY a.sync_date DESC, a.campaign_id ASC;"""

# ── Schema Definitions: ad_campaign_metrics ─────────────────────────────────
CREATE_TABLE_AD_CAMPAIGN_METRICS: Final = """CREATE TABLE IF NOT EXISTS ad_campaign_metrics (
    campaign_id VARCHAR NOT NULL,
    sync_date   DATE    NOT NULL,
    ad_platform VARCHAR CHECK(ad_platform IN ('google_ads', 'meta_ads', 'linkedin_ads', 'tiktok_ads', 'pinterest_ads')),
    spend_usd   DECIMAL(10, 2) NOT NULL CHECK(spend_usd >= 0),
    clicks      INTEGER        NOT NULL CHECK(clicks >= 0),
    impressions INTEGER        NOT NULL CHECK(impressions >= 0),
    PRIMARY KEY (campaign_id, sync_date)
);"""

CREATE_INDEX_ADCM_CAMPAIGN_ID: Final = """CREATE INDEX IF NOT EXISTS idx_adcm_campaign_id
ON ad_campaign_metrics (campaign_id);"""

CREATE_INDEX_ACM_SYNC_DATE: Final = """CREATE INDEX IF NOT EXISTS idx_acm_sync_date
    ON ad_campaign_metrics (sync_date);"""

CREATE_INDEX_ACM_PLATFORM: Final = """CREATE INDEX IF NOT EXISTS idx_acm_platform
    ON ad_campaign_metrics (ad_platform, sync_date);"""

# ── Schema Definitions: hubspot_signups ─────────────────────────────────────
CREATE_TABLE_HUBSPOT_SIGNUPS: Final = """CREATE TABLE IF NOT EXISTS hubspot_signups (
    email            VARCHAR   PRIMARY KEY,
    utm_campaign     VARCHAR,
    signup_timestamp TIMESTAMP NOT NULL
);"""

CREATE_INDEX_HS_UTM_CAMPAIGN: Final = """CREATE INDEX IF NOT EXISTS idx_hs_utm_campaign
    ON hubspot_signups (utm_campaign);"""

CREATE_INDEX_HS_EMAIL: Final = """CREATE INDEX IF NOT EXISTS idx_hs_email
    ON hubspot_signups (email);"""

# ── Schema Definitions: product_activations ─────────────────────────────────
CREATE_TABLE_PRODUCT_ACTIVATIONS: Final = """CREATE TABLE IF NOT EXISTS product_activations (
    user_id VARCHAR PRIMARY KEY,
    email VARCHAR NOT NULL,
    signup_timestamp TIMESTAMP NOT NULL,
    activation_timestamp TIMESTAMP,
    profile_completed BOOLEAN NOT NULL CHECK(profile_completed IN (0, 1)),
    campaign_run BOOLEAN NOT NULL CHECK(campaign_run IN (0, 1)),
    FOREIGN KEY (email) REFERENCES hubspot_signups(email),
    CHECK (activation_timestamp IS NULL OR signup_timestamp <= activation_timestamp)
);"""

CREATE_INDEX_PA_EMAIL: Final = """CREATE INDEX IF NOT EXISTS idx_pa_email
    ON product_activations (email);"""

CREATE_INDEX_PA_TIMESTAMPS: Final = """CREATE INDEX IF NOT EXISTS idx_pa_timestamps
    ON product_activations (signup_timestamp, activation_timestamp);"""


# ── Helper Functions for Dynamic Inspection ────────────────────────────────
def count_rows_query(table_name: str) -> str:
    """Return a safe COUNT query for a sanitized table name."""
    clean_name = re.sub(r"[^\w_]", "", table_name)
    return f"SELECT COUNT(*) FROM {clean_name};"


def table_info_query(table_name: str) -> str:
    """Return a PRAGMA table_info query for a sanitized table name."""
    clean_name = re.sub(r"[^\w_]", "", table_name)
    return f"PRAGMA table_info({clean_name});"