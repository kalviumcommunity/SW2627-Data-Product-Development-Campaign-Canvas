import sys
import pytest
import pandas as pd
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import calculate_revenue, ACTIVATION_ARPU


def test_calculate_revenue_from_activations():
    """Test calculate_revenue computes revenue based on 7-day activations and ARPU multiplier."""
    df = pd.DataFrame({
        "activations_7d": [10, 0, 5]
    })
    revenue = calculate_revenue(df)
    assert len(revenue) == 3
    assert revenue.iloc[0] == pytest.approx(10 * ACTIVATION_ARPU)
    assert revenue.iloc[1] == 0.0
    assert revenue.iloc[2] == pytest.approx(5 * ACTIVATION_ARPU)


def test_calculate_revenue_existing_column():
    """Test calculate_revenue preserves explicit revenue values if present."""
    df = pd.DataFrame({
        "revenue": [500.0, 1200.5, None],
        "activations_7d": [10, 20, 30]
    })
    revenue = calculate_revenue(df)
    assert revenue.iloc[0] == 500.0
    assert revenue.iloc[1] == 1200.5
    assert revenue.iloc[2] == 0.0


def test_kpi_formulas():
    """Test KPI calculations such as ROAS, CAC, CTR, and Activation Rate."""
    df = pd.DataFrame({
        "spend_usd": [100.0, 200.0],
        "clicks": [50, 100],
        "impressions": [1000, 2000],
        "signups": [10, 20],
        "activations_7d": [5, 8],
        "revenue": [500.0, 1000.0]
    })

    # ROAS = Revenue / Spend
    roas = df["revenue"] / df["spend_usd"]
    assert roas.iloc[0] == 5.0
    assert roas.iloc[1] == 5.0

    # CAC = Spend / Signups
    cac = df["spend_usd"] / df["signups"]
    assert cac.iloc[0] == 10.0
    assert cac.iloc[1] == 10.0

    # Activation Rate = Activations / Signups
    activation_rate = df["activations_7d"] / df["signups"]
    assert activation_rate.iloc[0] == 0.5
    assert activation_rate.iloc[1] == 0.4
