"""Pytest plugin for documentation test options."""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register command line options for documentation tests."""
    parser.addoption(
        "--docs",
        action="store_true",
        default=False,
        help="Run documentation tests",
    )
    parser.addoption(
        "--no-mock-api",
        action="store_true",
        default=False,
        help="Run documentation tests with real API calls",
    )

