from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import sqlite3

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

DATA_ROOT = Path(__file__).resolve().parents[2] / "data"

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
            print(f"Error running ETL pipeline: {e}")
            
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            
            # Query with SQL Joins to generate the unified campaign overview
            query = """
            WITH campaign_signups AS (
                SELECT 
                    utm_campaign,
                    COUNT(*) as signups
                FROM hubspot_signups
                GROUP BY utm_campaign
            ),
            campaign_activations AS (
                SELECT 
                    h.utm_campaign,
                    SUM(p.profile_completed) as profile_completed,
                    SUM(p.campaign_run) as campaign_run,
                    SUM(CASE WHEN p.profile_completed = 1 AND p.campaign_run = 1 AND 
                             (julianday(p.activation_timestamp) - julianday(p.signup_timestamp)) <= 7.0 THEN 1 ELSE 0 END) as activations_7d
                FROM hubspot_signups h
                JOIN product_activations p ON h.email = p.email
                GROUP BY h.utm_campaign
            )
            SELECT 
                a.sync_date as date,
                a.campaign_id,
                a.ad_platform,
                a.spend_usd,
                a.clicks,
                a.impressions,
                COALESCE(s.signups, 0) as signups,
                COALESCE(c.profile_completed, 0) as profile_completed,
                COALESCE(c.campaign_run, 0) as campaign_run,
                COALESCE(c.activations_7d, 0) as activations_7d
            FROM ad_campaign_metrics a
            LEFT JOIN campaign_signups s ON a.campaign_id = s.utm_campaign
            LEFT JOIN campaign_activations c ON a.campaign_id = c.utm_campaign
            """
            
            df = pd.read_sql_query(query, conn)
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
            df["revenue"] = df["activations_7d"] * 135.287876
            return df, False
        except Exception as e:
            print(f"Error reading from SQLite database: {e}")
            
    # Fallback to demo data if SQLite load fails
    df_demo = _build_demo_data()
    df_demo["revenue"] = df_demo["activations_7d"] * 135.287876
    return df_demo, True

def _build_demo_data() -> pd.DataFrame:
    """Builds a fallback demo DataFrame in case the database is completely empty."""
    import numpy as np
    rng = np.random.default_rng(7)
    dates = pd.date_range("2026-06-01", periods=14, freq="D")
    campaigns = [
        "c_google_brand", "c_google_nonbrand", "c_meta_prospect", "c_meta_retarget", "c_youtube_awareness"
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
                "activations_7d": activations
            })
            
    return pd.DataFrame(rows)

def compute_kpis(frame: pd.DataFrame) -> dict[str, float]:
    """Computes high-level aggregated KPIs from the campaign dataframe."""
    if frame.empty:
        return {
            "totalSpend": 0.0,
            "totalSignups": 0.0,
            "totalActivations": 0.0,
            "wastedSpend": 0.0,
            "ctr": 0.0,
            "cpa": 0.0,
            "cpau": 0.0,
            "cvr": 0.0,
            "activationRate": 0.0,
            "totalCampaigns": 0.0
        }

    # Column mappings to support both original schema and SQL join schema
    spend_col = "spend_usd" if "spend_usd" in frame.columns else "spend"
    signup_col = "signups" if "signups" in frame.columns else ("conversions" if "conversions" in frame.columns else "signup_count")
    activation_col = "activations_7d" if "activations_7d" in frame.columns else ("conversions" if "conversions" in frame.columns else "activation_count")
    campaign_col = "campaign_id" if "campaign_id" in frame.columns else "campaign"

    total_spend = float(frame[spend_col].sum())
    total_clicks = float(frame["clicks"].sum())
    total_impressions = float(frame["impressions"].sum())
    total_signups = float(frame[signup_col].sum())
    total_activations = float(frame[activation_col].sum())
    
    # Calculate Wasted Spend at the campaign level (<10% downstream activation rate)
    campaign_groups = frame.groupby(campaign_col).agg(
        spend=(spend_col, "sum"),
        signups=(signup_col, "sum"),
        activations=(activation_col, "sum")
    ).reset_index()
    
    campaign_groups["activation_rate"] = campaign_groups["activations"] / campaign_groups["signups"]
    wasted_spend = float(campaign_groups[campaign_groups["activation_rate"] < 0.10]["spend"].sum())

    return {
        "totalCampaigns": float(frame[campaign_col].nunique()),
        "totalSpend": total_spend,
        "totalSignups": total_signups,
        "totalActivations": total_activations,
        "wastedSpend": wasted_spend,
        "ctr": total_clicks / total_impressions if total_impressions else 0.0,
        "cpa": total_spend / total_signups if total_signups else 0.0,
        "cpau": total_spend / total_activations if total_activations else 0.0,
        "cvr": total_signups / total_clicks if total_clicks else 0.0,
        "activationRate": total_activations / total_signups if total_signups else 0.0,
    }

