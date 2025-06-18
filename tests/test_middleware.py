import pytest
from unittest.mock import patch
import httpx

from openalex import OpenAlexConfig, Works
from openalex.middleware import RequestInterceptor, ResponseInterceptor


class HeaderInterceptor(RequestInterceptor):
    def process_request(self, request: httpx.Request) -> httpx.Request:
        request.headers["X-Test"] = "42"
        return request


class TitleUpperInterceptor(ResponseInterceptor):
    def process_response(self, response: httpx.Response) -> httpx.Response:
        data = response.json()
        if "title" in data:
            data["title"] = data["title"].upper()
        return httpx.Response(
            status_code=response.status_code,
            headers=response.headers,
            json=data,
            request=response.request,
        )


class OrderInterceptor(RequestInterceptor):
    def __init__(self, order: list[str], name: str) -> None:
        self.order = order
        self.name = name

    def process_request(self, request: httpx.Request) -> httpx.Request:
        self.order.append(self.name)
        return request


class TestMiddleware:
    def test_request_interceptor_adds_headers(self):
        config = OpenAlexConfig()
        config.middleware.request_interceptors.append(HeaderInterceptor())
        works = Works(config=config)

        mock_response = httpx.Response(
            200,
            json={"results": []},
            request=httpx.Request("GET", "https://api.openalex.org/works"),
        )

        with patch(
            "httpx.Client.send", return_value=mock_response
        ) as mock_send:
            works.get("W1")
            args, kwargs = mock_send.call_args
            sent_request = args[0]
            assert sent_request.headers.get("X-Test") == "42"

    def test_response_interceptor_transforms_data(self):
        config = OpenAlexConfig(cache_enabled=False)
        config.middleware.response_interceptors.append(TitleUpperInterceptor())
        works = Works(config=config)

        data = {
            "id": "https://openalex.org/W1",
            "display_name": "Test",
            "title": "original",
        }
        mock_response = httpx.Response(
            200,
            json=data,
            request=httpx.Request("GET", "https://api.openalex.org/works/W1"),
        )

        with patch("httpx.Client.send", return_value=mock_response):
            work = works.get("W1")
            assert work.title == "ORIGINAL"

    def test_multiple_interceptors_execute_in_order(self):
        order: list[str] = []
        config = OpenAlexConfig()
        config.middleware.request_interceptors.extend(
            [
                OrderInterceptor(order, "first"),
                OrderInterceptor(order, "second"),
            ]
        )
        works = Works(config=config)

        mock_response = httpx.Response(
            200,
            json={"results": []},
            request=httpx.Request("GET", "https://api.openalex.org/works"),
        )

        with patch("httpx.Client.send", return_value=mock_response):
            works.list()
            assert order == ["first", "second"]
