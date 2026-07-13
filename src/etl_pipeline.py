import sys
from pathlib import Path
import numpy as np
import pandas as pd
import sqlite3

# Add root directory to path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.database.db_client import get_connection, init_db

def generate_mock_data():
    """Generates mock raw datasets corresponding to the PRD specifications."""
    print("Generating mock raw datasets...")
    rng = np.random.default_rng(42)
    
    # 1. Campaigns Definition
    campaigns = [
        {"id": "c_google_brand", "name": "Search - Brand", "platform": "google_ads", "quality_coef": 1.2, "cost_coef": 1.0},
        {"id": "c_google_nonbrand", "name": "Search - Nonbrand", "platform": "google_ads", "quality_coef": 0.8, "cost_coef": 1.1},
        {"id": "c_meta_prospect", "name": "Paid Social - Prospecting", "platform": "meta_ads", "quality_coef": 0.55, "cost_coef": 1.3},
        {"id": "c_meta_retarget", "name": "Paid Social - Retargeting", "platform": "meta_ads", "quality_coef": 1.4, "cost_coef": 0.9},
        {"id": "c_youtube_awareness", "name": "YouTube - Awareness", "platform": "google_ads", "quality_coef": 0.08, "cost_coef": 1.5},
        {"id": "c_display_remarketing", "name": "Display - Remarketing", "platform": "google_ads", "quality_coef": 0.05, "cost_coef": 1.2},
    ]

    dates = pd.date_range("2026-06-01", "2026-06-30", freq="D")
    
    # Generate ad_campaign_metrics
    ad_rows = []
    for date in dates:
        for c in campaigns:
            spend = float(rng.uniform(50, 600) * c["cost_coef"])
            impressions = int(spend * rng.uniform(80, 150))
            clicks = int(impressions * rng.uniform(0.01, 0.05))
            
            ad_rows.append({
                "campaign_id": c["id"],
                "ad_platform": c["platform"],
                "spend_usd": max(0.0, round(spend, 2)),
                "clicks": max(0, clicks),
                "impressions": max(0, impressions),
                "sync_date": date.strftime("%Y-%m-%d")
            })
            
    df_ads = pd.DataFrame(ad_rows)
    
    # Generate signups & activations
    signup_rows = []
    activation_rows = []
    user_idx = 1000
    
    for idx, ad in enumerate(ad_rows):
        c_id = ad["campaign_id"]
        c_info = next(item for item in campaigns if item["id"] == c_id)
        
        signup_rate = 0.08 * c_info["quality_coef"]
        num_signups = int(ad["clicks"] * signup_rate)
        num_signups = max(0, num_signups + rng.choice([-1, 0, 1]))
        
        for _ in range(num_signups):
            email = f"user_{user_idx}@gmail.com"
            # Add some test emails
            if rng.uniform(0, 1) < 0.02:
                email = f"test_{user_idx}@company.com"
            elif rng.uniform(0, 1) < 0.02:
                email = f"user_test_{user_idx}@gmail.com"
                
            user_id = f"usr_{user_idx}"
            base_date = pd.to_datetime(ad["sync_date"])
            signup_time = base_date + pd.to_timedelta(rng.uniform(0, 23.9), unit="h")
            
            # Missing UTM mapping check (4% missing utm_campaign)
            utm_campaign = c_id
            if rng.uniform(0, 1) < 0.04:
                utm_campaign = None
                
            signup_rows.append({
                "email": email,
                "utm_campaign": utm_campaign,
                "signup_timestamp": signup_time.isoformat()
            })
            
            activation_rate = 0.58 * c_info["quality_coef"]
            if c_id in ["c_youtube_awareness", "c_display_remarketing"]:
                activation_rate = 0.07  # Low activation performers
                
            is_profile_completed = rng.uniform(0, 1) < (activation_rate * 1.3)
            is_campaign_run = rng.uniform(0, 1) < (activation_rate * 1.1)
            activated = is_profile_completed and is_campaign_run
            
            activation_time = None
            if activated:
                days_to_activate = rng.uniform(0.1, 10.0)
                act_time = signup_time + pd.to_timedelta(days_to_activate, unit="d")
                activation_time = act_time.isoformat()
                
            activation_rows.append({
                "user_id": user_id,
                "email": email,
                "signup_timestamp": signup_time.isoformat(),
                "activation_timestamp": activation_time,
                "profile_completed": int(is_profile_completed),
                "campaign_run": int(is_campaign_run)
            })
            
            user_idx += 1
            
    df_signups = pd.DataFrame(signup_rows)
    df_activations = pd.DataFrame(activation_rows)
    
    raw_dir = Path(root_dir) / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    df_ads.to_csv(raw_dir / "ad_campaign_metrics.csv", index=False)
    df_signups.to_csv(raw_dir / "hubspot_signups.csv", index=False)
    df_activations.to_csv(raw_dir / "product_activations.csv", index=False)
    print(f"Generated raw data: {len(df_ads)} ads, {len(df_signups)} signups, {len(df_activations)} activations.")