def aggregate_by(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    """Aggregates metrics by a key (e.g., 'campaign_id', 'ad_platform', or 'campaign_name')."""
    if frame.empty:
        return pd.DataFrame()
        
    spend_col = "spend_usd" if "spend_usd" in frame.columns else "spend"
    signup_col = "signups" if "signups" in frame.columns else ("conversions" if "conversions" in frame.columns else "signup_count")
    activation_col = "activations_7d" if "activations_7d" in frame.columns else ("conversions" if "conversions" in frame.columns else "activation_count")
    
    agg_dict = {
        spend_col: "sum",
        "clicks": "sum",
        "impressions": "sum",
        signup_col: "sum",
        activation_col: "sum"
    }
    
    if "revenue" in frame.columns:
        agg_dict["revenue"] = "sum"
    if "profile_completed" in frame.columns:
        agg_dict["profile_completed"] = "sum"
    if "campaign_run" in frame.columns:
        agg_dict["campaign_run"] = "sum"
        
    group_keys = [key]
    if key in ["campaign_id", "campaign_name", "campaign"]:
        for extra in ["campaign_id", "campaign_name", "campaign", "ad_platform"]:
            if extra in frame.columns and extra not in group_keys:
                group_keys.append(extra)
                
    grouped = frame.groupby(group_keys, dropna=False, as_index=False).agg(agg_dict)
    
    # Normalize column names for UI consistency
    grouped = grouped.rename(columns={
        key: "name",
        spend_col: "spend_usd",
        signup_col: "signups",
        activation_col: "activations_7d"
    })
    
    if "campaign_name" in grouped.columns and key != "campaign_name":
        grouped["display_name"] = grouped["campaign_name"]
    else:
        grouped["display_name"] = grouped["name"]
        
    # Calculate rates
    grouped["ctr"] = grouped["clicks"] / grouped["impressions"]
    grouped["cvr"] = grouped["signups"] / grouped["clicks"]
    grouped["activation_rate"] = grouped["activations_7d"] / grouped["signups"]
    grouped["cpau"] = grouped["spend_usd"] / grouped["activations_7d"]
    
    # Fill division by zero nulls
    grouped["ctr"] = grouped["ctr"].fillna(0.0)
    grouped["cvr"] = grouped["cvr"].fillna(0.0)
    grouped["activation_rate"] = grouped["activation_rate"].fillna(0.0)
    grouped["cpau"] = grouped["cpau"].fillna(0.0)
    
    # Maintain column interfaces expected by original tests
    if "spend" not in grouped.columns:
        grouped["totalSpend"] = grouped["spend_usd"]
        if "revenue" in grouped.columns:
            grouped["totalRevenue"] = grouped["revenue"]
            grouped["roas"] = grouped["revenue"] / grouped["spend_usd"]
        else:
            grouped["totalRevenue"] = grouped["spend_usd"] * 1.5
            grouped["roas"] = 1.5
        grouped["totalConversions"] = grouped["activations_7d"]
        grouped["cpa"] = grouped["spend_usd"] / grouped["activations_7d"]
        
    return grouped.sort_values(["spend_usd", "activations_7d"], ascending=[False, False]).reset_index(drop=True)

def fmt_currency(value: float) -> str:
    return f"${value:,.0f}" if abs(value) >= 1_000 else f"${value:,.2f}"

def fmt_num(value: float) -> str:
    return f"{value:,.0f}"

def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"