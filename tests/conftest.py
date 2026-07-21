"""
Pytest configuration and shared fixtures.
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import pytest
from tests.fixtures import test_db_path, test_db_connection, TestDataFactory


pytest_plugins = ["tests.fixtures"]


@pytest.fixture(scope="session")
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )

