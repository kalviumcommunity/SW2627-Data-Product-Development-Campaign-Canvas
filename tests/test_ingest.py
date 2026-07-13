import sys
from pathlib import Path
import pandas as pd
import pytest

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data, compute_kpis, aggregate_by

def test_load_campaign_data():
    """Test that campaign dataset load function returns a DataFrame and a boolean indicator."""
    df, is_demo = load_campaign_data()
    assert isinstance(df, pd.DataFrame)
    assert isinstance(is_demo, bool)
    if not df.empty:
        required_cols = ["date", "campaign_id", "spend_usd", "clicks", "impressions", "signups", "activations_7d"]
        for col in required_cols:
            assert col in df.columns

def test_compute_kpis():
    """Test computation of marketing and activation KPIs."""
    mock_data = pd.DataFrame([
        {
            "campaign_id": "c1", "campaign_name": "Camp 1", "ad_platform": "google_ads", "date": "2026-06-01",
            "spend_usd": 100.0, "clicks": 200, "impressions": 1000, "signups": 20, "profile_completed": 5, "campaign_run": 5, "activations_7d": 5
        },
        {
            "campaign_id": "c2", "campaign_name": "Camp 2", "ad_platform": "meta_ads", "date": "2026-06-01",
            "spend_usd": 200.0, "clicks": 100, "impressions": 500, "signups": 5, "profile_completed": 0, "campaign_run": 0, "activations_7d": 0
        }
    ])
    
    kpis = compute_kpis(mock_data)
    assert kpis["totalCampaigns"] == 2.0
    assert kpis["totalSpend"] == 300.0
    assert kpis["totalSignups"] == 25.0
    assert kpis["totalActivations"] == 5.0
    assert kpis["ctr"] == 300 / 1500
    assert kpis["cvr"] == 25 / 300
    # Camp 2 has 0 activations / 5 signups = 0% activation rate (<10%). So its spend of 200.0 is wasted.
    # Camp 1 has 5 activations / 20 signups = 25% activation rate (>=10%). Not wasted.
    assert kpis["wastedSpend"] == 200.0

def test_aggregate_by_campaign():
    """Test aggregation groupings."""
    mock_data = pd.DataFrame([
        {
            "campaign_id": "c1", "campaign_name": "Camp 1", "ad_platform": "google_ads", "date": "2026-06-01",
            "spend_usd": 100.0, "clicks": 200, "impressions": 1000, "signups": 20, "profile_completed": 5, "campaign_run": 5, "activations_7d": 5
        },
        {
            "campaign_id": "c1", "campaign_name": "Camp 1", "ad_platform": "google_ads", "date": "2026-06-02",
            "spend_usd": 50.0, "clicks": 100, "impressions": 500, "signups": 10, "profile_completed": 2, "campaign_run": 2, "activations_7d": 2
        }
    ])
    
    aggregated = aggregate_by(mock_data, "campaign_id")
    assert not aggregated.empty
    assert aggregated.loc[0, "name"] == "c1"
    assert aggregated.loc[0, "spend_usd"] == 150.0
    assert aggregated.loc[0, "signups"] == 30
    assert aggregated.loc[0, "activations_7d"] == 7
