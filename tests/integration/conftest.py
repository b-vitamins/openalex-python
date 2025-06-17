import pytest

from openalex.cache.manager import clear_cache, _cache_managers
from openalex.api import _connection_pool


@pytest.fixture(autouse=True)
def reset_openalex_state():
    """Reset shared caches and connection pools around each test."""
    clear_cache()
    _cache_managers.clear()
    # replace with new dict to avoid id reuse issues
    import openalex.cache.manager as manager_module

    manager_module._cache_managers = {}
    _connection_pool.clear()
    yield
    clear_cache()
    _cache_managers.clear()
    manager_module._cache_managers = {}
    _connection_pool.clear()
