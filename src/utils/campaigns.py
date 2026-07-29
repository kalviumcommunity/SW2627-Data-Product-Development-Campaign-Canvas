from __future__ import annotations

import logging
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import sqlite3
import streamlit as st

logger = logging.getLogger(__name__)

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.database.queries import CAMPAIGN_OVERVIEW_QUERY

DATA_ROOT = Path(__file__).resolve().parents[2] / "data"

ACTIVATION_ARPU = 135.287876


def calculate_revenue(frame: pd.DataFrame) -> pd.Series:
    """Calculates standardized revenue derived from activations or returns existing revenue."""
    if frame.empty:
        return pd.Series(dtype=float)

    if "revenue" in frame.columns and not frame["revenue"].isnull().all():
        return frame["revenue"].fillna(0.0)

    activation_col = (
        "activations_7d"
        if "activations_7d" in frame.columns
        else "activations"
        if "activations" in frame.columns
        else "conversions"
        if "conversions" in frame.columns
        else "signups"
    )

    if activation_col in frame.columns:
        return frame[activation_col].fillna(0.0) * ACTIVATION_ARPU

    return pd.Series(0.0, index=frame.index)


@st.cache_data(show_spinner=False)
def load_campaign_data() -> tuple[pd.DataFrame, bool]:
    """Loads campaign activation daily dataset from the SQLite database.
    If the DB is not found, runs the ETL to populate it.
    Returns:
        (DataFrame, is_demo)
    """
    db_path = DATA_ROOT / "processed" / "marketing.db"

    if not db_path.exists():
        try:
            from src.etl_pipeline import run_etl
            run_etl()
        except Exception as e:
            logger.error(f"Error running ETL pipeline: {e}")

    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))

            df = pd.read_sql_query(CAMPAIGN_OVERVIEW_QUERY, conn)
            conn.close()

            campaign_names = {
                "c_google_brand": "Search - Brand",
                "c_google_nonbrand": "Search - Nonbrand",
                "c_meta_prospect": "Paid Social - Prospecting",
                "c_meta_retarget": "Paid Social - Retargeting",
                "c_youtube_awareness": "YouTube - Awareness",
                "c_display_remarketing": "Display - Remarketing",
            }
            df["campaign_name"] = df["campaign_id"].map(campaign_names).fillna(df["campaign_id"])
            df["revenue"] = calculate_revenue(df)
            return df, False
        except Exception as e:
            logger.error(f"Error reading from SQLite database: {e}")

    # Fallback to demo data if SQLite load fails
    df_demo = _build_demo_data()
    df_demo["revenue"] = calculate_revenue(df_demo)
    return df_demo, True


def add_marketing_dimensions(frame: pd.DataFrame) -> pd.DataFrame:
    """Adds reusable audience and channel dimensions for charting using vectorized operations."""
    if frame.empty:
        return frame.copy()

    enriched = frame.copy()
    c_id = (
        enriched["campaign_id"].astype(str).str.lower()
        if "campaign_id" in enriched.columns
        else pd.Series("", index=enriched.index)
    )
    c_name = (
        enriched["campaign_name"].astype(str).str.lower()
        if "campaign_name" in enriched.columns
        else c_id
    )
    platform = (
        enriched["ad_platform"].astype(str).str.lower()
        if "ad_platform" in enriched.columns
        else pd.Series("", index=enriched.index)
    )

    combined_c = c_id + " " + c_name

    # Channel mapping
    cond_channel = [
        combined_c.str.contains("email|mailchimp|klaviyo", regex=True),
        combined_c.str.contains("youtube|video", regex=True),
        combined_c.str.contains("display|remarketing", regex=True),
        combined_c.str.contains("brand|search", regex=True),
    ]
    choices_channel = ["Email", "Video", "Display", "Search"]
    enriched["channel"] = np.select(cond_channel, choices_channel, default="Social")

    # Platform grouped mapping
    cond_platform = [
        platform.str.contains("google", regex=False) | c_id.str.contains("google", regex=False),
        c_id.str.contains("youtube", regex=False),
        c_id.str.contains("display", regex=False),
        platform.str.contains("meta", regex=False) | c_id.str.contains("meta|instagram", regex=True),
        c_id.str.contains("linkedin", regex=False),
        c_id.str.contains("tiktok", regex=False),
        c_id.str.contains("pinterest", regex=False),
    ]
    choices_platform = ["Google", "YouTube", "Programmatic", "Meta", "LinkedIn", "TikTok", "Pinterest"]
    enriched["platform_grouped"] = np.select(cond_platform, choices_platform, default="Other")

    # Region mapping
    cond_region = [
        c_id.str.contains("brand", regex=False),
        c_id.str.contains("nonbrand|retarget", regex=True),
        c_id.str.contains("prospect|leadgen", regex=True),
    ]
    choices_region = ["US", "EU", "LATAM"]
    enriched["region"] = np.select(cond_region, choices_region, default="APAC")

    # Device mapping
    cond_device = [
        c_id.str.contains("brand|prospect|instagram|tiktok", regex=True)
    ]
    choices_device = ["Mobile"]
    enriched["device"] = np.select(cond_device, choices_device, default="Desktop")

    return enriched


