import pytest


def pytest_configure(config):
    """Register custom markers for documentation tests."""
    config.addinivalue_line("markers", "docs: mark test as documentation test")


@pytest.fixture
def mock_api_responses():
    """No-op fixture to allow real API calls."""
    yield