def run_etl():
    """Runs the ETL cleaning and loads into SQLite database tables."""
    raw_dir = Path(root_dir) / "data" / "raw"
    
    if not (raw_dir / "ad_campaign_metrics.csv").exists():
        generate_mock_data()
        
    print("Running database schema init...")
    init_db()
    
    print("Loading raw files and cleaning...")
    df_ads = pd.read_csv(raw_dir / "ad_campaign_metrics.csv")
    df_signups = pd.read_csv(raw_dir / "hubspot_signups.csv")
    df_activations = pd.read_csv(raw_dir / "product_activations.csv")
    
    # 1. Clean Signups: Filter out test signups
    df_signups_clean = df_signups[
        (~df_signups["email"].str.endswith("@company.com")) & 
        (~df_signups["email"].str.contains("test", case=False))
    ].copy()
    
    # Handle attribution fallback: null utm_campaign -> 'Organic/Unknown'
    # For SQLite integrity, if the foreign key checks are on, 'Organic/Unknown' must exist in ad_campaign_metrics,
    # or we set utm_campaign to NULL so it's a valid nullable FK, or we insert 'Organic/Unknown' dummy campaign.
    # Setting it to NULL is standard for nullable foreign keys.
    df_signups_clean["utm_campaign"] = df_signups_clean["utm_campaign"].replace({np.nan: None})
    
    # 2. Clean Activations: Filter out test activations
    df_activations_clean = df_activations[
        (~df_activations["email"].str.endswith("@company.com")) & 
        (~df_activations["email"].str.contains("test", case=False))
    ].copy()
    
    # Convert timestamps
    df_activations_clean["signup_timestamp"] = pd.to_datetime(df_activations_clean["signup_timestamp"])
    df_activations_clean["activation_timestamp"] = pd.to_datetime(df_activations_clean["activation_timestamp"])
    
    # Ensure signup_timestamp <= activation_timestamp
    invalid_mask = (df_activations_clean["activation_timestamp"] < df_activations_clean["signup_timestamp"])
    # Set activation_timestamp to None or shift it for invalid records
    df_activations_clean.loc[invalid_mask, "activation_timestamp"] = None
    
    # Format back to ISO strings for SQLite storage
    df_activations_clean["signup_timestamp"] = df_activations_clean["signup_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df_activations_clean["activation_timestamp"] = df_activations_clean["activation_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").replace({np.nan: None})
    
    # 3. Clean Ad metrics: Aggregate by campaign_id to satisfy primary key constraint
    df_ads_clean = df_ads.copy()
    df_ads_clean["spend_usd"] = df_ads_clean["spend_usd"].clip(lower=0.0)
    df_ads_clean["clicks"] = df_ads_clean["clicks"].clip(lower=0)
    df_ads_clean["impressions"] = df_ads_clean["impressions"].clip(lower=0)
    
    df_ads_clean = df_ads_clean.groupby(["campaign_id", "ad_platform"], as_index=False).agg({
        "spend_usd": "sum",
        "clicks": "sum",
        "impressions": "sum",
        "sync_date": "max" # Keep the latest sync date
    })
    
    # Write to SQLite
    print("Writing records to SQLite tables...")
    conn = get_connection()
    
    # Disable foreign keys temporarily during load to handle forward declarations easily
    conn.execute("PRAGMA foreign_keys = OFF;")
    
    # Empty tables first to avoid unique constraint violations on re-run
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product_activations;")
    cursor.execute("DELETE FROM hubspot_signups;")
    cursor.execute("DELETE FROM ad_campaign_metrics;")
    conn.commit()
    
    # Write tables
    df_ads_clean.to_sql("ad_campaign_metrics", conn, if_exists="append", index=False)
    df_signups_clean.to_sql("hubspot_signups", conn, if_exists="append", index=False)
    df_activations_clean.to_sql("product_activations", conn, if_exists="append", index=False)
    
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.close()
    
    print("ETL successfully completed and loaded to SQLite!")

if __name__ == "__main__":
    run_etl()