def _build_demo_data() -> pd.DataFrame:
    """Builds a fallback demo DataFrame in case the database is completely empty."""
    import numpy as np

    rng = np.random.default_rng(7)
    dates = pd.date_range("2026-06-01", periods=14, freq="D")
    campaigns = [
        "c_google_brand",
        "c_google_nonbrand",
        "c_meta_prospect",
        "c_meta_retarget",
        "c_youtube_awareness",
    ]

    rows = []
    for date in dates:
        for index, campaign in enumerate(campaigns):
            spend = float(rng.uniform(120, 900) * (1 + index * 0.08))
            clicks = int(rng.uniform(120, 1900) * (1 + index * 0.05))
            impressions = int(clicks * rng.uniform(9.0, 20.0))
            signups = int(clicks * rng.uniform(0.04, 0.10))
            profile_completed = int(signups * rng.uniform(0.5, 0.8))
            activations = int(profile_completed * rng.uniform(0.4, 0.7))

            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "campaign_id": campaign,
                "campaign_name": campaign.replace("_", " ").title(),
                "ad_platform": "google_ads" if "google" in campaign else "meta_ads",
                "spend_usd": round(spend, 2),
                "clicks": clicks,
                "impressions": impressions,
                "signups": signups,
                "profile_completed": profile_completed,
                "campaign_run": activations,
                "activations_7d": activations,
            })

    return pd.DataFrame(rows)


def calculate_metrics(frame: pd.DataFrame) -> dict[str, float]:
    """Calculates high-level aggregated metrics from the campaign dataframe."""

    if frame.empty:
        return {
            "totalSpend": 0.0,
            "totalRevenue": 0.0,
            "totalSignups": 0.0,
            "totalActivations": 0.0,
            "wastedSpend": 0.0,
            "ctr": 0.0,
            "cpa": 0.0,
            "cpau": 0.0,
            "cvr": 0.0,
            "activationRate": 0.0,
            "roas": 0.0,
            "roi": 0.0,
            "aov": 0.0,
            "cpc": 0.0,
            "cpl": 0.0,
            "totalCampaigns": 0.0,
        }

    spend_col = "spend_usd" if "spend_usd" in frame.columns else "spend"

    signup_col = (
        "signups"
        if "signups" in frame.columns
        else "conversions"
        if "conversions" in frame.columns
        else "signup_count"
    )

    activation_col = (
        "activations_7d"
        if "activations_7d" in frame.columns
        else "activations"
        if "activations" in frame.columns
        else "conversions"
        if "conversions" in frame.columns
        else "activation_count"
    )

    campaign_col = (
        "campaign_id"
        if "campaign_id" in frame.columns
        else "campaign"
    )

    total_spend = (
        float(frame[spend_col].sum())
        if spend_col in frame.columns
        else 0.0
    )

    total_clicks = (
        float(frame["clicks"].sum())
        if "clicks" in frame.columns
        else 0.0
    )

    total_impressions = (
        float(frame["impressions"].sum())
        if "impressions" in frame.columns
        else 0.0
    )

    total_signups = (
        float(frame[signup_col].sum())
        if signup_col in frame.columns
        else 0.0
    )

    total_activations = (
        float(frame[activation_col].sum())
        if activation_col in frame.columns
        else 0.0
    )

    total_revenue = float(calculate_revenue(frame).sum())

    # Calculate wasted spend for campaigns with less than 10% activation rate
    if (
        campaign_col in frame.columns
        and spend_col in frame.columns
        and signup_col in frame.columns
        and activation_col in frame.columns
    ):
        campaign_groups = (
            frame.groupby(campaign_col)
            .agg(
                spend=(spend_col, "sum"),
                signups=(signup_col, "sum"),
                activations=(activation_col, "sum"),
            )
            .reset_index()
        )

        campaign_groups["activation_rate"] = (
            campaign_groups["activations"]
            / campaign_groups["signups"].replace(0, pd.NA)
        )

        wasted_spend = float(
            campaign_groups.loc[
                campaign_groups["activation_rate"] < 0.10,
                "spend",
            ].sum()
        )
    else:
        wasted_spend = 0.0

    total_campaigns = (
        float(frame[campaign_col].nunique())
        if campaign_col in frame.columns
        else 0.0
    )

    return {
        "totalCampaigns": total_campaigns,
        "totalSpend": total_spend,
        "totalRevenue": total_revenue,
        "totalSignups": total_signups,
        "totalActivations": total_activations,
        "wastedSpend": wasted_spend,
        "ctr": (
            total_clicks / total_impressions
            if total_impressions
            else 0.0
        ),
        "cpa": (
            total_spend / total_signups
            if total_signups
            else 0.0
        ),
        "cpau": (
            total_spend / total_activations
            if total_activations
            else 0.0
        ),
        "cvr": (
            total_signups / total_clicks
            if total_clicks
            else 0.0
        ),
        "activationRate": (
            total_activations / total_signups
            if total_signups
            else 0.0
        ),
        "roas": (
            total_revenue / total_spend
            if total_spend
            else 0.0
        ),
        "roi": (
            (total_revenue - total_spend) / total_spend * 100
            if total_spend
            else 0.0
        ),
        "aov": (
            total_revenue / total_activations
            if total_activations
            else 0.0
        ),
        "cpc": (
            total_spend / total_clicks
            if total_clicks
            else 0.0
        ),
        "cpl": (
            total_spend / total_signups
            if total_signups
            else 0.0
        ),
    }


