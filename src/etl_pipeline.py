from __future__ import annotations


import logging
import sys
from pathlib import Path


import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


# Add root directory to path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


from src.database.db_client import get_connection, init_db
from src.database.queries import (
    DELETE_AD_CAMPAIGN_METRICS,
    DELETE_HUBSPOT_SIGNUPS,
    DELETE_PRODUCT_ACTIVATIONS,
)




def generate_mock_data() -> None:
    """Generates mock raw datasets corresponding to the PRD specifications."""
    logger.info("Generating mock raw datasets...")
    rng = np.random.default_rng(42)


    # 1. Campaigns Definition
    campaigns = [
        {
            "id": "c_google_brand",
            "name": "Search - Brand",
            "platform": "google_ads",
            "quality_coef": 1.2,
            "cost_coef": 1.0,
        },
        {
            "id": "c_google_nonbrand",
            "name": "Search - Nonbrand",
            "platform": "google_ads",
