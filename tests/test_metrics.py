import httpx
import pytest
from unittest.mock import patch

from openalex import OpenAlexConfig, Works
from tests.base import IsolatedTestCase


class TestMetrics(IsolatedTestCase):
    @pytest.mark.isolated
    def test_metrics_collection_when_enabled(self):

        config = OpenAlexConfig(
            collect_metrics=True,
            retry_enabled=False,
            cache_enabled=False,
            email="enabled@example.com",
        )
        works = Works(config=config)

        resp1 = httpx.Response(
            200,
            json={"id": "https://openalex.org/W2000000001", "title": "x"},
            request=httpx.Request(
                "GET", "https://api.openalex.org/works/W2000000001"
            ),
        )
        resp2 = httpx.Response(
            200,
            json={"id": "https://openalex.org/W2000000002", "title": "y"},
            request=httpx.Request(
                "GET", "https://api.openalex.org/works/W2000000002"
            ),
        )

        with patch("httpx.Client.request", side_effect=[resp1, resp2]):
            works.get("W2000000001")
            works.get("W2000000002")

        report = works.get_metrics()

        assert report is not None
        assert report.total_requests == 2
        assert report.requests_by_endpoint["works"] == 2

    def test_no_metrics_when_disabled(self):
        config = OpenAlexConfig(
            collect_metrics=False,
            retry_enabled=False,
            email="disabled@example.com",
        )
        works = Works(config=config)

        resp = httpx.Response(
            200,
            json={"id": "https://openalex.org/W2000000001"},
            request=httpx.Request(
                "GET", "https://api.openalex.org/works/W2000000001"
            ),
        )

        with patch("httpx.Client.request", return_value=resp):
            works.get("W2000000001")

        report = works.get_metrics()
        assert report is None

    @pytest.mark.isolated
    def test_cache_metrics_tracked(self):

        config = OpenAlexConfig(
            collect_metrics=True,
            cache_enabled=True,
            retry_enabled=False,
            email="cache@example.com",
        )
        works = Works(config=config)

        resp = httpx.Response(
            200,
            json={"id": "https://openalex.org/W2000000001"},
            request=httpx.Request(
                "GET", "https://api.openalex.org/works/W2000000001"
            ),
        )

        with patch("httpx.Client.request", return_value=resp) as mock_request:
            works.get("W2000000001")
            works.get("W2000000001")
            assert mock_request.call_count == 1

        report = works.get_metrics()
        assert report.cache_hits == 1
        assert report.cache_misses == 1
        assert report.cache_hit_rate == 0.5
