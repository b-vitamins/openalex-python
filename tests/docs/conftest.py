import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register command line options."""
    parser.addoption(
        "--docs",
        action="store_true",
        default=False,
        help="Run documentation tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for documentation tests."""
    config.addinivalue_line("markers", "docs: mark test as documentation test")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip docs tests unless --docs flag is used."""
    if config.getoption("--docs"):
        return

    skip_docs = pytest.mark.skip(reason="need --docs option to run")
    for item in items:
        if "docs" in item.keywords:
            item.add_marker(skip_docs)


@pytest.fixture
def mock_api_responses() -> None:
    """No-op fixture to allow real API calls."""
    return
