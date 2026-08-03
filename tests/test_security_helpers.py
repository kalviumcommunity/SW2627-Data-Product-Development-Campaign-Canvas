import pytest

from src.utils.clerk_auth import initialize_auth_state
from src.utils.sql_safety import validate_sql_query


def test_initialize_auth_state_sets_safe_defaults():
    state = {}

    initialize_auth_state(state)

    assert state["logged_in"] is False
    assert state["email"] == ""
    assert state["name"] == ""
    assert state["theme"] == "dark"


def test_validate_sql_query_allows_read_only_select():
    normalized = validate_sql_query("SELECT * FROM campaigns")

    assert normalized == "SELECT * FROM campaigns"


def test_validate_sql_query_rejects_dangerous_statements():
    with pytest.raises(ValueError, match="read-only"):
        validate_sql_query("DELETE FROM campaigns")

    with pytest.raises(ValueError, match="read-only"):
        validate_sql_query("ALTER TABLE campaigns ADD COLUMN hacker INT")

    with pytest.raises(ValueError, match="read-only"):
        validate_sql_query("DROP TABLE campaigns")


def test_validate_sql_query_rejects_multiple_statements():
    with pytest.raises(ValueError, match="single read-only statement"):
        validate_sql_query("SELECT 1; DROP TABLE campaigns;")

