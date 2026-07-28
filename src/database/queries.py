"""Reusable SQL query strings for CampaignCanvas."""

from __future__ import annotations

from typing import Final

PRAGMA_FOREIGN_KEYS_ON: Final = "PRAGMA foreign_keys = ON;"
PRAGMA_FOREIGN_KEYS_OFF: Final = "PRAGMA foreign_keys = OFF;"

DELETE_PRODUCT_ACTIVATIONS: Final = "DELETE FROM product_activations;"
DELETE_HUBSPOT_SIGNUPS: Final = "DELETE FROM hubspot_signups;"
DELETE_AD_CAMPAIGN_METRICS: Final = "DELETE FROM ad_campaign_metrics;"

SQL_WORKSPACE_DEFAULT_QUERY: Final = """SELECT channel, SUM(revenue) AS revenue, SUM(spend) AS spend,
       ROUND(SUM(revenue)*1.0/NULLIF(SUM(spend),0), 2) AS roas
FROM campaigns
GROUP BY channel
ORDER BY revenue DESC"""

CAMPAIGN_OVERVIEW_QUERY: Final = """WITH campaign_signups AS (
    SELECT 
        utm_campaign,
        COUNT(*) AS signups
    FROM hubspot_signups
    GROUP BY utm_campaign
),
campaign_activations AS (
    SELECT 
        h.utm_campaign,
        SUM(p.profile_completed) AS profile_completed,
        SUM(p.campaign_run) AS campaign_run,
        SUM(CASE WHEN p.profile_completed = 1 AND p.campaign_run = 1 AND 
                 (julianday(p.activation_timestamp) - julianday(p.signup_timestamp)) <= 7.0 THEN 1 ELSE 0 END) AS activations_7d
    FROM hubspot_signups h
    JOIN product_activations p ON h.email = p.email
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
LEFT JOIN campaign_activations c ON a.campaign_id = c.utm_campaign"""

CREATE_TABLE_AD_CAMPAIGN_METRICS: Final = """CREATE TABLE IF NOT EXISTS ad_campaign_metrics (
    campaign_id VARCHAR NOT NULL,
    sync_date   DATE    NOT NULL,
    ad_platform VARCHAR CHECK(ad_platform IN ('google_ads', 'meta_ads', 'linkedin_ads', 'tiktok_ads', 'pinterest_ads')),
    spend_usd   DECIMAL(10, 2) NOT NULL CHECK(spend_usd >= 0),
    clicks      INTEGER        NOT NULL CHECK(clicks >= 0),
    impressions INTEGER        NOT NULL CHECK(impressions >= 0),
    PRIMARY KEY (campaign_id, sync_date)
);"""

CREATE_UNIQUE_INDEX_ADCM_CAMPAIGN_ID: Final = """CREATE UNIQUE INDEX IF NOT EXISTS uix_adcm_campaign_id
ON ad_campaign_metrics (campaign_id);"""

CREATE_INDEX_ACM_SYNC_DATE: Final = """CREATE INDEX IF NOT EXISTS idx_acm_sync_date
    ON ad_campaign_metrics (sync_date);"""

CREATE_INDEX_ACM_PLATFORM: Final = """CREATE INDEX IF NOT EXISTS idx_acm_platform
    ON ad_campaign_metrics (ad_platform, sync_date);"""

CREATE_TABLE_HUBSPOT_SIGNUPS: Final = """CREATE TABLE IF NOT EXISTS hubspot_signups (
    email            VARCHAR   PRIMARY KEY,
    utm_campaign     VARCHAR,
    signup_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (utm_campaign) REFERENCES ad_campaign_metrics(campaign_id)
);"""

CREATE_INDEX_HS_UTM_CAMPAIGN: Final = """CREATE INDEX IF NOT EXISTS idx_hs_utm_campaign
    ON hubspot_signups (utm_campaign);"""

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


def count_rows_query(table_name: str) -> str:
    """Return a safe COUNT query for a table name."""
    return f"SELECT COUNT(*) FROM {table_name}"


def table_info_query(table_name: str) -> str:
    """Return a PRAGMA table_info query for a table name."""
    return f"PRAGMA table_info({table_name})"
