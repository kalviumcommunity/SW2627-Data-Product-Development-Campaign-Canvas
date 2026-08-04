import pandas as pd

from src.utils.campaigns import fmt_currency, fmt_num, fmt_pct


def test_formatters_handle_missing_values_safely():
    """Formatting helpers should not crash when the UI passes missing values."""
    assert fmt_currency(None) == "$0.00"
    assert fmt_currency(float("nan")) == "$0.00"
    assert fmt_num(pd.NA) == "0"
    assert fmt_pct(float("nan")) == "0.0%"