def aggregate_by(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    """Aggregates metrics by a key (e.g., 'campaign_id', 'ad_platform', or 'campaign_name')."""
    if frame.empty:
        return pd.DataFrame()

    frame_copy = frame.copy()
    frame_copy["revenue"] = calculate_revenue(frame_copy)

    spend_col = "spend_usd" if "spend_usd" in frame_copy.columns else "spend"
    signup_col = (
        "signups"
        if "signups" in frame_copy.columns
        else ("conversions" if "conversions" in frame_copy.columns else "signup_count")
    )
    activation_col = (
        "activations_7d"
        if "activations_7d" in frame_copy.columns
        else ("activations" if "activations" in frame_copy.columns else "activation_count")
    )

    agg_dict = {
        spend_col: "sum",
        "clicks": "sum",
        "impressions": "sum",
        signup_col: "sum",
        activation_col: "sum",
        "revenue": "sum",
    }

    if "profile_completed" in frame_copy.columns:
        agg_dict["profile_completed"] = "sum"
    if "campaign_run" in frame_copy.columns:
        agg_dict["campaign_run"] = "sum"

    group_keys = [key]
    if key in ["campaign_id", "campaign_name", "campaign"]:
        for extra in ["campaign_id", "campaign_name", "campaign", "ad_platform"]:
            if extra in frame_copy.columns and extra not in group_keys:
                group_keys.append(extra)

    grouped = frame_copy.groupby(group_keys, dropna=False, as_index=False).agg(agg_dict)

    # Normalize column names for UI consistency
    grouped = grouped.rename(columns={
        key: "name",
        spend_col: "spend_usd",
        signup_col: "signups",
        activation_col: "activations_7d",
    })

    if "campaign_name" in grouped.columns and key != "campaign_name":
        grouped["display_name"] = grouped["campaign_name"]
    else:
        grouped["display_name"] = grouped["name"]

    # Calculate rates safely
    grouped["ctr"] = (grouped["clicks"] / grouped["impressions"]).fillna(0.0)
    grouped["cvr"] = (grouped["signups"] / grouped["clicks"]).fillna(0.0)
    grouped["activation_rate"] = (grouped["activations_7d"] / grouped["signups"]).fillna(0.0)
    grouped["cpau"] = (grouped["spend_usd"] / grouped["activations_7d"]).fillna(0.0)

    # Standardize column interfaces for downstream components
    grouped["totalSpend"] = grouped["spend_usd"]
    grouped["totalRevenue"] = grouped["revenue"]
    grouped["roas"] = (grouped["totalRevenue"] / grouped["spend_usd"]).fillna(0.0)
    grouped["totalConversions"] = grouped["activations_7d"]
    grouped["cpa"] = (grouped["spend_usd"] / grouped["signups"]).fillna(0.0)

    return grouped.sort_values(["spend_usd", "activations_7d"], ascending=[False, False]).reset_index(drop=True)


def fmt_currency(value: float) -> str:
    return f"${value:,.0f}" if abs(value) >= 1_000 else f"${value:,.2f}"


def fmt_num(value: float) -> str:
    return f"{value:,.0f}"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"