import pytest

from openalex.cache.manager import clear_cache, _cache_managers
from openalex.api import _connection_pool


@pytest.fixture(autouse=True)
def reset_openalex_state():
    """Reset shared caches and connection pools around each test."""
    clear_cache()
    _cache_managers.clear()
    _connection_pool.clear()
    yield
    clear_cache()
    _cache_managers.clear()
    _connection_pool.clear()
